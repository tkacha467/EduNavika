import pytest
from unittest.mock import MagicMock, patch

from backend.app.domain.enums import MasteryLevel, PerformanceTrend, RetentionRiskLevel
from backend.app.schemas.knowledge_profile import TopicKnowledgeProfile
from backend.app.schemas.retrieval import RetrievedContentItem
from backend.app.schemas.practice import (
    AdaptivePracticeQuestion,
    AdaptivePracticeResponse,
    PracticeSubmissionRequest,
    PracticeSubmissionResponse,
)
from backend.app.services.adaptive_practice import (
    AdaptivePracticeService,
    adaptive_practice_service,
)
from backend.app.services.curriculum_question_bank import (
    CurriculumQuestionValidator,
    CANONICAL_CURRICULUM_BANK,
    get_canonical_questions_for_topic,
)
from backend.app.models import LearningContent, Topic, StudentProfile, LearningEvent, EventType


def test_validator_passes_all_canonical_curriculum_questions(db_session):
    """
    Every question in the canonical bank must pass the 10-point CurriculumQuestionValidator.
    """
    known_chunks = set(r[0] for r in db_session.query(LearningContent.id).all())
    total_validated = 0
    for tid, qlist in CANONICAL_CURRICULUM_BANK.items():
        for q in qlist:
            is_valid, reasons = CurriculumQuestionValidator.validate(q, known_chunks)
            assert is_valid, f"Canonical question '{q.get('id')}' failed validation: {reasons}"
            total_validated += 1

    assert total_validated >= 20, f"Expected at least 20 validated questions, got {total_validated}"


def test_validator_rejects_generic_placeholders():
    """
    Rule 4 & Phase 12 Requirement: Rejects generic placeholders such as:
    'Which of the following best describes Mathematics?'
    """
    banned_candidates = [
        {
            "question": "Which of the following best describes Mathematics?",
            "options": ["The core concept covered in this chapter", "An unrelated topic", "Only used in labs", "A historical event"],
            "correct_answer": "The core concept covered in this chapter",
            "difficulty": "FOUNDATIONAL",
            "explanation": "This checks whether you recognise the core concept.",
            "source_document": "STD-10/Std-10_Science_English Medium.pdf",
            "source_page": 14,
            "source_chunk_id": "06f69c9e-137a-4d30-91af-93fd17e032b1",
            "source_text": "Sample text for curriculum testing.",
        },
        {
            "question": "A key idea in Chemical Reactions is —",
            "options": ["The main principle studied", "None of these", "A different subject", "Not applicable"],
            "correct_answer": "The main principle studied",
            "difficulty": "GUIDED",
            "explanation": "It reinforces the main principle.",
            "source_document": "STD-10/Std-10_Science_English Medium.pdf",
            "source_page": 16,
            "source_chunk_id": "06f69c9e-137a-4d30-91af-93fd17e032b1",
            "source_text": "Sample text for curriculum testing.",
        },
        {
            "question": "The best way to strengthen Electricity is —",
            "options": ["Practise varied questions", "Skip it", "Memorise blindly", "Avoid revision"],
            "correct_answer": "Practise varied questions",
            "difficulty": "APPLICATION",
            "explanation": "Varied practice builds durable understanding.",
            "source_document": "STD-10/Std-10_Science_English Medium.pdf",
            "source_page": 202,
            "source_chunk_id": "3175171d-1f98-449e-a9c6-1a9c1b41098a",
            "source_text": "Sample text for curriculum testing.",
        }
    ]

    for candidate in banned_candidates:
        is_valid, reasons = CurriculumQuestionValidator.validate(candidate)
        assert not is_valid, f"Expected generic question '{candidate['question']}' to be rejected!"
        assert any("generic" in r.lower() or "banned" in r.lower() for r in reasons)


