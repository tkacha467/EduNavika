"""
Milestone 5.6: Production Ingestion Gate and Pilot Integrity Tests.
Exercises the actual QuestionIngestionService, AnswerKeyReconciliationService,
and CompetitiveAssessmentService on an isolated disposable SQLite database.

Verifies:
1. Valid reviewed text-only question passes ingestion, reconciliation, and becomes scoring eligible & visible.
2. Missing option is caught by ingestion validation gate and rejected.
3. Missing diagram question is quarantined and cannot be promoted by answer key reconciliation.
4. Mismatched official answer key (booklet code / exam mismatch) fails safely.
5. Correct key with unverified content remains INELIGIBLE_UNVERIFIED_CONTENT.
6. Question with publish_permission='FORBIDDEN' is blocked from serving/assessments.
7. Deduplication by content hash and clean transaction rollback on failure.
8. Persistent database edunavika.db remains strictly at 0 competitive records.
"""

import os
import uuid
import sqlite3
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
from backend.app.services.question_ingestion_service import (
    QuestionIngestionService,
    compute_content_hash,
)
from backend.app.services.answer_key_reconciliation_service import (
    AnswerKeyReconciliationService,
    ReconciliationError,
)
from backend.app.services.competitive_assessment_service import (
    CompetitiveAssessmentService,
)


@pytest.fixture
def disposable_gate_db():
    engine = create_engine("sqlite:///:memory:", future=True)
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine, future=True)
    session = Session()

    # Seed base examination and curriculum records
    exam = Examination(
        code="NEET_UG",
        name="National Eligibility cum Entrance Test (UG)",
        conducting_body="NTA",
        is_active=True,
    )
    std = Standard(id=str(uuid.uuid4()), grade_number=12, name="Class 12")
    session.add(exam)
    session.add(std)
    session.flush()

    subj = Subject(
        id=str(uuid.uuid4()),
        standard_id=std.id,
        name="Physics",
        code="PHYS12",
        is_active=True,
    )
    session.add(subj)
    session.flush()

    chap = Chapter(
        id=str(uuid.uuid4()),
        subject_id=subj.id,
        chapter_number=1,
        title="Electrostatics",
        is_active=True,
    )
    session.add(chap)
    session.flush()

    topic = Topic(
        id=str(uuid.uuid4()),
        chapter_id=chap.id,
        topic_order=1,
        title="Electric Charges and Fields",
        is_active=True,
    )
    session.add(topic)
    session.commit()

    yield session, topic.id, chap.id

    session.close()
    engine.dispose()


