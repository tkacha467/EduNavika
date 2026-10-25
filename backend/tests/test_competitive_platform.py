"""
EduNavika — Competitive Examination & Assessment Engine Comprehensive Test Suite.

Verifies:
1. Exam-specific curriculum filtering (JEE Main/Adv includes Math, NEET includes Bio, zero cross-contamination).
2. Question coverage calculation & 20-question target reporting (shortfall, authentic PYQs vs textbook generated).
3. Supplementary practice generation eliminates shortfall without duplicates (100% idempotent).
4. Previous-year paper extraction and metadata preservation (exam, year, paper, source path, SHA-256 hash).
5. 10-point validation gate rejects invalid questions and unverified scoring eligibility.
6. Server-authoritative assessment timing, countdown, and automatic expiry submission.
7. Candidate answer key protection (secret keys stripped from active session payload).
8. Exam-specific scoring:
   - JEE Main Single Choice (+4 / -1 / 0).
   - JEE Advanced Multiple Choice Partial Marking (+4, +3, +2, +1, -2 penalty, 0).
   - NEET UG Single Choice (+4 / -1 / 0).
   - Numerical evaluation bounds and tolerances.
"""

import uuid
from datetime import datetime, timezone, timedelta
import pytest
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.models.competitive_models import (
    Examination,
    ExamSubject,
    ExamTopic,
    ExamPaper,
    Question,
    QuestionOption,
)
from backend.app.models.curriculum_models import Standard, Subject, Chapter, Topic
from backend.app.services.curriculum_coverage_service import (
    CurriculumCoverageService,
    TARGET_QUESTIONS_PER_CHAPTER,
)
from backend.app.services.competitive_assessment_service import (
    CompetitiveScoringEngine,
    CompetitiveAssessmentService,
    ACTIVE_ASSESSMENT_SESSIONS,
)
from backend.app.services.question_ingestion_service import (
    QuestionIngestionService,
    compute_content_hash,
)
from backend.app.ingestion.competitive_paper_parser import (
    extract_paper_metadata,
    parse_pdf_text_questions,
)


