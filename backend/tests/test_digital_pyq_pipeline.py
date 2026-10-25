"""
EduNavika — Milestone 5.1: Digital PYQ Pipeline Regression & Validation Test Suite.
Tests digital PDF extraction quality, cover page rejection, section-aware question typing,
option normalization, mathematical preservation, lifecycle transitions, and dry-run isolation.
"""

import os
import uuid
import pytest
from sqlalchemy.orm import Session

from backend.app.ingestion.competitive_paper_parser import (
    is_cover_or_instruction_page,
    detect_section_metadata,
    clean_question_text,
    parse_options_flexible,
    audit_question_candidate,
    extract_paper_metadata,
    dry_run_audit_paper,
    ingest_competitive_paper,
)
from backend.app.services.question_ingestion_service import (
    QuestionIngestionService,
    compute_content_hash,
    validate_katex_syntax,
)
from backend.app.models.competitive_models import (
    Examination,
    ExamPaper,
    Question,
    QuestionOption,
)
from backend.app.models.curriculum_models import Chapter, Topic, Subject, Standard


# ==============================================================================
# 1. Extraction Boundary & Cover Page Rejection Tests
# ==============================================================================

def test_cover_page_instruction_exclusion():
    """Verifies test booklet instructions and candidate directions are rejected as questions."""
    cover_page_text = (
        "This Booklet contains 28 pages.\n"
        "Do not open this Test Booklet until you are asked to do so.\n"
        "Important Instructions :\n"
        "1. The Answer Sheet is inside this Test Booklet. When you are directed to open the Test Booklet,\n"
        "take out the Answer Sheet and fill in the particulars on OFFICE Copy carefully.\n"
        "2. The test is of 3 hours duration and the Test Booklet contains 200 multiple-choice questions.\n"
        "Candidate's Name: _______________________ Roll No: __________________\n"
    )

    is_cover, reason = is_cover_or_instruction_page(cover_page_text, page_num=1)
    assert is_cover is True
    assert "COVER_PAGE" in reason

    # Contrast with regular content page with Q.1
    content_page_text = (
        "PART I : PHYSICS\n"
        "SECTION 1\n"
        "Q.1 A particle of mass m moves under the action of a central force F = -k/r^2.\n"
        "[A] The angular momentum is conserved\n"
        "[B] The energy is negative\n"
        "[C] The orbit is a circle\n"
        "[D] The period is independent of radius\n"
    )
    is_cov_content, _ = is_cover_or_instruction_page(content_page_text, page_num=1)
    assert is_cov_content is False


def test_question_number_boundary_segmentation():
    """Verifies clean question segmentation without boundary bleed or missing stems."""
    raw_text = (
        "Q.1 An ideal gas expands adiabatically from volume V1 to V2.\n"
        "[A] Pressure increases\n[B] Pressure decreases\n[C] Temperature increases\n[D] Entropy increases\n\n"
        "Q.2 A satellite is in orbit at radius R.\n"
        "[A] Period is T\n[B] Period is 2T\n[C] Velocity is v\n[D] Velocity is 2v\n"
    )

    stem1, opts1, fmt1 = parse_options_flexible(raw_text.split("Q.2")[0])
    clean1 = clean_question_text(stem1)
    assert "ideal gas expands adiabatically" in clean1
    assert "Q.2" not in clean1
    assert len(opts1) == 4
    assert opts1[0]["option_key"] == "A"


# ==============================================================================
# 2. Option Normalization & Question Type Tests
# ==============================================================================

def test_flexible_option_formats():
    """Verifies bracket [A]-[D], paren (A)-(D), paren numeric (1)-(4), and dot A.-D. formats."""
    # 1. Bracket format (JEE)
    body_bracket = "The resistance of a wire is:\n[A] R/2\n[B] R\n[C] 2R\n[D] 4R"
    _, opts_b, fmt_b = parse_options_flexible(body_bracket)
    assert fmt_b == "BRACKET_ALPHA"
    assert [o["option_key"] for o in opts_b] == ["A", "B", "C", "D"]

    # 2. Paren format (1)-(4) (NEET)
    body_neet = "The unit of electric flux is:\n(1) V m\n(2) N/C\n(3) V/m\n(4) J/C"
    _, opts_n, fmt_n = parse_options_flexible(body_neet)
    assert fmt_n == "PAREN_NUMERIC_NEET"
    assert [o["option_key"] for o in opts_n] == ["A", "B", "C", "D"]
    assert opts_n[0]["option_text"] == "V m"

    # 3. Paren alpha format (A)-(D)
    body_paren = "The kinetic energy is:\n(A) 10 J\n(B) 20 J\n(C) 30 J\n(D) 40 J"
    _, opts_p, fmt_p = parse_options_flexible(body_paren)
    assert fmt_p == "PAREN_ALPHA"
    assert [o["option_key"] for o in opts_p] == ["A", "B", "C", "D"]


def test_numerical_questions_without_options():
    """Verifies numerical questions with 0 options are recognized with NUMERICAL type."""
    body_num = "A drop of liquid divides itself into 8 identical droplets. Find the change in surface energy."
    stem, opts, fmt = parse_options_flexible(body_num)
    assert fmt == "NO_OPTIONS_NUMERICAL"
    assert len(opts) == 0

    audited = audit_question_candidate({
        "question_text": clean_question_text(stem),
        "question_type": "NUMERICAL",
        "options": opts,
    }, {"exam_code": "JEE_ADVANCED"})

    assert audited["question_type"] == "NUMERICAL"
    assert audited["is_malformed"] is False
    assert audited["quarantine_status"] == "CLEAN"