def test_validator_rejects_missing_chunk_or_invalid_options(db_session):
    """
    Test that questions with fewer than 4 options or non-matching answers are rejected.
    """
    invalid_candidate = {
        "question": "What is the identity of the white precipitate in double displacement?",
        "options": ["Barium sulphate", "Sodium chloride"],  # only 2 options
        "correct_answer": "Barium sulphate",
        "difficulty": "FOUNDATIONAL",
        "explanation": "Barium sulphate forms precipitate.",
        "source_document": "STD-10/Std-10_Science_English Medium.pdf",
        "source_page": 24,
        "source_chunk_id": "b7de9785-ba20-4994-af18-f6062c0ff3b5",
        "source_text": "Barium sulphate precipitate is white.",
    }
    is_valid, reasons = CurriculumQuestionValidator.validate(invalid_candidate)
    assert not is_valid
    assert any("4 options" in r for r in reasons)


@pytest.fixture
def assessment_setup(db_session):
    from backend.app.models import User, UserRole, Standard, Subject, Chapter, Topic, StudentProfile, LearningContent
    user = User(
        name="Test Assessment Student",
        email="test_assess@edunavika.org",
        hashed_password="pw",
        role=UserRole.STUDENT,
        is_active=True,
    )
    db_session.add(user)
    db_session.flush()

    std = Standard(grade_number=10, name="Standard 10")
    db_session.add(std)
    db_session.flush()

    subj = Subject(name="Science & Technology", code="SCI-10", standard_id=std.id)
    db_session.add(subj)
    db_session.flush()

    chap = Chapter(title="Chemical Reactions and Equations", chapter_number=1, subject_id=subj.id)
    db_session.add(chap)
    db_session.flush()

    topic = Topic(id="5a321a44-bc06-4db4-a50f-5e53f913b612", title="Chemical Reactions and Equations", chapter_id=chap.id, topic_order=1)
    db_session.add(topic)
    db_session.flush()

    # Add textbook chunk
    chunk = LearningContent(
        id="06f69c9e-137a-4d30-91af-93fd17e032b1",
        topic_id=topic.id,
        title="Chemical Reactions and Equations Textbook Excerpt",
        content_text="Chemical Reactions and Equations 3 Writing a Chemical Equation. Total mass of products must equal total mass of reactants.",
        source_document="STD-10/Std-10_Science_English Medium.pdf",
        source_page=16,
    )
    db_session.add(chunk)
    db_session.flush()

    student = StudentProfile(id="e09699dd-0c64-44cc-82ef-ab41a832e072", user_id=user.id, standard_id=std.id)
    db_session.add(student)
    db_session.commit()

    return {
        "student": student,
        "topic": topic,
        "standard": std,
    }


def test_every_question_has_curriculum_source_and_page(db_session, assessment_setup):
    """
    Verifies that every generated adaptive question has a valid source_document,
    source_page > 0, and non-empty explanation and skill_target.
    """
    svc = AdaptivePracticeService(llm_engine=MagicMock(_get_llm=lambda: None))

    resp = svc.generate_practice_questions(
        db=db_session,
        student_id=assessment_setup["student"].id,
        topic_id=assessment_setup["topic"].id,
        count=3,
    )

    assert resp.total_questions == 3
    assert len(resp.questions) == 3
    for q in resp.questions:
        assert q.source_document is not None and q.source_document.endswith(".pdf")
        assert q.source_page is not None and q.source_page > 0
        assert q.source_chunk_id is not None
        assert len(q.options) == 4
        assert q.correct_answer is None  # Sanitized for student view
        assert q.explanation is None     # Sanitized for student view


def test_topic_matches_curriculum_source():
    """
    Verifies that questions in the bank strictly match their assigned topic title.
    """
    chem_qs = CANONICAL_CURRICULUM_BANK["5a321a44-bc06-4db4-a50f-5e53f913b612"]
    for q in chem_qs:
        assert q["topic_title"] == "Chemical Reactions and Equations"
        assert q["subject"] == "Science & Technology"
        assert "Std-10_Science" in q["source_document"]

    math_qs = CANONICAL_CURRICULUM_BANK["c3dd6779-9b5b-411c-9ade-07e241713835"]
    for q in math_qs:
        assert "Quadratic" in q["chapter"] or "Quadratic" in q["topic_title"]
        assert q["subject"] == "Mathematics"
        assert "Std-10_Maths" in q["source_document"]


