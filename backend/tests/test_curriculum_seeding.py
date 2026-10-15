"""
EduNavika — Milestone 4: Canonical Curriculum Seeding & Validation Tests.
Phase E / E.2: Evidence-Based Manifest Correction & Seeder Hardening Test Suite.

Verifies:
1. Dry-run performs zero writes to the database.
2. Clean disposable database receives expected curriculum hierarchy (with review quarantine).
3. Re-running the seeder creates no duplicates (idempotency).
4. Existing Standard 10 records remain completely unchanged.
5. Exam-subject associations remain correct.
6. Foreign keys and uniqueness constraints are strictly respected.
7. Safe conflict policies (ABORT, WARN, OVERWRITE) prevent silent overwrites.
8. Corrected Biology canonical IDs (STD11-BIO- and STD12-BIO-) are strictly formatted.
9. Exam applicability matches official ground truth (subtopic-level exclusions enforced).
10. Repeated execution produces deterministic, reproducible UUIDs.
"""

import os
import copy
import json
import uuid
import pytest
from pathlib import Path
from sqlalchemy import text

from backend.app.core.database import Base
from backend.app.models.curriculum_models import Standard, Subject, Chapter, Topic
from backend.app.db.seed_canonical_curriculum import seed_canonical_curriculum as seed_base_curriculum
from backend.app.services.curriculum_seeder import (
    seed_canonical_curriculum,
    load_manifest,
    deterministic_uuid,
    CurriculumConflictError,
    DEFAULT_MANIFEST_PATH,
)


@pytest.fixture
def seeded_prerequisites(db_session):
    """
    Sets up the base environment in the disposable test database:
    - Standard 10 (Legacy) with chapters and topics to verify legacy preservation.
    - Standard 11 & Standard 12 with the 8 canonical STEM subjects (via Phase B seeder).
    - The 18 Exam-Subject associations across JEE Main, JEE Adv, and NEET UG.
    """
    # 1. Create legacy Standard 10 data
    std10 = Standard(
        id=str(uuid.uuid4()),
        grade_number=10,
        name="Standard 10",
        description="Legacy GSEB/NCERT Class 10 Secondary",
        is_active=True,
    )
    db_session.add(std10)
    db_session.flush()

    subj10 = Subject(
        id=str(uuid.uuid4()),
        standard_id=std10.id,
        name="Science 10",
        code="SCI10",
        description="Class 10 Science",
        is_active=True,
    )
    db_session.add(subj10)
    db_session.flush()

    ch10 = Chapter(
        id=str(uuid.uuid4()),
        subject_id=subj10.id,
        chapter_number=1,
        title="Chemical Reactions and Equations",
        source_reference="GSEB Std 10 Science Ch 1",
        is_active=True,
    )
    db_session.add(ch10)
    db_session.flush()

    top10 = Topic(
        id=str(uuid.uuid4()),
        chapter_id=ch10.id,
        topic_order=1,
        title="Chemical Equations",
        description="Writing and balancing chemical equations",
        is_active=True,
    )
    db_session.add(top10)
    db_session.flush()

    # 2. Seed Base Examinations, Standards 11 & 12, Subjects, Exam-Subject links
    seed_base_curriculum(db_session, dry_run=False)
    db_session.commit()

    return {
        "std10_id": std10.id,
        "subj10_id": subj10.id,
        "ch10_id": ch10.id,
        "top10_id": top10.id,
    }


def test_01_dry_run_performs_zero_writes(db_session, seeded_prerequisites):
    """Test 1: Dry-run performs zero writes to the database."""
    pre_chapters = db_session.query(Chapter).count()
    pre_topics = db_session.query(Topic).count()
    assert pre_chapters == 1
    assert pre_topics == 1

    report = seed_canonical_curriculum(db_session, dry_run=True, include_unreviewed=True)

    assert report["dry_run"] is True
    assert report["chapters_created"] == 106
    assert report["topics_created"] == 626

    post_chapters = db_session.query(Chapter).count()
    post_topics = db_session.query(Topic).count()
    assert post_chapters == pre_chapters
    assert post_topics == pre_topics


