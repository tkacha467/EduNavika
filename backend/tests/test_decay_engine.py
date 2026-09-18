import pytest
from datetime import datetime, timedelta, timezone
from backend.app.models import LearningEvent, EventType
from backend.app.models import TopicPerformance
from backend.app.models import ForgettingSignal, ForgettingSignalStatus
from backend.app.models import RevisionPlan, RevisionCompletionState
from backend.app.domain.enums import RevisionPriority
from backend.app.domain.constants import (
    EVIDENCE_STRENGTH_STRONG,
    EVIDENCE_STRENGTH_MODERATE,
    EVIDENCE_STRENGTH_WEAK,
    VALID_EVIDENCE_STRENGTHS,
)
from backend.app.domain.decay_engine.schemas import DecayDetectionConfig, EvidenceProfile
from backend.app.domain.decay_engine.strength_evaluator import EvidenceStrengthEvaluator
from backend.app.domain.decay_engine.detector import LongitudinalDecayDetector
from backend.app.domain.decay_engine.scheduler import SpacedRepetitionScheduler
from backend.app.domain.decay_engine.service import AdaptiveLearningService


def test_heuristic_operational_definitions_and_metadata():
    """
    Test 1: Verifies that detection triggers on heuristic operational thresholds
    and labels them as operational definitions rather than cognitive laws.
    """
    detector = LongitudinalDecayDetector()
    now = datetime.now(timezone.utc)

    # 4 baseline attempts 10 days ago (100% accuracy)
    base_time = now - timedelta(days=10)
    events = [
        LearningEvent(
            student_id="std_1",
            topic_id="top_1",
            event_type=EventType.PRACTICE,
            timestamp=base_time + timedelta(minutes=i * 5),
            correctness=True,
            response_time_ms=5000,
        )
        for i in range(4)
    ]

    # 2 post-delay attempts today (0% accuracy) -> 10-day gap
    events.extend([
        LearningEvent(
            student_id="std_1",
            topic_id="top_1",
            event_type=EventType.PRACTICE,
            timestamp=now + timedelta(minutes=i * 5),
            correctness=False,
            response_time_ms=8000,
        )
        for i in range(2)
    ])

    signals = detector.detect_for_topic(
        student_id="std_1",
        topic_id="top_1",
        events=events,
    )

    assert len(signals) == 1
    sig = signals[0]
    assert sig.evidence_type == "ACCURACY_DROP_POST_DELAY"
    assert sig.prior_performance_reference["accuracy"] == 100.0
    assert sig.later_performance_reference["accuracy"] == 0.0
    
    # Must state operational definition
    assert "operational_definition" in sig.evidence_metadata
    assert "Heuristic operational criteria" in sig.evidence_metadata["operational_definition"]


def test_multi_factor_evidence_strength_derivation():
    """
    Test 2: Verifies that qualitative evidence strength is derived
    from observable multi-factor indicators rather than arbitrary assignment.
    """
    # Strong profile: large sample, large drop, long delay, prior mastery
    strong_profile = EvidenceProfile(
        prior_attempts=7,
        baseline_accuracy=95.0,
        post_delay_attempts=3,
        post_delay_accuracy=20.0,
        delay_days=25.0,
        prior_mastery_state="MASTERED",
        is_consecutive_failure=True,
        consecutive_failures_count=2,
    )
    strength_strong, meta_strong = EvidenceStrengthEvaluator.evaluate(strong_profile)
    assert strength_strong == EVIDENCE_STRENGTH_STRONG
    assert meta_strong["total_evidence_points"] >= 5
    assert "observation_volume" in meta_strong["factor_breakdown"]
    assert "accuracy_drop" in meta_strong["factor_breakdown"]

    # Weak profile: small drop, short delay, no prior mastery
    weak_profile = EvidenceProfile(
        prior_attempts=3,
        baseline_accuracy=72.0,
        post_delay_attempts=1,
        post_delay_accuracy=55.0,
        delay_days=8.0,
        prior_mastery_state="NOVICE",
    )
    strength_weak, meta_weak = EvidenceStrengthEvaluator.evaluate(weak_profile)
    assert strength_weak == EVIDENCE_STRENGTH_WEAK
    assert meta_weak["total_evidence_points"] < 3


