"""
Milestone 4 — Phase D: Controlled Pilot-Ingestion Design and Validation Tests.

Verifies:
1. Dry-run performs zero writes to the database.
2. Reprocessing identical data is idempotent and creates zero duplicates.
3. Unverified answers cannot enter scored practice (eligibility guard).
4. Pending rights cannot trigger publication or redistribution (publish_permission guard).
5. Dropped or disputed questions are excluded from scoring.
6. Missing topics and uncertain mappings are quarantined for review.
7. Failures roll back the transaction cleanly.
8. The persistent database remains completely unchanged during disposable-database tests.
"""

import os
import uuid
import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from backend.app.core.database import Base
from backend.app.models import (
    Standard,
    Subject,
    Chapter,
    Topic,
    Examination,
    ExamPaper,
    Question,
    QuestionOption,
    QuestionVerificationLog,
)
from backend.app.services.question_ingestion_service import (
    QuestionIngestionService,
    compute_content_hash,
    validate_katex_syntax,
)

# ---------------------------------------------------------------------------
# Sample 10 Representative Pilot Questions (NTA JEE Main 2024 Session 1)
# ---------------------------------------------------------------------------
def get_sample_pilot_paper_and_questions(topic_id: str):
    paper_info = {
        "id": "paper-jee-main-2024-29jan-s1",
        "paper_identifier": "JEE_MAIN_2024_JAN_29_SHIFT_1",
        "exam_code": "JEE_MAIN",
        "exam_year": 2024,
        "session_or_shift": "Session 1 - 29 Jan 2024 Shift 1",
        "paper_code": "Paper 1 (B.E./B.Tech)",
        "exam_date": "2024-01-29",
        "total_questions": 10,
        "source_pdf_path": "official_archive/JEE_Main_2024_29Jan_Shift1.pdf",
        "source_pdf_hash": "4a71b128e49320dcfb940e4f3a7f80219c63283f510b6d21e89b21f37b1248ac",
    }

    questions = [
        # Q1: Physics - SCQ - Work, Energy & Power
        {
            "paper_question_number": 1,
            "topic_id": topic_id,
            "question_type": "SCQ",
            "question_text": "A body of mass $m$ is dropped from a height $h$ on a sand floor. If it penetrates $x$ distance into the sand, the average resistance force offered by the sand to the body is:",
            "options": [
                {"option_key": "A", "option_text": "$mg \\left(1 + \\frac{h}{x}\\right)$", "is_correct": True, "sort_order": 0},
                {"option_key": "B", "option_text": "$mg \\left(1 - \\frac{h}{x}\\right)$", "is_correct": False, "sort_order": 1},
                {"option_key": "C", "option_text": "$mg \\left(\\frac{h}{x}\\right)$", "is_correct": False, "sort_order": 2},
                {"option_key": "D", "option_text": "$mg \\left(1 + \\frac{x}{h}\\right)$", "is_correct": False, "sort_order": 3},
            ],
            "correct_answer_raw": "A",
            "answer_verification_status": "VERIFIED_OFFICIAL_KEY",
            "solution_text": "By Work-Energy Theorem: $W_{gravity} + W_{sand} = \\Delta K = 0 \\implies mg(h+x) - F_{avg} x = 0 \\implies F_{avg} = mg(1 + h/x)$.",
            "ncert_citation": "NCERT Class 11 Physics Part 1, Chapter 6, Section 6.4",
            "evaluation_policy": "SCQ_EXACT",
            "difficulty_tier": "MEDIUM",
            "cognitive_level": "APPLYING",
            "source_type": "OFFICIAL_PYQ",
            "rights_status": "PENDING_LEGAL_REVIEW",
            "publish_permission": "FORBIDDEN",
            "official_status": "REGULAR",
            "quarantine_status": "CLEAN",
            "eligibility_for_scoring": "INELIGIBLE_UNVERIFIED_KEY",  # Strict until complete review
            "verification_status": "ALGORITHMICALLY_VERIFIED",
        },
        # Q2: Physics - Numerical Value Question - Springs & Conservation of Energy
        {
            "paper_question_number": 2,
            "topic_id": topic_id,
            "question_type": "NUMERICAL",
            "question_text": "A block of mass $m = 2\\text{ kg}$ is attached to a massless spring of spring constant $k = 200\\text{ N/m}$. The other end of the spring is fixed to a rigid vertical wall. The block rests on a horizontal frictionless surface. If the block is pulled by a distance $x_0 = 10\\text{ cm}$ from its equilibrium position and released from rest, the maximum speed of the block during oscillation is $v_{\\max} = \\text{______ } \\times 10^{-1}\\text{ m/s}$.",
            "options": [],
            "correct_answer_raw": "10",
            "numerical_min_val": 10.0,
            "numerical_max_val": 10.0,
            "numerical_precision_type": "INTEGER",
            "evaluation_policy": "INTEGER_EXACT",
            "solution_text": "Using conservation of mechanical energy: $\\frac{1}{2} k x_0^2 = \\frac{1}{2} m v_{\\max}^2 \\implies v_{\\max} = x_0 \\sqrt{k/m} = 0.1 \\times \\sqrt{200/2} = 1.0\\text{ m/s} = 10 \\times 10^{-1}\\text{ m/s}$.",
            "ncert_citation": "NCERT Class 11 Physics Part 1, Chapter 6, Page 124",
            "difficulty_tier": "MEDIUM",
            "cognitive_level": "APPLYING",
            "source_type": "OFFICIAL_PYQ",
            "rights_status": "PENDING_LEGAL_REVIEW",
            "publish_permission": "FORBIDDEN",
            "official_status": "REGULAR",
            "quarantine_status": "CLEAN",
            "eligibility_for_scoring": "INELIGIBLE_UNVERIFIED_KEY",
            "verification_status": "ALGORITHMICALLY_VERIFIED",
        },
        # Q3: Physics - Diagram-Dependent - Current Electricity
        {
            "paper_question_number": 3,
            "topic_id": topic_id,
            "question_type": "SCQ",
            "question_text": "In the given circuit, the potential difference between terminals $A$ and $B$ (i.e. $V_A - V_B$) is: [Circuit diagram with $R_1=4\\,\\Omega, R_2=6\\,\\Omega, E=12\\text{ V}$]",
            "diagram_asset_url": "/assets/diagrams/jee_main_2024_29jan_s1_q3.svg",
            "options": [
                {"option_key": "A", "option_text": "$4.8\\text{ V}$", "is_correct": True, "sort_order": 0},
                {"option_key": "B", "option_text": "$2.4\\text{ V}$", "is_correct": False, "sort_order": 1},
                {"option_key": "C", "option_text": "$7.2\\text{ V}$", "is_correct": False, "sort_order": 2},
                {"option_key": "D", "option_text": "$0\\text{ V}$", "is_correct": False, "sort_order": 3},
            ],
            "correct_answer_raw": "A",
            "answer_verification_status": "VERIFIED_OFFICIAL_KEY",
            "solution_text": "Current $I = E / (R_1 + R_2) = 12 / 10 = 1.2\\text{ A}$. Voltage $V_{AB} = I R_1 = 1.2 \\times 4 = 4.8\\text{ V}$.",
            "ncert_citation": "NCERT Class 12 Physics Part 1, Chapter 3",
            "evaluation_policy": "SCQ_EXACT",
            "difficulty_tier": "EASY",
            "cognitive_level": "UNDERSTANDING",
            "source_type": "OFFICIAL_PYQ",
            "rights_status": "PENDING_LEGAL_REVIEW",
            "publish_permission": "FORBIDDEN",
            "official_status": "REGULAR",
            "quarantine_status": "CLEAN",
            "eligibility_for_scoring": "INELIGIBLE_UNVERIFIED_KEY",
            "verification_status": "ALGORITHMICALLY_VERIFIED",
        },
        # Q4: Chemistry - SCQ - VSEPR & Chemical Bonding
        {
            "paper_question_number": 4,
            "topic_id": topic_id,
            "question_type": "SCQ",
            "question_text": "Among the following molecules/ions, the species having square planar geometry according to VSEPR theory is:",
            "options": [
                {"option_key": "A", "option_text": "$\\text{XeF}_4$", "is_correct": True, "sort_order": 0},
                {"option_key": "B", "option_text": "$\\text{SF}_4$", "is_correct": False, "sort_order": 1},
                {"option_key": "C", "option_text": "$\\text{BF}_4^-$", "is_correct": False, "sort_order": 2},
                {"option_key": "D", "option_text": "$\\text{NH}_4^+$", "is_correct": False, "sort_order": 3},
            ],
            "correct_answer_raw": "A",
            "answer_verification_status": "VERIFIED_OFFICIAL_KEY",
            "solution_text": "$\\text{XeF}_4$ has 4 bond pairs and 2 lone pairs on Xe ($sp^3d^2$ hybridisation), forming a square planar geometry.",
            "ncert_citation": "NCERT Class 11 Chemistry Part 1, Chapter 4",
            "evaluation_policy": "SCQ_EXACT",
            "difficulty_tier": "EASY",
            "cognitive_level": "REMEMBERING",
            "source_type": "OFFICIAL_PYQ",
            "rights_status": "PENDING_LEGAL_REVIEW",
            "publish_permission": "FORBIDDEN",
            "official_status": "REGULAR",
            "quarantine_status": "CLEAN",
            "eligibility_for_scoring": "INELIGIBLE_UNVERIFIED_KEY",
            "verification_status": "ALGORITHMICALLY_VERIFIED",
        },
        # Q5: Chemistry - SCQ - Thermodynamics Spontaneity
        {
            "paper_question_number": 5,
            "topic_id": topic_id,
            "question_type": "SCQ",
            "question_text": "For a spontaneous chemical process at all temperatures, the thermodynamic criteria is:",
            "options": [
                {"option_key": "A", "option_text": "$\\Delta H < 0$ and $\\Delta S > 0$", "is_correct": True, "sort_order": 0},
                {"option_key": "B", "option_text": "$\\Delta H > 0$ and $\\Delta S > 0$", "is_correct": False, "sort_order": 1},
                {"option_key": "C", "option_text": "$\\Delta H < 0$ and $\\Delta S < 0$", "is_correct": False, "sort_order": 2},
                {"option_key": "D", "option_text": "$\\Delta H > 0$ and $\\Delta S < 0$", "is_correct": False, "sort_order": 3},
            ],
            "correct_answer_raw": "A",
            "answer_verification_status": "VERIFIED_OFFICIAL_KEY",
            "solution_text": "$\\Delta G = \\Delta H - T\\Delta S$. When $\\Delta H < 0$ and $\\Delta S > 0$, $\\Delta G$ is negative at all temperatures.",
            "ncert_citation": "NCERT Class 11 Chemistry Part 1, Chapter 6",
            "evaluation_policy": "SCQ_EXACT",
            "difficulty_tier": "EASY",
            "cognitive_level": "UNDERSTANDING",
            "source_type": "OFFICIAL_PYQ",
            "rights_status": "PENDING_LEGAL_REVIEW",
            "publish_permission": "FORBIDDEN",
            "official_status": "REGULAR",
            "quarantine_status": "CLEAN",
            "eligibility_for_scoring": "INELIGIBLE_UNVERIFIED_KEY",
            "verification_status": "ALGORITHMICALLY_VERIFIED",
        },
        # Q6: Chemistry - NVQ - Electrochemistry / Nernst Equation
        {
            "paper_question_number": 6,
            "topic_id": topic_id,
            "question_type": "NUMERICAL",
            "question_text": "The standard reduction potential of a half-cell is $E^\\circ = +0.80\\text{ V}$. For a 1-electron transfer process at $298\\text{ K}$, when the concentration of oxidised form is 10 times the reduced form, the cell potential is $E = \\text{______ } \\times 10^{-2}\\text{ V}$. (Take $\\frac{2.303 RT}{F} = 0.059\\text{ V}$)",
            "options": [],
            "correct_answer_raw": "86",
            "numerical_min_val": 85.8,
            "numerical_max_val": 86.0,
            "numerical_precision_type": "ROUNDED_INTEGER",
            "evaluation_policy": "INTEGER_ROUNDED",
            "solution_text": "$E = E^\\circ - \\frac{0.059}{1} \\log\\left(\\frac{[\\text{red}]}{[\\text{ox}]}\\right) = 0.80 - 0.059(-1) = 0.859\\text{ V} \\approx 86 \\times 10^{-2}\\text{ V}$.",
            "ncert_citation": "NCERT Class 12 Chemistry Part 1, Chapter 3",
            "difficulty_tier": "MEDIUM",
            "cognitive_level": "APPLYING",
            "source_type": "OFFICIAL_PYQ",
            "rights_status": "PENDING_LEGAL_REVIEW",
            "publish_permission": "FORBIDDEN",
            "official_status": "REGULAR",
            "quarantine_status": "CLEAN",
            "eligibility_for_scoring": "INELIGIBLE_UNVERIFIED_KEY",
            "verification_status": "ALGORITHMICALLY_VERIFIED",
        },
        # Q7: Mathematics - SCQ - Limits
        {
            "paper_question_number": 7,
            "topic_id": topic_id,
            "question_type": "SCQ",
            "question_text": "The value of the limit $\\lim_{x \\to 0} \\frac{e^{x^2} - \\cos x}{x^2}$ is equal to:",
            "options": [
                {"option_key": "A", "option_text": "$\\frac{3}{2}$", "is_correct": True, "sort_order": 0},
                {"option_key": "B", "option_text": "$\\frac{1}{2}$", "is_correct": False, "sort_order": 1},
                {"option_key": "C", "option_text": "$1$", "is_correct": False, "sort_order": 2},
                {"option_key": "D", "option_text": "$2$", "is_correct": False, "sort_order": 3},
            ],
            "correct_answer_raw": "A",
            "answer_verification_status": "VERIFIED_OFFICIAL_KEY",
            "solution_text": "Using Taylor expansions: $e^{x^2} = 1 + x^2 + \\dots$ and $\\cos x = 1 - x^2/2 + \\dots$. Numerator = $x^2 + x^2/2 = \\frac{3}{2} x^2$. Limit is $3/2$.",
            "ncert_citation": "NCERT Class 11 Mathematics, Chapter 13",
            "evaluation_policy": "SCQ_EXACT",
            "difficulty_tier": "MEDIUM",
            "cognitive_level": "APPLYING",
            "source_type": "OFFICIAL_PYQ",
            "rights_status": "PENDING_LEGAL_REVIEW",
            "publish_permission": "FORBIDDEN",
            "official_status": "REGULAR",
            "quarantine_status": "CLEAN",
            "eligibility_for_scoring": "INELIGIBLE_UNVERIFIED_KEY",
            "verification_status": "ALGORITHMICALLY_VERIFIED",
        },
        # Q8: Mathematics - NVQ - Definite Integrals
        {
            "paper_question_number": 8,
            "topic_id": topic_id,
            "question_type": "NUMERICAL",
            "question_text": "If $I = \\int_0^{\\pi/2} \\frac{\\sin^3 x}{\\sin^3 x + \\cos^3 x} \\, dx$, then the value of $\\frac{8I}{\\pi}$ is equal to:",
            "options": [],
            "correct_answer_raw": "2",
            "numerical_min_val": 2.0,
            "numerical_max_val": 2.0,
            "numerical_precision_type": "INTEGER",
            "evaluation_policy": "INTEGER_EXACT",
            "solution_text": "Using $\\int_0^a f(x)dx = \\int_0^a f(a-x)dx$: $2I = \\int_0^{\\pi/2} 1 \\, dx = \\pi/2 \\implies I = \\pi/4$. Thus $8I/\\pi = 8(\\pi/4)/\\pi = 2$.",
            "ncert_citation": "NCERT Class 12 Mathematics Part 2, Chapter 7",
            "difficulty_tier": "EASY",
            "cognitive_level": "APPLYING",
            "source_type": "OFFICIAL_PYQ",
            "rights_status": "PENDING_LEGAL_REVIEW",
            "publish_permission": "FORBIDDEN",
            "official_status": "REGULAR",
            "quarantine_status": "CLEAN",
            "eligibility_for_scoring": "INELIGIBLE_UNVERIFIED_KEY",
            "verification_status": "ALGORITHMICALLY_VERIFIED",
        },
        # Q9: Physics - Official Dropped Question (Ambiguous Axis)
        {
            "paper_question_number": 9,
            "topic_id": topic_id,
            "question_type": "SCQ",
            "question_text": "A thin uniform rod of length $L$ is bent at its midpoint such that the two halves are mutually perpendicular. The moment of inertia of the bent rod about an axis passing through the bend and perpendicular to the plane of the rod is: [Disputed/Dropped in official NTA key]",
            "options": [
                {"option_key": "A", "option_text": "$\\frac{1}{12} M L^2$", "is_correct": False, "sort_order": 0},
                {"option_key": "B", "option_text": "$\\frac{1}{24} M L^2$", "is_correct": False, "sort_order": 1},
                {"option_key": "C", "option_text": "$\\frac{1}{3} M L^2$", "is_correct": False, "sort_order": 2},
                {"option_key": "D", "option_text": "$\\frac{1}{6} M L^2$", "is_correct": False, "sort_order": 3},
            ],
            "correct_answer_raw": None,
            "answer_verification_status": "UNVERIFIED",
            "solution_text": "Question dropped by NTA due to ambiguous specification of rotation axis in translated Hindi/English versions.",
            "ncert_citation": "NCERT Class 11 Physics Part 1, Chapter 7",
            "evaluation_policy": "UNSCORED_DROPPED",
            "difficulty_tier": "HARD",
            "cognitive_level": "ANALYZING",
            "source_type": "OFFICIAL_PYQ",
            "rights_status": "PENDING_LEGAL_REVIEW",
            "publish_permission": "FORBIDDEN",
            "official_status": "DROPPED",
            "official_status_evidence": "NTA Final Answer Key 2024 Session 1 Notice: Item dropped due to ambiguity.",
            "quarantine_status": "CLEAN",
            "eligibility_for_scoring": "INELIGIBLE_DROPPED",
            "verification_status": "INGESTED",
        },
        # Q10: Mathematics - Uncertain Topic Mapping (Quarantined)
        {
            "paper_question_number": 10,
            "topic_id": "non_existent_topic_guid",  # Intentionally unmapped
            "question_type": "SCQ",
            "question_text": "Let $S$ be the set of all complex numbers $z$ satisfying $|z - 1| \\le 1$ and $z(1 + i) + \\bar{z}(1 - i) \\le 2$. The area of the region $S$ is:",
            "options": [
                {"option_key": "A", "option_text": "$\\frac{\\pi}{2} - 1$", "is_correct": True, "sort_order": 0},
                {"option_key": "B", "option_text": "$\\frac{\\pi}{4}$", "is_correct": False, "sort_order": 1},
                {"option_key": "C", "option_text": "$\\pi - 1$", "is_correct": False, "sort_order": 2},
                {"option_key": "D", "option_text": "$\\frac{\\pi}{2}$", "is_correct": False, "sort_order": 3},
            ],
            "correct_answer_raw": "A",
            "answer_verification_status": "UNVERIFIED",
            "solution_text": "Area is region inside circle $|z-1|\\le 1$ and half plane $x - y \\le 1$.",
            "ncert_citation": "NCERT Class 11 Mathematics, Chapter 5",
            "evaluation_policy": "UNRESOLVED_POLICY",
            "difficulty_tier": "HARD",
            "cognitive_level": "ANALYZING",
            "source_type": "OFFICIAL_PYQ",
            "rights_status": "PENDING_LEGAL_REVIEW",
            "publish_permission": "FORBIDDEN",
            "official_status": "REGULAR",
            "quarantine_status": "QUARANTINED",
            "quarantine_reason": "UNCERTAIN_TOPIC_MAPPING: Classifier confidence 0.42 below 0.85 threshold",
            "eligibility_for_scoring": "INELIGIBLE_QUARANTINED",
            "verification_status": "INGESTED",
        },
    ]
    return paper_info, questions


