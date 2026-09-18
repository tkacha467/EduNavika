import pytest
from datetime import datetime, timedelta, timezone
from backend.app.models import LearningEvent, EventType
from backend.app.models import TopicPerformance
from backend.app.domain.prediction import (
    PointInTimeFeatures,
    PointInTimeFeatureExtractor,
    CausalDatasetGenerator,
    CutoffSelectionConfig,
)


def _make_event(
    student_id: str,
    topic_id: str,
    timestamp: datetime,
    event_type: EventType = EventType.PRACTICE,
    correctness: bool = True,
    score: float = 100.0,
    response_time_ms: int = 5000,
    hint_used: bool = False,
    event_id: str = None,
) -> LearningEvent:
    e = LearningEvent(
        student_id=student_id,
        topic_id=topic_id,
        event_type=event_type,
        timestamp=timestamp,
        correctness=correctness,
        score=score,
        response_time_ms=response_time_ms,
        hint_used=hint_used,
    )
    if event_id:
        e.id = event_id
    return e


def test_leakage_future_events_cannot_affect_features_at_cutoff_t():
    """
    Test 1 (Leakage Invariant):
    Verifies that future events occurring after cutoff T cannot alter
    the feature vector X(T) in any way.
    """
    now = datetime(2026, 9, 15, 12, 0, 0, tzinfo=timezone.utc)
    t_cutoff = now

    # Past events: 3 events at T - 3h, T - 2h, T - 1h
    past_events = [
        _make_event("std_1", "top_1", now - timedelta(hours=3), correctness=True, response_time_ms=4000),
        _make_event("std_1", "top_1", now - timedelta(hours=2), correctness=True, response_time_ms=4500),
        _make_event("std_1", "top_1", now - timedelta(hours=1), correctness=False, response_time_ms=6000),
    ]

    feat_before = PointInTimeFeatureExtractor.extract(
        student_id="std_1",
        topic_id="top_1",
        cutoff_timestamp=t_cutoff,
        events=past_events,
    )

    # Future events: 5 dramatic events occurring after T (failures, latency spikes, different topics)
    future_events = [
        _make_event("std_1", "top_1", now + timedelta(hours=1), correctness=False, response_time_ms=90000),
        _make_event("std_1", "top_1", now + timedelta(hours=2), correctness=False, response_time_ms=95000),
        _make_event("std_1", "top_1", now + timedelta(days=1), correctness=True, response_time_ms=3000),
        _make_event("std_1", "top_2", now + timedelta(days=2), correctness=True, response_time_ms=2000),
    ]

    combined_events = past_events + future_events

    feat_after = PointInTimeFeatureExtractor.extract(
        student_id="std_1",
        topic_id="top_1",
        cutoff_timestamp=t_cutoff,
        events=combined_events,
    )

    # Every single field in feat_before must match feat_after exactly
    assert feat_before.to_dict() == feat_after.to_dict()
    assert feat_after.cumulative_topic_attempts == 3
    assert feat_after.cumulative_topic_correct_count == 2
    assert feat_after.cumulative_topic_accuracy == 66.67


def test_leakage_future_correctness_cannot_appear_inside_x_t():
    """
    Test 2 (Leakage Invariant):
    Verifies that the upcoming correctness on a target attempt is not leaked into X(T).
    """
    base_time = datetime(2026, 9, 10, 10, 0, 0, tzinfo=timezone.utc)
    target_time = base_time + timedelta(days=5)
    cutoff_time = target_time - timedelta(seconds=1)

    # History: 100% correct (3/3)
    history = [
        _make_event("std_1", "top_1", base_time + timedelta(hours=i), correctness=True, score=100.0)
        for i in range(3)
    ]
    # Upcoming target event at target_time: Failed (correctness=False)
    target_event = _make_event("std_1", "top_1", target_time, correctness=False, score=0.0)

    all_events = history + [target_event]

    feat = PointInTimeFeatureExtractor.extract(
        student_id="std_1",
        topic_id="top_1",
        cutoff_timestamp=cutoff_time,
        events=all_events,
    )

    # Features at cutoff MUST show 100% accuracy and 3 attempts (NOT 75% or 4 attempts)
    assert feat.cumulative_topic_attempts == 3
    assert feat.cumulative_topic_correct_count == 3
    assert feat.cumulative_topic_accuracy == 100.0
    assert feat.ewma_topic_accuracy == 100.0


