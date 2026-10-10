"""
Automated Test Suite for Step 2: Evidence-Grounded Misconception Remediation.
Tests:
1. Incorrect practice answer returns structured RemediationEvidence.
2. Correct answer does NOT return remediation evidence (remediation is None).
3. Textbook citation fields (source_document, source_page, textbook_excerpt) are authentic.
4. Mathematics incorrect answer extracts Mathematics textbook passage and page.
5. Idempotent retries record separate atomic learning events and update knowledge profile safely.
6. Follow-up practice question is suggested from canonical bank for the same topic.
"""

import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.core.database import SessionLocal
from backend.app.models import StudentProfile, User, UserRole, Topic, LearningEvent
from backend.app.services.topic_resolver import resolve_topic
from backend.app.services.knowledge_model import KnowledgeModelService

client = TestClient(app)


@pytest.fixture(scope="module")
def remediation_student():
    db = SessionLocal()
    user = db.query(User).filter(User.email == "remediation_tester@edunavika.local").first()
    if not user:
        user = User(
            id="remediation-student-001",
            email="remediation_tester@edunavika.local",
            hashed_password="test_hashed_password",
            name="Remediation Test Student",
            role=UserRole.STUDENT,
        )
        db.add(user)
        db.commit()
    profile = db.query(StudentProfile).filter(StudentProfile.user_id == user.id).first()
    if not profile:
        profile = StudentProfile(
            id="remediation-profile-001",
            user_id=user.id,
            enrollment_number="EN-REMED-01",
            division="B",
            preferred_language="en",
        )
        db.add(profile)
        db.commit()
    db.close()
    return "remediation-profile-001"


def test_incorrect_answer_returns_structured_remediation_evidence(remediation_student):
    """
    Submitting an incorrect answer must return non-null `remediation` containing
    diagnosis, concept explanation, textbook excerpt, authentic source doc, and page citation.
    """
    db = SessionLocal()
    topic = resolve_topic(db, "Chemical Reactions")
    assert topic is not None
    topic_id = topic.id
    db.close()

    # Question chem-ch1-f01 correct is Option A:
    # "Total mass of elements in products must equal total mass in reactants"
    # Submit incorrect option B:
    resp = client.post(
        "/api/v1/adaptive/practice/submit",
        json={
            "student_id": remediation_student,
            "question_id": "chem-ch1-f01",
            "topic_id": topic_id,
            "selected_answer": "B",
            "response_time_ms": 6000,
            "hint_used": False,
        },
    )
    assert resp.status_code == 200
    data = resp.json()

    assert data["correct"] is False
    assert "remediation" in data
    remediation = data["remediation"]
    assert remediation is not None, "Remediation evidence must be returned for incorrect answer"

    assert "concept_target" in remediation
    assert "what_went_wrong" in remediation
    assert len(remediation["what_went_wrong"]) > 10
    assert "concept_explanation" in remediation
    assert remediation["can_retry"] is True

    # Textbook citation & excerpt verification
    assert remediation["source_document"] == "STD-10/Std-10_Science_English Medium.pdf"
    assert remediation["source_page"] == 16
    assert remediation["textbook_excerpt"] is not None
    assert len(remediation["textbook_excerpt"]) > 20
    assert "mass" in remediation["textbook_excerpt"].lower() or "chemical" in remediation["textbook_excerpt"].lower()

    # Follow-up related question should be suggested
    assert remediation["follow_up_question_id"] is not None
    assert remediation["follow_up_question_id"] != "chem-ch1-f01"


def test_correct_answer_omits_remediation_evidence(remediation_student):
    """
    Submitting a correct answer must grade True and return remediation=None.
    """
    db = SessionLocal()
    topic = resolve_topic(db, "Chemical Reactions")
    topic_id = topic.id
    db.close()

    resp = client.post(
        "/api/v1/adaptive/practice/submit",
        json={
            "student_id": remediation_student,
            "question_id": "chem-ch1-f01",
            "topic_id": topic_id,
            "selected_answer": "A",
            "response_time_ms": 4500,
            "hint_used": False,
        },
    )
    assert resp.status_code == 200
    data = resp.json()

    assert data["correct"] is True
    assert data["remediation"] is None


