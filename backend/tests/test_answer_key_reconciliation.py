"""
EduNavika — Milestone 5.2: Official Answer-Key Reconciliation Test Suite.
Tests deterministic matching, multiple-correct options, numerical bounds,
revised keys, dropped/bonus questions, booklet-code isolation, audit trails, and dry-run safety.
"""

import uuid
import pytest
from datetime import datetime, timezone
from sqlalchemy.orm import Session

from backend.app.services.answer_key_reconciliation_service import (
    AnswerKeyReconciliationService,
    ReconciliationError,
)
from backend.app.models.competitive_models import (
    Examination,
    ExamPaper,
    Question,
    QuestionOption,
    QuestionVerificationLog,
)
from backend.app.models.curriculum_models import Chapter, Topic, Subject, Standard


# ==============================================================================
# Synthetic Test Fixtures (Clearly labelled; never used in production)
# ==============================================================================

SYNTHETIC_OFFICIAL_MANIFEST = {
    "manifest_version": "1.0",
    "is_synthetic_fixture": True,
    "exam_code": "JEE_ADVANCED",
    "exam_year": 2017,
    "paper_session": "Paper 1",
    "paper_code": "Code 1",
    "authority": "IIT Madras (Synthetic Test Fixture)",
    "official_document_ref": "SYNTHETIC_JEE_ADV_2017_FINAL_KEYS_P1.pdf",
    "source_url": "https://jeeadv.ac.in/archive/synthetic/final_keys_p1.pdf",
    "key_version": "FINAL_OFFICIAL_V1",
    "answers": {
        "1": {
            "question_number": 1,
            "question_type": "MCQ_MULTI",
            "official_raw_answer": "A, C",
            "action": "REGULAR",
        },
        "2": {
            "question_number": 2,
            "question_type": "MCQ_MULTI",
            "official_raw_answer": "B, D",
            "action": "REGULAR",
        },
        "8": {
            "question_number": 8,
            "question_type": "NUMERICAL",
            "official_raw_answer": "4",
            "action": "REGULAR",
        },
        "9": {
            "question_number": 9,
            "question_type": "NUMERICAL",
            "official_raw_answer": "12.4 to 12.6",
            "action": "REGULAR",
        },
        "15": {
            "question_number": 15,
            "question_type": "SCQ",
            "official_raw_answer": None,
            "action": "DROPPED",
        },
    },
}