def test_1_valid_reviewed_text_only_question(disposable_gate_db):
    """Case 1: Valid reviewed text-only question passes full ingestion and promotion pipeline."""
    session, topic_id, chap_id = disposable_gate_db
    ingestion_service = QuestionIngestionService(session)

    paper_info = {
        "id": "paper-neet-2021-gate-test",
        "paper_identifier": "NEET_UG_2021_M4_GATE_PILOT",
        "exam_code": "NEET_UG",
        "exam_year": 2021,
        "session_or_shift": "Main",
        "paper_code": "M4",
        "total_questions": 1,
        "source_pdf_path": "GSEB-Dataset/Dataset/Dataset/Neet/neet-2021.pdf",
        "source_pdf_hash": "e9acdfb29dfcff0a3a186819f7336330af4ce51855990d1081c78637b338587a",
    }

    questions_data = [
        {
            "paper_question_number": 1,
            "topic_id": topic_id,
            "question_type": "SCQ",
            "question_text": "A dipole of dipole moment $p$ is placed in a uniform electric field $E$. The torque acting on the dipole is:",
            "options": [
                {"option_key": "A", "option_text": "$\\vec{\\tau} = \\vec{p} \\times \\vec{E}$", "is_correct": False, "sort_order": 0},
                {"option_key": "B", "option_text": "$\\vec{\\tau} = \\vec{p} \\cdot \\vec{E}$", "is_correct": False, "sort_order": 1},
                {"option_key": "C", "option_text": "$\\vec{\\tau} = \\vec{E} \\times \\vec{p}$", "is_correct": False, "sort_order": 2},
                {"option_key": "D", "option_text": "$\\vec{\\tau} = 0$", "is_correct": False, "sort_order": 3},
            ],
            "correct_answer_raw": None,
            "answer_verification_status": "UNVERIFIED",
            "solution_text": "Torque on a dipole in uniform field is tau = p x E.",
            "ncert_citation": "NCERT Class 12 Physics Part 1, Chapter 1",
            "evaluation_policy": "SCQ_EXACT",
            "difficulty_tier": "EASY",
            "cognitive_level": "REMEMBERING",
            "source_type": "OFFICIAL_PYQ",
            "rights_status": "OFFICIAL_FAIR_USE",
            "publish_permission": "ALLOWED",
            "official_status": "REGULAR",
            "quarantine_status": "CLEAN",
            "eligibility_for_scoring": "INELIGIBLE_UNVERIFIED_KEY",
            "verification_status": "CONTENT_VERIFIED",
        }
    ]

    # Ingest through real QuestionIngestionService
    res = ingestion_service.ingest_paper_batch(paper_info, questions_data, dry_run=False)
    assert res["valid_count"] == 1
    assert res["inserted_count"] == 1

    # Reconcile with official answer key manifest
    reconciler = AnswerKeyReconciliationService(session)
    manifest = {
        "manifest_version": "1.0",
        "exam_code": "NEET_UG",
        "exam_year": 2021,
        "paper_session": "Main",
        "paper_code": "M4",
        "authority": "National Testing Agency (NTA)",
        "official_document_ref": "Notice_20211101205130.pdf",
        "key_version": "FINAL_OFFICIAL_DECLARED_01.11.2021",
        "answers": {
            "1": {"question_number": 1, "question_type": "SCQ", "official_raw_answer": "1", "action": "REGULAR"}
        },
    }

    recon_res = reconciler.reconcile_paper_batch(paper_info["id"], manifest, dry_run=False)
    assert recon_res["reconciled_count"] == 1
    assert recon_res["promoted_to_eligible_count"] == 1

    # Verify database state
    q = session.query(Question).filter(Question.paper_question_number == 1).first()
    assert q is not None
    assert q.eligibility_for_scoring == "ELIGIBLE_FOR_SCORING"
    assert q.answer_verification_status == "OFFICIAL_KEY_VERIFIED"
    assert q.verification_status == "VERIFIED"
    assert q.correct_answer_raw == "A"
    assert q.options[0].is_correct is True
    assert q.options[1].is_correct is False

    # Verify assessment engine / API visibility
    assess_svc = CompetitiveAssessmentService(session)
    sess_data = assess_svc.start_assessment_session(
        student_id="student_123",
        exam_code="NEET_UG",
        chapter_id=chap_id,
        duration_minutes=30,
        total_questions=1,
    )
    assert sess_data["total_questions"] == 1
    assert sess_data["questions"][0]["question_id"] == q.id


def test_2_question_with_missing_option(disposable_gate_db):
    """Case 2: Ingestion service validation rejects a question with missing options."""
    session, topic_id, _ = disposable_gate_db
    ingestion_service = QuestionIngestionService(session)

    paper_info = {
        "id": "paper-missing-opt",
        "paper_identifier": "NEET_UG_2021_M4_MISSING_OPT",
        "exam_code": "NEET_UG",
        "exam_year": 2021,
        "session_or_shift": "Main",
        "paper_code": "M4",
        "total_questions": 1,
    }

    # Only 3 options instead of required 4
    defective_question = [
        {
            "paper_question_number": 2,
            "topic_id": topic_id,
            "question_type": "SCQ",
            "question_text": "An electron moves with velocity $v$ in magnetic field $B$. The force is:",
            "options": [
                {"option_key": "A", "option_text": "$q(\\vec{v} \\times \\vec{B})$", "is_correct": True},
                {"option_key": "B", "option_text": "$q(\\vec{v} \\cdot \\vec{B})$", "is_correct": False},
                {"option_key": "C", "option_text": "$0$", "is_correct": False},
            ],
            "correct_answer_raw": "A",
            "answer_verification_status": "UNVERIFIED",
            "quarantine_status": "CLEAN",
            "eligibility_for_scoring": "INELIGIBLE_UNVERIFIED_KEY",
        }
    ]

    res = ingestion_service.ingest_paper_batch(paper_info, defective_question, dry_run=False)
    assert res["invalid_count"] == 1
    assert res["inserted_count"] == 0
    assert any("requires exactly 4 options" in err for err in res["validation_errors"]["Q2"])

    # Ensure zero records inserted
    assert session.query(Question).count() == 0


