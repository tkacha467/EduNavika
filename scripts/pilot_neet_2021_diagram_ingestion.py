"""
EduNavika Milestone 5.8: Controlled Ingestion Pilot for NEET 2021 Diagram Questions.

Executes a reproducible, auditable pilot on the 13 quarantined diagram questions
(4 stem diagram, 9 graphical options, 41 total assets) using:
- Disposable isolated SQLite database (zero canonical DB writes)
- Real QuestionIngestionService & 10-point validation gate
- DiagramAssetLinkingService (manifest validation + SHA-256 verification)
- QuestionVerificationService (human review audit log & state transitions)
"""

import hashlib
import json
import logging
import os
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

# Ensure repo root is on sys.path
REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from sqlalchemy import create_engine, event, text
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
from backend.app.services.diagram_asset_linking_service import DiagramAssetLinkingService
from backend.app.services.question_ingestion_service import QuestionIngestionService
from backend.app.services.question_verification_service import QuestionVerificationService

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

CANONICAL_DB_PATH = Path("D:/EduSens/edunavika.db")
MANIFEST_PATH = REPO_ROOT / "data/processed/neet_2021_diagram_manifest.json"
AUDIT_DATA_PATH = REPO_ROOT / "data/processed/neet_2021_quality_audit.json"

TARGET_QUESTION_NUMBERS = [4, 20, 26, 38, 40, 49, 60, 62, 63, 79, 82, 88, 99]


def get_file_sha256(filepath: Path) -> str:
    """Returns hexadecimal SHA-256 hash of a file."""
    if not filepath.exists():
        return "FILE_NOT_FOUND"
    hasher = hashlib.sha256()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def create_isolated_pilot_db():
    """Creates a temporary in-memory database with foreign keys enabled."""
    engine = create_engine("sqlite:///:memory:", echo=False)

    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return engine, SessionLocal()


def seed_curriculum_and_paper(db):
    """Seeds prerequisite examination, subject, chapter, and topic records."""
    exam = Examination(
        code="NEET_UG",
        name="National Eligibility cum Entrance Test (UG)",
        conducting_body="NTA",
        is_active=True,
    )
    db.add(exam)

    paper = ExamPaper(
        id=str(uuid.uuid4()),
        paper_identifier="NEET_2021_M4",
        exam_code="NEET_UG",
        exam_year=2021,
        paper_code="M4",
        session_or_shift="Main",
        total_questions=200,
        source_pdf_path="GSEB-Dataset/Dataset/Dataset/Neet/neet-2021.pdf",
        source_pdf_hash="e9acdfb29dfcff0a3a186819f7336330af4ce51855990d1081c78637b338587a",
    )
    db.add(paper)

    std = Standard(id=str(uuid.uuid4()), grade_number=12, name="Class 12")
    db.add(std)

    subj = Subject(id=str(uuid.uuid4()), standard_id=std.id, code="PHYSICS_12", name="Physics")
    db.add(subj)

    chap = Chapter(id=str(uuid.uuid4()), subject_id=subj.id, chapter_number=3, title="Electromagnetism & Circuits")
    db.add(chap)

    topic = Topic(id=str(uuid.uuid4()), chapter_id=chap.id, topic_order=1, title="Circuits and Devices")
    db.add(topic)

    db.commit()
    return exam, paper, topic


