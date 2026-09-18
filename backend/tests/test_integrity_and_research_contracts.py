import pytest
from datetime import datetime, timezone
from sqlalchemy.exc import IntegrityError

from backend.app.models import User, UserRole
from backend.app.models import Standard
from backend.app.models import Attempt, Answer, AttemptStatus
from backend.app.models import LearningEvent, EventType
from backend.app.models import ForgettingSignal, ForgettingSignalStatus
from backend.app.domain.constants import EVIDENCE_STRENGTH_STRONG, VALID_EVIDENCE_STRENGTHS


def test_learning_event_append_only_api_contracts(client, seed_data):
    """
    Verifies that LearningEvent is strictly append-only:
    - Creation (POST) is permitted.
    - Mutation (PUT/PATCH) and Deletion (DELETE) are NOT exposed and rejected (404/405).
    """
    student = seed_data["student_profile"]
    topic = seed_data["topic"]

    # 1. Creation works
    res = client.post("/api/v1/learning-events", json={
        "student_id": student.id,
        "topic_id": topic.id,
        "event_type": "PRACTICE",
        "score": 10.0,
        "correctness": True,
        "response_time_ms": 12000,
        "attempt_number": 1,
    })
    assert res.status_code == 201
    event_id = res.json()["id"]

    # 2. DELETE endpoint does NOT exist for LearningEvent
    res_del_collection = client.delete("/api/v1/learning-events")
    assert res_del_collection.status_code in [404, 405]

    res_del_item = client.delete(f"/api/v1/learning-events/{event_id}")
    assert res_del_item.status_code in [404, 405]

    # 3. PUT / PATCH endpoints do NOT exist for LearningEvent
    res_put = client.put(f"/api/v1/learning-events/{event_id}", json={"score": 5.0})
    assert res_put.status_code in [404, 405]

    res_patch = client.patch(f"/api/v1/learning-events/{event_id}", json={"score": 5.0})
    assert res_patch.status_code in [404, 405]


def test_attempt_and_answer_integrity_constraints(db_session, seed_data):
    """
    Verifies database-level check constraints on attempt scores, percentages, and latencies.
    """
    student = seed_data["student_profile"]
    topic = seed_data["topic"]

    # Negative percentage should violate check constraint
    invalid_attempt = Attempt(
        student_id=student.id,
        assessment_id="any-id",
        percentage=-5.0,  # Violates percentage >= 0
        total_score=0.0,
    )
    db_session.add(invalid_attempt)
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()

    # Percentage > 100 should violate check constraint
    invalid_attempt_high = Attempt(
        student_id=student.id,
        assessment_id="any-id",
        percentage=105.0,  # Violates percentage <= 100
        total_score=0.0,
    )
    db_session.add(invalid_attempt_high)
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()

    # Negative response_time_ms on Answer should violate check constraint
    invalid_answer = Answer(
        attempt_id="any-attempt",
        question_id="any-question",
        selected_option="A",
        is_correct=True,
        response_time_ms=-500,  # Violates response_time_ms >= 0
    )
    db_session.add(invalid_answer)
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()


def test_learning_event_integrity_constraints(db_session, seed_data):
    """
    Verifies database-level check constraints on LearningEvent.
    """
    student = seed_data["student_profile"]
    topic = seed_data["topic"]

    # Negative attempt number violates constraint
    invalid_event = LearningEvent(
        student_id=student.id,
        topic_id=topic.id,
        event_type=EventType.PRACTICE,
        attempt_number=-1,  # Violates attempt_number >= 0
    )
    db_session.add(invalid_event)
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()

    # Negative response time violates constraint
    invalid_event_time = LearningEvent(
        student_id=student.id,
        topic_id=topic.id,
        event_type=EventType.PRACTICE,
        response_time_ms=-100,  # Violates response_time_ms >= 0
    )
    db_session.add(invalid_event_time)
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()


def test_forgetting_signal_research_semantics(client, seed_data):
    """
    Verifies ForgettingSignal represents empirical comparative evidence
    rather than an invented decay/forget probability.
    """
    student = seed_data["student_profile"]
    topic = seed_data["topic"]

    res = client.post("/api/v1/forgetting-signals", json={
        "student_id": student.id,
        "topic_id": topic.id,
        "evidence_type": "ACCURACY_DROP_AFTER_INTERVAL",
        "evidence_strength": EVIDENCE_STRENGTH_STRONG,
        "prior_performance_reference": {"accuracy": 100.0, "consecutive_success": 5},
        "later_performance_reference": {"accuracy": 0.0, "latency_ms": 24000},
        "evidence_metadata": {"days_elapsed": 21, "intervening_activities": 0},
    })
    assert res.status_code == 201
    data = res.json()

    # Ensure research-safe field names
    assert data["evidence_strength"] in VALID_EVIDENCE_STRENGTHS
    assert "forget_probability" not in data
    assert "decay_probability" not in data
    assert "retention_score" not in data
    assert data["prior_performance_reference"]["accuracy"] == 100.0
    assert data["later_performance_reference"]["accuracy"] == 0.0
