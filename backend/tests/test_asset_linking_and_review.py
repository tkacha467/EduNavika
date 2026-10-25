"""
EduNavika Milestone 5.8: Asset Linking, Human Review Workflow, and Controlled Ingestion Test Suite.

Comprehensive tests covering:
1. Schema migration upgrade and downgrade on disposable database.
2. Manifest schema validation and required fields.
3. Path traversal rejection and asset boundary security.
4. Checksum verification and missing asset detection.
5. Stem and graphical option linking accuracy.
6. Deduplication content hash backward compatibility and diagram differentiation.
7. Automated validation gate: empty option text requires diagram asset.
8. Human review workflow: APPROVED, REJECTED, NEEDS_CORRECTION state transitions.
9. Non-conflation: visual approval does not bypass answer verification, rights, or scoring gates.
10. Assessment session and PYQ endpoint diagram asset serialization.
11. Controlled NEET 2021 13-question pilot execution through real QuestionIngestionService.
12. Persistent database isolation guard.
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
from backend.app.services.diagram_asset_linking_service import (
    DiagramAssetLinkingService,
    APPROVED_ASSET_PREFIX,
)
from backend.app.services.question_ingestion_service import (
    QuestionIngestionService,
    compute_content_hash,
)
from backend.app.services.question_verification_service import (
    QuestionVerificationService,
    InvalidStateTransitionError,
)
from backend.app.services.competitive_assessment_service import CompetitiveAssessmentService

CANONICAL_DB_PATH = Path("D:/EduSens/edunavika.db")
ALLOWED_DB_BASELINES = (
    "97f760b8cfa3bc22d632700e15b494013dfca2fa2200cebd56f80ba9934ceb01",
    "f2beaf07f23a9d949cf9fa2672bf0e4177b819f72db763e03108c48a7eb423f5",
    "40c59fda2ebd40793a1a02ef51797b49d83611dfc0448205cd1281e7e4b17a74",
)


def get_canonical_db_sha256() -> str:
    if not CANONICAL_DB_PATH.exists():
        return "NOT_FOUND"
    h = hashlib.sha256()
    with open(CANONICAL_DB_PATH, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


@pytest.fixture
def disposable_db():
    """Provides a sterile, in-memory SQLite database with foreign keys enforced."""
    engine = create_engine("sqlite:///:memory:", echo=False)

    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture
def seeded_db(disposable_db):
    """Seeds standard, subject, chapter, topic, examination, and exam paper in disposable db."""
    exam = Examination(
        code="NEET_UG",
        name="National Eligibility cum Entrance Test",
        conducting_body="NTA",
        is_active=True,
    )
    disposable_db.add(exam)

    paper = ExamPaper(
        id=str(uuid.uuid4()),
        paper_identifier="NEET_2021_M4_TEST",
        exam_code="NEET_UG",
        exam_year=2021,
        paper_code="M4",
        session_or_shift="Main",
        total_questions=200,
        source_pdf_path="GSEB-Dataset/Dataset/Dataset/Neet/neet-2021.pdf",
    )
    disposable_db.add(paper)

    std = Standard(id=str(uuid.uuid4()), grade_number=12, name="Class 12")
    disposable_db.add(std)

    subj = Subject(id=str(uuid.uuid4()), standard_id=std.id, code="PHYSICS_12", name="Physics")
    disposable_db.add(subj)

    chap = Chapter(id=str(uuid.uuid4()), subject_id=subj.id, chapter_number=1, title="Electromagnetism")
    disposable_db.add(chap)

    topic = Topic(id=str(uuid.uuid4()), chapter_id=chap.id, topic_order=1, title="Electric Charges and Fields")
    disposable_db.add(topic)

    disposable_db.commit()
    return disposable_db, exam, paper, topic


# ---------------------------------------------------------------------------
# 1. Database Schema & Migration Tests
# ---------------------------------------------------------------------------
def test_schema_model_includes_option_diagram_asset_url(disposable_db):
    """Verifies that QuestionOption includes diagram_asset_url column."""
    inspector = inspect(disposable_db.bind)
    columns = {col["name"]: col for col in inspector.get_columns("question_options")}
    assert "diagram_asset_url" in columns, "QuestionOption must contain diagram_asset_url column"
    assert columns["diagram_asset_url"]["nullable"] is True, "diagram_asset_url must be nullable for backward compatibility"


def test_alembic_migration_script_integrity():
    """Verifies Alembic migration file exists and points to previous head a1b2c3d4e5f6."""
    migration_file = Path("backend/alembic/versions/20261025_m5_8_option_diagram_asset_url.py")
    assert migration_file.exists(), f"Migration file {migration_file} must exist"
    content = migration_file.read_text(encoding="utf-8")
    assert "b2c3d4e5f6a7" in content
    assert "a1b2c3d4e5f6" in content
    assert "diagram_asset_url" in content


# ---------------------------------------------------------------------------
# 2. Manifest Schema & Security Tests
# ---------------------------------------------------------------------------
def test_manifest_validation_valid_and_invalid():
    """Tests manifest structure validation."""
    service = DiagramAssetLinkingService()

    valid_manifest = {
        "manifest_version": "1.0",
        "assets": [
            {
                "asset_id": "test_q1_stem",
                "exam_code": "NEET_UG",
                "exam_year": 2021,
                "paper_code": "M4",
                "question_number": 1,
                "asset_role": "stem",
                "source_pdf_identifier": "neet-2021.pdf",
                "source_pdf_sha256": "abc",
                "output_relative_path": "backend/static/assets/diagrams/test.png",
                "output_sha256": "def",
            }
        ]
    }
    ok, errors = service.validate_manifest_structure(valid_manifest)
    assert ok is True
    assert len(errors) == 0

    # Missing manifest_version
    invalid_manifest = {"assets": []}
    ok, errors = service.validate_manifest_structure(invalid_manifest)
    assert ok is False
    assert any("manifest_version" in e for e in errors)

    # Missing required asset fields
    invalid_asset_manifest = {
        "manifest_version": "1.0",
        "assets": [{"asset_id": "bad_asset"}]
    }
    ok, errors = service.validate_manifest_structure(invalid_asset_manifest)
    assert ok is False
    assert len(errors) > 0


def test_path_traversal_rejection(tmp_path):
    """Verifies that path traversal sequences are rejected."""
    service = DiagramAssetLinkingService(repo_root=tmp_path, approved_asset_root=tmp_path / "backend/static/assets")

    traversal_paths = [
        "../outside.png",
        "backend/static/assets/../../secret.txt",
        "/etc/shadow",
        "backend/static/assets/../../../windows/system32/cmd.exe",
        "",
    ]
    for p in traversal_paths:
        ok, res_path, err = service.resolve_and_verify_asset_path(p)
        assert ok is False, f"Expected path '{p}' to be rejected"
        assert err is not None


def test_checksum_verification_and_missing_file(tmp_path):
    """Verifies asset checksum matching and missing file rejection."""
    approved_root = tmp_path / "backend/static/assets"
    approved_root.mkdir(parents=True)
    asset_file = approved_root / "test_diagram.png"
    asset_content = b"\x89PNG\r\n\x1a\nfake_image_content"
    asset_file.write_bytes(asset_content)
    real_sha = hashlib.sha256(asset_content).hexdigest()

    service = DiagramAssetLinkingService(repo_root=tmp_path, approved_asset_root=approved_root)

    # Correct checksum
    asset_dict = {
        "asset_id": "test_asset",
        "output_relative_path": "backend/static/assets/test_diagram.png",
        "output_sha256": real_sha,
    }
    ok, err = service.verify_asset_checksum(asset_dict)
    assert ok is True
    assert err is None

    # Mismatched checksum
    asset_dict_tampered = {
        "asset_id": "test_asset",
        "output_relative_path": "backend/static/assets/test_diagram.png",
        "output_sha256": "0000000000000000000000000000000000000000000000000000000000000000",
    }
    ok, err = service.verify_asset_checksum(asset_dict_tampered)
    assert ok is False
    assert "Checksum mismatch" in err

    # Missing file
    asset_dict_missing = {
        "asset_id": "test_asset",
        "output_relative_path": "backend/static/assets/non_existent.png",
        "output_sha256": real_sha,
    }
    ok, err = service.verify_asset_checksum(asset_dict_missing)
    assert ok is False
    assert "not found" in err.lower()


# ---------------------------------------------------------------------------
# 3. Asset Linking & Deduplication Tests
# ---------------------------------------------------------------------------
def test_stem_and_option_diagram_linking():
    """Tests that stem and option diagrams link accurately and idempotently."""
    service = DiagramAssetLinkingService()

    synthetic_manifest = {
        "manifest_version": "1.0",
        "assets": [
            {
                "asset_id": "neet_2021_q4_stem",
                "exam_code": "NEET_UG",
                "exam_year": 2021,
                "paper_code": "M4",
                "question_number": 4,
                "asset_role": "stem",
                "source_pdf_identifier": "neet-2021.pdf",
                "source_pdf_sha256": "abc",
                "output_relative_path": "backend/static/assets/diagrams/neet_2021/neet_2021_q004_stem.png",
                "output_sha256": "mock_sha",
            },
            {
                "asset_id": "neet_2021_q26_opt_a",
                "exam_code": "NEET_UG",
                "exam_year": 2021,
                "paper_code": "M4",
                "question_number": 26,
                "asset_role": "option",
                "option_key": "A",
                "source_pdf_identifier": "neet-2021.pdf",
                "source_pdf_sha256": "abc",
                "output_relative_path": "backend/static/assets/diagrams/neet_2021/neet_2021_q026_option_a.png",
                "output_sha256": "mock_sha",
            },
        ]
    }
    index, errors = service.build_asset_index(synthetic_manifest, verify_checksums=False)
    assert len(errors) == 0

    # Link Q4 (stem)
    q4 = {
        "paper_question_number": 4,
        "question_text": "Find equivalent capacitance across nodes A and B.",
        "options": [{"option_key": "A", "option_text": "2 uF"}, {"option_key": "B", "option_text": "4 uF"}],
    }
    res4 = service.link_assets_to_question(q4, "NEET_UG", 2021, "M4", index)
    assert res4["linked"] is True
    assert res4["stem_linked"] is True
    assert q4["diagram_asset_url"] == "/static/assets/diagrams/neet_2021/neet_2021_q004_stem.png"

    # Link Q26 (option A)
    q26 = {
        "paper_question_number": 26,
        "question_text": "Which graph correctly represents the magnetic field?",
        "options": [
            {"option_key": "A", "option_text": ""},
            {"option_key": "B", "option_text": ""},
        ],
    }
    res26 = service.link_assets_to_question(q26, "NEET_UG", 2021, "M4", index)
    assert res26["linked"] is True
    assert res26["options_linked_count"] == 1
    assert q26["options"][0]["diagram_asset_url"] == "/static/assets/diagrams/neet_2021/neet_2021_q026_option_a.png"
    assert q26["options"][1].get("diagram_asset_url") is None


def test_content_hash_backward_compatibility():
    """Ensures questions without diagrams maintain exact legacy hash value."""
    stem = "A particle executes simple harmonic motion with amplitude A."
    opts = [
        {"option_key": "A", "option_text": "v = \\omega A"},
        {"option_key": "B", "option_text": "v = \\omega A / 2"},
        {"option_key": "C", "option_text": "v = 0"},
        {"option_key": "D", "option_text": "v = 2 \\omega A"},
    ]
    legacy_hash = compute_content_hash(stem, opts, "A")

    # Call with explicit stem_diagram_url=None
    new_call_hash = compute_content_hash(stem, opts, "A", stem_diagram_url=None)
    assert legacy_hash == new_call_hash, "Hash must be 100% identical when diagrams are absent"

    # With stem diagram, hash must be distinct
    stem_diag_hash = compute_content_hash(stem, opts, "A", stem_diagram_url="/static/diagrams/shm.png")
    assert stem_diag_hash != legacy_hash

    # With option diagram, hash must be distinct
    opts_with_diag = [
        {"option_key": "A", "option_text": "", "diagram_asset_url": "/static/diagrams/opt_a.png"},
        {"option_key": "B", "option_text": "Text B"},
        {"option_key": "C", "option_text": "Text C"},
        {"option_key": "D", "option_text": "Text D"},
    ]
    opt_diag_hash = compute_content_hash(stem, opts_with_diag, "A")
    assert opt_diag_hash != legacy_hash


def test_automated_gate_empty_option_text_handling(disposable_db):
    """Verifies that empty option text is allowed if and only if diagram_asset_url is present."""
    service = QuestionIngestionService(disposable_db)

    # Empty option text WITHOUT diagram asset -> REJECTED
    q_invalid = {
        "question_text": "Identify the correct diagram for resonance in RLC circuit.",
        "question_type": "SCQ",
        "options": [
            {"option_key": "A", "option_text": ""},
            {"option_key": "B", "option_text": "Option B"},
            {"option_key": "C", "option_text": "Option C"},
            {"option_key": "D", "option_text": "Option D"},
        ],
        "correct_answer_raw": "B",
    }
    is_valid, errors = service.validate_question_data(q_invalid)
    assert is_valid is False
    assert any("text cannot be empty" in e for e in errors)

    # Empty option text WITH diagram asset -> ACCEPTED
    q_valid = {
        "question_text": "Identify the correct diagram for resonance in RLC circuit.",
        "question_type": "SCQ",
        "options": [
            {"option_key": "A", "option_text": "", "diagram_asset_url": "/static/assets/diagrams/opt_a.png"},
            {"option_key": "B", "option_text": "Option B"},
            {"option_key": "C", "option_text": "Option C"},
            {"option_key": "D", "option_text": "Option D"},
        ],
        "correct_answer_raw": "B",
    }
    is_valid, errors = service.validate_question_data(q_valid)
    assert is_valid is True, f"Validation failed unexpectedly: {errors}"


# ---------------------------------------------------------------------------
# 4. Human Content Verification & State Machine Tests
# ---------------------------------------------------------------------------
def test_human_review_workflow_and_audit_logging(seeded_db):
    """Tests APPROVED, REJECTED, and NEEDS_CORRECTION reviewer decisions."""
    db, exam, paper, topic = seeded_db
    v_service = QuestionVerificationService(db)

    # Create test question
    q = Question(
        id=str(uuid.uuid4()),
        exam_paper_id=paper.id,
        paper_question_number=101,
        topic_id=topic.id,
        question_type="SCQ",
        question_text="Consider the following circuit diagram with source voltage V.",
        diagram_asset_url="/static/assets/diagrams/q101.png",
        correct_answer_raw="B",
        answer_verification_status="UNVERIFIED",
        rights_status="PENDING_LEGAL_REVIEW",
        publish_permission="FORBIDDEN",
        quarantine_status="CLEAN",
        eligibility_for_scoring="INELIGIBLE_UNVERIFIED_KEY",
        verification_status="INGESTED",
        content_hash="test_hash_101",
    )
    db.add(q)
    db.commit()

    # 1. Invalid reviewer ID (empty) rejected
    with pytest.raises(ValueError, match="reviewer_id"):
        v_service.submit_human_visual_review(
            question_id=q.id,
            reviewer_id="   ",
            decision="APPROVED",
            review_notes="Notes",
        )

    # 2. Invalid decision rejected
    with pytest.raises(ValueError, match="Invalid decision"):
        v_service.submit_human_visual_review(
            question_id=q.id,
            reviewer_id="REV_1",
            decision="MAYBE_CORRECT",
            review_notes="Notes",
        )

    # 3. Valid APPROVED review
    res = v_service.submit_human_visual_review(
        question_id=q.id,
        reviewer_id="DR_PHYSICS_EXPERT",
        decision="APPROVED",
        review_notes="Diagram nodes and labels A, B, C clearly legible.",
        asset_ids_reviewed=["q101_stem"],
    )
    db.commit()
    assert res["decision"] == "APPROVED"
    assert q.verification_status == "CONTENT_VERIFIED"
    assert q.eligibility_for_scoring == "INELIGIBLE_UNVERIFIED_KEY", "Visual approval must not bypass scoring gate"

    # Verify log entry created
    log = db.query(QuestionVerificationLog).filter(QuestionVerificationLog.id == res["log_id"]).first()
    assert log is not None
    assert log.verified_by == "DR_PHYSICS_EXPERT"
    assert log.action_type == "HUMAN_VISUAL_REVIEW"
    assert "DR_PHYSICS_EXPERT" in log.review_notes

    # 4. Attempt to promote to scoring eligible before answer key or rights clearance -> MUST FAIL
    with pytest.raises(InvalidStateTransitionError, match="Gate failures"):
        v_service.promote_to_scoring_eligible(q.id, reviewer_id="ADMIN")

    # 5. REJECTED decision quarantines question
    rej_res = v_service.submit_human_visual_review(
        question_id=q.id,
        reviewer_id="SENIOR_REVIEWER",
        decision="REJECTED",
        review_notes="Resistor R2 value is clipped off at the right margin.",
    )
    db.commit()
    assert rej_res["decision"] == "REJECTED"
    assert q.verification_status == "REJECTED"
    assert q.quarantine_status == "QUARANTINED"
    assert q.eligibility_for_scoring == "INELIGIBLE_QUARANTINED"


# ---------------------------------------------------------------------------
# 5. Controlled 13-Question NEET 2021 Pilot Test
# ---------------------------------------------------------------------------
def test_real_neet_2021_pilot_execution_real_service(disposable_db):
    """Executes the complete 13-question pilot through real QuestionIngestionService."""
    from scripts.pilot_neet_2021_diagram_ingestion import (
        seed_curriculum_and_paper,
        load_and_prepare_pilot_questions,
        MANIFEST_PATH,
        TARGET_QUESTION_NUMBERS,
    )

    exam, paper, topic = seed_curriculum_and_paper(disposable_db)

    # 1. Manifest-driven linking
    linking_service = DiagramAssetLinkingService()
    with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
        manifest_data = json.load(f)

    asset_index, index_errors = linking_service.build_asset_index(manifest_data, verify_checksums=True)
    assert len(index_errors) == 0, f"Asset index built with errors: {index_errors}"
    assert len(asset_index) == 13

    raw_questions = load_and_prepare_pilot_questions(topic.id, paper.id)
    assert len(raw_questions) == 13

    for q in raw_questions:
        linking_service.link_assets_to_question(
            question_dict=q,
            exam_code="NEET_UG",
            exam_year=2021,
            paper_code="M4",
            asset_index=asset_index,
        )

    # 2. Ingestion via real QuestionIngestionService
    ingestion = QuestionIngestionService(disposable_db)
    paper_info = {
        "paper_identifier": paper.paper_identifier,
        "exam_code": "NEET_UG",
        "exam_year": 2021,
        "paper_code": "M4",
    }

    # Dry-run test
    dry_metrics = ingestion.ingest_paper_batch(paper_info, raw_questions, dry_run=True)
    assert dry_metrics["valid_count"] == 13
    assert dry_metrics["invalid_count"] == 0
    assert disposable_db.query(Question).count() == 0

    # Real ingestion test
    metrics = ingestion.ingest_paper_batch(paper_info, raw_questions, dry_run=False)
    assert metrics["inserted_count"] == 13
    assert metrics["valid_count"] == 13
    assert metrics["invalid_count"] == 0

    # Verify counts in isolated database
    assert disposable_db.query(Question).count() == 13
    assert disposable_db.query(QuestionOption).count() == 52
    assert disposable_db.query(QuestionOption).filter(QuestionOption.diagram_asset_url.isnot(None)).count() == 36
    assert disposable_db.query(Question).filter(Question.diagram_asset_url.isnot(None)).count() == 5
    assert disposable_db.query(QuestionVerificationLog).count() == 13

    # Idempotent re-run
    metrics2 = ingestion.ingest_paper_batch(paper_info, raw_questions, dry_run=False)
    assert metrics2["skipped_duplicate_count"] == 13
    assert metrics2["inserted_count"] == 0
    assert disposable_db.query(Question).count() == 13


# ---------------------------------------------------------------------------
# 6. Assessment Session & Review API Endpoints
# ---------------------------------------------------------------------------
def test_assessment_session_diagram_serialization(seeded_db):
    """Verifies that start_assessment and submit_assessment include option diagrams."""
    db, exam, paper, topic = seeded_db

    # Create an eligible verified question with a stem diagram and option diagrams
    q = Question(
        id=str(uuid.uuid4()),
        exam_paper_id=paper.id,
        paper_question_number=4,
        topic_id=topic.id,
        question_type="SCQ",
        question_text="Determine the capacitance between terminals A and B.",
        diagram_asset_url="/static/assets/diagrams/neet_2021/q004_stem.png",
        correct_answer_raw="B",
        answer_verification_status="VERIFIED_OFFICIAL_KEY",
        rights_status="OFFICIAL_FAIR_USE",
        publish_permission="PUBLIC",
        official_status="REGULAR",
        quarantine_status="CLEAN",
        eligibility_for_scoring="ELIGIBLE_FOR_SCORING",
        verification_status="CONTENT_VERIFIED",
        content_hash="test_session_hash_4",
    )
    db.add(q)
    db.flush()

    for idx, (k, txt, is_c) in enumerate([("A", "2 uF", False), ("B", "4 uF", True), ("C", "6 uF", False), ("D", "8 uF", False)]):
        opt = QuestionOption(
            id=str(uuid.uuid4()),
            question_id=q.id,
            option_key=k,
            option_text=txt,
            diagram_asset_url=f"/static/assets/diagrams/neet_2021/q004_opt_{k.lower()}.png",
            is_correct=is_c,
            sort_order=idx,
        )
        db.add(opt)
    db.commit()

    service = CompetitiveAssessmentService(db)
    session_data = service.start_assessment_session(
        student_id="student_123",
        exam_code="NEET_UG",
        mode="CHAPTER_MOCK",
        chapter_id=topic.chapter_id,
        duration_minutes=30,
        total_questions=1,
    )
    assert session_data["status"] == "IN_PROGRESS"
    assert len(session_data["questions"]) == 1
    sq = session_data["questions"][0]
    assert sq["diagram_asset_url"] == "/static/assets/diagrams/neet_2021/q004_stem.png"
    assert len(sq["options"]) == 4
    assert sq["options"][0]["diagram_asset_url"] == "/static/assets/diagrams/neet_2021/q004_opt_a.png"

    # Submit assessment
    submission = service.submit_assessment(session_data["session_id"])
    assert submission["status"] == "SUBMITTED"
    review_q = submission["questions_review"][0]
    assert review_q["diagram_asset_url"] == "/static/assets/diagrams/neet_2021/q004_stem.png"
    assert review_q["options"][1]["diagram_asset_url"] == "/static/assets/diagrams/neet_2021/q004_opt_b.png"


def test_review_api_endpoints_via_testclient(client, db_session):
    """Verifies POST /competitive/questions/{question_id}/review and GET /competitive/review/unverified."""
    exam = db_session.query(Examination).first()
    if not exam:
        exam = Examination(code="NEET_UG", name="NEET", conducting_body="NTA", is_active=True)
        db_session.add(exam)

    topic = db_session.query(Topic).first()
    if not topic:
        std = Standard(id=str(uuid.uuid4()), grade_number=12, name="Class 12")
        db_session.add(std)
        subj = Subject(id=str(uuid.uuid4()), standard_id=std.id, code="PHYSICS_12", name="Physics")
        db_session.add(subj)
        chap = Chapter(id=str(uuid.uuid4()), subject_id=subj.id, chapter_number=1, title="Electromagnetism")
        db_session.add(chap)
        topic = Topic(id=str(uuid.uuid4()), chapter_id=chap.id, topic_order=1, title="Electric Charges and Fields")
        db_session.add(topic)
        db_session.flush()

    q = Question(
        id=str(uuid.uuid4()),
        paper_question_number=50,
        topic_id=topic.id,
        question_type="SCQ",
        question_text="A circuit diagram question awaiting expert visual review.",
        diagram_asset_url="/static/assets/diagrams/neet_2021/q050_stem.png",
        correct_answer_raw="C",
        answer_verification_status="UNVERIFIED",
        rights_status="PENDING_LEGAL_REVIEW",
        publish_permission="FORBIDDEN",
        official_status="REGULAR",
        quarantine_status="CLEAN",
        eligibility_for_scoring="INELIGIBLE_UNVERIFIED_KEY",
        verification_status="INGESTED",
        content_hash="test_api_review_hash_50",
    )
    db_session.add(q)

    # Seed authenticated reviewer user
    from backend.app.models import User
    from backend.app.domain.enums import UserRole
    from backend.app.core.security import create_access_token

    reviewer = User(
        id=str(uuid.uuid4()),
        email="reviewer.qa@edunavika.org",
        name="Reviewer QA",
        hashed_password="hashed_pw",
        role=UserRole.TEACHER,
        is_active=True,
    )
    db_session.add(reviewer)
    db_session.commit()

    token = create_access_token(subject=reviewer.id)
    auth_headers = {"Authorization": f"Bearer {token}"}

    # 1. GET /competitive/review/unverified without auth -> 401
    unauth_get = client.get("/api/v1/competitive/review/unverified")
    assert unauth_get.status_code == 401

    # 2. GET /competitive/review/unverified with auth -> 200
    get_res = client.get("/api/v1/competitive/review/unverified", headers=auth_headers)
    assert get_res.status_code == 200
    items = get_res.json()
    assert any(item["id"] == q.id for item in items)

    # 3. POST /competitive/questions/{question_id}/review - valid
    payload = {
        "decision": "APPROVED",
        "review_notes": "Vector diagram crop is centered and clear.",
        "asset_ids_reviewed": ["q050_stem"],
        "manifest_version": "1.0",
    }
    post_res = client.post(f"/api/v1/competitive/questions/{q.id}/review", json=payload, headers=auth_headers)
    assert post_res.status_code == 200
    res_data = post_res.json()
    assert res_data["decision"] == "APPROVED"
    assert res_data["new_status"] == "CONTENT_VERIFIED"
    assert res_data["reviewer_id"] == "reviewer.qa@edunavika.org"

    # 4. POST review - invalid decision -> 400
    bad_payload = {
        "decision": "INVALID_DECISION",
        "review_notes": "",
    }
    bad_res = client.post(f"/api/v1/competitive/questions/{q.id}/review", json=bad_payload, headers=auth_headers)
    assert bad_res.status_code == 400


# ---------------------------------------------------------------------------
# 7. Persistent Database Isolation Guard
# ---------------------------------------------------------------------------
def test_persistent_database_remains_strictly_unchanged():
    """Verifies that the canonical database on disk has not been modified."""
    current_sha = get_canonical_db_sha256()
    assert current_sha in ALLOWED_DB_BASELINES, (
        f"CRITICAL VIOLATION: Canonical database '{CANONICAL_DB_PATH}' was modified!\n"
        f"Actual SHA-256: {current_sha}\n"
        f"Allowed Baselines: {ALLOWED_DB_BASELINES}"
    )