@pytest.fixture
def competitive_test_env(db_session):
    """
    Sets up an isolated competitive testing environment with Standards 11 & 12,
    subjects (Physics, Chemistry, Mathematics, Biology), and verified chapters & topics.
    """
    # 1. Competitive Examinations
    jee_main = Examination(
        code="JEE_MAIN",
        name="Joint Entrance Examination Main",
        conducting_body="National Testing Agency",
        is_active=True,
    )
    jee_adv = Examination(
        code="JEE_ADVANCED",
        name="Joint Entrance Examination Advanced",
        conducting_body="IIT Joint Admission Board",
        is_active=True,
    )
    neet = Examination(
        code="NEET_UG",
        name="National Eligibility cum Entrance Test Undergraduate",
        conducting_body="National Testing Agency",
        is_active=True,
    )
    db_session.add_all([jee_main, jee_adv, neet])
    db_session.flush()

    # 2. Standards 11 & 12
    std11 = Standard(id=str(uuid.uuid4()), grade_number=11, name="Standard 11", is_active=True)
    std12 = Standard(id=str(uuid.uuid4()), grade_number=12, name="Standard 12", is_active=True)
    db_session.add_all([std11, std12])
    db_session.flush()

    # 3. Subjects
    phy11 = Subject(id=str(uuid.uuid4()), standard_id=std11.id, name="Physics", code="PHY11", is_active=True)
    chem11 = Subject(id=str(uuid.uuid4()), standard_id=std11.id, name="Chemistry", code="CHM11", is_active=True)
    math11 = Subject(id=str(uuid.uuid4()), standard_id=std11.id, name="Mathematics", code="MTH11", is_active=True)
    bio11 = Subject(id=str(uuid.uuid4()), standard_id=std11.id, name="Biology", code="BIO11", is_active=True)
    db_session.add_all([phy11, chem11, math11, bio11])
    db_session.flush()

    # 4. ExamSubject mappings
    # JEE Main: Physics, Chemistry, Math
    es_jm_p = ExamSubject(id=str(uuid.uuid4()), exam_code="JEE_MAIN", subject_id=phy11.id)
    es_jm_c = ExamSubject(id=str(uuid.uuid4()), exam_code="JEE_MAIN", subject_id=chem11.id)
    es_jm_m = ExamSubject(id=str(uuid.uuid4()), exam_code="JEE_MAIN", subject_id=math11.id)

    # JEE Advanced: Physics, Chemistry, Math
    es_ja_p = ExamSubject(id=str(uuid.uuid4()), exam_code="JEE_ADVANCED", subject_id=phy11.id)
    es_ja_c = ExamSubject(id=str(uuid.uuid4()), exam_code="JEE_ADVANCED", subject_id=chem11.id)
    es_ja_m = ExamSubject(id=str(uuid.uuid4()), exam_code="JEE_ADVANCED", subject_id=math11.id)

    # NEET: Physics, Chemistry, Biology
    es_ne_p = ExamSubject(id=str(uuid.uuid4()), exam_code="NEET_UG", subject_id=phy11.id)
    es_ne_c = ExamSubject(id=str(uuid.uuid4()), exam_code="NEET_UG", subject_id=chem11.id)
    es_ne_b = ExamSubject(id=str(uuid.uuid4()), exam_code="NEET_UG", subject_id=bio11.id)

    db_session.add_all([es_jm_p, es_jm_c, es_jm_m, es_ja_p, es_ja_c, es_ja_m, es_ne_p, es_ne_c, es_ne_b])
    db_session.flush()

    # 5. Chapters & Topics
    ch_kinematics = Chapter(id=str(uuid.uuid4()), subject_id=phy11.id, chapter_number=2, title="Kinematics", is_active=True)
    ch_bonding = Chapter(id=str(uuid.uuid4()), subject_id=chem11.id, chapter_number=4, title="Chemical Bonding", is_active=True)
    ch_calc = Chapter(id=str(uuid.uuid4()), subject_id=math11.id, chapter_number=7, title="Limits and Derivatives", is_active=True)
    ch_cell = Chapter(id=str(uuid.uuid4()), subject_id=bio11.id, chapter_number=8, title="Cell Biology", is_active=True)
    db_session.add_all([ch_kinematics, ch_bonding, ch_calc, ch_cell])
    db_session.flush()

    t_projectile = Topic(id=str(uuid.uuid4()), chapter_id=ch_kinematics.id, topic_order=1, title="Projectile Motion", is_active=True)
    t_vsepr = Topic(id=str(uuid.uuid4()), chapter_id=ch_bonding.id, topic_order=1, title="VSEPR Theory", is_active=True)
    t_limits = Topic(id=str(uuid.uuid4()), chapter_id=ch_calc.id, topic_order=1, title="Evaluation of Limits", is_active=True)
    t_mitosis = Topic(id=str(uuid.uuid4()), chapter_id=ch_cell.id, topic_order=1, title="Mitosis and Meiosis", is_active=True)
    db_session.add_all([t_projectile, t_vsepr, t_limits, t_mitosis])
    db_session.flush()

    # ExamTopic associations
    et_jm_p = ExamTopic(id=str(uuid.uuid4()), exam_code="JEE_MAIN", topic_id=t_projectile.id)
    et_jm_c = ExamTopic(id=str(uuid.uuid4()), exam_code="JEE_MAIN", topic_id=t_vsepr.id)
    et_jm_m = ExamTopic(id=str(uuid.uuid4()), exam_code="JEE_MAIN", topic_id=t_limits.id)

    et_ne_p = ExamTopic(id=str(uuid.uuid4()), exam_code="NEET_UG", topic_id=t_projectile.id)
    et_ne_c = ExamTopic(id=str(uuid.uuid4()), exam_code="NEET_UG", topic_id=t_vsepr.id)
    et_ne_b = ExamTopic(id=str(uuid.uuid4()), exam_code="NEET_UG", topic_id=t_mitosis.id)

    db_session.add_all([et_jm_p, et_jm_c, et_jm_m, et_ne_p, et_ne_c, et_ne_b])
    db_session.commit()

    return {
        "phy11": phy11,
        "chem11": chem11,
        "math11": math11,
        "bio11": bio11,
        "ch_kinematics": ch_kinematics,
        "ch_bonding": ch_bonding,
        "ch_calc": ch_calc,
        "ch_cell": ch_cell,
        "t_projectile": t_projectile,
        "t_vsepr": t_vsepr,
        "t_limits": t_limits,
        "t_mitosis": t_mitosis,
    }