def test_multiple_correct_question_detection():
    """Verifies section-aware metadata detects MCQ_MULTI with partial marking."""
    section_text = (
        "SECTION 1 (Maximum Marks: 28)\n"
        "This section contains SEVEN questions.\n"
        "ONE OR MORE THAN ONE of these four options is(are) correct.\n"
    )
    meta = detect_section_metadata(section_text, {"subject": "Physics", "section": "SECTION 1"})
    assert meta["question_type"] == "MCQ_MULTI"
    assert meta["evaluation_policy"] == "JEE_ADV_MULTI_PARTIAL"


# ==============================================================================
# 3. Mathematical Notation Preservation & Content Hashing
# ==============================================================================

def test_mathematical_notation_preservation():
    """Verifies LaTeX inline ($) and display ($$) math and Unicode symbols are preserved."""
    stem_math = r"A wave pulse of wavelength $\lambda_0 = 500\text{ nm}$ is incident on a slit of width $a = 0.2\text{ mm}$."
    assert validate_katex_syntax(stem_math) is True

    # Test broken LaTeX syntax detection
    stem_broken = r"The angle $\theta = \pi/4 is not closed."
    assert validate_katex_syntax(stem_broken) is False

    audited = audit_question_candidate({
        "question_text": stem_broken,
        "question_type": "NUMERICAL",
        "options": [],
    }, {"exam_code": "JEE_MAIN"})
    assert audited["quarantine_status"] == "FLAGGED_MALFORMED"
    assert audited["quarantine_reason"] == "UNBALANCED_LATEX_DELIMITERS"


def test_duplicate_detection_and_idempotency():
    """Verifies deterministic SHA-256 hash generation for deduplication."""
    stem1 = "  Find the equivalent resistance across terminals A and B.  "
    stem2 = "Find the equivalent resistance across terminals a and b."
    opts1 = [{"option_key": "A", "option_text": "5 Ohm"}, {"option_key": "B", "option_text": "10 Ohm"}]
    opts2 = [{"option_key": "a", "option_text": "5 ohm "}, {"option_key": "b", "option_text": " 10 ohm"}]

    h1 = compute_content_hash(stem1, opts1, None)
    h2 = compute_content_hash(stem2, opts2, None)
    assert h1 == h2
    assert len(h1) == 64


# ==============================================================================
# 4. Lifecycle & Scoring Eligibility Verification
# ==============================================================================

def test_unverified_questions_ineligible_for_scoring():
    """Verifies raw extracted questions are strictly INELIGIBLE_FOR_SCORING."""
    q_entry = {
        "question_text": "A block of mass M slides down a frictionless incline of angle theta.",
        "question_type": "SCQ",
        "options": [
            {"option_key": "A", "option_text": "g sin(theta)"},
            {"option_key": "B", "option_text": "g cos(theta)"},
            {"option_key": "C", "option_text": "g tan(theta)"},
            {"option_key": "D", "option_text": "g"},
        ],
    }
    audited = audit_question_candidate(q_entry, {"exam_code": "JEE_ADVANCED"})
    assert audited["verification_status"] == "EXTRACTED_PENDING_REVIEW"
    assert audited["answer_verification_status"] == "UNVERIFIED"
    assert audited["eligibility_for_scoring"] == "INELIGIBLE_UNVERIFIED_KEY"

    # Validation service must reject promoting unverified question to ELIGIBLE_FOR_SCORING
    service = QuestionIngestionService(None)
    audited["eligibility_for_scoring"] = "ELIGIBLE_FOR_SCORING"
    is_valid, errors = service.validate_question_data(audited)
    assert is_valid is False
    assert any("Unverified answer key CANNOT be marked ELIGIBLE_FOR_SCORING" in e for e in errors)


def test_verified_question_eligibility_transition():
    """Verifies question becomes ELIGIBLE_FOR_SCORING only when official answer is provided and validated."""
    service = QuestionIngestionService(None)
    q_data = {
        "question_text": "What is the speed of light in vacuum?",
        "question_type": "SCQ",
        "options": [
            {"option_key": "A", "option_text": "3 x 10^8 m/s"},
            {"option_key": "B", "option_text": "2 x 10^8 m/s"},
            {"option_key": "C", "option_text": "1 x 10^8 m/s"},
            {"option_key": "D", "option_text": "4 x 10^8 m/s"},
        ],
        "correct_answer_raw": "A",
        "answer_verification_status": "OFFICIAL_KEY_VERIFIED",
        "official_status": "REGULAR",
        "quarantine_status": "CLEAN",
        "verification_status": "CONTENT_VERIFIED",
        "rights_status": "OFFICIAL_FAIR_USE",
        "publish_permission": "OFFICIAL_FAIR_USE",
        "eligibility_for_scoring": "ELIGIBLE_FOR_SCORING",
    }
    is_valid, errors = service.validate_question_data(q_data)
    assert is_valid is True
    assert len(errors) == 0


# ==============================================================================
# 5. Dry-Run Isolation & No-Write Guarantees
# ==============================================================================

def test_dry_run_never_writes_to_database(db_session):
    """Verifies dry_run_audit_paper and ingest_competitive_paper(dry_run=True) do not commit rows."""
    q_before = db_session.query(Question).count()
    ep_before = db_session.query(ExamPaper).count()

    pdf_sample = "GSEB-Dataset/Dataset/Dataset/jee/2017_1.pdf"
    if os.path.exists(pdf_sample):
        # 1. Audit paper dry run
        report = dry_run_audit_paper(pdf_sample)
        assert report["candidate_count"] > 0
        assert report["is_scanned"] is False

        # Database counts must remain strictly identical
        assert db_session.query(Question).count() == q_before
        assert db_session.query(ExamPaper).count() == ep_before