def test_3_question_with_missing_diagram(disposable_gate_db):
    """Case 3: Missing diagram question is quarantined and cannot be promoted to scoring eligibility."""
    session, topic_id, chap_id = disposable_gate_db
    ingestion_service = QuestionIngestionService(session)

    paper_info = {
        "id": "paper-missing-diag",
        "paper_identifier": "NEET_UG_2021_M4_MISSING_DIAG",
        "exam_code": "NEET_UG",
        "exam_year": 2021,
        "session_or_shift": "Main",
        "paper_code": "M4",
        "total_questions": 1,
    }

    quarantined_question = [
        {
            "paper_question_number": 4,
            "topic_id": topic_id,
            "question_type": "SCQ",
            "question_text": "The equivalent capacitance of the combination shown in the figure is:",
            "options": [
                {"option_key": "A", "option_text": "$2C$", "is_correct": False},
                {"option_key": "B", "option_text": "$C/2$", "is_correct": False},
                {"option_key": "C", "option_text": "$3C$", "is_correct": False},
                {"option_key": "D", "option_text": "$C$", "is_correct": False},
            ],
            "correct_answer_raw": None,
            "answer_verification_status": "UNVERIFIED",
            "quarantine_status": "INELIGIBLE_REQUIRES_ASSET",
            "quarantine_reason": "MISSING_DIAGRAM_IN_STEM: Capacitor bridge schematic not extracted",
            "eligibility_for_scoring": "INELIGIBLE_QUARANTINED",
            "verification_status": "CONTENT_VERIFIED",
            "publish_permission": "FORBIDDEN",
        }
    ]

    res = ingestion_service.ingest_paper_batch(paper_info, quarantined_question, dry_run=False)
    assert res["inserted_count"] == 1
    assert res["quarantined_count"] == 1

    # Reconcile with official key
    reconciler = AnswerKeyReconciliationService(session)
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
            "4": {"question_number": 4, "question_type": "SCQ", "official_raw_answer": "2", "action": "REGULAR"}
        },
    }

    recon_res = reconciler.reconcile_paper_batch(paper_info["id"], manifest, dry_run=False)
    assert recon_res["reconciled_count"] == 1
    assert recon_res["promoted_to_eligible_count"] == 0  # NOT promoted!

    q = session.query(Question).filter(Question.paper_question_number == 4).first()
    assert q.answer_verification_status == "OFFICIAL_KEY_VERIFIED"
    assert q.eligibility_for_scoring == "INELIGIBLE_MALFORMED"

    # Assessment engine must exclude this quarantined question
    assess_svc = CompetitiveAssessmentService(session)
    with pytest.raises(ValueError, match="No eligible verified questions available"):
        assess_svc.start_assessment_session(
            student_id="student_123",
            exam_code="NEET_UG",
            chapter_id=chap_id,
            duration_minutes=30,
            total_questions=1,
        )