def test_02_clean_disposable_database_receives_curriculum_hierarchy(db_session, seeded_prerequisites):
    """Test 2: A clean disposable database receives the expected curriculum hierarchy."""
    # Under default production mode (include_unreviewed=False), 2 unreviewed topics are quarantined
    report = seed_canonical_curriculum(db_session, dry_run=False, include_unreviewed=False)

    assert report["dry_run"] is False
    assert report["success"] is True
    assert report["chapters_created"] == 106
    assert report["topics_created"] == 624  # 626 - 2 quarantined
    assert report["quarantined_count"] == 2
    quarantined_ids = [item["canonical_id"] for item in report["quarantined_items"]]
    assert "STD11-BIO-CH05-T07" in quarantined_ids
    assert "STD11-BIO-CH07-T03" in quarantined_ids

    # Total chapters = 106 + 1 (legacy Std 10) = 107
    assert db_session.query(Chapter).count() == 107
    # Total topics = 624 + 1 (legacy Std 10) = 625
    assert db_session.query(Topic).count() == 625


def test_03_rerunning_seeder_creates_no_duplicates(db_session, seeded_prerequisites):
    """Test 3: Re-running the seeder creates no duplicates (100% idempotent)."""
    r1 = seed_canonical_curriculum(db_session, dry_run=False, include_unreviewed=False)
    assert r1["chapters_created"] == 106
    assert r1["topics_created"] == 624

    r2 = seed_canonical_curriculum(db_session, dry_run=False, include_unreviewed=False)
    assert r2["chapters_created"] == 0
    assert r2["topics_created"] == 0
    assert r2["chapters_existing"] == 106
    assert r2["topics_existing"] == 624
    assert len(r2["conflicts"]) == 0

    assert db_session.query(Chapter).count() == 107
    assert db_session.query(Topic).count() == 625


def test_04_existing_standard_10_records_remain_unchanged(db_session, seeded_prerequisites):
    """Test 4: Existing Standard 10 records remain completely unchanged."""
    std10_id = seeded_prerequisites["std10_id"]
    subj10_id = seeded_prerequisites["subj10_id"]
    ch10_id = seeded_prerequisites["ch10_id"]
    top10_id = seeded_prerequisites["top10_id"]

    seed_canonical_curriculum(db_session, dry_run=False)

    std10 = db_session.query(Standard).filter(Standard.id == std10_id).first()
    assert std10 is not None and std10.grade_number == 10

    subj10 = db_session.query(Subject).filter(Subject.id == subj10_id).first()
    assert subj10 is not None and subj10.code == "SCI10"

    ch10 = db_session.query(Chapter).filter(Chapter.id == ch10_id).first()
    assert ch10 is not None and ch10.title == "Chemical Reactions and Equations"

    top10 = db_session.query(Topic).filter(Topic.id == top10_id).first()
    assert top10 is not None and top10.title == "Chemical Equations"


def test_05_exam_subject_associations_remain_correct(db_session, seeded_prerequisites):
    """Test 5: Exam-subject associations remain correct and intact."""
    seed_canonical_curriculum(db_session, dry_run=False)

    conn = db_session.connection()
    rows = conn.exec_driver_sql(
        """
        SELECT es.exam_code, s.code, s.name, es.curriculum_role
        FROM exam_subjects es
        JOIN subjects s ON es.subject_id = s.id
        ORDER BY es.exam_code, s.code
        """
    ).fetchall()

    assert len(rows) == 18
    jee_main_subjects = [r[1] for r in rows if r[0] == "JEE_MAIN"]
    neet_subjects = [r[1] for r in rows if r[0] == "NEET_UG"]

    assert "BIO11" not in jee_main_subjects and "BIO12" not in jee_main_subjects
    assert "MATH11" not in neet_subjects and "MATH12" not in neet_subjects


def test_06_foreign_keys_and_uniqueness_constraints_respected(db_session, seeded_prerequisites):
    """Test 6: Foreign keys and uniqueness constraints are strictly respected."""
    seed_canonical_curriculum(db_session, dry_run=False)

    raw_conn = db_session.connection()
    fk_violations = raw_conn.exec_driver_sql("PRAGMA foreign_key_check").fetchall()
    assert len(fk_violations) == 0, f"FK violations: {fk_violations}"

    integrity = raw_conn.exec_driver_sql("PRAGMA integrity_check").fetchall()
    assert integrity == [("ok",)], f"Integrity failed: {integrity}"