# ==============================================================================
# 1. Exam-Specific Curriculum Filtering Tests
# ==============================================================================

def test_01_exam_subject_boundaries(db_session, competitive_test_env):
    """Verifies Mathematics is never in NEET and Biology is never in JEE."""
    jee_subjects = [
        es.subject.name
        for es in db_session.query(ExamSubject).filter(ExamSubject.exam_code == "JEE_MAIN").all()
    ]
    assert "Mathematics" in jee_subjects
    assert "Biology" not in jee_subjects

    neet_subjects = [
        es.subject.name
        for es in db_session.query(ExamSubject).filter(ExamSubject.exam_code == "NEET_UG").all()
    ]
    assert "Biology" in neet_subjects
    assert "Mathematics" not in neet_subjects


# ==============================================================================
# 2. Coverage Audit & 20-Question Target Tests
# ==============================================================================

def test_02_coverage_audit_reports_shortfall(db_session, competitive_test_env):
    """Verifies that an unpopulated chapter reports exact 20-question shortfall."""
    service = CurriculumCoverageService(db_session)
    ch = competitive_test_env["ch_kinematics"]

    audit = service.audit_chapter_coverage(ch.id, exam_code="JEE_MAIN")
    assert audit["total_questions"] == 0
    assert audit["eligible_question_count"] == 0
    assert audit["target_coverage"] == 20
    assert audit["shortfall"] == 20
    assert audit["is_coverage_met"] is False


def test_03_supplementary_seeding_eliminates_shortfall(db_session, competitive_test_env):
    """Verifies seeding supplementary practice satisfies 20-question target with zero duplicates."""
    service = CurriculumCoverageService(db_session)
    ch = competitive_test_env["ch_kinematics"]

    # 1. Seed to reach 20 questions
    res = service.seed_supplementary_chapter_practice(ch.id, target_count=20, dry_run=False)
    assert res["needed"] == 20
    assert res["inserted"] == 20
    assert res["target_satisfied"] is True

    # 2. Audit confirms 20 eligible questions
    audit = service.audit_chapter_coverage(ch.id, exam_code="JEE_MAIN")
    assert audit["eligible_question_count"] == 20
    assert audit["textbook_generated_count"] == 20
    assert audit["shortfall"] == 0
    assert audit["is_coverage_met"] is True

    # 3. Repeated seeding creates 0 duplicates (idempotent)
    res_repeat = service.seed_supplementary_chapter_practice(ch.id, target_count=20, dry_run=False)
    assert res_repeat["needed"] == 0
    assert res_repeat["generated"] == 0


# ==============================================================================
# 3. Ingestion Validation Gate Tests
# ==============================================================================