def test_4_question_with_mismatched_official_key(disposable_gate_db):
    """Case 4: Reconciliation fails safely when booklet code or exam metadata mismatches."""
    session, topic_id, _ = disposable_gate_db
    ingestion_service = QuestionIngestionService(session)

    paper_info = {
        "id": "paper-mismatch-test",
        "paper_identifier": "NEET_UG_2021_M4_MISMATCH",
        "exam_code": "NEET_UG",
        "exam_year": 2021,
        "session_or_shift": "Main",
        "paper_code": "M4",
        "total_questions": 1,
    }

    questions_data = [
        {
            "paper_question_number": 5,
            "topic_id": topic_id,
            "question_type": "SCQ",
            "question_text": "An electric dipole consists of two opposite charges $q$ separated by distance $2a$.",
            "options": [
                {"option_key": "A", "option_text": "$2qa$", "is_correct": False},
                {"option_key": "B", "option_text": "$qa$", "is_correct": False},
                {"option_key": "C", "option_text": "$q/2a$", "is_correct": False},
                {"option_key": "D", "option_text": "$2q/a$", "is_correct": False},
            ],
            "correct_answer_raw": None,
            "answer_verification_status": "UNVERIFIED",
            "quarantine_status": "CLEAN",
            "eligibility_for_scoring": "INELIGIBLE_UNVERIFIED_KEY",
            "verification_status": "CONTENT_VERIFIED",
        }
    ]

    ingestion_service.ingest_paper_batch(paper_info, questions_data, dry_run=False)

    reconciler = AnswerKeyReconciliationService(session)

    # 1. Booklet code mismatch (Paper has M4, manifest has P1)
    bad_booklet_manifest = {
        "manifest_version": "1.0",
        "exam_code": "NEET_UG",
        "exam_year": 2021,
        "paper_session": "Main",
        "paper_code": "P1",  # Wrong booklet!
        "authority": "NTA",
        "official_document_ref": "Notice.pdf",
        "key_version": "V1",
        "answers": {"5": {"question_number": 5, "question_type": "SCQ", "official_raw_answer": "1"}},
    }
    with pytest.raises(ReconciliationError, match="AMBIGUOUS_BOOKLET_CODE"):
        reconciler.reconcile_paper_batch(paper_info["id"], bad_booklet_manifest, dry_run=False)

    # 2. Exam code mismatch
    bad_exam_manifest = dict(bad_booklet_manifest)
    bad_exam_manifest["paper_code"] = "M4"
    bad_exam_manifest["exam_code"] = "JEE_MAIN"
    with pytest.raises(ValueError, match="Exam code mismatch"):
        reconciler.reconcile_paper_batch(paper_info["id"], bad_exam_manifest, dry_run=False)

    # Question must remain in original unverified state
    q = session.query(Question).filter(Question.paper_question_number == 5).first()
    assert q.answer_verification_status == "UNVERIFIED"
    assert q.eligibility_for_scoring == "INELIGIBLE_UNVERIFIED_KEY"


def test_5_question_with_correct_key_but_unverified_content(disposable_gate_db):
    """Case 5: A question with an official answer key cannot be promoted if content verification is pending."""
    session, topic_id, chap_id = disposable_gate_db
    ingestion_service = QuestionIngestionService(session)

    paper_info = {
        "id": "paper-unverified-content",
        "paper_identifier": "NEET_UG_2021_M4_UNVERIFIED_CONTENT",
        "exam_code": "NEET_UG",
        "exam_year": 2021,
        "session_or_shift": "Main",
        "paper_code": "M4",
        "total_questions": 1,
    }

    # Ingested with verification_status='INGESTED' (not CONTENT_VERIFIED)
    unverified_content_q = [
        {
            "paper_question_number": 8,
            "topic_id": topic_id,
            "question_type": "SCQ",
            "question_text": "A convex lens of focal length $f$ produces a real image of magnification $m$.",
            "options": [
                {"option_key": "A", "option_text": "$f(1 + 1/m)$", "is_correct": False},
                {"option_key": "B", "option_text": "$f(1 - 1/m)$", "is_correct": False},
                {"option_key": "C", "option_text": "$f(1 + m)$", "is_correct": False},
                {"option_key": "D", "option_text": "$f(1 - m)$", "is_correct": False},
            ],
            "correct_answer_raw": None,
            "answer_verification_status": "UNVERIFIED",
            "quarantine_status": "CLEAN",
            "eligibility_for_scoring": "INELIGIBLE_UNVERIFIED_KEY",
            "verification_status": "INGESTED",  # Content not yet verified against source PDF!
        }
    ]

    ingestion_service.ingest_paper_batch(paper_info, unverified_content_q, dry_run=False)

    # Reconcile with official key
    reconciler = AnswerKeyReconciliationService(session)
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
            "8": {"question_number": 8, "question_type": "SCQ", "official_raw_answer": "1", "action": "REGULAR"}
        },
    }

    recon_res = reconciler.reconcile_paper_batch(paper_info["id"], manifest, dry_run=False)
    assert recon_res["reconciled_count"] == 1
    assert recon_res["promoted_to_eligible_count"] == 0  # Blocked from promotion!

    q = session.query(Question).filter(Question.paper_question_number == 8).first()
    assert q.answer_verification_status == "OFFICIAL_KEY_VERIFIED"
    assert q.eligibility_for_scoring == "INELIGIBLE_UNVERIFIED_CONTENT"

    # Assessment engine excludes questions with unverified content
    assess_svc = CompetitiveAssessmentService(session)
    with pytest.raises(ValueError, match="No eligible verified questions available"):
        assess_svc.start_assessment_session(
            student_id="student_123",
            exam_code="NEET_UG",
            chapter_id=chap_id,
            duration_minutes=30,
            total_questions=1,
        )