def load_and_prepare_pilot_questions(topic_id: str, paper_id: str) -> List[Dict[str, Any]]:
    """
    Loads authentic NEET 2021 audit data for the 13 diagram questions
    and formats them for ingestion.
    """
    with open(AUDIT_DATA_PATH, "r", encoding="utf-8") as f:
        all_questions = json.load(f)

    target_audit_map = {q["question_number"]: q for q in all_questions if q["question_number"] in TARGET_QUESTION_NUMBERS}

    formatted_questions = []
    for q_num in TARGET_QUESTION_NUMBERS:
        q_raw = target_audit_map.get(q_num)
        if not q_raw:
            continue

        options = [
            {"option_key": "A", "option_text": q_raw.get("option_A_raw", "").strip(), "sort_order": 0},
            {"option_key": "B", "option_text": q_raw.get("option_B_raw", "").strip(), "sort_order": 1},
            {"option_key": "C", "option_text": q_raw.get("option_C_raw", "").strip(), "sort_order": 2},
            {"option_key": "D", "option_text": q_raw.get("option_D_raw", "").strip(), "sort_order": 3},
        ]

        formatted_questions.append({
            "paper_question_number": q_num,
            "topic_id": topic_id,
            "question_type": "SCQ",
            "question_text": q_raw.get("raw_stem", "").strip(),
            "options": options,
            "correct_answer_raw": q_raw.get("normalized_answer"),
            "answer_verification_status": "UNVERIFIED",  # Enforce separate answer reconciliation gate
            "solution_text": f"Authentic NEET 2021 question from Booklet M4 Q{q_num}.",
            "ncert_citation": "NCERT Physics/Chemistry relevant section",
            "evaluation_policy": "SCQ_EXACT",
            "difficulty_tier": "MEDIUM",
            "cognitive_level": "APPLYING",
            "source_type": "OFFICIAL_PYQ",
            "rights_status": "PENDING_LEGAL_REVIEW",
            "publish_permission": "FORBIDDEN",
            "official_status": "REGULAR",
            "quarantine_status": "CLEAN",
            "eligibility_for_scoring": "INELIGIBLE_UNVERIFIED_KEY",
            "verification_status": "INGESTED",
        })

    return formatted_questions