def test_mathematics_incorrect_answer_retrieves_math_textbook_passage(remediation_student):
    """
    Submitting an incorrect answer for a Mathematics question must ground remediation
    in the authentic Std-10_Maths_EnglishMedium.pdf and correct chapter page.
    """
    db = SessionLocal()
    topic = resolve_topic(db, "Quadratic Equations")
    assert topic is not None
    topic_id = topic.id
    db.close()

    # Question math-ch4-f01 correct answer is Option A (b² - 4ac > 0)
    # Submit incorrect option C (b² - 4ac < 0)
    resp = client.post(
        "/api/v1/adaptive/practice/submit",
        json={
            "student_id": remediation_student,
            "question_id": "math-ch4-f01",
            "topic_id": topic_id,
            "selected_answer": "C",
            "response_time_ms": 7000,
            "hint_used": False,
        },
    )
    assert resp.status_code == 200
    data = resp.json()

    assert data["correct"] is False
    rem = data["remediation"]
    assert rem is not None

    # Must be grounded in Mathematics textbook
    assert rem["source_document"] == "STD-10/Std-10_Maths_EnglishMedium.pdf"
    assert rem["source_page"] == 54
    assert rem["textbook_excerpt"] is not None
    assert "quadratic" in rem["textbook_excerpt"].lower() or "root" in rem["textbook_excerpt"].lower() or "discriminant" in rem["textbook_excerpt"].lower()


def test_remediation_retry_flow_is_atomic_and_idempotent(remediation_student):
    """
    Verifies the student remediation retry flow:
    1. Student gets question wrong -> records event, flags weakness.
    2. Student reviews excerpt and retries with correct answer -> records new event, updates accuracy.
    Both attempts exist as independent historical events.
    """
    db = SessionLocal()
    topic = resolve_topic(db, "Probability")
    topic_id = topic.id

    initial_events_count = db.query(LearningEvent).filter(
        LearningEvent.student_id == remediation_student,
        LearningEvent.topic_id == topic_id,
    ).count()

    # Attempt 1: Miss the question
    r1 = client.post(
        "/api/v1/adaptive/practice/submit",
        json={
            "student_id": remediation_student,
            "question_id": "math-prob-f01",
            "topic_id": topic_id,
            "selected_answer": "D",  # Wrong
            "response_time_ms": 8000,
            "hint_used": False,
        },
    )
    assert r1.status_code == 200
    d1 = r1.json()
    assert d1["correct"] is False
    assert d1["remediation"] is not None
    assert d1["remediation"]["can_retry"] is True

    # Attempt 2: After reviewing remediation, student retries and succeeds
    r2 = client.post(
        "/api/v1/adaptive/practice/submit",
        json={
            "student_id": remediation_student,
            "question_id": "math-prob-f01",
            "topic_id": topic_id,
            "selected_answer": "A",  # Correct: (H, H), (H, T), (T, H), and (T, T)
            "response_time_ms": 3000,
            "hint_used": False,
        },
    )
    assert r2.status_code == 200
    d2 = r2.json()
    assert d2["correct"] is True
    assert d2["remediation"] is None

    # Check database integrity: both events must exist
    final_events = db.query(LearningEvent).filter(
        LearningEvent.student_id == remediation_student,
        LearningEvent.topic_id == topic_id,
    ).order_by(LearningEvent.timestamp.asc()).all()

    assert len(final_events) == initial_events_count + 2
    last_two = final_events[-2:]
    assert last_two[0].correctness is False
    assert last_two[1].correctness is True

    # Topic profile should reflect the recovery
    profile = KnowledgeModelService.calculate_topic_profile(db, remediation_student, topic)
    assert profile.total_attempts >= 2
    assert profile.accuracy > 0.0

    db.close()