# ---------------------------------------------------------------------------
# Test Fixture: Dedicated Disposable Database
# ---------------------------------------------------------------------------
@pytest.fixture
def disposable_pilot_db():
    engine = create_engine("sqlite:///:memory:", future=True)
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine, future=True)
    session = Session()

    # Seed base examination and curriculum records
    exam = Examination(
        code="JEE_MAIN",
        name="Joint Entrance Examination (Main)",
        conducting_body="NTA",
        is_active=True,
    )
    std = Standard(grade_number=11, name="Standard 11")
    session.add(exam)
    session.add(std)
    session.flush()

    subj = Subject(
        id=str(uuid.uuid4()),
        standard_id=std.id,
        name="Physics",
        code="PHYS11",
        is_active=True,
    )
    session.add(subj)
    session.flush()

    chap = Chapter(
        id=str(uuid.uuid4()),
        subject_id=subj.id,
        chapter_number=6,
        title="Work, Energy and Power",
        is_active=True,
    )
    session.add(chap)
    session.flush()

    topic = Topic(
        id=str(uuid.uuid4()),
        chapter_id=chap.id,
        topic_order=1,
        title="Work-Energy Theorem",
        is_active=True,
    )
    session.add(topic)
    session.commit()

    yield session, topic.id

    session.close()
    engine.dispose()


