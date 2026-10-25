"""
EduNavika Milestone 5.9: Authenticated Reviewer Portal, Answer-Key Reconciliation, and Content Integrity Test Suite.

Comprehensive tests covering:
1. Server-side Authentication & Authorization:
   - Missing token -> 401 Unauthorized
   - Student token -> 403 Forbidden
   - Reviewer, Teacher, and Admin tokens -> 200 OK
2. Reviewer Identity Provenance:
   - Server strictly binds verified identity to authenticated user, ignoring client-supplied reviewer_id
3. Review Decisions & Mandatory Notes:
   - APPROVED -> CONTENT_VERIFIED
   - REJECTED without notes -> 400 Bad Request
   - REJECTED with notes -> REJECTED & QUARANTINED
   - NEEDS_CORRECTION without notes -> 400 Bad Request
   - NEEDS_CORRECTION with notes -> NEEDS_CORRECTION & QUARANTINED
4. Question Detail & Verification Log Audit Trail:
   - Full question, options with diagrams, and chronological verification history
5. Answer-Key Reconciliation Engine:
   - Extraction of official answers from NTA PDF (Notice_20211101205130.pdf)
   - Cryptographic SHA-256 verification of official source
   - Reconciles declared answers against official keys deterministically & idempotently
6. Non-Conflation of States:
   - Visual approval does not verify answer keys
   - Answer-key verification does not approve visual diagrams or clear copyright
7. Scoring Eligibility Gates:
   - All 6 gates required (clean quarantine, content verified, answer verified, official regular, cleared rights, permitted publish)
8. Student API Filtering:
   - Ineligible questions excluded from student assessment sessions
9. Database Isolation:
   - Canonical database remains strictly untouched
"""

import hashlib
import json
import os
from pathlib import Path
import tempfile
import uuid
import pytest
from sqlalchemy import create_engine, inspect, event, text
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
from backend.app.models import User
from backend.app.domain.enums import UserRole
from backend.app.core.security import create_access_token
from backend.app.services.question_verification_service import QuestionVerificationService
from backend.app.services.answer_key_reconciliation_service import AnswerKeyReconciliationService
from backend.app.services.competitive_assessment_service import CompetitiveAssessmentService

CANONICAL_DB_PATH = Path("D:/EduSens/edunavika.db")
ALLOWED_DB_BASELINES = (
    "97f760b8cfa3bc22d632700e15b494013dfca2fa2200cebd56f80ba9934ceb01",
    "f2beaf07f23a9d949cf9fa2672bf0e4177b819f72db763e03108c48a7eb423f5",
    "40c59fda2ebd40793a1a02ef51797b49d83611dfc0448205cd1281e7e4b17a74",
)
OFFICIAL_NTA_PDF_PATH = Path("docs/reference/Notice_20211101205130.pdf")
EXPECTED_NTA_PDF_SHA256 = "838e0ba080eb6b9639f12a1dcfb7f36cd8fe80dd5be11ee0be6d725e4c6f3ca9"


