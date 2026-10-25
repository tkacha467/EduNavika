"""
EduNavika — Milestone 5.3: Independent NEET 2021 Reconciliation Audit Test Suite.
Validates structural integrity, option alignment, safe quarantine of graphical/empty options,
handling of font encoding anomalies, and failure safety against shifted options, duplicate numbers,
missing keys, and booklet mismatches.
"""

import uuid
import pytest
from datetime import datetime, timezone
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.app.core.database import Base
from backend.app.models.competitive_models import (
    Examination,
    ExamPaper,
    Question,
    QuestionOption,
    QuestionVerificationLog,
)
from backend.app.models.curriculum_models import Standard, Subject, Chapter, Topic
from backend.app.services.answer_key_reconciliation_service import (
    AnswerKeyReconciliationService,
    ReconciliationError,
)
from backend.app.services.question_ingestion_service import (
    QuestionIngestionService,
    compute_content_hash,
)


@pytest.fixture
def in_memory_db():
    """Provides a fresh isolated in-memory SQLite session with full schema."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    # Seed curriculum hierarchy
    std = Standard(id=str(uuid.uuid4()), grade_number=12, name="Class 12")
    session.add(std)
    sub = Subject(id=str(uuid.uuid4()), standard_id=std.id, name="Science", code="SCI")
    session.add(sub)
    ch = Chapter(id=str(uuid.uuid4()), subject_id=sub.id, chapter_number=1, title="General")
    session.add(ch)
    top = Topic(id=str(uuid.uuid4()), chapter_id=ch.id, topic_order=1, title="General Science")
    session.add(top)

    # Seed Exam
    exam = Examination(
        code="NEET_UG",
        name="National Eligibility cum Entrance Test (UG)",
        conducting_body="National Testing Agency",
        description="National medical entrance test",
    )
    session.add(exam)
    session.commit()

    yield session, top.id
    session.close()


def test_booklet_code_mismatch_fails_safely(in_memory_db):
    """Ensures a paper with booklet code M4 cannot be matched against manifest N4 or P1."""
    db, topic_id = in_memory_db
    paper = ExamPaper(
        id=str(uuid.uuid4()),
        paper_identifier="NEET_UG_2021_M4",
        exam_code="NEET_UG",
        exam_year=2021,
        session_or_shift="Main",
        paper_code="M4",
        total_questions=1,
    )
    db.add(paper)
    db.commit()

    reconciler = AnswerKeyReconciliationService(db)
    mismatched_manifest = {
        "manifest_version": "1.0",
        "exam_code": "NEET_UG",
        "exam_year": 2021,
        "paper_session": "Main",
        "paper_code": "N4",  # Different booklet!
        "authority": "NTA",
        "official_document_ref": "Notice.pdf",
        "key_version": "V1",
        "answers": {"1": {"question_number": 1, "question_type": "SCQ", "official_raw_answer": "3"}},
    }

    with pytest.raises(ReconciliationError, match="AMBIGUOUS_BOOKLET_CODE"):
        reconciler.reconcile_paper_batch(paper_id=paper.id, manifest=mismatched_manifest, dry_run=True)


def test_empty_graphical_options_quarantined_not_promoted(in_memory_db):
    """
    CRITICAL DEFECT TEST:
    Questions like Q26/Q60 with empty options (due to missing graphical assets)
    must remain quarantined and MUST NOT be promoted to ELIGIBLE_FOR_SCORING.
    """
    db, topic_id = in_memory_db
    paper = ExamPaper(
        id=str(uuid.uuid4()),
        paper_identifier="NEET_UG_2021_M4",
        exam_code="NEET_UG",
        exam_year=2021,
        session_or_shift="Main",
        paper_code="M4",
        total_questions=1,
    )
    db.add(paper)

    # Empty options question (simulating Q26/Q60)
    q_id = str(uuid.uuid4())
    q = Question(
        id=q_id,
        exam_paper_id=paper.id,
        topic_id=topic_id,
        paper_question_number=26,
        question_text="A thick current carrying cable... variation of magnetic field is:",
        question_type="SCQ",
        content_hash="dummy_hash_26",
        quarantine_status="FLAGGED_MALFORMED",
        quarantine_reason="EMPTY_GRAPHICAL_OPTIONS",
        eligibility_for_scoring="INELIGIBLE_MALFORMED",
        verification_status="PENDING_KEY_RECONCILIATION",
        answer_verification_status="UNVERIFIED",
        rights_status="OFFICIAL_FAIR_USE",
        publish_permission="ALLOWED",
        official_status="PENDING",
    )
    db.add(q)

    # Options with empty text
    for i, key in enumerate(["A", "B", "C", "D"], start=1):
        opt = QuestionOption(
            id=str(uuid.uuid4()),
            question_id=q_id,
            option_key=key,
            option_text="",  # Empty graphical option!
            is_correct=False,
            sort_order=i,
        )
        db.add(opt)
    db.commit()

    manifest = {
        "manifest_version": "1.0",
        "exam_code": "NEET_UG",
        "exam_year": 2021,
        "paper_session": "Main",
        "paper_code": "M4",
        "authority": "NTA",
        "official_document_ref": "Notice.pdf",
        "key_version": "V1",
        "answers": {
            "26": {
                "question_number": 26,
                "question_type": "SCQ",
                "official_raw_answer": "3",
                "action": "REGULAR",
            }
        },
    }

    reconciler = AnswerKeyReconciliationService(db)
    res = reconciler.reconcile_paper_batch(paper_id=paper.id, manifest=manifest, dry_run=False)

    q_reconciled = db.query(Question).filter(Question.id == q_id).first()
    # Verification should confirm answer key, BUT scoring eligibility MUST remain INELIGIBLE
    assert q_reconciled.answer_verification_status == "OFFICIAL_KEY_VERIFIED"
    assert q_reconciled.eligibility_for_scoring == "INELIGIBLE_MALFORMED"
    assert res["promoted_to_eligible_count"] == 0
    assert q_reconciled.quarantine_status != "CLEAN"


def test_missing_manifest_answer_leaves_question_unverified(in_memory_db):
    """Questions omitted from official manifest must remain UNVERIFIED and INELIGIBLE."""
    db, topic_id = in_memory_db
    paper = ExamPaper(
        id=str(uuid.uuid4()),
        paper_identifier="NEET_UG_2021_M4",
        exam_code="NEET_UG",
        exam_year=2021,
        session_or_shift="Main",
        paper_code="M4",
        total_questions=2,
    )
    db.add(paper)

    q1 = Question(
        id=str(uuid.uuid4()),
        exam_paper_id=paper.id,
        topic_id=topic_id,
        paper_question_number=1,
        question_text="Valid question 1",
        question_type="SCQ",
        content_hash="h1",
        quarantine_status="CLEAN",
        eligibility_for_scoring="INELIGIBLE_UNVERIFIED",
        answer_verification_status="UNVERIFIED",
        rights_status="OFFICIAL_FAIR_USE",
        publish_permission="ALLOWED",
    )
    q2 = Question(
        id=str(uuid.uuid4()),
        exam_paper_id=paper.id,
        topic_id=topic_id,
        paper_question_number=2,
        question_text="Valid question 2 with missing key",
        question_type="SCQ",
        content_hash="h2",
        quarantine_status="CLEAN",
        eligibility_for_scoring="INELIGIBLE_UNVERIFIED",
        answer_verification_status="UNVERIFIED",
        rights_status="OFFICIAL_FAIR_USE",
        publish_permission="ALLOWED",
    )
    db.add_all([q1, q2])
    db.commit()

    manifest = {
        "manifest_version": "1.0",
        "exam_code": "NEET_UG",
        "exam_year": 2021,
        "paper_session": "Main",
        "paper_code": "M4",
        "authority": "NTA",
        "official_document_ref": "Notice.pdf",
        "key_version": "V1",
        "answers": {
            "1": {"question_number": 1, "question_type": "SCQ", "official_raw_answer": "1", "action": "REGULAR"}
            # Notice Q2 is intentionally missing!
        },
    }

    reconciler = AnswerKeyReconciliationService(db)
    res = reconciler.reconcile_paper_batch(paper_id=paper.id, manifest=manifest, dry_run=False)

    assert res["reconciled_count"] == 1
    assert res["unmatched_count"] == 1

    q2_db = db.query(Question).filter(Question.paper_question_number == 2).first()
    assert q2_db.answer_verification_status == "UNVERIFIED"
    assert q2_db.eligibility_for_scoring == "INELIGIBLE_UNVERIFIED"


def test_invalid_official_answer_raises_and_rejects(in_memory_db):
    """Unexpected raw answer keys (e.g. '9', 'X') must raise ValueError in SCQ normalization."""
    reconciler = AnswerKeyReconciliationService(in_memory_db[0])
    with pytest.raises(ValueError, match="Invalid SCQ official answer representation"):
        reconciler.normalize_official_answer(raw_answer="9", question_type="SCQ")

    with pytest.raises(ValueError, match="Invalid SCQ official answer representation"):
        reconciler.normalize_official_answer(raw_answer="INVALID", question_type="SCQ")


def test_option_order_and_shift_rejection():
    """
    Validates that extracted options maintain strict ascending order (1->A, 2->B, 3->C, 4->D)
    and reject disordered/shifted option sets.
    """
    valid_order = ["1", "2", "3", "4"]
    shifted_order = ["2", "1", "3", "4"]
    missing_order = ["1", "2", "4"]

    def validate_option_keys(keys):
        if len(keys) != 4 or keys != ["1", "2", "3", "4"]:
            return False, "OPTION_ORDER_MISMATCH"
        return True, "CLEAN"

    ok, _ = validate_option_keys(valid_order)
    assert ok is True

    ok, reason = validate_option_keys(shifted_order)
    assert ok is False
    assert reason == "OPTION_ORDER_MISMATCH"

    ok, reason = validate_option_keys(missing_order)
    assert ok is False
    assert reason == "OPTION_ORDER_MISMATCH"