# ---------------------------------------------------------------------------
# Safety & Regression Tests (Step 5)
# ---------------------------------------------------------------------------
def test_1_dry_run_performs_zero_writes(disposable_pilot_db):
    session, topic_id = disposable_pilot_db
    paper_info, questions = get_sample_pilot_paper_and_questions(topic_id)
    svc = QuestionIngestionService(session)

    res = svc.ingest_paper_batch(paper_info, questions, dry_run=True)
    assert res["dry_run"] is True
    assert res["valid_count"] == 10
    assert res["invalid_count"] == 0

    # Verify zero database writes
    assert session.query(ExamPaper).count() == 0
    assert session.query(Question).count() == 0
    assert session.query(QuestionOption).count() == 0
    assert session.query(QuestionVerificationLog).count() == 0


def test_2_reprocessing_does_not_create_duplicates(disposable_pilot_db):
    session, topic_id = disposable_pilot_db
    paper_info, questions = get_sample_pilot_paper_and_questions(topic_id)
    svc = QuestionIngestionService(session)

    # First ingestion run
    res1 = svc.ingest_paper_batch(paper_info, questions, dry_run=False)
    assert res1["inserted_count"] == 10
    assert res1["skipped_duplicate_count"] == 0
    q_count_1 = session.query(Question).count()
    opt_count_1 = session.query(QuestionOption).count()
    assert q_count_1 == 10
    assert opt_count_1 == 28  # 7 SCQs * 4 options = 28 options

    # Second ingestion run (idempotency check)
    res2 = svc.ingest_paper_batch(paper_info, questions, dry_run=False)
    assert res2["inserted_count"] == 0
    assert res2["skipped_duplicate_count"] == 10

    # Counts must NOT increase
    assert session.query(Question).count() == q_count_1
    assert session.query(QuestionOption).count() == opt_count_1


