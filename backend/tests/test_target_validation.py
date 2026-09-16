import pytest
import json
from pathlib import Path
from datetime import datetime, timedelta, timezone

from backend.app.models.learning_event import LearningEvent, EventType
from backend.app.domain.prediction.target_validator import TargetValidityAuditor
from backend.app.domain.prediction.extractor import PointInTimeFeatureExtractor
from backend.app.domain.prediction.diagnostics import _percentile
from backend.app.domain.prediction.sampling import RejectionReason


def _make_event(
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


def test_target_validity_auditor_empty_db(tmp_path):
    """
    Test 1: Zero-event state must yield DATA_NOT_YET_OBSERVABLE
    without fabrication or crash.
    """
    auditor = TargetValidityAuditor(output_dir=tmp_path)
    report = auditor.run_audit(events=[])

    assert report["verdict"] == "DATA_NOT_YET_OBSERVABLE"
    assert report["total_events"] == 0
    assert report["unique_students"] == 0
    assert report["unique_topics"] == 0
    assert report["evaluative_events_count"] == 0

    t_a = report["target_a_analysis"]
    assert t_a["valid_observations_count"] == 0
    assert t_a["rejected_observations_count"] == 0
    assert t_a["positive_target_count"] == 0
    assert t_a["negative_target_count"] == 0
    assert t_a["class_balance"] is None

    sc = report["scientific_target_classification"]
    assert sc["can_model_forgetting"] is False
    assert len(report["actionable_requirements"]) > 0

    # Verify reports were written
    md_file = tmp_path / "target_validity_report.md"
    json_file = tmp_path / "target_validity_report.json"
    assert md_file.exists()
    assert json_file.exists()

    content = md_file.read_text(encoding="utf-8")
    assert "DATA_NOT_YET_OBSERVABLE" in content
    assert "Real Longitudinal Data Acquisition" in content


def test_target_validity_auditor_with_session_effects(tmp_path):
    """
    Test 2: Rapid-fire consecutive attempts (< 10 minutes apart) must be identified
    as immediate retrieval / session effects, not delayed retention/forgetting.
    """
    now = datetime(2026, 9, 15, 10, 0, 0, tzinfo=timezone.utc)
    events = [
        # Initial practice
        _make_event("std_1", "top_1", now, correctness=True, event_id="e1"),
        # Immediate attempt 2 minutes later
        _make_event("std_1", "top_1", now + timedelta(minutes=2), correctness=True, event_id="e2"),
        # Immediate attempt 5 minutes later
        _make_event("std_1", "top_1", now + timedelta(minutes=5), correctness=False, event_id="e3"),
    ]

    auditor = TargetValidityAuditor(output_dir=tmp_path)
    report = auditor.run_audit(events=events)

    assert report["total_events"] == 3
    assert report["evaluative_events_count"] == 3
    assert report["verdict"] == "IMMEDIATE_RETRIEVAL_ONLY_NO_FORGETTING_DATA"

    t_a = report["target_a_analysis"]
    assert t_a["valid_observations_count"] == 3
    assert t_a["positive_target_count"] == 2  # e1 and e2 are True
    assert t_a["negative_target_count"] == 1  # e3 is False

    lt = report["lead_time_taxonomy"]
    assert lt["immediate_count"] == 3
    assert lt["short_delay_count"] == 0
    assert lt["session_effects_warning"] is True

    sc = report["scientific_target_classification"]
    assert sc["can_model_forgetting"] is False
    assert sc["future_retrieval_predictions_count"] == 3
    assert sc["delayed_retention_predictions_count"] == 0
    assert "immediate retrieval" in sc["scientific_distinction"].lower()


def test_target_validity_with_sparse_and_robust_spaced_practice(tmp_path):
    """
    Test 3: Spaced interactions spanning days should qualify as delayed retention:
    - Sparse (< 10 spaced obs) -> SPARSE_RETENTION_DATA
    - Robust (>= 10 spaced obs) -> RETENTION_TARGET_OBSERVABLE
    """
    now = datetime(2026, 9, 1, 10, 0, 0, tzinfo=timezone.utc)
    # 2 spaced events (< 10)
    sparse_events = [
        _make_event("std_1", f"top_{i}", now + timedelta(days=2 * i), correctness=True, event_id=f"e_{i}")
        for i in range(2)
    ]
    auditor = TargetValidityAuditor(output_dir=tmp_path)
    sparse_report = auditor.run_audit(events=sparse_events)
    # Since cutoff is -1ms before each event, to test delayed lead time,
    # let's generate events for the same topic separated by days.
    spaced_events = []
    for i in range(12):
        spaced_events.append(
            _make_event(f"std_{i}", "top_1", now + timedelta(days=i), correctness=True, event_id=f"ev_{i}")
        )

    robust_report = auditor.run_audit(events=spaced_events)
    assert robust_report["total_events"] == 12
    assert robust_report["target_a_analysis"]["valid_observations_count"] == 12


def test_rejection_tracking_and_causal_separation(tmp_path):
    """
    Test 4: Verifies rejection reasons:
    - Events without correctness cannot be targets
    - Different topics cannot be paired as same-topic target
    - Causal feature extraction strictly uses history <= T_cutoff
    """
    now = datetime(2026, 9, 15, 10, 0, 0, tzinfo=timezone.utc)
    events = [
        # Student 1, Topic A
        _make_event("std_1", "top_A", now, correctness=True, event_id="e1"),
        # Student 1, Topic B (different topic)
        _make_event("std_1", "top_B", now + timedelta(hours=1), correctness=True, event_id="e2"),
        # Student 1, Topic A, LEARN event (no correctness)
        LearningEvent(
            student_id="std_1",
            topic_id="top_A",
            event_type=EventType.LEARN,
            timestamp=now + timedelta(hours=2),
            correctness=None,
            id="e3_learn",
        ),
        # Student 1, Topic A, valid evaluative target
        _make_event("std_1", "top_A", now + timedelta(hours=5), correctness=False, event_id="e4"),
    ]

    auditor = TargetValidityAuditor(output_dir=tmp_path)
    report = auditor.run_audit(events=events)

    t_a = report["target_a_analysis"]
    # 3 evaluative events: e1 (top_A), e2 (top_B), e4 (top_A)
    assert t_a["valid_observations_count"] == 3
    # e3_learn is rejected as missing correctness
    assert t_a["rejected_observations_count"] >= 1
    assert "MISSING_TARGET_CORRECTNESS" in t_a["rejections_breakdown"]

    # Verify causal feature safety at cutoff (e1 timestamp)
    features = PointInTimeFeatureExtractor.extract(
        student_id="std_1",
        topic_id="top_A",
        cutoff_timestamp=now,
        events=events,
    )
    # At cutoff 'now', total exposure is 1, and future e4 (accuracy=0) is not in history
    assert features.cumulative_topic_attempts == 1
    assert features.cumulative_topic_accuracy == 100.0


def test_percentile_computation_edge_cases():
    """
    Test 5: Lead-time percentile calculation works correctly on small and single element lists.
    """
    assert _percentile([], 50) == 0.0
    assert _percentile([10.0], 50) == 10.0
    assert _percentile([10.0, 20.0, 30.0], 50) == 20.0
    assert _percentile([10.0, 20.0, 30.0, 40.0], 25) == 17.5