def test_6_question_without_established_publication_permission(disposable_gate_db):
    """Case 6: A scoring-eligible question with publish_permission='FORBIDDEN' is blocked from serving."""
    session, topic_id, chap_id = disposable_gate_db
    ingestion_service = QuestionIngestionService(session)

    paper_info = {
        "id": "paper-rights-forbidden",
        "paper_identifier": "NEET_UG_2021_M4_FORBIDDEN_RIGHTS",
        "exam_code": "NEET_UG",
        "exam_year": 2021,
        "session_or_shift": "Main",
        "paper_code": "M4",
        "total_questions": 1,
    }

    questions_data = [
        {
            "paper_question_number": 35,
            "topic_id": topic_id,
            "question_type": "SCQ",
            "question_text": "A nucleus with mass number 240 breaks into two fragments each of mass number 120.",
            "options": [
                {"option_key": "A", "option_text": "$100\\text{ MeV}$", "is_correct": False},
                {"option_key": "B", "option_text": "$200\\text{ MeV}$", "is_correct": False},
                {"option_key": "C", "option_text": "$216\\text{ MeV}$", "is_correct": False},
                {"option_key": "D", "option_text": "$120\\text{ MeV}$", "is_correct": False},
            ],
            "correct_answer_raw": None,
            "answer_verification_status": "UNVERIFIED",
            "rights_status": "PENDING_LEGAL_REVIEW",
            "publish_permission": "FORBIDDEN",  # Strict prohibition on publication
            "quarantine_status": "CLEAN",
            "eligibility_for_scoring": "INELIGIBLE_UNVERIFIED_KEY",
            "verification_status": "CONTENT_VERIFIED",
        }
    ]

    ingestion_service.ingest_paper_batch(paper_info, questions_data, dry_run=False)

    reconciler = AnswerKeyReconciliationService(session)
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
            "35": {"question_number": 35, "question_type": "SCQ", "official_raw_answer": "3", "action": "REGULAR"}
        },
    }

    recon_res = reconciler.reconcile_paper_batch(paper_info["id"], manifest, dry_run=False)
    assert recon_res["promoted_to_eligible_count"] == 1

    q = session.query(Question).filter(Question.paper_question_number == 35).first()
    assert q.eligibility_for_scoring == "ELIGIBLE_FOR_SCORING"
    assert q.publish_permission == "FORBIDDEN"

    # The serving layer must block this question because publish_permission == 'FORBIDDEN'
    assess_svc = CompetitiveAssessmentService(session)
    with pytest.raises(ValueError, match="No eligible verified questions available"):
        assess_svc.start_assessment_session(
            student_id="student_123",
            exam_code="NEET_UG",
            chapter_id=chap_id,
            duration_minutes=30,
            total_questions=1,
        )


