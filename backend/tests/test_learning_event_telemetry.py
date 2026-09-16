import pytest
from datetime import datetime, timezone
from backend.app.models.learning_event import LearningEvent, EventType
from backend.app.models.mcq import MCQQuestion, QuestionDifficulty, QuestionStatus
from backend.app.models.assessment import Assessment, AssessmentQuestion, AssessmentStatus
from backend.app.models.attempt import Attempt, AttemptStatus
from backend.app.domain.enums import OptionKey
from backend.app.domain.prediction.audit import LearningEventAuditor


def test_learn_event_telemetry_flow(client, db_session, seed_data):
    """
    Test 1 (LEARN Telemetry Flow):
    Verifies that calling POST /topics/{id}/study records a valid LEARN LearningEvent.
    """
    student = seed_data["student_profile"]
    topic = seed_data["topic"]

    res = client.post(
        f"/api/v1/topics/{topic.id}/study",
        json={
            "student_id": student.id,
            "session_id": "session_study_101",
            "dwell_time_seconds": 45,
            "idempotency_key": "study_key_1",
        }
    )
    assert res.status_code == 201
    data = res.json()
    assert data["event_type"] == "LEARN"
    assert data["student_id"] == student.id
    assert data["topic_id"] == topic.id
    assert data["correctness"] is None
    assert data["score"] is None
    assert data["response_time_ms"] == 45000

    # Verify DB record
    events = db_session.query(LearningEvent).filter_by(student_id=student.id, event_type=EventType.LEARN).all()
    assert len(events) == 1
    assert events[0].event_metadata["dwell_time_seconds"] == 45


def test_practice_event_telemetry_flow(client, db_session, seed_data):
    """
    Test 2 (PRACTICE Telemetry Flow):
    Verifies that calling POST /mcqs/{id}/practice records a valid PRACTICE LearningEvent.
    """
    student = seed_data["student_profile"]
    topic = seed_data["topic"]

    # Create MCQ
    mcq = MCQQuestion(
        topic_id=topic.id,
        question_text="What is the chemical symbol for Gold?",
        option_a="Ag",
        option_b="Au",
        option_c="Fe",
        option_d="Pb",
        correct_option=OptionKey.B,
        difficulty=QuestionDifficulty.MEDIUM,
        status=QuestionStatus.APPROVED,
    )
    db_session.add(mcq)
    db_session.commit()
    db_session.refresh(mcq)

    # Submit practice answer (Correct)
    res = client.post(
        f"/api/v1/mcqs/{mcq.id}/practice",
        json={
            "student_id": student.id,
            "selected_option": "B",
            "response_time_ms": 4200,
            "hint_used": False,
            "session_id": "practice_session_1",
            "idempotency_key": "mcq_practice_key_1",
        }
    )
    assert res.status_code == 200
    data = res.json()
    assert data["is_correct"] is True
    assert data["correct_option"] == "B"

    # Verify DB record
    events = db_session.query(LearningEvent).filter_by(student_id=student.id, event_type=EventType.PRACTICE).all()
    assert len(events) == 1
    assert events[0].correctness is True
    assert events[0].score == 100.0
    assert events[0].response_time_ms == 4200


def test_mcq_attempt_telemetry_flow(client, db_session, seed_data):
    """
    Test 3 (MCQ_ATTEMPT Telemetry Flow):
    Verifies that answering during an assessment attempt records MCQ_ATTEMPT event.
    """
    teacher = seed_data["teacher_profile"]
    student = seed_data["student_profile"]
    topic = seed_data["topic"]

    # Assessment & MCQ
    mcq = MCQQuestion(
        topic_id=topic.id,
        question_text="What is the acceleration due to gravity on Earth?",
        option_a="8.9 m/s^2",
        option_b="9.8 m/s^2",
        option_c="10.8 m/s^2",
        option_d="12.0 m/s^2",
        correct_option=OptionKey.B,
    )
    db_session.add(mcq)
    db_session.flush()

    assessment = Assessment(
        teacher_id=teacher.id,
        title="Physics Class 10 Quiz",
        topic_id=topic.id,
        status=AssessmentStatus.PUBLISHED,
    )
    db_session.add(assessment)
    db_session.flush()

    aq = AssessmentQuestion(
        assessment_id=assessment.id,
        question_id=mcq.id,
        question_order=1,
        points=2.0,
    )
    db_session.add(aq)
    db_session.commit()

    # Start attempt
    att_res = client.post("/api/v1/attempts", json={"student_id": student.id, "assessment_id": assessment.id})
    assert att_res.status_code == 201
    att_id = att_res.json()["id"]

    # Submit answer
    ans_res = client.post(
        f"/api/v1/attempts/{att_id}/answers",
        json={
            "question_id": mcq.id,
            "selected_option": "B",
            "response_time_ms": 3500,
            "hint_used": False,
        }
    )
    assert ans_res.status_code == 201

    events = db_session.query(LearningEvent).filter_by(student_id=student.id, event_type=EventType.MCQ_ATTEMPT).all()
    assert len(events) == 1
    assert events[0].attempt_id == att_id
    assert events[0].correctness is True
    assert events[0].score == 2.0