@pytest.fixture
def reconciliation_env(db_session: Session):
    """Sets up an isolated synthetic exam paper with questions for reconciliation testing."""
    # 1. Examination
    exam = Examination(
        code="JEE_ADVANCED",
        name="JEE (Advanced)",
        conducting_body="IITs",
        is_active=True,
    )
    db_session.add(exam)
    db_session.flush()

    # 2. Curriculum Anchor
    std = Standard(id=str(uuid.uuid4()), grade_number=12, name="Standard 12", is_active=True)
    subj = Subject(id=str(uuid.uuid4()), standard_id=std.id, name="Physics", code="PHY12", is_active=True)
    ch = Chapter(id=str(uuid.uuid4()), subject_id=subj.id, chapter_number=1, title="Mechanics", is_active=True)
    top = Topic(id=str(uuid.uuid4()), chapter_id=ch.id, topic_order=1, title="Rotational Dynamics", is_active=True)
    db_session.add_all([std, subj, ch, top])
    db_session.flush()

    # 3. ExamPaper (Code 1)
    paper = ExamPaper(
        id=str(uuid.uuid4()),
        paper_identifier="JEE_ADV_2017_P1_EN_SYNTH",
        exam_code="JEE_ADVANCED",
        exam_year=2017,
        session_or_shift="Paper 1",
        paper_code="Code 1",
        total_questions=5,
    )
    db_session.add(paper)
    db_session.flush()

    # 4. Questions
    # Q1: MCQ_MULTI with 4 options
    q1 = Question(
        id=str(uuid.uuid4()),
        exam_paper_id=paper.id,
        paper_question_number=1,
        topic_id=top.id,
        question_type="MCQ_MULTI",
        question_text="A flat plate moves through gas under constant force. Which options are correct?",
        evaluation_policy="JEE_ADV_MULTI_PARTIAL",
        answer_verification_status="UNVERIFIED",
        eligibility_for_scoring="INELIGIBLE_UNVERIFIED_KEY",
        quarantine_status="CLEAN",
        verification_status="CONTENT_VERIFIED",
        content_hash="hash_synth_q1",
    )
    # Q8: NUMERICAL with 0 options
    q8 = Question(
        id=str(uuid.uuid4()),
        exam_paper_id=paper.id,
        paper_question_number=8,
        topic_id=top.id,
        question_type="NUMERICAL",
        question_text="A drop of liquid divides into droplets. Find the integer value.",
        evaluation_policy="NUMERICAL_TOLERANCE",
        answer_verification_status="UNVERIFIED",
        eligibility_for_scoring="INELIGIBLE_UNVERIFIED_KEY",
        quarantine_status="CLEAN",
        verification_status="CONTENT_VERIFIED",
        content_hash="hash_synth_q8",
    )
    # Q9: NUMERICAL with range
    q9 = Question(
        id=str(uuid.uuid4()),
        exam_paper_id=paper.id,
        paper_question_number=9,
        topic_id=top.id,
        question_type="NUMERICAL",
        question_text="Calculate the acceleration in m/s^2.",
        evaluation_policy="NUMERICAL_TOLERANCE",
        answer_verification_status="UNVERIFIED",
        eligibility_for_scoring="INELIGIBLE_UNVERIFIED_KEY",
        quarantine_status="CLEAN",
        verification_status="CONTENT_VERIFIED",
        content_hash="hash_synth_q9",
    )
    # Q15: Dropped SCQ
    q15 = Question(
        id=str(uuid.uuid4()),
        exam_paper_id=paper.id,
        paper_question_number=15,
        topic_id=top.id,
        question_type="SCQ",
        question_text="Disputed question with ambiguous diagram.",
        evaluation_policy="STANDARD_SCQ",
        answer_verification_status="UNVERIFIED",
        eligibility_for_scoring="INELIGIBLE_UNVERIFIED_KEY",
        quarantine_status="CLEAN",
        verification_status="CONTENT_VERIFIED",
        content_hash="hash_synth_q15",
    )
    # Q99: Unmatched in manifest
    q99 = Question(
        id=str(uuid.uuid4()),
        exam_paper_id=paper.id,
        paper_question_number=99,
        topic_id=top.id,
        question_type="SCQ",
        question_text="Question missing from official key manifest.",
        evaluation_policy="STANDARD_SCQ",
        answer_verification_status="UNVERIFIED",
        eligibility_for_scoring="INELIGIBLE_UNVERIFIED_KEY",
        quarantine_status="CLEAN",
        verification_status="CONTENT_VERIFIED",
        content_hash="hash_synth_q99",
    )

    db_session.add_all([q1, q8, q9, q15, q99])
    db_session.flush()

    # Options for Q1
    opts1 = [
        QuestionOption(id=str(uuid.uuid4()), question_id=q1.id, option_key="A", option_text="Option A text", is_correct=False, sort_order=1),
        QuestionOption(id=str(uuid.uuid4()), question_id=q1.id, option_key="B", option_text="Option B text", is_correct=False, sort_order=2),
        QuestionOption(id=str(uuid.uuid4()), question_id=q1.id, option_key="C", option_text="Option C text", is_correct=False, sort_order=3),
        QuestionOption(id=str(uuid.uuid4()), question_id=q1.id, option_key="D", option_text="Option D text", is_correct=False, sort_order=4),
    ]
    # Options for Q15
    opts15 = [
        QuestionOption(id=str(uuid.uuid4()), question_id=q15.id, option_key="A", option_text="Opt A", is_correct=False, sort_order=1),
        QuestionOption(id=str(uuid.uuid4()), question_id=q15.id, option_key="B", option_text="Opt B", is_correct=False, sort_order=2),
        QuestionOption(id=str(uuid.uuid4()), question_id=q15.id, option_key="C", option_text="Opt C", is_correct=False, sort_order=3),
        QuestionOption(id=str(uuid.uuid4()), question_id=q15.id, option_key="D", option_text="Opt D", is_correct=False, sort_order=4),
    ]
    # Options for Q99
    opts99 = [
        QuestionOption(id=str(uuid.uuid4()), question_id=q99.id, option_key="A", option_text="Opt A", is_correct=False, sort_order=1),
        QuestionOption(id=str(uuid.uuid4()), question_id=q99.id, option_key="B", option_text="Opt B", is_correct=False, sort_order=2),
    ]

    db_session.add_all(opts1 + opts15 + opts99)
    db_session.commit()

    return {
        "paper": paper,
        "q1": q1,
        "q8": q8,
        "q9": q9,
        "q15": q15,
        "q99": q99,
    }


# ==============================================================================
# 1. Manifest Schema & Answer Normalization Tests
# ==============================================================================

def test_manifest_schema_validation():
    """Verifies manifest schema validation enforces provenance fields."""
    # Valid manifest
    ok, errors = AnswerKeyReconciliationService.validate_manifest_schema(SYNTHETIC_OFFICIAL_MANIFEST)
    assert ok is True
    assert len(errors) == 0

    # Missing required fields
    bad_manifest = {"manifest_version": "1.0", "exam_code": "INVALID_EXAM"}
    ok_bad, err_bad = AnswerKeyReconciliationService.validate_manifest_schema(bad_manifest)
    assert ok_bad is False
    assert any("Missing required manifest field" in e for e in err_bad)
    assert any("Invalid exam_code" in e for e in err_bad)