def test_07_conflict_policy_prevents_silent_overwrites(db_session, seeded_prerequisites):
    """Test 7: Conflict policy strictly prevents silent overwriting of existing modified records."""
    # Seed baseline
    seed_canonical_curriculum(db_session, dry_run=False, include_unreviewed=True)

    # Simulate a customized chapter title in DB
    raw_conn = db_session.connection()
    raw_conn.exec_driver_sql(
        "UPDATE chapters SET title = 'Customized Title in Database' WHERE chapter_number = 1 AND subject_id = (SELECT id FROM subjects WHERE code = 'PHYS11')"
    )
    db_session.commit()

    # 1. Under ABORT policy (default): must raise CurriculumConflictError and rollback
    report_abort = seed_canonical_curriculum(db_session, dry_run=False, conflict_policy="ABORT")
    assert report_abort["success"] is False
    assert len(report_abort["conflicts"]) > 0
    assert any("Conflict on chapter PHYS11 #1" in err for err in report_abort["errors"])

    # Helper to fetch current title cleanly
    def get_ch1_title():
        ch = db_session.query(Chapter).filter(
            Chapter.chapter_number == 1,
            Chapter.subject_id == db_session.query(Subject.id).filter(Subject.code == "PHYS11").scalar()
        ).first()
        return ch.title if ch else None

    # Verify customized title was NOT overwritten
    assert get_ch1_title() == "Customized Title in Database"

    # 2. Under WARN policy: logs conflict, preserves existing record without error
    report_warn = seed_canonical_curriculum(db_session, dry_run=False, conflict_policy="WARN")
    assert len(report_warn["conflicts"]) > 0
    assert len(report_warn["errors"]) == 0
    assert get_ch1_title() == "Customized Title in Database"

    # 3. Under OVERWRITE policy: explicitly authorized update succeeds
    report_overwrite = seed_canonical_curriculum(db_session, dry_run=False, conflict_policy="OVERWRITE")
    assert report_overwrite["chapters_updated"] == 1
    assert get_ch1_title() == "Units and Measurements"


def test_08_biology_canonical_ids_are_correctly_formatted(db_session, seeded_prerequisites):
    """Test 8: Biology canonical IDs strictly use prefix STD11-BIO- and STD12-BIO-."""
    manifest = load_manifest()
    for std in manifest["standards"]:
        for subj in std["subjects"]:
            if subj["code"] in ("BIO11", "BIO12"):
                grade = std["grade_number"]
                for ch in subj["chapters"]:
                    assert ch["canonical_id"].startswith(f"STD{grade}-BIO-CH")
                    assert not ch["canonical_id"].startswith(f"STD{grade}-BIO1-CH")
                    for t in ch["topics"]:
                        assert t["canonical_id"].startswith(f"STD{grade}-BIO-CH")
                        assert not t["canonical_id"].startswith(f"STD{grade}-BIO1-CH")


def test_09_exam_applicability_subtopic_exclusions():
    """Test 9: Verifies that subtopic-level exam exclusions are accurately reflected."""
    manifest = load_manifest()
    topics_map = {}
    for std in manifest["standards"]:
        for subj in std["subjects"]:
            for ch in subj["chapters"]:
                for t in ch["topics"]:
                    topics_map[t["canonical_id"]] = t

    # Carnot engine: retained in JEE Advanced only; deleted from Main & NEET
    carnot = topics_map["STD11-PHYS-CH11-T08"]
    assert carnot["applicable_exams"] == ["JEE_ADVANCED"]
    assert carnot["exam_verification_status"] == "PARTIAL_MAPPING"

    # Newton's law of cooling: pruned from all entrance exams
    cooling = topics_map["STD11-PHYS-CH10-T07"]
    assert cooling["applicable_exams"] == []
    assert cooling["exam_verification_status"] == "VERIFIED_TEXTBOOK_ONLY"

    # Tangents and Normals: retained in JEE Advanced only; deleted from Main
    tangents = topics_map["STD12-MATH-CH06-T03"]
    assert tangents["applicable_exams"] == ["JEE_ADVANCED"]
    assert tangents["exam_verification_status"] == "PARTIAL_MAPPING"

    # Doppler effect: retained in JEE Advanced only; deleted from Main & NEET
    doppler = topics_map["STD11-PHYS-CH14-T07"]
    assert doppler["applicable_exams"] == ["JEE_ADVANCED"]
    assert doppler["exam_verification_status"] == "PARTIAL_MAPPING"


def test_10_deterministic_uuid_reproducibility():
    """Test 10: Ensures chapter and topic UUIDs are 100% deterministic and reproducible."""
    id1 = deterministic_uuid("edunavika.chapter.STD11-PHYS-CH01")
    id2 = deterministic_uuid("edunavika.chapter.STD11-PHYS-CH01")
    assert id1 == id2

    bio_id1 = deterministic_uuid("edunavika.chapter.STD11-BIO-CH01")
    bio_id2 = deterministic_uuid("edunavika.chapter.STD11-BIO-CH01")
    assert bio_id1 == bio_id2
    assert bio_id1 != id1
