import pytest
from datetime import datetime, timedelta, timezone
from backend.app.models.learning_event import LearningEvent, EventType
from backend.app.domain.prediction import (
    PointInTimeFeatureExtractor,
    ObservationSampler,
    RejectionReason,
    DatasetDiagnostics,
    DatasetSerializer,
    CutoffSelectionConfig,
    CausalDatasetMatrix,
)


def _create_event(
    student_id: str,
    topic_id: str,
    timestamp: datetime,
    correctness: bool = True,
    score: float = 100.0,
    response_time_ms: int = 5000,
    event_type: EventType = EventType.PRACTICE,
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
    )
    if event_id:
        e.id = event_id
    return e


def test_observation_sampler_rejects_missing_target_correctness():
    """
    Test 1: Verifies that events without correctness (e.g. LEARN / reading)
    are rejected from being target outcomes.
    """
    now = datetime(2026, 9, 15, 10, 0, 0, tzinfo=timezone.utc)
    events = [
        # Evaluative event
        _create_event("std_1", "top_1", now + timedelta(hours=1), correctness=True, event_id="ev_1"),
        # Non-evaluative LEARN event (correctness=None)
        LearningEvent(
            student_id="std_1",
            topic_id="top_1",
            event_type=EventType.LEARN,
            timestamp=now + timedelta(hours=2),
            correctness=None,
            id="ev_learn",
        ),
    ]

    sampler = ObservationSampler()
    dataset, audit = sampler.sample_observations(events)

    assert dataset.total_samples == 1
    assert dataset.samples[0].target_event_id == "ev_1"
    assert audit.rejected_samples_count == 1
    assert audit.rejections_by_reason[RejectionReason.MISSING_TARGET_CORRECTNESS] == 1


def test_observation_sampler_rejects_duplicate_pairs():
    """
    Test 2: Verifies that duplicate observation/target pairs are rejected.
    """
    now = datetime(2026, 9, 15, 10, 0, 0, tzinfo=timezone.utc)
    ev = _create_event("std_1", "top_1", now + timedelta(hours=1), correctness=True, event_id="ev_dup")
    # Feed duplicate identical event in raw stream
    events = [ev, ev]

    sampler = ObservationSampler()
    dataset, audit = sampler.sample_observations(events)

    assert dataset.total_samples == 1
    assert audit.rejected_samples_count == 1
    assert audit.rejections_by_reason[RejectionReason.DUPLICATE_OBSERVATION_TARGET] == 1


def test_observation_sampler_enforces_history_threshold():
    """
    Test 3: Verifies filtering when min_prior_topic_attempts is configured.
    """
    now = datetime(2026, 9, 15, 10, 0, 0, tzinfo=timezone.utc)
    events = [
        _create_event("std_1", "top_1", now + timedelta(hours=1), correctness=True, event_id="ev_1"),
        _create_event("std_1", "top_1", now + timedelta(hours=2), correctness=True, event_id="ev_2"),
        _create_event("std_1", "top_1", now + timedelta(hours=3), correctness=False, event_id="ev_3"),
    ]

    # Require at least 2 prior attempts
    config = CutoffSelectionConfig(min_prior_topic_attempts=2)
    sampler = ObservationSampler(config=config)
    dataset, audit = sampler.sample_observations(events)

    # Only ev_3 has >= 2 prior attempts
    assert dataset.total_samples == 1
    assert dataset.samples[0].target_event_id == "ev_3"
    assert audit.rejected_samples_count == 2
    assert audit.rejections_by_reason[RejectionReason.INSUFFICIENT_HISTORY] == 2


def test_empty_dataset_diagnostics_handling():
    """
    Test 4: Verifies diagnostics behavior on zero observations
    (accurately representing the initial unpopulated DB state).
    """
    empty_matrix = CausalDatasetMatrix(samples=[])
    diag = DatasetDiagnostics(empty_matrix)

    assert diag.has_data is False
    assert diag.total_observations == 0
    assert diag.unique_students == 0
    assert diag.unique_topics == 0
    assert diag.class_balance is None
    assert diag.cold_start_proportion == 0.0
    assert "no real longitudinal observations exist yet" in diag.dataset_status_message

    md = diag.to_markdown()
    assert "no real longitudinal observations exist yet" in md