def test_scq_answer_normalization():
    """Verifies SCQ normalization for letter and numeric keys."""
    norm_a = AnswerKeyReconciliationService.normalize_official_answer("A", "SCQ")
    assert norm_a["normalized_answer"] == "A"
    assert norm_a["correct_options"] == ["A"]

    # NEET numeric format (3 -> C)
    norm_3 = AnswerKeyReconciliationService.normalize_official_answer(3, "SCQ")
    assert norm_3["normalized_answer"] == "C"
    assert norm_3["correct_options"] == ["C"]

    # Invalid key
    with pytest.raises(ValueError, match="Invalid SCQ official answer"):
        AnswerKeyReconciliationService.normalize_official_answer("Z", "SCQ")


def test_mcq_multi_answer_normalization():
    """Verifies MCQ_MULTI normalization sorts and validates all option combinations."""
    # Comma string: "C, A" -> "A, C"
    norm_ca = AnswerKeyReconciliationService.normalize_official_answer("C, A", "MCQ_MULTI")
    assert norm_ca["normalized_answer"] == "A, C"
    assert norm_ca["correct_options"] == ["A", "C"]

    # List input with numbers: ["1", "4"] -> "A, D"
    norm_num = AnswerKeyReconciliationService.normalize_official_answer(["1", "4"], "MCQ_MULTI")
    assert norm_num["normalized_answer"] == "A, D"
    assert norm_num["correct_options"] == ["A", "D"]

    # All four options: "A, B, C, D"
    norm_all = AnswerKeyReconciliationService.normalize_official_answer("A, B, C, D", "MCQ_MULTI")
    assert norm_all["correct_options"] == ["A", "B", "C", "D"]


def test_numerical_answer_normalization():
    """Verifies numerical integer, decimal, and range normalization."""
    # Single integer
    norm_int = AnswerKeyReconciliationService.normalize_official_answer("4", "NUMERICAL")
    assert norm_int["numerical_min"] == 4.0
    assert norm_int["numerical_max"] == 4.0
    assert norm_int["normalized_answer"] == "4.00"

    # Range: "12.4 to 12.6"
    norm_rng = AnswerKeyReconciliationService.normalize_official_answer("12.4 to 12.6", "NUMERICAL")
    assert norm_rng["numerical_min"] == 12.4
    assert norm_rng["numerical_max"] == 12.6
    assert norm_rng["normalized_answer"] == "[12.40, 12.60]"

    # Inverted range error
    with pytest.raises(ValueError, match="min_val .* cannot exceed max_val"):
        AnswerKeyReconciliationService.normalize_official_answer({"min_val": 15.0, "max_val": 10.0}, "NUMERICAL")


# ==============================================================================
# 2. Verification Transitions & Provenance Audit Tests
# ==============================================================================

def test_reconcile_question_and_verify_audit_log(db_session, reconciliation_env):
    """Verifies question transitions to ELIGIBLE_FOR_SCORING and writes QuestionVerificationLog."""
    service = AnswerKeyReconciliationService(db_session)
    q1 = reconciliation_env["q1"]

    assert q1.answer_verification_status == "UNVERIFIED"
    assert q1.eligibility_for_scoring == "INELIGIBLE_UNVERIFIED_KEY"

    res = service.reconcile_question_record(
        question=q1,
        manifest_entry=SYNTHETIC_OFFICIAL_MANIFEST["answers"]["1"],
        manifest_meta=SYNTHETIC_OFFICIAL_MANIFEST,
        reviewer="expert:physics_faculty_01",
    )

    assert res["status"] == "SUCCESS"
    assert res["normalized_answer"] == "A, C"
    assert res["eligibility_for_scoring"] == "ELIGIBLE_FOR_SCORING"

    # Verify options synchronization
    opts = {o.option_key: o.is_correct for o in q1.options}
    assert opts["A"] is True
    assert opts["B"] is False
    assert opts["C"] is True
    assert opts["D"] is False

    # Verify QuestionVerificationLog was written
    logs = db_session.query(QuestionVerificationLog).filter(QuestionVerificationLog.question_id == q1.id).all()
    assert len(logs) == 1
    assert "expert:physics_faculty_01" in logs[0].verified_by
    assert logs[0].action_type == "OFFICIAL_KEY_RECONCILED"
    assert "Normalized answer: A, C" in logs[0].review_notes