def test_leakage_mutable_topic_performance_cannot_influence_historical_features(db_session, seed_data):
    """
    Test 3 (Isolation Invariant):
    Verifies that mutations to the live TopicPerformance table have zero effect
    on historical feature extraction.
    """
    student = seed_data["student_profile"]
    topic = seed_data["topic"]
    now = datetime.now(timezone.utc)

    # 1. Add 2 historical learning events
    db_session.add(_make_event(student.id, topic.id, now - timedelta(days=2), correctness=True, response_time_ms=4000))
    db_session.add(_make_event(student.id, topic.id, now - timedelta(days=1), correctness=False, response_time_ms=8000))
    db_session.commit()

    # 2. Extract features at cutoff (T = now)
    feat_clean = PointInTimeFeatureExtractor.extract_from_db(
        db=db_session,
        student_id=student.id,
        topic_id=topic.id,
        cutoff_timestamp=now,
    )
    assert feat_clean.cumulative_topic_attempts == 2
    assert feat_clean.cumulative_topic_accuracy == 50.0

    # 3. Deliberately corrupt mutable TopicPerformance with leaked/future data
    corrupted_perf = TopicPerformance(
        student_id=student.id,
        topic_id=topic.id,
        total_attempts=999,
        correct_attempts=999,
        accuracy=100.0,
        mastery_state="MASTERED",
        average_response_time=123.45,
    )
    db_session.add(corrupted_perf)
    db_session.commit()

    # 4. Extract features again from DB
    feat_after_corruption = PointInTimeFeatureExtractor.extract_from_db(
        db=db_session,
        student_id=student.id,
        topic_id=topic.id,
        cutoff_timestamp=now,
    )

    # Historical feature extractor must ignore TopicPerformance completely
    assert feat_after_corruption.cumulative_topic_attempts == 2
    assert feat_after_corruption.cumulative_topic_accuracy == 50.0
    assert feat_after_corruption.mean_response_time_ms == 6000.0
    assert feat_after_corruption.to_dict() == feat_clean.to_dict()


def test_determinism_same_event_history_produces_identical_features():
    """
    Test 4 (Determinism Invariant):
    Verifies that extracting features twice (even if raw input order is shuffled)
    produces bit-for-bit identical results.
    """
    now = datetime(2026, 9, 15, 10, 0, 0, tzinfo=timezone.utc)
    events = [
        _make_event("std_1", "top_1", now - timedelta(minutes=30), correctness=True, response_time_ms=5000),
        _make_event("std_1", "top_1", now - timedelta(minutes=20), correctness=False, response_time_ms=7000),
        _make_event("std_1", "top_2", now - timedelta(minutes=15), correctness=True, response_time_ms=3000),
        _make_event("std_1", "top_1", now - timedelta(minutes=10), correctness=True, response_time_ms=4500),
    ]

    shuffled_events = list(reversed(events))

    feat_1 = PointInTimeFeatureExtractor.extract("std_1", "top_1", now, events)
    feat_2 = PointInTimeFeatureExtractor.extract("std_1", "top_1", now, shuffled_events)

    assert feat_1.to_dict() == feat_2.to_dict()