def test_dataset_diagnostics_distribution_calculations():
    """
    Test 5: Verifies statistical distribution metrics across multi-student, multi-topic events.
    """
    now = datetime(2026, 9, 15, 10, 0, 0, tzinfo=timezone.utc)
    events = [
        # Student 1: 3 attempts on Topic 1 (True, False, True)
        _create_event("std_1", "top_1", now + timedelta(hours=1), correctness=True, event_id="e1_1"),
        _create_event("std_1", "top_1", now + timedelta(hours=2), correctness=False, event_id="e1_2"),
        _create_event("std_1", "top_1", now + timedelta(hours=3), correctness=True, event_id="e1_3"),
        # Student 2: 2 attempts on Topic 1 (True, True), 1 attempt on Topic 2 (False)
        _create_event("std_2", "top_1", now + timedelta(hours=1), correctness=True, event_id="e2_1"),
        _create_event("std_2", "top_1", now + timedelta(hours=2), correctness=True, event_id="e2_2"),
        _create_event("std_2", "top_2", now + timedelta(hours=4), correctness=False, event_id="e2_3"),
    ]

    sampler = ObservationSampler()
    dataset, _ = sampler.sample_observations(events)

    diag = DatasetDiagnostics(dataset)
    assert diag.has_data is True
    assert diag.total_observations == 6
    assert diag.unique_students == 2
    assert diag.unique_topics == 2

    # Target correctness: 4 True (1), 2 False (0)
    assert diag.positive_target_count == 4
    assert diag.negative_target_count == 2
    assert diag.class_balance == round(4 / 6, 4)

    # Observations per student: std_1 has 3, std_2 has 3 -> min=3, max=3, mean=3.0, median=3.0
    assert diag.observations_per_student["min"] == 3.0
    assert diag.observations_per_student["max"] == 3.0
    assert diag.observations_per_student["mean"] == 3.0

    # Observations per topic: top_1 has 5, top_2 has 1
    assert diag.observations_per_topic["min"] == 1.0
    assert diag.observations_per_topic["max"] == 5.0
    assert diag.observations_per_topic["median"] == 3.0

    # Cold start proportion: std_1 top_1 (1), std_2 top_1 (1), std_2 top_2 (1) = 3 / 6 = 0.5
    assert diag.cold_start_proportion == 0.5

    # Missing feature rates should contain all features
    assert "cumulative_topic_accuracy" in diag.missing_feature_rates
    assert diag.missing_feature_rates["cumulative_topic_accuracy"] == 0.5  # Missing for 3 cold starts


def test_deterministic_dataset_serialization_and_hash():
    """
    Test 6: Verifies that serializing a dataset produces identical CSV string
    and identical SHA-256 hash regardless of raw event input ordering.
    """
    now = datetime(2026, 9, 15, 10, 0, 0, tzinfo=timezone.utc)
    events_a = [
        _create_event("std_1", "top_1", now + timedelta(hours=1), correctness=True, event_id="e1"),
        _create_event("std_1", "top_1", now + timedelta(hours=2), correctness=False, event_id="e2"),
        _create_event("std_2", "top_1", now + timedelta(hours=3), correctness=True, event_id="e3"),
    ]
    events_b = list(reversed(events_a))

    sampler = ObservationSampler()
    ds_a, _ = sampler.sample_observations(events_a)
    ds_b, _ = sampler.sample_observations(events_b)

    csv_a = DatasetSerializer.export_csv_string(ds_a)
    csv_b = DatasetSerializer.export_csv_string(ds_b)
    hash_a = DatasetSerializer.compute_sha256(csv_a)
    hash_b = DatasetSerializer.compute_sha256(csv_b)

    assert csv_a == csv_b
    assert hash_a == hash_b
    assert len(hash_a) == 64

    # Test JSON export package
    json_pkg = DatasetSerializer.export_json(ds_a)
    assert json_pkg["metadata"]["content_sha256"] == hash_a
    assert json_pkg["metadata"]["total_samples"] == 3
    assert len(json_pkg["records"]) == 3


def test_temporal_lead_time_is_strictly_positive():
    """
    Test 7: Verifies that for every valid observation, lead_time_seconds > 0.
    """
    now = datetime(2026, 9, 15, 10, 0, 0, tzinfo=timezone.utc)
    events = [
        _create_event("std_1", "top_1", now + timedelta(minutes=i * 10), correctness=True, event_id=f"e_{i}")
        for i in range(5)
    ]

    sampler = ObservationSampler()
    dataset, _ = sampler.sample_observations(events)

    for s in dataset.samples:
        assert s.lead_time_seconds > 0.0
        assert s.cutoff_timestamp < s.target_timestamp