def test_dropped_question_transitions_to_ineligible_dropped(db_session, reconciliation_env):
    """Verifies cancelled/dropped question is marked INELIGIBLE_DROPPED without negative penalties."""
    service = AnswerKeyReconciliationService(db_session)
    q15 = reconciliation_env["q15"]

    res = service.reconcile_question_record(
        question=q15,
        manifest_entry=SYNTHETIC_OFFICIAL_MANIFEST["answers"]["15"],
        manifest_meta=SYNTHETIC_OFFICIAL_MANIFEST,
    )

    assert res["status"] == "SUCCESS"
    assert res["eligibility_for_scoring"] == "INELIGIBLE_DROPPED"
    assert q15.official_status == "DROPPED"
    assert q15.answer_verification_status == "OFFICIAL_KEY_VERIFIED"


def test_revised_key_reconciliation_maintains_full_history(db_session, reconciliation_env):
    """Verifies revising a previously reconciled key creates a KEY_REVISED audit record."""
    service = AnswerKeyReconciliationService(db_session)
    q1 = reconciliation_env["q1"]

    # 1. Initial Key Reconciliation (A, C)
    service.reconcile_question_record(
        question=q1,
        manifest_entry=SYNTHETIC_OFFICIAL_MANIFEST["answers"]["1"],
        manifest_meta=SYNTHETIC_OFFICIAL_MANIFEST,
    )

    # 2. Board Issues Revised Final Key: Challenge accepted, answer updated to (A, B, C)
    revised_entry = {
        "question_number": 1,
        "question_type": "MCQ_MULTI",
        "official_raw_answer": "A, B, C",
        "action": "REGULAR",
    }
    revised_manifest = dict(SYNTHETIC_OFFICIAL_MANIFEST)
    revised_manifest["key_version"] = "FINAL_REVISED_KEY_V2"

    res = service.reconcile_question_record(
        question=q1,
        manifest_entry=revised_entry,
        manifest_meta=revised_manifest,
        reviewer="pipeline:challenge_resolution_v2",
    )

    assert res["is_revision"] is True
    assert res["action_type"] == "KEY_REVISED"
    assert q1.correct_answer_raw == "A, B, C"

    # Full audit history must contain exactly 2 chronological entries
    logs = db_session.query(QuestionVerificationLog).filter(QuestionVerificationLog.question_id == q1.id).order_by(QuestionVerificationLog.reviewed_at.asc()).all()
    assert len(logs) == 2
    assert logs[0].action_type == "OFFICIAL_KEY_RECONCILED"
    assert logs[1].action_type == "KEY_REVISED"
    assert "ANS:A, C" in logs[1].previous_status
    assert "ANS:A, B, C" in logs[1].new_status


# ==============================================================================
# 3. Booklet Code Isolation & Unmatched Items
# ==============================================================================

def test_booklet_code_mismatch_prevents_cross_contamination(db_session, reconciliation_env):
    """Verifies reconciliation strictly rejects manifests with mismatched booklet codes."""
    service = AnswerKeyReconciliationService(db_session)
    paper = reconciliation_env["paper"]  # Paper has booklet code "Code 1"

    conflicting_manifest = dict(SYNTHETIC_OFFICIAL_MANIFEST)
    conflicting_manifest["paper_code"] = "Code 2"  # Different booklet code with permuted numbers

    with pytest.raises(ReconciliationError, match="AMBIGUOUS_BOOKLET_CODE"):
        service.reconcile_paper_batch(
            paper_id=paper.id,
            manifest=conflicting_manifest,
            dry_run=True,
        )


def test_unmatched_questions_remain_ineligible(db_session, reconciliation_env):
    """Verifies questions lacking an entry in the official manifest remain UNVERIFIED."""
    service = AnswerKeyReconciliationService(db_session)
    paper = reconciliation_env["paper"]
    q99 = reconciliation_env["q99"]

    batch_res = service.reconcile_paper_batch(
        paper_id=paper.id,
        manifest=SYNTHETIC_OFFICIAL_MANIFEST,
        dry_run=False,
    )

    assert batch_res["unmatched_count"] >= 1
    assert q99.answer_verification_status == "UNVERIFIED"
    assert q99.eligibility_for_scoring == "INELIGIBLE_UNVERIFIED_KEY"


def test_dry_run_never_writes_to_database(db_session, reconciliation_env):
    """Verifies reconcile_paper_batch(dry_run=True) rolls back all mutations."""
    service = AnswerKeyReconciliationService(db_session)
    paper = reconciliation_env["paper"]

    log_count_before = db_session.query(QuestionVerificationLog).count()

    batch_res = service.reconcile_paper_batch(
        paper_id=paper.id,
        manifest=SYNTHETIC_OFFICIAL_MANIFEST,
        dry_run=True,
    )

    assert batch_res["dry_run"] is True
    assert batch_res["reconciled_count"] > 0

    # In dry run, database must contain 0 committed verification logs
    log_count_after = db_session.query(QuestionVerificationLog).count()
    assert log_count_after == log_count_before