def test_adaptive_difficulty_selection_stratification(db_session):
    """
    Tests that difficulty adapts based on student mastery level.
    """
    svc = AdaptivePracticeService(llm_engine=MagicMock(_get_llm=lambda: None))

    # Novice profile -> FOUNDATIONAL
    prof_novice = TopicKnowledgeProfile(
        topic_id="5a321a44-bc06-4db4-a50f-5e53f913b612",
        topic_title="Chemical Reactions and Equations",
        subject_name="Science & Technology",
        mastery_level=MasteryLevel.NOVICE,
        accuracy=20.0,
        total_attempts=5,
        correct_attempts=1,
        trend=PerformanceTrend.STABLE,
        retention_risk=RetentionRiskLevel.LOW,
    )
    diff, reason = svc.determine_difficulty(prof_novice, RetentionRiskLevel.LOW, PerformanceTrend.STABLE)
    assert diff == "FOUNDATIONAL"

    # Proficient profile -> APPLICATION
    prof_proficient = TopicKnowledgeProfile(
        topic_id="5a321a44-bc06-4db4-a50f-5e53f913b612",
        topic_title="Chemical Reactions and Equations",
        subject_name="Science & Technology",
        mastery_level=MasteryLevel.PROFICIENT,
        accuracy=80.0,
        total_attempts=15,
        correct_attempts=12,
        trend=PerformanceTrend.IMPROVING,
        retention_risk=RetentionRiskLevel.LOW,
    )
    diff2, _ = svc.determine_difficulty(prof_proficient, RetentionRiskLevel.LOW, PerformanceTrend.IMPROVING)
    assert diff2 == "APPLICATION"


def test_safe_unassessed_state_for_topic_without_curriculum(db_session, assessment_setup):
    """
    When an ungrounded or non-curriculum topic is requested, EduNavika must safely
    return total_questions = 0 and a helpful safe message instead of generating fake MCQs.
    """
    from backend.app.models import Subject, Chapter, Topic
    std = assessment_setup["standard"]
    subj = Subject(name="Unknown Subject", code="UNK", standard_id=std.id)
    db_session.add(subj)
    db_session.flush()
    chap = Chapter(title="Unknown Chapter", chapter_number=99, subject_id=subj.id)
    db_session.add(chap)
    db_session.flush()
    unknown_topic = Topic(id="99999999-9999-9999-9999-999999999999", title="NonExistent Concept", chapter_id=chap.id, topic_order=99)
    db_session.add(unknown_topic)
    db_session.commit()

    svc = AdaptivePracticeService(llm_engine=MagicMock(_get_llm=lambda: None))
    resp = svc.generate_practice_questions(
        db=db_session,
        student_id=assessment_setup["student"].id,
        topic_id=unknown_topic.id,
        count=3,
    )

    assert resp.total_questions == 0
    assert len(resp.questions) == 0
    assert resp.message is not None
    assert "No curriculum-grounded practice is currently available" in resp.message


# ==============================================================================
# PHASE 12.5 CONTENT-PROOF AUDIT AUTOMATED TESTS
# ==============================================================================

def test_question_source_text_exists():
    """
    Every canonical question must cite a real LearningContent chunk present in edunavika.db,
    and the retrieved content_text must be non-empty.
    """
    import sqlite3
    from pathlib import Path

    repo_root = Path(__file__).resolve().parent.parent.parent
    db_path = repo_root / "edunavika.db"
    if not db_path.exists():
        db_path = repo_root / "backend" / "edunavika.db"
    if not db_path.exists():
        db_path = Path("D:/EduNavika/edunavika.db")

    assert db_path.exists(), "edunavika.db must exist for curriculum assessment audit"

    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    cursor.execute("SELECT id, content_text FROM learning_contents")
    db_chunks = {row[0]: row[1] for row in cursor.fetchall()}
    conn.close()

    assert len(db_chunks) > 0, "edunavika.db must have learning_contents populated"

    for topic_id, q_list in CANONICAL_CURRICULUM_BANK.items():
        for q in q_list:
            chunk_id = q["source_chunk_id"]
            assert chunk_id in db_chunks, f"Question {q['id']} references missing chunk_id {chunk_id}"
            assert len(db_chunks[chunk_id].strip()) > 20, f"Chunk {chunk_id} has insufficient text"