def test_7_duplicate_ingestion_and_rollback(disposable_gate_db):
    """Case 7: Duplicate ingestion skips existing content hashes; transaction failures roll back cleanly."""
    session, topic_id, _ = disposable_gate_db
    ingestion_service = QuestionIngestionService(session)

    paper_info = {
        "id": "paper-idempotency",
        "paper_identifier": "NEET_UG_2021_M4_IDEMPOTENCY",
        "exam_code": "NEET_UG",
        "exam_year": 2021,
        "session_or_shift": "Main",
        "paper_code": "M4",
        "total_questions": 1,
    }

    questions_data = [
        {
            "paper_question_number": 51,
            "topic_id": topic_id,
            "question_type": "SCQ",
            "question_text": "The Mayer relation between molar heat capacities $C_p$ and $C_v$ of an ideal gas is:",
            "options": [
                {"option_key": "A", "option_text": "$C_p + C_v = R$", "is_correct": False},
                {"option_key": "B", "option_text": "$C_p - C_v = R$", "is_correct": True},
                {"option_key": "C", "option_text": "$C_p / C_v = R$", "is_correct": False},
                {"option_key": "D", "option_text": "$C_v - C_p = R$", "is_correct": False},
            ],
            "correct_answer_raw": "B",
            "answer_verification_status": "OFFICIAL_KEY_VERIFIED",
            "rights_status": "OFFICIAL_FAIR_USE",
            "publish_permission": "ALLOWED",
            "quarantine_status": "CLEAN",
            "eligibility_for_scoring": "ELIGIBLE_FOR_SCORING",
            "verification_status": "CONTENT_VERIFIED",
        }
    ]

    # First run
    res1 = ingestion_service.ingest_paper_batch(paper_info, questions_data, dry_run=False)
    assert res1["inserted_count"] == 1
    assert res1["skipped_duplicate_count"] == 0
    assert session.query(Question).count() == 1

    # Second run with identical content
    res2 = ingestion_service.ingest_paper_batch(paper_info, questions_data, dry_run=False)
    assert res2["inserted_count"] == 0
    assert res2["skipped_duplicate_count"] == 1
    assert session.query(Question).count() == 1  # No duplicate question created!

    # Transaction rollback test: Invalidate exam code to trigger ValueError
    bad_paper_info = dict(paper_info)
    bad_paper_info["exam_code"] = "NON_EXISTENT_EXAM"
    bad_paper_info["paper_identifier"] = "NEET_BAD_ROLLBACK"

    with pytest.raises(ValueError, match="does not exist in examinations table"):
        ingestion_service.ingest_paper_batch(bad_paper_info, questions_data, dry_run=False)

    # Confirm that bad paper was not committed
    assert session.query(ExamPaper).filter(ExamPaper.paper_identifier == "NEET_BAD_ROLLBACK").count() == 0


def test_8_persistent_database_counts_remain_zero():
    """Case 8: Read-only verification that edunavika.db remains untouched with 0 competitive records."""
    db_path = r"D:\EduSens\edunavika.db"
    if not os.path.exists(db_path):
        pytest.skip(f"Persistent database not found at {db_path}")

    conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
    c = conn.cursor()

    c.execute("SELECT COUNT(*) FROM questions")
    assert c.fetchone()[0] == 0, "Persistent questions table must remain 0"

    c.execute("SELECT COUNT(*) FROM exam_papers")
    assert c.fetchone()[0] == 0, "Persistent exam_papers table must remain 0"

    c.execute("SELECT COUNT(*) FROM question_options")
    assert c.fetchone()[0] == 0, "Persistent question_options table must remain 0"

    c.execute("SELECT COUNT(*) FROM question_verification_logs")
    assert c.fetchone()[0] == 0, "Persistent question_verification_logs table must remain 0"

    c.execute("SELECT COUNT(*) FROM mcq_questions")
    legacy_count = c.fetchone()[0]
    assert legacy_count == 80, f"Legacy mcq_questions must remain exactly 80, found {legacy_count}"

    conn.close()