def test_3_unverified_answers_cannot_enter_scored_practice(disposable_pilot_db):
    session, topic_id = disposable_pilot_db
    svc = QuestionIngestionService(session)

    bad_question = {
        "question_text": "A valid test question stem with LaTeX $x = y$.",
        "question_type": "SCQ",
        "options": [
            {"option_key": "A", "option_text": "Opt A", "is_correct": True},
            {"option_key": "B", "option_text": "Opt B", "is_correct": False},
            {"option_key": "C", "option_text": "Opt C", "is_correct": False},
            {"option_key": "D", "option_text": "Opt D", "is_correct": False},
        ],
        "correct_answer_raw": "A",
        "answer_verification_status": "UNVERIFIED",
        "eligibility_for_scoring": "ELIGIBLE_FOR_SCORING",  # ILLEGAL
    }
    is_valid, errors = svc.validate_question_data(bad_question)
    assert is_valid is False
    assert any("Unverified answer key CANNOT be marked ELIGIBLE_FOR_SCORING" in e for e in errors)


def test_4_pending_rights_cannot_trigger_publication(disposable_pilot_db):
    session, topic_id = disposable_pilot_db
    svc = QuestionIngestionService(session)

    bad_question = {
        "question_text": "A valid test question stem with LaTeX $E = mc^2$.",
        "question_type": "SCQ",
        "options": [
            {"option_key": "A", "option_text": "Opt A", "is_correct": True},
            {"option_key": "B", "option_text": "Opt B", "is_correct": False},
            {"option_key": "C", "option_text": "Opt C", "is_correct": False},
            {"option_key": "D", "option_text": "Opt D", "is_correct": False},
        ],
        "correct_answer_raw": "A",
        "rights_status": "PENDING_LEGAL_REVIEW",
        "publish_permission": "ALLOWED",  # ILLEGAL
    }
    is_valid, errors = svc.validate_question_data(bad_question)
    assert is_valid is False
    assert any("publish_permission='FORBIDDEN'" in e for e in errors)