def test_revision_event_telemetry_flow(client, db_session, seed_data):
    """
    Test 4 (REVISION Telemetry Flow):
    Verifies that calling POST /adaptive/revision-outcome records a REVISION LearningEvent.
    """
    student = seed_data["student_profile"]
    topic = seed_data["topic"]

    res = client.post(
        "/api/v1/adaptive/revision-outcome",
        json={
            "student_id": student.id,
            "topic_id": topic.id,
            "score": 85.0,
            "correctness": True,
            "response_time_ms": 5500,
            "idempotency_key": "rev_outcome_key_1",
        }
    )
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "SUCCESS"
    assert "event_id" in data

    events = db_session.query(LearningEvent).filter_by(student_id=student.id, event_type=EventType.REVISION).all()
    assert len(events) == 1
    assert events[0].score == 85.0
    assert events[0].correctness is True
    assert events[0].response_time_ms == 5500


def test_review_event_telemetry_flow(client, db_session, seed_data):
    """
    Test 5 (REVIEW Telemetry Flow):
    Verifies that calling POST /attempts/{id}/review records a REVIEW LearningEvent.
    """
    teacher = seed_data["teacher_profile"]
    student = seed_data["student_profile"]
    topic = seed_data["topic"]

    assessment = Assessment(
        teacher_id=teacher.id,
        title="Sample Exam",
        topic_id=topic.id,
        status=AssessmentStatus.PUBLISHED,
    )
    db_session.add(assessment)
    db_session.flush()

    attempt = Attempt(
        student_id=student.id,
        assessment_id=assessment.id,
        status=AttemptStatus.SUBMITTED,
        total_score=80.0,
        percentage=80.0,
    )
    db_session.add(attempt)
    db_session.commit()

    # Review attempt
    res = client.post(
        f"/api/v1/attempts/{attempt.id}/review",
        json={
            "student_id": student.id,
            "review_duration_ms": 25000,
            "idempotency_key": "review_key_1",
        }
    )
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "REVIEW_RECORDED"

    events = db_session.query(LearningEvent).filter_by(student_id=student.id, event_type=EventType.REVIEW).all()
    assert len(events) == 1
    assert events[0].score == 80.0
    assert events[0].correctness is None
    assert events[0].response_time_ms == 25000


def test_telemetry_idempotency_safeguards(client, db_session, seed_data):
    """
    Test 6 (Idempotency Safeguards):
    Verifies that submitting with the same idempotency_key prevents duplicate rows.
    """
    student = seed_data["student_profile"]
    topic = seed_data["topic"]

    payload = {
        "student_id": student.id,
        "session_id": "session_idem",
        "dwell_time_seconds": 30,
        "idempotency_key": "unique_idem_123",
    }

    # Call 1
    res1 = client.post(f"/api/v1/topics/{topic.id}/study", json=payload)
    assert res1.status_code == 201

    # Call 2 (Network retry / double click)
    res2 = client.post(f"/api/v1/topics/{topic.id}/study", json=payload)
    assert res2.status_code == 201

    # Must only have 1 row in DB
    events = db_session.query(LearningEvent).filter_by(student_id=student.id, topic_id=topic.id).all()
    assert len(events) == 1


def test_telemetry_validation_safeguards(client, seed_data):
    """
    Test 7 (Validation Safeguards):
    Verifies that negative latencies or scores are rejected.
    """
    student = seed_data["student_profile"]
    topic = seed_data["topic"]

    # Negative dwell time
    res = client.post(
        f"/api/v1/topics/{topic.id}/study",
        json={
            "student_id": student.id,
            "dwell_time_seconds": -10,
        }
    )
    assert res.status_code == 422  # Pydantic validation error


def test_learning_event_auditor_verification(db_session, seed_data):
    """
    Test 8 (Auditor Verification):
    Verifies that LearningEventAuditor correctly tabulates event distributions
    and verifies zero violations on valid data.
    """
    student = seed_data["student_profile"]
    topic = seed_data["topic"]
    now = datetime.now(timezone.utc)

    # Ingest 1 of each type
    for et in EventType:
        db_session.add(
            LearningEvent(
                student_id=student.id,
                topic_id=topic.id,
                event_type=et,
                timestamp=now,
                correctness=True if et in (EventType.PRACTICE, EventType.MCQ_ATTEMPT, EventType.REVISION) else None,
                score=100.0 if et in (EventType.PRACTICE, EventType.MCQ_ATTEMPT, EventType.REVISION) else None,
                response_time_ms=5000,
            )
        )
    db_session.commit()

    auditor = LearningEventAuditor()
    rep = auditor.run_audit(db=db_session)

    assert rep["verdict"] == "PASS"
    assert rep["total_events"] == 5
    for et in EventType:
        assert rep["event_type_distribution"][et.value] == 1
    assert rep["data_quality_violations"]["total_violations"] == 0