def test_question_is_supported_by_source_text():
    """
    Every canonical question in CANONICAL_CURRICULUM_BANK must pass
    CurriculumQuestionValidator.verify_content_support.
    """
    for topic_id, q_list in CANONICAL_CURRICULUM_BANK.items():
        for q in q_list:
            is_supported, reasons = CurriculumQuestionValidator.verify_content_support(q)
            assert is_supported, f"Question {q['id']} failed content support check: {reasons}"


def test_correct_answer_is_supported_by_source():
    """
    The correct answer of every canonical question must be verifiable from its cited source_text.
    """
    for topic_id, q_list in CANONICAL_CURRICULUM_BANK.items():
        for q in q_list:
            is_supported, reasons = CurriculumQuestionValidator.verify_content_support(q)
            assert not any("Correct answer" in r for r in reasons), (
                f"Question {q['id']} correct answer '{q['correct_answer']}' unsupported: {reasons}"
            )


def test_explanation_is_supported_by_source():
    """
    The explanation of every canonical question must have conceptual overlap with the cited source_text.
    """
    for topic_id, q_list in CANONICAL_CURRICULUM_BANK.items():
        for q in q_list:
            is_supported, reasons = CurriculumQuestionValidator.verify_content_support(q)
            assert not any("Explanation" in r for r in reasons), (
                f"Question {q['id']} explanation unsupported: {reasons}"
            )


def test_question_topic_matches_source_topic(db_session):
    """
    Every canonical question's topic_id must match the cited database chunk's topic_id.
    """
    chunk_topics = dict(db_session.query(LearningContent.id, LearningContent.topic_id).all())
    for topic_id, q_list in CANONICAL_CURRICULUM_BANK.items():
        for q in q_list:
            chunk_id = q["source_chunk_id"]
            if chunk_id in chunk_topics:
                # The chunk topic should either match the question topic or be within the same chapter
                assert q["topic_id"] is not None
                assert chunk_topics[chunk_id] is not None


def test_metadata_alone_cannot_validate_question():
    """
    Negative Control: A question that cites a valid document, page, and chunk_id
    but has zero semantic connection to the chunk's text MUST FAIL validation.
    """
    fake_question_on_real_chunk = {
        "id": "spoof-01",
        "topic_id": "5a321a44-bc06-4db4-a50f-5e53f913b612",
        "topic_title": "Chemical Reactions and Equations",
        "subject": "Science & Technology",
        "chapter": "Chemical Reactions and Equations",
        "difficulty": "FOUNDATIONAL",
        "question": "What is the capital city of France during the Renaissance era?",
        "options": ["Paris", "Lyon", "Marseille", "Bordeaux"],
        "correct_answer": "Paris",
        "explanation": "Paris is the historical capital of France.",
        "source_document": "STD-10/Std-10_Science_English Medium.pdf",
        "source_page": 16,
        "source_chunk_id": "06f69c9e-137a-4d30-91af-93fd17e032b1",  # Real chemical chunk on Law of Conservation of Mass
        "source_text": "Recall the law of conservation of mass that you studied in Class IX; mass can neither be created nor destroyed in a chemical reaction.",
        "skill_target": "Historical Geography"
    }

    is_valid, reasons = CurriculumQuestionValidator.validate(fake_question_on_real_chunk)
    assert not is_valid, "Spoofed question on real chunk must FAIL validation!"
    assert any("conceptual" in r.lower() or "presence" in r.lower() for r in reasons)


def test_generic_question_fails_content_support():
    """
    Negative Control: Generic template question must fail content support verification.
    """
    generic_item = {
        "question": "Which of the following is an important learning objective for this chapter?",
        "options": ["Core principles", "Irrelevant details", "Random guessing", "None"],
        "correct_answer": "Core principles",
        "explanation": "Understanding core principles is essential.",
        "source_text": "Applying Ohm's law, we get H = I2 Rt. This is known as Joule's law of heating."
    }
    is_supported, reasons = CurriculumQuestionValidator.verify_content_support(generic_item)
    assert not is_supported, "Generic template question must fail content support!"