def test_5_dropped_or_disputed_questions_excluded_from_scoring(disposable_pilot_db):
    session, topic_id = disposable_pilot_db
    svc = QuestionIngestionService(session)

    dropped_question = {
        "question_text": "A dropped question with ambiguous text $F = ma$.",
        "question_type": "SCQ",
        "options": [
            {"option_key": "A", "option_text": "Opt A", "is_correct": False},
            {"option_key": "B", "option_text": "Opt B", "is_correct": False},
            {"option_key": "C", "option_text": "Opt C", "is_correct": False},
            {"option_key": "D", "option_text": "Opt D", "is_correct": False},
        ],
        "correct_answer_raw": None,
        "official_status": "DROPPED",
        "eligibility_for_scoring": "ELIGIBLE_FOR_SCORING",  # ILLEGAL
    }
    is_valid, errors = svc.validate_question_data(dropped_question)
    assert is_valid is False
    assert any("DROPPED question CANNOT be marked ELIGIBLE_FOR_SCORING" in e for e in errors)


def test_6_missing_topics_and_uncertain_mappings_quarantined(disposable_pilot_db):
    session, topic_id = disposable_pilot_db
    paper_info, questions = get_sample_pilot_paper_and_questions(topic_id)
    svc = QuestionIngestionService(session)

    res = svc.ingest_paper_batch(paper_info, questions, dry_run=False)
    assert res["quarantined_count"] == 1

    # Verify that the unmapped Question 10 has QUARANTINED status and is ineligible for scoring
    q10 = session.query(Question).filter(Question.paper_question_number == 10).first()
    assert q10 is not None
    assert q10.quarantine_status == "QUARANTINED"
    assert "UNCERTAIN_TOPIC_MAPPING" in q10.quarantine_reason
    assert q10.eligibility_for_scoring == "INELIGIBLE_QUARANTINED"


def test_7_failures_rollback_pilot_transaction(disposable_pilot_db):
    session, topic_id = disposable_pilot_db
    paper_info, questions = get_sample_pilot_paper_and_questions(topic_id)
    svc = QuestionIngestionService(session)

    # Invalidate exam_code to trigger an integrity error
    paper_info_bad = dict(paper_info)
    paper_info_bad["exam_code"] = "NON_EXISTENT_EXAM"

    with pytest.raises(Exception):
        svc.ingest_paper_batch(paper_info_bad, questions, dry_run=False)

    # Confirm rollback
    assert session.query(ExamPaper).count() == 0
    assert session.query(Question).count() == 0


def test_8_persistent_database_is_unchanged(isolated_db_info):
    """Verifies that running pilot tests never alters edunavika.db baseline."""
    get_state = isolated_db_info["get_persistent_db_state"]
    state = get_state()
    assert state is not None
    assert state["sha256"] == "84432e58eb4b67f12da53a914e806b448212948a307a799f7de35b4cf04a2174"
    assert state["row_counts"]["questions"] == 0
    assert state["row_counts"]["exam_papers"] == 0
    assert state["row_counts"]["examinations"] == 3