def run_pilot():
    """Main execution of Milestone 5.8 Controlled Pilot."""
    print("=" * 70)
    print("EDUNAVIKA MILESTONE 5.8: CONTROLLED DIAGRAM INGESTION PILOT")
    print("=" * 70)

    # 1. Verify Canonical DB safety
    initial_db_sha = get_file_sha256(CANONICAL_DB_PATH)
    print(f"[GUARD] Canonical DB Path: {CANONICAL_DB_PATH}")
    print(f"[GUARD] Canonical DB SHA-256 before pilot: {initial_db_sha[:16]}...")

    # 2. Setup isolated database
    engine, db = create_isolated_pilot_db()
    exam, paper, topic = seed_curriculum_and_paper(db)
    print(f"[DATABASE] Initialized isolated in-memory SQLite database. Paper: {paper.paper_identifier}")

    # 3. Load extraction manifest & build asset index
    linking_service = DiagramAssetLinkingService(repo_root=REPO_ROOT)
    with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
        manifest_data = json.load(f)

    is_manifest_valid, manifest_errors = linking_service.validate_manifest_structure(manifest_data)
    if not is_manifest_valid:
        raise ValueError(f"Manifest schema validation failed: {manifest_errors}")

    asset_index, index_errors = linking_service.build_asset_index(manifest_data, verify_checksums=True)
    if index_errors:
        raise ValueError(f"Asset index verification failed: {index_errors}")

    print(f"[ASSET LINKING] Validated manifest ({manifest_data.get('manifest_version')}) with {len(manifest_data['assets'])} assets across {len(asset_index)} question keys.")

    # 4. Prepare questions and link assets
    raw_questions = load_and_prepare_pilot_questions(topic_id=topic.id, paper_id=paper.id)
    print(f"[PREPARATION] Loaded {len(raw_questions)} target NEET 2021 questions from authentic audit.")

    stem_linked_count = 0
    option_assets_linked_total = 0

    for q in raw_questions:
        res = linking_service.link_assets_to_question(
            question_dict=q,
            exam_code="NEET_UG",
            exam_year=2021,
            paper_code="M4",
            asset_index=asset_index,
        )
        if res["stem_linked"]:
            stem_linked_count += 1
        option_assets_linked_total += res["options_linked_count"]

    print(f"[LINKING SUMMARY] Linked {stem_linked_count} stem diagrams and {option_assets_linked_total} option diagrams.")
    assert stem_linked_count == 5, f"Expected 5 stem diagrams (Q4, Q20, Q38, Q40, Q49), got {stem_linked_count}"
    assert option_assets_linked_total == 36, f"Expected 36 option diagrams (9 questions * 4), got {option_assets_linked_total}"
    assert (stem_linked_count + option_assets_linked_total) == 41, "Expected 41 total diagram assets linked"

    # 5. Ingestion Gate: Dry-run check
    ingestion_service = QuestionIngestionService(db)
    paper_info = {
        "paper_identifier": "NEET_2021_M4",
        "exam_code": "NEET_UG",
        "exam_year": 2021,
        "paper_code": "M4",
    }
    dry_metrics = ingestion_service.ingest_paper_batch(paper_info, raw_questions, dry_run=True)
    print(f"[DRY RUN] valid={dry_metrics['valid_count']}, invalid={dry_metrics['invalid_count']}, dry_inserted={dry_metrics['inserted_count']}")
    assert dry_metrics["valid_count"] == 13, f"Expected 13 valid questions in dry run, got {dry_metrics['valid_count']}"
    assert db.query(Question).count() == 0, "Dry run must perform ZERO database inserts"

    # 6. Ingestion Gate: Real ingestion into isolated DB
    real_metrics = ingestion_service.ingest_paper_batch(paper_info, raw_questions, dry_run=False)
    print(f"[REAL INGESTION] inserted={real_metrics['inserted_count']}, valid={real_metrics['valid_count']}, errors={len(real_metrics['validation_errors'])}")
    assert real_metrics["inserted_count"] == 13, f"Expected 13 inserted questions, got {real_metrics['inserted_count']}"

    db_question_count = db.query(Question).count()
    db_option_count = db.query(QuestionOption).count()
    db_option_diag_count = db.query(QuestionOption).filter(QuestionOption.diagram_asset_url.isnot(None)).count()
    db_stem_diag_count = db.query(Question).filter(Question.diagram_asset_url.isnot(None)).count()
    db_vlog_count = db.query(QuestionVerificationLog).count()

    print(f"[DB VERIFICATION] Persisted: {db_question_count} questions, {db_option_count} options ({db_option_diag_count} with diagrams), {db_stem_diag_count} stem diagrams, {db_vlog_count} verification logs")
    assert db_question_count == 13
    assert db_option_count == 52
    assert db_stem_diag_count == 5
    assert db_option_diag_count == 36
    assert db_vlog_count == 13

    # 7. Ingestion Gate: Deduplication & Idempotency
    dup_metrics = ingestion_service.ingest_paper_batch(paper_info, raw_questions, dry_run=False)
    print(f"[IDEMPOTENCY] Second execution: skipped_duplicates={dup_metrics['skipped_duplicate_count']}, inserted={dup_metrics['inserted_count']}")
    assert dup_metrics["skipped_duplicate_count"] == 13
    assert dup_metrics["inserted_count"] == 0
    assert db.query(Question).count() == 13

    # 8. Human Review Workflow Testing
    verification_service = QuestionVerificationService(db)
    q4 = db.query(Question).filter(Question.paper_question_number == 4).first()
    assert q4 is not None

    # Test APPROVED visual review
    review_res = verification_service.submit_human_visual_review(
        question_id=q4.id,
        reviewer_id="REV_EXPERT_NEET_PHYSICS_01",
        decision="APPROVED",
        review_notes="Approved capacitor bridge crop; all plates and nodes legible.",
        asset_ids_reviewed=[q4.diagram_asset_url],
        source_manifest_version="1.0",
    )
    db.commit()
    print(f"[HUMAN REVIEW] Q4 visual review submitted: {review_res['decision']}, new_status={review_res['new_status']}")
    assert q4.verification_status == "CONTENT_VERIFIED"
    assert q4.eligibility_for_scoring == "INELIGIBLE_UNVERIFIED_KEY", "Visual approval must not promote unverified keys to scoring eligible"

    # Test gate enforcement: scoring eligibility promotion blocked if answer key unverified or rights forbidden
    is_eligible, blockers = verification_service.evaluate_scoring_eligibility(q4)
    print(f"[SCORING GATE] Q4 eligible: {is_eligible}, blockers count: {len(blockers)}")
    assert not is_eligible
    assert any("answer_verification_status" in b or "Answer key" in b for b in blockers)
    assert any("Rights clearance" in b or "rights_status" in b for b in blockers)

    # 9. Verify Canonical DB remained untouched throughout
    final_db_sha = get_file_sha256(CANONICAL_DB_PATH)
    print(f"[GUARD] Canonical DB SHA-256 after pilot: {final_db_sha[:16]}...")
    assert initial_db_sha == final_db_sha, "CRITICAL: Canonical database was modified during pilot execution!"

    print("=" * 70)
    print("PILOT EXECUTION COMPLETE: 100% CHECKS PASSED WITH ZERO LEAKS")
    print("=" * 70)
    return True


if __name__ == "__main__":
    success = run_pilot()
    if not success:
        sys.exit(1)