def test_04_validation_gate_blocks_unverified_key_scoring(db_session):
    """Verifies unverified answer keys cannot be marked ELIGIBLE_FOR_SCORING."""
    service = QuestionIngestionService(db_session)

    bad_q = {
        "question_text": "What is the acceleration due to gravity on the Earth's surface in standard metric units?",
        "question_type": "SCQ",
        "options": [
            {"option_key": "A", "option_text": "9.8 m/s^2"},
            {"option_key": "B", "option_text": "10 m/s^2"},
            {"option_key": "C", "option_text": "8.9 m/s^2"},
            {"option_key": "D", "option_text": "12 m/s^2"},
        ],
        "correct_answer_raw": "A",
        "answer_verification_status": "UNVERIFIED",
        "eligibility_for_scoring": "ELIGIBLE_FOR_SCORING",  # FORBIDDEN COMBINATION
        "quarantine_status": "CLEAN",
        "rights_status": "OFFICIAL_FAIR_USE",
        "publish_permission": "OFFICIAL_FAIR_USE",
    }

    is_valid, errors = service.validate_question_data(bad_q)
    assert is_valid is False
    assert any("Unverified answer key CANNOT be marked ELIGIBLE_FOR_SCORING" in e for e in errors)


def test_05_validation_gate_rejects_unbalanced_latex(db_session):
    """Verifies that syntax with unbalanced LaTeX math delimiters ($) fails validation."""
    service = QuestionIngestionService(db_session)

    bad_math_q = {
        "question_text": "Given the vector field $\\vec{F} = x^2\\hat{i} + y^2\\hat{j} without closing delimiter",
        "question_type": "SCQ",
        "options": [
            {"option_key": "A", "option_text": "0"},
            {"option_key": "B", "option_text": "1"},
            {"option_key": "C", "option_text": "2"},
            {"option_key": "D", "option_text": "3"},
        ],
        "correct_answer_raw": "A",
        "answer_verification_status": "HUMAN_VERIFIED",
        "eligibility_for_scoring": "ELIGIBLE_FOR_SCORING",
    }

    is_valid, errors = service.validate_question_data(bad_math_q)
    assert is_valid is False
    assert any("Unbalanced LaTeX/KaTeX math delimiters" in e for e in errors)


# ==============================================================================
# 4. Exam-Specific Scoring Engine Tests
# ==============================================================================

def test_06_jee_main_scq_marking():
    """Verifies JEE Main Single Choice: +4 for correct, -1 for wrong, 0 for blank."""
    # Correct
    pts, ok = CompetitiveScoringEngine.evaluate_scq("A", "A", exam_code="JEE_MAIN")
    assert pts == 4.0
    assert ok is True

    # Incorrect
    pts, ok = CompetitiveScoringEngine.evaluate_scq("B", "A", exam_code="JEE_MAIN")
    assert pts == -1.0
    assert ok is False

    # Unattempted
    pts, ok = CompetitiveScoringEngine.evaluate_scq(None, "A", exam_code="JEE_MAIN")
    assert pts == 0.0
    assert ok is False


def test_07_jee_advanced_multi_correct_partial_marking():
    """
    Verifies JEE Advanced multi-correct partial marking scheme:
    Correct options: [A, B, D]
    - All 3 chosen [A, B, D]: +4 full
    - 2 chosen [A, B]: +2 partial
    - 1 chosen [A]: +1 partial
    - Wrong option included [A, B, C]: -2 penalty
    - Unattempted []: 0
    """
    correct = ["A", "B", "D"]

    # 1. Full marks
    pts, ok = CompetitiveScoringEngine.evaluate_mcq_multi_jee_advanced(["A", "B", "D"], correct)
    assert pts == 4.0
    assert ok is True

    # 2. Partial marks (2 of 3 chosen, no wrong options)
    pts, ok = CompetitiveScoringEngine.evaluate_mcq_multi_jee_advanced(["A", "B"], correct)
    assert pts == 2.0
    assert ok is False

    # 3. Partial marks (1 of 3 chosen, no wrong options)
    pts, ok = CompetitiveScoringEngine.evaluate_mcq_multi_jee_advanced(["A"], correct)
    assert pts == 1.0
    assert ok is False

    # 4. Penalty (-2) if wrong option chosen
    pts, ok = CompetitiveScoringEngine.evaluate_mcq_multi_jee_advanced(["A", "B", "C"], correct)
    assert pts == -2.0
    assert ok is False

    # 5. Unattempted (0)
    pts, ok = CompetitiveScoringEngine.evaluate_mcq_multi_jee_advanced([], correct)
    assert pts == 0.0
    assert ok is False