def test_deterministic_baseline_scheduler():
    """
    Test 3: Verifies initial deterministic baseline spaced-repetition intervals
    and priority mapping without claiming cognitive perfection.
    """
    now = datetime(2026, 9, 14, 12, 0, tzinfo=timezone.utc)

    # Urgent schedule from strong signal
    from backend.app.domain.decay_engine.schemas import DecaySignalDraft
    strong_draft = DecaySignalDraft(
        student_id="s1",
        topic_id="t1",
        evidence_type="ACCURACY_DROP_POST_DELAY",
        evidence_strength=EVIDENCE_STRENGTH_STRONG,
        prior_performance_reference={},
        later_performance_reference={},
        evidence_metadata={},
        detected_at=now,
        episode_fingerprint="fp123",
    )

    plan = SpacedRepetitionScheduler.schedule_from_signal(strong_draft, now=now)
    assert plan.priority == RevisionPriority.URGENT
    assert plan.recommended_revision_at == now + timedelta(days=1)
    assert "[Baseline Policy]" in plan.reason


def test_idempotency_and_deduplication(db_session, seed_data):
    """
    Test 4: Running detection repeatedly over the same student history
    must NOT create duplicate ForgettingSignal or RevisionPlan records.
    """
    student = seed_data["student_profile"]
    topic = seed_data["topic"]
    service = AdaptiveLearningService()

    now = datetime.now(timezone.utc)
    base_time = now - timedelta(days=14)

    # Ingest historical events into DB
    for i in range(4):
        db_session.add(LearningEvent(
            student_id=student.id,
            topic_id=topic.id,
            event_type=EventType.PRACTICE,
            timestamp=base_time + timedelta(minutes=i * 10),
            correctness=True,
            response_time_ms=4000,
        ))

    for i in range(2):
        db_session.add(LearningEvent(
            student_id=student.id,
            topic_id=topic.id,
            event_type=EventType.PRACTICE,
            timestamp=now - timedelta(minutes=(2 - i) * 10),
            correctness=False,
            response_time_ms=9000,
        ))
    db_session.commit()

    # Call 1: Should detect and persist 1 signal, 1 plan
    resp1 = service.detect_and_schedule_for_student(db_session, student_id=student.id, topic_id=topic.id)
    assert resp1.signals_created == 1
    assert resp1.signals_deduplicated == 0
    assert resp1.plans_scheduled == 1

    # Call 2: Identical state -> must be deduplicated
    resp2 = service.detect_and_schedule_for_student(db_session, student_id=student.id, topic_id=topic.id)
    assert resp2.signals_created == 0
    assert resp2.signals_deduplicated == 1
    assert resp2.plans_scheduled == 0

    # Verify DB counts
    signals = db_session.query(ForgettingSignal).filter(ForgettingSignal.student_id == student.id).all()
    plans = db_session.query(RevisionPlan).filter(RevisionPlan.student_id == student.id).all()
    assert len(signals) == 1
    assert len(plans) == 1


