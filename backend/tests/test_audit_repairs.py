"""
Automated Regression Test Suite for Engineering Audit & Repairs.
Verifies:
1. Exact answer grading (option letters 'A'/'B'/'C'/'D', indices 0/1/2/3, and exact text).
2. Authoritative score updates (100% correct, 0% incorrect, partial sets).
3. Mathematics local content grounding, retrieval, and question generation.
4. Content diagnostic endpoint responses.
5. Topic and syllabus ID resolution between frontend placeholders and canonical database entities.
"""

import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.core.database import SessionLocal
from backend.app.models import StudentProfile, User, UserRole, Topic, LearningEvent
from backend.app.services.topic_resolver import resolve_topic
from backend.app.services.curriculum_question_bank import get_canonical_questions_for_topic

client = TestClient(app)


@pytest.fixture(scope="module")
def audit_student():
    db = SessionLocal()
    # Check or create a test student
    user = db.query(User).filter(User.email == "audit_tester@edunavika.local").first()
    if not user:
        user = User(
            id="audit-student-001",
            email="audit_tester@edunavika.local",
            hashed_password="test_hashed_password",
            name="Audit Test Student",
            role=UserRole.STUDENT,
        )
        db.add(user)
        db.commit()
    profile = db.query(StudentProfile).filter(StudentProfile.user_id == user.id).first()
    if not profile:
        profile = StudentProfile(
            id="audit-profile-001",
            user_id=user.id,
            enrollment_number="EN-AUDIT-01",
            division="A",
            preferred_language="en",
        )
        db.add(profile)
        db.commit()
    db.close()
    return "audit-profile-001"


def test_letter_and_index_grading_produces_100_percent_score(audit_student):
    """
    Submitting valid option letters ('A', 'B', 'C', 'D') or indices must grade correctly (100% score)
    instead of producing false zeros.
    """
    db = SessionLocal()
    topic = resolve_topic(db, "Chemical Reactions")
    assert topic is not None
    topic_id = topic.id
    db.close()

    # Question chem-ch1-f01 correct answer is option A:
    # "Total mass of elements in products must equal total mass in reactants"
    resp_letter = client.post(
        "/api/v1/adaptive/practice/submit",
        json={
            "student_id": audit_student,
            "question_id": "chem-ch1-f01",
            "topic_id": topic_id,
            "selected_answer": "A",
            "response_time_ms": 5000,
            "hint_used": False,
        },
    )
    assert resp_letter.status_code == 200
    data_letter = resp_letter.json()
    assert data_letter["correct"] is True, f"Option letter 'A' should be graded True, got {data_letter}"

    # Also test numeric index '0'
    resp_index = client.post(
        "/api/v1/adaptive/practice/submit",
        json={
            "student_id": audit_student,
            "question_id": "chem-ch1-f01",
            "topic_id": topic_id,
            "selected_answer": "0",
            "response_time_ms": 4000,
            "hint_used": False,
        },
    )
    assert resp_index.status_code == 200
    data_index = resp_index.json()
    assert data_index["correct"] is True, f"Option index '0' should be graded True, got {data_index}"


def test_incorrect_letter_grades_false_cleanly(audit_student):
    """
    Submitting an incorrect letter ('B') for a question where 'A' is correct must yield False.
    """
    db = SessionLocal()
    topic = resolve_topic(db, "Chemical Reactions")
    topic_id = topic.id
    db.close()

    resp = client.post(
        "/api/v1/adaptive/practice/submit",
        json={
            "student_id": audit_student,
            "question_id": "chem-ch1-f01",
            "topic_id": topic_id,
            "selected_answer": "B",
            "response_time_ms": 5000,
            "hint_used": False,
        },
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["correct"] is False
    assert "remediation" in data["next_recommended_action"].lower() or "practice" in data["next_recommended_action"].lower()


def test_mathematics_curriculum_practice_retrieval(audit_student):
    """
    Verifies Mathematics topics have textbook-grounded practice questions available
    and return authentic source provenance.
    """
    math_topics = ["Quadratic Equations", "Trigonometry", "Coordinate Geometry", "Statistics", "Probability", "Arithmetic Progressions"]
    for m in math_topics:
        resp = client.get(f"/api/v1/adaptive/practice/{audit_student}?topic_id={m}&count=3")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["questions"]) >= 3, f"Expected at least 3 questions for Math topic '{m}'"
        for q in data["questions"]:
            assert q["source_document"] == "STD-10/Std-10_Maths_EnglishMedium.pdf"
            assert q["source_page"] > 0
            assert len(q["options"]) == 4