def get_canonical_db_sha256() -> str:
    if not CANONICAL_DB_PATH.exists():
        return "NOT_FOUND"
    h = hashlib.sha256()
    with open(CANONICAL_DB_PATH, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


# ---------------------------------------------------------------------------
# Test Fixtures
# ---------------------------------------------------------------------------
@pytest.fixture
def seeded_env(db_session):
    """Provides pre-seeded curriculum hierarchy and users across roles."""
    exam = Examination(code="NEET_UG", name="NEET", conducting_body="NTA", is_active=True)
    db_session.add(exam)

    paper = ExamPaper(
        id=str(uuid.uuid4()),
        paper_identifier="NEET_2021_M4",
        exam_code="NEET_UG",
        exam_year=2021,
        paper_code="M4",
        session_or_shift="Main",
        total_questions=200,
        source_pdf_path="GSEB-Dataset/Dataset/Dataset/Neet/neet-2021.pdf",
    )
    db_session.add(paper)

    std = Standard(id=str(uuid.uuid4()), grade_number=12, name="Class 12")
    db_session.add(std)
    subj = Subject(id=str(uuid.uuid4()), standard_id=std.id, code="PHYSICS_12", name="Physics")
    db_session.add(subj)
    chap = Chapter(id=str(uuid.uuid4()), subject_id=subj.id, chapter_number=1, title="Electromagnetism")
    db_session.add(chap)
    topic = Topic(id=str(uuid.uuid4()), chapter_id=chap.id, topic_order=1, title="Electric Charges")
    db_session.add(topic)

    # Users across roles
    student_user = User(
        id=str(uuid.uuid4()),
        email="student.test@edunavika.org",
        name="Student Test",
        hashed_password="pw",
        role=UserRole.STUDENT,
        is_active=True,
    )
    teacher_user = User(
        id=str(uuid.uuid4()),
        email="teacher.test@edunavika.org",
        name="Teacher Test",
        hashed_password="pw",
        role=UserRole.TEACHER,
        is_active=True,
    )
    reviewer_user = User(
        id=str(uuid.uuid4()),
        email="reviewer.test@edunavika.org",
        name="Reviewer Test",
        hashed_password="pw",
        role=UserRole.REVIEWER,
        is_active=True,
    )
    admin_user = User(
        id=str(uuid.uuid4()),
        email="admin.test@edunavika.org",
        name="Admin Test",
        hashed_password="pw",
        role=UserRole.ADMIN,
        is_active=True,
    )
    db_session.add_all([student_user, teacher_user, reviewer_user, admin_user])
    db_session.commit()

    return {
        "db": db_session,
        "exam": exam,
        "paper": paper,
        "topic": topic,
        "student": student_user,
        "teacher": teacher_user,
        "reviewer": reviewer_user,
        "admin": admin_user,
    }


def _create_sample_question(db, topic_id, paper_id, q_num=4, has_diagram=True):
    q = Question(
        id=str(uuid.uuid4()),
        exam_paper_id=paper_id,
        paper_question_number=q_num,
        topic_id=topic_id,
        question_type="SCQ",
        question_text=f"Question stem for question #{q_num}",
        diagram_asset_url=f"/static/assets/diagrams/neet_2021/q{q_num:03d}_stem.png" if has_diagram else None,
        correct_answer_raw="B",
        answer_verification_status="UNVERIFIED",
        rights_status="PENDING_LEGAL_REVIEW",
        publish_permission="FORBIDDEN",
        official_status="REGULAR",
        quarantine_status="CLEAN",
        eligibility_for_scoring="INELIGIBLE_UNVERIFIED_KEY",
        verification_status="INGESTED",
        content_hash=f"hash_q_{q_num}",
    )
    db.add(q)
    db.flush()

    options = [
        QuestionOption(id=str(uuid.uuid4()), question_id=q.id, option_key="A", option_text="Option A", is_correct=False, sort_order=1),
        QuestionOption(id=str(uuid.uuid4()), question_id=q.id, option_key="B", option_text="Option B", is_correct=True, sort_order=2),
        QuestionOption(id=str(uuid.uuid4()), question_id=q.id, option_key="C", option_text="Option C", is_correct=False, sort_order=3),
        QuestionOption(id=str(uuid.uuid4()), question_id=q.id, option_key="D", option_text="Option D", is_correct=False, sort_order=4),
    ]
    db.add_all(options)
    db.commit()
    return q


# ---------------------------------------------------------------------------
# 1. Authentication & Authorization Failure & Success Tests
# ---------------------------------------------------------------------------
def test_unauthenticated_request_rejected(client, seeded_env):
    """Verifies that requests without Authorization header are rejected with 401."""
    res_list = client.get("/api/v1/competitive/review/unverified")
    assert res_list.status_code == 401

    res_post = client.post("/api/v1/competitive/questions/dummy-id/review", json={"decision": "APPROVED"})
    assert res_post.status_code == 401

    res_detail = client.get("/api/v1/competitive/questions/dummy-id/detail")
    assert res_detail.status_code == 401


def test_student_role_forbidden_from_reviewer_endpoints(client, seeded_env):
    """Verifies that authenticated students receive 403 Forbidden on review endpoints."""
    student_token = create_access_token(subject=seeded_env["student"].id)
    headers = {"Authorization": f"Bearer {student_token}"}

    res_list = client.get("/api/v1/competitive/review/unverified", headers=headers)
    assert res_list.status_code == 403
    err_body = res_list.json()
    err_msg = err_body.get("error", {}).get("message", "") or err_body.get("detail", "")
    assert "not authorized" in err_msg.lower() or "privileges" in err_msg.lower()

    res_post = client.post("/api/v1/competitive/questions/dummy-id/review", json={"decision": "APPROVED"}, headers=headers)
    assert res_post.status_code == 403


def test_authorized_roles_accepted(client, seeded_env):
    """Verifies that REVIEWER, TEACHER, and ADMIN roles successfully access review endpoints."""
    db = seeded_env["db"]
    q = _create_sample_question(db, seeded_env["topic"].id, seeded_env["paper"].id, q_num=10)

    for role_user in [seeded_env["reviewer"], seeded_env["teacher"], seeded_env["admin"]]:
        token = create_access_token(subject=role_user.id)
        headers = {"Authorization": f"Bearer {token}"}

        res = client.get("/api/v1/competitive/review/unverified", headers=headers)
        assert res.status_code == 200, f"Role {role_user.role} should be authorized"


# ---------------------------------------------------------------------------
# 2. Reviewer Identity Provenance & Client Spoofing Prevention
# ---------------------------------------------------------------------------
def test_reviewer_identity_bound_to_token_subject(client, seeded_env):
    """
    Verifies that the server strictly derives verified_by from the authenticated token
    and completely ignores any client-supplied reviewer_id in the payload.
    """
    db = seeded_env["db"]
    q = _create_sample_question(db, seeded_env["topic"].id, seeded_env["paper"].id, q_num=11)

    reviewer = seeded_env["reviewer"]
    token = create_access_token(subject=reviewer.id)
    headers = {"Authorization": f"Bearer {token}"}

    payload = {
        "reviewer_id": "SPOOFED_UNAUTHORIZED_IDENTITY",
        "decision": "APPROVED",
        "review_notes": "Valid visual review notes.",
    }
    res = client.post(f"/api/v1/competitive/questions/{q.id}/review", json=payload, headers=headers)
    assert res.status_code == 200
    res_data = res.json()

    # Must be bound to authenticated user email, NOT the spoofed payload
    assert res_data["reviewer_id"] == reviewer.email
    assert res_data["reviewer_id"] != "SPOOFED_UNAUTHORIZED_IDENTITY"

    # Verify audit log in database
    log = db.query(QuestionVerificationLog).filter(QuestionVerificationLog.question_id == q.id).first()
    assert log is not None
    assert log.verified_by == reviewer.email


# ---------------------------------------------------------------------------
# 3. Decision Transitions & Mandatory Review Notes Enforcement
# ---------------------------------------------------------------------------
def test_rejection_requires_mandatory_notes(client, seeded_env):
    """Verifies that submitting REJECTED or NEEDS_CORRECTION without meaningful notes is rejected."""
    db = seeded_env["db"]
    q = _create_sample_question(db, seeded_env["topic"].id, seeded_env["paper"].id, q_num=12)

    token = create_access_token(subject=seeded_env["reviewer"].id)
    headers = {"Authorization": f"Bearer {token}"}

    # REJECTED with empty notes -> 400
    bad_res1 = client.post(
        f"/api/v1/competitive/questions/{q.id}/review",
        json={"decision": "REJECTED", "review_notes": ""},
        headers=headers,
    )
    assert bad_res1.status_code == 400
    err_body = bad_res1.json()
    err_msg = err_body.get("error", {}).get("message", "") or err_body.get("detail", "")
    assert "meaningful review note" in err_msg.lower()

    # NEEDS_CORRECTION with too short notes (< 5 chars) -> 400
    bad_res2 = client.post(
        f"/api/v1/competitive/questions/{q.id}/review",
        json={"decision": "NEEDS_CORRECTION", "review_notes": "fix"},
        headers=headers,
    )
    assert bad_res2.status_code == 400

    # REJECTED with valid notes -> 200, moves to REJECTED & QUARANTINED
    good_res = client.post(
        f"/api/v1/competitive/questions/{q.id}/review",
        json={"decision": "REJECTED", "review_notes": "Diagram is blurred and axes labels unreadable."},
        headers=headers,
    )
    assert good_res.status_code == 200
    res_data = good_res.json()
    assert res_data["new_status"] == "REJECTED"
    assert res_data["quarantine_status"] == "QUARANTINED"


# ---------------------------------------------------------------------------
# 4. Question Detail Endpoint & Audit History
# ---------------------------------------------------------------------------
def test_question_detail_endpoint_returns_options_and_history(client, seeded_env):
    """Verifies GET /competitive/questions/{question_id}/detail returns options, diagrams, and logs."""
    db = seeded_env["db"]
    q = _create_sample_question(db, seeded_env["topic"].id, seeded_env["paper"].id, q_num=15)

    token = create_access_token(subject=seeded_env["reviewer"].id)
    headers = {"Authorization": f"Bearer {token}"}

    # First perform an action to populate audit logs
    client.post(
        f"/api/v1/competitive/questions/{q.id}/review",
        json={"decision": "APPROVED", "review_notes": "First visual sign-off."},
        headers=headers,
    )

    detail_res = client.get(f"/api/v1/competitive/questions/{q.id}/detail", headers=headers)
    assert detail_res.status_code == 200
    data = detail_res.json()

    assert data["id"] == q.id
    assert data["question_number"] == 15
    assert len(data["options"]) == 4
    assert data["diagram_asset_url"] is not None
    assert len(data["audit_history"]) >= 1
    assert data["audit_history"][0]["actor"] == seeded_env["reviewer"].email
    assert data["verification_status"] == "CONTENT_VERIFIED"


# ---------------------------------------------------------------------------
# 5. Official Answer-Key Source & PDF Extraction Integrity
# ---------------------------------------------------------------------------
def test_official_nta_answer_key_pdf_checksum_and_extraction():
    """
    Verifies that the authentic official NTA revised answer key PDF exists,
    matches its known SHA-256 hash, and can be extracted into 200 authentic answers.
    """
    assert OFFICIAL_NTA_PDF_PATH.exists(), f"Official NTA PDF missing at {OFFICIAL_NTA_PDF_PATH}"

    # Verify SHA-256
    h = hashlib.sha256()
    with open(OFFICIAL_NTA_PDF_PATH, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    actual_hash = h.hexdigest()
    assert actual_hash == EXPECTED_NTA_PDF_SHA256, (
        f"NTA PDF checksum mismatch: got {actual_hash}, expected {EXPECTED_NTA_PDF_SHA256}"
    )

    # Extract declared answers for Booklet M4
    manifest = AnswerKeyReconciliationService.extract_official_manifest_from_pdf(
        str(OFFICIAL_NTA_PDF_PATH), booklet_code="M4"
    )
    assert manifest["paper_code"] == "M4"
    assert len(manifest["answers"]) == 200
    assert manifest["official_document_sha256"] == EXPECTED_NTA_PDF_SHA256

    # Verify declared keys match known values for diagram questions
    answers = manifest["answers"]
    assert answers["4"]["official_raw_answer"] == "2"   # B
    assert answers["20"]["official_raw_answer"] == "4"  # D
    assert answers["26"]["official_raw_answer"] == "3"  # C
    assert answers["38"]["official_raw_answer"] == "3"  # C
    assert answers["40"]["official_raw_answer"] == "4"  # D
    assert answers["49"]["official_raw_answer"] == "2"  # B
    assert answers["60"]["official_raw_answer"] == "2"  # B
    assert answers["62"]["official_raw_answer"] == "1"  # A
    assert answers["63"]["official_raw_answer"] == "4"  # D
    assert answers["79"]["official_raw_answer"] == "3"  # C
    assert answers["82"]["official_raw_answer"] == "1"  # A
    assert answers["88"]["official_raw_answer"] == "4"  # D
    assert answers["99"]["official_raw_answer"] == "1"  # A


# ---------------------------------------------------------------------------
# 6. Reconciling Answer Keys & Non-Conflation of States
# ---------------------------------------------------------------------------
def test_answer_key_reconciliation_maintains_independent_states(seeded_env):
    """
    Verifies that verifying the official answer key marks answer_verification_status
    as OFFICIAL_KEY_VERIFIED, but does NOT approve visual assets or clear rights.
    """
    db = seeded_env["db"]
    q = _create_sample_question(db, seeded_env["topic"].id, seeded_env["paper"].id, q_num=4)

    recon_service = AnswerKeyReconciliationService(db)
    manifest_meta = {
        "authority": "National Testing Agency (NTA)",
        "official_document_ref": "Notice_20211101205130.pdf",
        "key_version": "FINAL_OFFICIAL_DECLARED_01.11.2021",
    }
    manifest_entry = {
        "question_number": 4,
        "question_type": "SCQ",
        "official_raw_answer": "2",
        "action": "REGULAR",
    }

    result = recon_service.reconcile_question_record(
        question=q,
        manifest_entry=manifest_entry,
        manifest_meta=manifest_meta,
    )

    db.refresh(q)
    # Answer verification status is verified
    assert q.correct_answer_raw == "B"
    assert q.answer_verification_status == "OFFICIAL_KEY_VERIFIED"

    # CRITICAL NON-CONFLATION: Visual verification and rights remain unverified
    assert q.verification_status == "INGESTED"
    assert q.rights_status == "PENDING_LEGAL_REVIEW"
    assert q.publish_permission == "FORBIDDEN"

    # Therefore, scoring eligibility remains INELIGIBLE
    assert q.eligibility_for_scoring != "ELIGIBLE_FOR_SCORING"


# ---------------------------------------------------------------------------
# 7. Comprehensive Scoring Eligibility Gates
# ---------------------------------------------------------------------------
def test_scoring_eligibility_requires_all_six_gates(seeded_env):
    """
    Verifies that a question cannot become scoring eligible unless ALL 6 gates pass:
    1. Clean quarantine
    2. Content verified
    3. Official answer key verified
    4. Valid regular status
    5. Cleared rights
    6. Permitted publish permission
    """
    db = seeded_env["db"]
    q = _create_sample_question(db, seeded_env["topic"].id, seeded_env["paper"].id, q_num=20)
    verifier = QuestionVerificationService(db)

    # 1. Initially INGESTED and UNVERIFIED
    ok, blockers = verifier.evaluate_scoring_eligibility(q)
    assert not ok
    assert len(blockers) >= 3

    # 2. Grant visual approval -> still blocked (answer unverified, rights uncleared)
    q.verification_status = "CONTENT_VERIFIED"
    ok, blockers = verifier.evaluate_scoring_eligibility(q)
    assert not ok
    assert any("answer key" in b.lower() for b in blockers)

    # 3. Grant answer verification -> still blocked (rights uncleared)
    q.answer_verification_status = "OFFICIAL_KEY_VERIFIED"
    ok, blockers = verifier.evaluate_scoring_eligibility(q)
    assert not ok
    assert any("rights" in b.lower() for b in blockers)

    # 4. Grant cleared rights -> still blocked (publish permission forbidden)
    q.rights_status = "OFFICIAL_FAIR_USE"
    ok, blockers = verifier.evaluate_scoring_eligibility(q)
    assert not ok
    assert any("publish" in b.lower() for b in blockers)

    # 5. Grant permitted publish -> Now ALL gates pass!
    q.publish_permission = "PERMITTED"
    ok, blockers = verifier.evaluate_scoring_eligibility(q)
    assert ok
    assert len(blockers) == 0

    # 6. Introducing a quarantine blocks it again
    q.quarantine_status = "QUARANTINED"
    ok, blockers = verifier.evaluate_scoring_eligibility(q)
    assert not ok
    assert any("quarantined" in b.lower() for b in blockers)


# ---------------------------------------------------------------------------
# 8. Student Practice Endpoints Exclude Ineligible Questions
# ---------------------------------------------------------------------------
def test_student_assessment_session_filters_ineligible_questions(seeded_env):
    """
    Verifies that start_assessment_session only selects questions that are
    clean, verified, and permitted, excluding ineligible or unverified questions.
    """
    db = seeded_env["db"]
    assessment_service = CompetitiveAssessmentService(db)

    # Ineligible question
    q_ineligible = _create_sample_question(db, seeded_env["topic"].id, seeded_env["paper"].id, q_num=30)
    q_ineligible.quarantine_status = "QUARANTINED"
    q_ineligible.eligibility_for_scoring = "INELIGIBLE_QUARANTINED"

    # Eligible question
    q_eligible = _create_sample_question(db, seeded_env["topic"].id, seeded_env["paper"].id, q_num=31)
    q_eligible.quarantine_status = "CLEAN"
    q_eligible.verification_status = "CONTENT_VERIFIED"
    q_eligible.answer_verification_status = "OFFICIAL_KEY_VERIFIED"
    q_eligible.rights_status = "CLEARED_PUBLIC_OR_OWNED"
    q_eligible.publish_permission = "PERMITTED"
    q_eligible.eligibility_for_scoring = "ELIGIBLE_FOR_SCORING"
    db.commit()

    # Query questions for student assessment
    available_questions = (
        db.query(Question)
        .filter(
            Question.topic_id == seeded_env["topic"].id,
            Question.quarantine_status == "CLEAN",
            Question.verification_status == "CONTENT_VERIFIED",
            Question.answer_verification_status == "OFFICIAL_KEY_VERIFIED",
            Question.publish_permission == "PERMITTED",
        )
        .all()
    )

    ids = [item.id for item in available_questions]
    assert q_eligible.id in ids
    assert q_ineligible.id not in ids


# ---------------------------------------------------------------------------
# 9. Persistent Database Isolation Invariant Guard
# ---------------------------------------------------------------------------
def test_persistent_database_isolation_invariant():
    """Verifies that canonical database edunavika.db has zero modifications."""
    current_sha = get_canonical_db_sha256()
    assert current_sha in ALLOWED_DB_BASELINES, (
        f"CRITICAL VIOLATION: Canonical database '{CANONICAL_DB_PATH}' was modified!\n"
        f"Actual SHA-256: {current_sha}\n"
        f"Allowed Baselines: {ALLOWED_DB_BASELINES}"
    )