def test_retrieval_vs_retention_lifecycle(db_session, seed_data):
    """
    Test 5: Explicitly differentiates immediate retrieval success from durable retention.
    Verifies failed revision leaves signal UNRESOLVED, while successful revision marks it ADDRESSED.
    """
    student = seed_data["student_profile"]
    topic = seed_data["topic"]
    service = AdaptiveLearningService()

    now = datetime.now(timezone.utc)

    # 1. Create an unresolved signal and pending plan
    sig = ForgettingSignal(
        student_id=student.id,
        topic_id=topic.id,
        detected_at=now - timedelta(days=2),
        evidence_type="ACCURACY_DROP_POST_DELAY",
        evidence_strength=EVIDENCE_STRENGTH_MODERATE,
        prior_performance_reference={"accuracy": 100.0},
        later_performance_reference={"accuracy": 0.0},
        status=ForgettingSignalStatus.UNRESOLVED,
        evidence_metadata={"episode_fingerprint": "test_fp"},
    )
    plan = RevisionPlan(
        student_id=student.id,
        topic_id=topic.id,
        recommended_revision_at=now,
        priority=RevisionPriority.HIGH,
        reason="Test high priority",
        completion_state=RevisionCompletionState.PENDING,
    )
    db_session.add(sig)
    db_session.add(plan)
    db_session.commit()

    # 2. Student takes revision attempt but FAILS (score 40%)
    res_fail = service.handle_revision_attempt(
        db=db_session,
        student_id=student.id,
        topic_id=topic.id,
        score=40.0,
        correctness=False,
    )
    db_session.refresh(sig)
    db_session.refresh(plan)

    # Plan was executed (retrieval attempted), but signal remains UNRESOLVED due to failure
    assert plan.completion_state == RevisionCompletionState.COMPLETED
    assert sig.status == ForgettingSignalStatus.UNRESOLVED
    assert res_fail["signals_retained_unresolved"] == 1

    # 3. Revision attempt with score 75% (correct=True but score < 80% threshold)
    res_borderline = service.handle_revision_attempt(
        db=db_session,
        student_id=student.id,
        topic_id=topic.id,
        score=75.0,
        correctness=True,
    )
    db_session.refresh(sig)
    # Must remain UNRESOLVED because 75% is below the required 80% successful-retrieval threshold
    assert sig.status == ForgettingSignalStatus.UNRESOLVED
    assert res_borderline["signals_retained_unresolved"] == 1

    # 4. Next revision attempt meets 80.0% threshold (score 80.0%, correct=True)
    res_succ = service.handle_revision_attempt(
        db=db_session,
        student_id=student.id,
        topic_id=topic.id,
        score=80.0,
        correctness=True,
    )
    db_session.refresh(sig)
    assert sig.status == ForgettingSignalStatus.ADDRESSED_BY_REVISION
    assert res_succ["signals_resolved"] == 1
    assert "resolved_at" in sig.evidence_metadata


def test_research_integrity_no_uncalibrated_probabilities(client, seed_data):
    """
    Test 6: Research Contract Invariant.
    Verifies that the Adaptive API outputs zero uncalibrated float probabilities.
    """
    student = seed_data["student_profile"]
    topic = seed_data["topic"]

    # Trigger detection via API
    res = client.post(f"/api/v1/adaptive/detect-decay/{student.id}?topic_id={topic.id}")
    assert res.status_code == 200
    data = res.json()

    # Check forbidden probabilistic keys
    forbidden = ["forget_probability", "decay_probability", "retention_score", "p_forget"]
    for k in forbidden:
        assert k not in data

    # Check schedule endpoint
    res_sched = client.get(f"/api/v1/adaptive/schedule/{student.id}")
    assert res_sched.status_code == 200
    sched_data = res_sched.json()
    for item in sched_data["revision_items"]:
        for k in forbidden:
            assert k not in item


def test_adaptive_api_endpoints(client, seed_data):
    """
    Test 7: Full API integration testing.
    Verifies /detect-decay, /schedule, and /revision-outcome routes.
    """
    student = seed_data["student_profile"]
    topic = seed_data["topic"]

    # 1. 404 on invalid student
    res_404 = client.post("/api/v1/adaptive/detect-decay/non-existent-student")
    assert res_404.status_code == 404

    # 2. Trigger detection for seed student
    res_detect = client.post(f"/api/v1/adaptive/detect-decay/{student.id}")
    assert res_detect.status_code == 200
    detect_json = res_detect.json()
    assert "signals_detected" in detect_json
    assert "signals_deduplicated" in detect_json

    # 3. Schedule retrieval
    res_sched = client.get(f"/api/v1/adaptive/schedule/{student.id}")
    assert res_sched.status_code == 200
    sched_json = res_sched.json()
    assert "total_pending_revisions" in sched_json
    assert "revision_items" in sched_json

    # 4. Revision outcome
    res_rev = client.post("/api/v1/adaptive/revision-outcome", json={
        "student_id": student.id,
        "topic_id": topic.id,
        "score": 90.0,
        "correctness": True,
        "response_time_ms": 7500,
    })
    assert res_rev.status_code == 200
    rev_json = res_rev.json()
    assert rev_json["status"] == "SUCCESS"
    assert "lifecycle_update" in rev_json