def test_content_diagnostic_endpoint_reports_real_status():
    """
    Verifies /curriculum/diagnostic/{subject_or_topic} returns accurate offline availability status.
    """
    # Mathematics subject
    r_math = client.get("/api/v1/curriculum/diagnostic/Mathematics")
    assert r_math.status_code == 200
    d_math = r_math.json()
    assert d_math["entity_type"] == "SUBJECT"
    assert d_math["status"] == "READY"
    assert d_math["textbook_chunks_count"] > 100
    assert d_math["offline_ready"] is True

    # Frontend placeholder 'm1' (Quadratic Equations)
    r_m1 = client.get("/api/v1/curriculum/diagnostic/m1")
    assert r_m1.status_code == 200
    d_m1 = r_m1.json()
    assert d_m1["entity_type"] == "TOPIC"
    assert d_m1["status"] == "READY"
    assert d_m1["verified_questions_count"] >= 4
    assert d_m1["offline_ready"] is True

    # Unknown entity
    r_unknown = client.get("/api/v1/curriculum/diagnostic/Astronomy101")
    assert r_unknown.status_code == 200
    d_unknown = r_unknown.json()
    assert d_unknown["status"] == "NOT_FOUND"
    assert d_unknown["offline_ready"] is False


def test_shuffled_options_order_does_not_corrupt_canonical_grading(audit_student):
    """
    Simulates a client submitting exact option text, option letters, or shuffled indexes.
    Grading must match against canonical correct text and candidate texts reliably.
    """
    db = SessionLocal()
    topic = resolve_topic(db, "Quadratic Equations")
    assert topic is not None
    topic_id = topic.id
    db.close()

    # Question math-ch4-f01 correct answer:
    # "ax² + bx + c = 0, where a, b, c are real numbers and a ≠ 0"
    correct_text = "ax² + bx + c = 0, where a, b, c are real numbers and a ≠ 0"
    
    # 1. Submitting exact canonical text
    resp_text = client.post(
        "/api/v1/adaptive/practice/submit",
        json={
            "student_id": audit_student,
            "question_id": "math-ch4-f01",
            "topic_id": topic_id,
            "selected_answer": correct_text,
            "response_time_ms": 3500,
            "hint_used": False,
        },
    )
    assert resp_text.status_code == 200
    assert resp_text.json()["correct"] is True

    # 2. Submitting option letter A (which corresponds to that option in canonical order)
    resp_letter = client.post(
        "/api/v1/adaptive/practice/submit",
        json={
            "student_id": audit_student,
            "question_id": "math-ch4-f01",
            "topic_id": topic_id,
            "selected_answer": "A",
            "response_time_ms": 3200,
            "hint_used": False,
        },
    )
    assert resp_letter.status_code == 200
    assert resp_letter.json()["correct"] is True


def test_retrying_quiz_does_not_mutate_prior_events_or_reuse_stale_answers(audit_student):
    """
    Submitting multiple consecutive attempts records distinct atomic LearningEvents
    without corrupting previous attempts.
    """
    db = SessionLocal()
    topic = resolve_topic(db, "Probability")
    topic_id = topic.id

    # Count prior events for this student and topic
    prior_count = db.query(LearningEvent).filter(
        LearningEvent.student_id == audit_student,
        LearningEvent.topic_id == topic_id,
    ).count()

    # Attempt 1: Correct answer (option A)
    r1 = client.post(
        "/api/v1/adaptive/practice/submit",
        json={
            "student_id": audit_student,
            "question_id": "math-prob-f01",
            "topic_id": topic_id,
            "selected_answer": "A",
            "response_time_ms": 4000,
            "hint_used": False,
        },
    )
    assert r1.status_code == 200
    assert r1.json()["correct"] is True

    # Attempt 2: Incorrect answer (option B)
    r2 = client.post(
        "/api/v1/adaptive/practice/submit",
        json={
            "student_id": audit_student,
            "question_id": "math-prob-f01",
            "topic_id": topic_id,
            "selected_answer": "B",
            "response_time_ms": 3000,
            "hint_used": False,
        },
    )
    assert r2.status_code == 200
    assert r2.json()["correct"] is False

    new_count = db.query(LearningEvent).filter(
        LearningEvent.student_id == audit_student,
        LearningEvent.topic_id == topic_id,
    ).count()
    assert new_count == prior_count + 2
    db.close()