def test_dataset_generator_strictly_temporal_cutoff_and_target_separation():
    """
    Test 5 & 6 (Temporal Ordering & Target Causality):
    Verifies that CausalDatasetGenerator produces samples where:
    - T_cutoff < T_target (lead_time > 0)
    - Target event occurs strictly after feature cutoff
    - Evaluative events are properly converted into binary Target A
    """
    now = datetime(2026, 9, 15, 10, 0, 0, tzinfo=timezone.utc)
    generator = CausalDatasetGenerator()

    # 4 sequential attempts: True, True, False, True
    events = [
        _make_event("std_1", "top_1", now + timedelta(hours=1), correctness=True, event_id="ev_1"),
        _make_event("std_1", "top_1", now + timedelta(hours=2), correctness=True, event_id="ev_2"),
        _make_event("std_1", "top_1", now + timedelta(hours=3), correctness=False, event_id="ev_3"),
        _make_event("std_1", "top_1", now + timedelta(hours=4), correctness=True, event_id="ev_4"),
    ]

    dataset = generator.generate_from_events(events)

    assert dataset.total_samples == 4
    assert dataset.positive_target_count == 3
    assert dataset.negative_target_count == 1

    for sample in dataset.samples:
        # Strict temporal inequality
        assert sample.cutoff_timestamp < sample.target_timestamp
        assert sample.lead_time_seconds > 0.0

        # Target event cannot be part of past attempts in features
        if sample.target_event_id == "ev_1":
            assert sample.target_correctness == 1
            assert sample.features.cumulative_topic_attempts == 0
            assert sample.features.is_first_topic_attempt is True
        elif sample.target_event_id == "ev_3":
            assert sample.target_correctness == 0
            assert sample.features.cumulative_topic_attempts == 2
            assert sample.features.cumulative_topic_accuracy == 100.0
        elif sample.target_event_id == "ev_4":
            assert sample.target_correctness == 1
            assert sample.features.cumulative_topic_attempts == 3
            assert sample.features.cumulative_topic_correct_count == 2
            assert sample.features.cumulative_topic_accuracy == 66.67


def test_isolation_no_student_cross_contamination():
    """
    Test 7 (Student Isolation Invariant):
    Verifies that events belonging to Student B never influence Student A's features.
    """
    now = datetime(2026, 9, 15, 12, 0, 0, tzinfo=timezone.utc)

    events_student_a = [
        _make_event("student_A", "top_1", now - timedelta(hours=2), correctness=True, response_time_ms=5000),
    ]
    events_student_b = [
        _make_event("student_B", "top_1", now - timedelta(hours=1), correctness=False, response_time_ms=99000),
        _make_event("student_B", "top_1", now - timedelta(minutes=30), correctness=False, response_time_ms=88000),
    ]

    all_events = events_student_a + events_student_b

    feat_a = PointInTimeFeatureExtractor.extract("student_A", "top_1", now, all_events)
    assert feat_a.cumulative_topic_attempts == 1
    assert feat_a.cumulative_topic_accuracy == 100.0
    assert feat_a.cumulative_global_attempts == 1

    feat_b = PointInTimeFeatureExtractor.extract("student_B", "top_1", now, all_events)
    assert feat_b.cumulative_topic_attempts == 2
    assert feat_b.cumulative_topic_accuracy == 0.0
    assert feat_b.cumulative_global_attempts == 2


def test_explicit_missing_data_preservation():
    """
    Test 8 (Missing Data Invariant):
    Verifies that missing information is explicitly flagged with boolean indicators.
    """
    now = datetime(2026, 9, 15, 12, 0, 0, tzinfo=timezone.utc)

    # Event with no latency recorded and LEARN event with no correctness
    events = [
        LearningEvent(
            student_id="std_1",
            topic_id="top_1",
            event_type=EventType.LEARN,
            timestamp=now - timedelta(hours=2),
            correctness=None,
            score=None,
            response_time_ms=None,
        )
    ]

    feat = PointInTimeFeatureExtractor.extract("std_1", "top_1", now, events)

    # Exposures exist, but evaluative attempts are 0 -> accuracy is missing
    assert feat.cumulative_topic_exposures == 1
    assert feat.cumulative_topic_attempts == 0
    assert feat.cumulative_topic_accuracy is None
    assert feat.topic_accuracy_is_missing is True
    assert feat.ewma_accuracy_is_missing is True
    assert feat.latency_is_missing is True
    assert feat.hint_data_is_missing is True
    assert feat.curriculum_context_is_missing is True