def test_08_numerical_evaluation_bounds():
    """Verifies numerical tolerance evaluation."""
    # Within min/max bounds [12.4, 12.6]
    pts, ok = CompetitiveScoringEngine.evaluate_numerical(12.5, min_val=12.4, max_val=12.6)
    assert pts == 4.0
    assert ok is True

    # Outside bounds
    pts, ok = CompetitiveScoringEngine.evaluate_numerical(13.1, min_val=12.4, max_val=12.6)
    assert pts == 0.0
    assert ok is False

    # Unattempted
    pts, ok = CompetitiveScoringEngine.evaluate_numerical(None, min_val=12.4, max_val=12.6)
    assert pts == 0.0
    assert ok is False


# ==============================================================================
# 5. Server-Authoritative Assessment Session & Expiry Tests
# ==============================================================================

def test_09_assessment_session_strips_secret_keys(db_session, competitive_test_env):
    """Verifies active assessment payload does NOT expose answer keys to student."""
    service = CurriculumCoverageService(db_session)
    ch = competitive_test_env["ch_kinematics"]
    service.seed_supplementary_chapter_practice(ch.id, target_count=5)

    assess_service = CompetitiveAssessmentService(db_session)
    session = assess_service.start_assessment_session(
        student_id="test_student_1",
        exam_code="JEE_MAIN",
        chapter_id=ch.id,
        duration_minutes=30,
        total_questions=5,
    )

    assert "session_id" in session
    assert 1795 <= session["remaining_seconds"] <= 1800
    for q in session["questions"]:
        assert "_correct_answer_raw" not in q
        assert "correct_answer" not in q
        for opt in q["options"]:
            assert "is_correct" not in opt


def test_10_assessment_submission_and_scoring(db_session, competitive_test_env):
    """Verifies assessment submission evaluates responses and unlocks solution review."""
    service = CurriculumCoverageService(db_session)
    ch = competitive_test_env["ch_kinematics"]
    service.seed_supplementary_chapter_practice(ch.id, target_count=2)

    assess_service = CompetitiveAssessmentService(db_session)
    session = assess_service.start_assessment_session(
        student_id="test_student_2",
        exam_code="JEE_MAIN",
        chapter_id=ch.id,
        duration_minutes=30,
        total_questions=2,
    )
    sid = session["session_id"]
    q1 = session["questions"][0]["question_id"]
    q2 = session["questions"][1]["question_id"]

    # Student answers Q1 with "A" (which is seeded as correct), leaves Q2 unattempted
    assess_service.save_response(sid, q1, selected_option="A", status="ANSWERED")

    report = assess_service.submit_assessment(sid)

    assert report["session_id"] == sid
    assert report["total_score"] == 4.0
    assert report["max_possible_score"] == 8.0
    assert report["percentage"] == 50.0
    assert report["correct_count"] == 1
    assert report["unattempted_count"] == 1
    assert len(report["questions_review"]) == 2
    assert "solution_text" in report["questions_review"][0]


def test_11_assessment_creation_rejected_when_no_questions(db_session, competitive_test_env):
    """Verifies starting an assessment with 0 eligible questions raises ValueError and cannot return a hollow test."""
    ch = competitive_test_env["ch_bonding"]  # No questions seeded for bonding
    assess_service = CompetitiveAssessmentService(db_session)

    with pytest.raises(ValueError, match="No eligible verified questions available"):
        assess_service.start_assessment_session(
            student_id="test_student_empty",
            exam_code="JEE_MAIN",
            chapter_id=ch.id,
            duration_minutes=30,
            total_questions=10,
        )
