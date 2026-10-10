"""
Comprehensive Tests for Curriculum Coverage, Real Textbook MCQ Practice,
and On-Device AI Runtime for EduNavika (PS-06, Team Varja).
"""

import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.core.database import SessionLocal
from backend.app.models.assessment_models import MCQQuestion, OptionKey, QuestionStatus
from backend.app.models import Topic, Subject, Chapter, LearningContent
from backend.app.services.topic_resolver import resolve_topic
from backend.app.services.curriculum_question_bank import (
    CANONICAL_CURRICULUM_BANK,
    CurriculumQuestionValidator,
    sync_canonical_questions_to_db,
)
from backend.app.services.adaptive_practice import AdaptivePracticeService


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c


@pytest.fixture(scope="module")
def db_session():
    db = SessionLocal()
    yield db
    db.close()


def test_1_subject_level_topic_resolution(db_session):
    """Verify all student-visible subjects and diagnostic queries resolve to valid topics with practice questions."""
    subjects_to_test = [
        "Mathematics",
        "math",
        "Science",
        "Physics",
        "Chemistry",
        "Biology",
        "English",
        "Diagnostic Check",
    ]
    for subj in subjects_to_test:
        topic = resolve_topic(db_session, subj)
        assert topic is not None, f"Subject query '{subj}' failed to resolve to a topic."
        assert topic.id is not None, f"Resolved topic for '{subj}' missing id."
        assert topic.title is not None, f"Resolved topic for '{subj}' missing title."


def test_2_curriculum_question_validator_all_canonical_questions():
    """Verify every question in CANONICAL_CURRICULUM_BANK passes the 10-point curriculum rubric."""
    total_questions = 0
    for topic_id, qlist in CANONICAL_CURRICULUM_BANK.items():
        for q in qlist:
            total_questions += 1
            is_valid, errors = CurriculumQuestionValidator.validate(q)
            assert is_valid, f"Question '{q.get('id')}' in topic '{topic_id}' failed validation: {errors}"
            assert len(q["options"]) == 4, f"Question '{q.get('id')}' must have exactly 4 options."
            assert q["correct_answer"] in q["options"], f"Question '{q.get('id')}' correct_answer not in options."
            assert q["source_document"].endswith(".pdf"), f"Question '{q.get('id')}' source_document must be a PDF."
            assert q["source_page"] > 0, f"Question '{q.get('id')}' source_page must be positive."
            assert len(q["explanation"]) > 10, f"Question '{q.get('id')}' explanation too short."

    assert total_questions >= 80, f"Expected at least 80 canonical curriculum questions, found {total_questions}."


def test_3_database_mcq_persistence_and_provenance(db_session):
    """Verify SQLite mcq_questions table is populated with real textbook MCQs linked to topics."""
    # Ensure sync has run
    sync_canonical_questions_to_db(db_session)
    count = db_session.query(MCQQuestion).count()
    assert count >= 60, f"Expected at least 60 persisted MCQ questions in SQLite, found {count}."

    sample_mcqs = db_session.query(MCQQuestion).limit(10).all()
    for mcq in sample_mcqs:
        assert mcq.topic_id is not None
        assert mcq.question_text is not None and len(mcq.question_text) >= 15
        assert mcq.option_a is not None
        assert mcq.option_b is not None
        assert mcq.option_c is not None
        assert mcq.option_d is not None
        assert mcq.correct_option in [OptionKey.A, OptionKey.B, OptionKey.C, OptionKey.D]
        assert mcq.status == QuestionStatus.PUBLISHED
        # Verify topic exists
        topic = db_session.query(Topic).filter(Topic.id == mcq.topic_id).first()
        assert topic is not None, f"MCQ {mcq.id} references non-existent topic {mcq.topic_id}"


def test_4_practice_generation_for_mathematics_and_subtopics(db_session):
    """Verify practice questions generate cleanly for Mathematics without unsupported curriculum warnings."""
    service = AdaptivePracticeService()
    student_id = "e09699dd-0c64-44cc-82ef-ab41a832e072"

    # Test subject-level practice for Mathematics
    math_resp = service.generate_practice_questions(db_session, student_id, "Mathematics", count=3)
    assert len(math_resp.questions) == 3, f"Expected 3 questions for Mathematics, got {len(math_resp.questions)}"
    for q in math_resp.questions:
        assert q.source_document is not None
        assert q.source_page is not None

    # Test subtopic practice for 1.1 Introduction1
    intro_resp = service.generate_practice_questions(
        db_session, student_id, "565bf22f-2a3c-4e5a-b78d-31bcd24bae0c", count=3
    )
    assert len(intro_resp.questions) == 3, f"Expected 3 questions for 1.1 Introduction1, got {len(intro_resp.questions)}"

    # Test Science subject practice
    sci_resp = service.generate_practice_questions(db_session, student_id, "Science", count=3)
    assert len(sci_resp.questions) == 3, f"Expected 3 questions for Science, got {len(sci_resp.questions)}"


def test_5_on_device_ai_runtime_diagnostic_endpoint(client):
    """Verify GET /api/v1/curriculum/runtime-status returns clean operational status without crashing."""
    resp = client.get("/api/v1/curriculum/runtime-status")
    assert resp.status_code == 200, f"Expected 200 from runtime-status, got {resp.status_code}: {resp.text}"
    data = resp.json()
    assert data["status"] == "OPERATIONAL"
    assert data["offline_ready"] is True
    assert data["fallback_engine_available"] is True
    assert data["model_file_present"] is True
    assert "Qwen2.5" in data["model_architecture"]
    assert data["active_mode"] in ["LOCAL_SLM", "DETERMINISTIC_FALLBACK"]


def test_6_curriculum_diagnostic_endpoint_coverage(client):
    """Verify GET /api/v1/curriculum/diagnostic/{subject_or_topic} accurately reports curriculum readiness."""
    resp_math = client.get("/api/v1/curriculum/diagnostic/Mathematics")
    assert resp_math.status_code == 200
    math_data = resp_math.json()
    assert math_data["status"] == "READY"
    assert math_data["offline_ready"] is True
    assert math_data["textbook_chunks_count"] > 0

    resp_chem = client.get("/api/v1/curriculum/diagnostic/Chemical Reactions and Equations")
    assert resp_chem.status_code == 200
    chem_data = resp_chem.json()
    assert chem_data["status"] == "READY"
    assert chem_data["offline_ready"] is True
    assert chem_data["verified_questions_count"] > 0