def test_intervening_interference_calculation():
    """
    Test 9 (Cognitive Interference Invariant):
    Verifies that events on other topics between consecutive topic interactions
    are correctly tallied.
    """
    now = datetime(2026, 9, 15, 12, 0, 0, tzinfo=timezone.utc)

    # Student studies Topic 1 at 08:00
    # Then studies Topic 2, Topic 3, Topic 2 between 08:00 and 12:00
    events = [
        _make_event("std_1", "top_1", now - timedelta(hours=4), correctness=True),
        _make_event("std_1", "top_2", now - timedelta(hours=3), correctness=True),
        _make_event("std_1", "top_3", now - timedelta(hours=2), correctness=False),
        _make_event("std_1", "top_2", now - timedelta(hours=1), correctness=True),
    ]

    feat = PointInTimeFeatureExtractor.extract("std_1", "top_1", now, events)

    assert feat.intervening_event_count == 3
    assert feat.intervening_distinct_topics_count == 2
    assert feat.intervening_evaluative_count == 3
    assert feat.is_first_topic_attempt is False


def test_ewma_accuracy_mathematical_progression():
    """
    Test 9 (EWMA Accuracy Invariant):
    Verifies EWMA accuracy updates with decay alpha=0.3.
    """
    now = datetime(2026, 9, 15, 12, 0, 0, tzinfo=timezone.utc)

    # e1: True (100) -> EWMA = 100.0
    # e2: False (0)  -> EWMA = 0.3*0 + 0.7*100 = 70.0
    # e3: False (0)  -> EWMA = 0.3*0 + 0.7*70 = 49.0
    # e4: True (100) -> EWMA = 0.3*100 + 0.7*49 = 30 + 34.3 = 64.3
    events = [
        _make_event("std_1", "top_1", now - timedelta(hours=4), correctness=True),
        _make_event("std_1", "top_1", now - timedelta(hours=3), correctness=False),
        _make_event("std_1", "top_1", now - timedelta(hours=2), correctness=False),
        _make_event("std_1", "top_1", now - timedelta(hours=1), correctness=True),
    ]

    feat = PointInTimeFeatureExtractor.extract("std_1", "top_1", now, events, ewma_alpha=0.3)
    assert feat.ewma_topic_accuracy == 64.3
    assert feat.ewma_accuracy_is_missing is False


def test_tabular_records_export_and_curriculum_lookup(db_session, seed_data):
    """
    Test 10: Verifies conversion of CausalDatasetMatrix to flat tabular records
    and resolution of curriculum context from DB.
    """
    student = seed_data["student_profile"]
    topic = seed_data["topic"]
    now = datetime.now(timezone.utc)

    events = [
        _make_event(student.id, topic.id, now - timedelta(hours=2), correctness=True, event_id="ev_t1"),
        _make_event(student.id, topic.id, now - timedelta(hours=1), correctness=False, event_id="ev_t2"),
    ]

    generator = CausalDatasetGenerator()
    dataset = generator.generate_from_events(events=events, db=db_session)

    assert dataset.total_samples == 2
    records = dataset.to_records()
    assert len(records) == 2

    # Check tabular record fields
    rec = records[1]
    assert rec["student_id"] == student.id
    assert rec["topic_id"] == topic.id
    assert rec["target_correctness"] == 0
    assert "feat_cumulative_topic_attempts" in rec
    assert rec["feat_cumulative_topic_attempts"] == 1
    assert rec["feat_cumulative_topic_accuracy"] == 100.0
    assert rec["feat_grade_level"] == 10
    assert rec["feat_subject_code"] == "SCI-10"
    assert rec["feat_topic_order"] == 1
    assert rec["feat_curriculum_context_is_missing"] is False

