"""
Phase E.4: Sandbox Validation Script
Tests Alembic migration 'a1b2c3d4e5f6', canonical curriculum seeding, and exam_topics synchronization
on an isolated sandbox clone of edunavika.db.
Ensures zero writes to the persistent database.
"""

import os
import sys
import shutil
import sqlite3
import hashlib
from pathlib import Path

root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(root))

from alembic.config import Config
from alembic import command
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.app.services.curriculum_seeder import seed_canonical_curriculum
from backend.app.services.exam_topic_sync_service import sync_exam_topics
from backend.app.models.competitive_models import ExamTopic, Examination
from backend.app.models.curriculum_models import Topic, Chapter, Subject, Standard

PERSISTENT_BASELINE_HASH = "84432e58eb4b67f12da53a914e806b448212948a307a799f7de35b4cf04a2174"

def compute_sha256(filepath: Path) -> str:
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()

def main():
    persistent_db = root / "edunavika.db"
    sandbox_db = root / "sandbox_test_phase_e4.db"

    # Pre-check persistent DB
    hash_pre = compute_sha256(persistent_db)
    print(f"Persistent DB Hash (Pre): {hash_pre}")
    assert hash_pre == PERSISTENT_BASELINE_HASH, f"Persistent DB hash mismatch! Expected {PERSISTENT_BASELINE_HASH}, got {hash_pre}"

    if sandbox_db.exists():
        sandbox_db.unlink()

    print(f"\n1. Cloning persistent DB to disposable sandbox: {sandbox_db.name}")
    shutil.copy2(persistent_db, sandbox_db)

    # Inspect initial counts
    conn = sqlite3.connect(sandbox_db)
    cur = conn.cursor()
    std10_topics_pre = cur.execute(
        "SELECT COUNT(*) FROM topics WHERE chapter_id IN (SELECT id FROM chapters WHERE subject_id IN (SELECT id FROM subjects WHERE standard_id IN (SELECT id FROM standards WHERE grade_number = 10)))"
    ).fetchone()[0]
    conn.close()
    print(f"Pre-migration: Standard 10 topics count = {std10_topics_pre}")

    # 2. Run Alembic migration on sandbox
    print("\n2. Executing Alembic migration 'a1b2c3d4e5f6' on sandbox DB...")
    sandbox_db_url = f"sqlite:///{sandbox_db.as_posix()}"
    old_env_db_url = os.environ.get("DATABASE_URL")
    os.environ["DATABASE_URL"] = sandbox_db_url

    alembic_cfg = Config(str(root / "backend" / "alembic.ini"))
    alembic_cfg.set_main_option("script_location", str(root / "backend" / "alembic"))
    alembic_cfg.set_main_option("sqlalchemy.url", sandbox_db_url)

    try:
        command.upgrade(alembic_cfg, "a1b2c3d4e5f6")
    finally:
        if old_env_db_url is not None:
            os.environ["DATABASE_URL"] = old_env_db_url
        else:
            os.environ.pop("DATABASE_URL", None)

    print("  [OK] Migration applied successfully to sandbox.")

    # 3. Verify table schema in sandbox
    conn = sqlite3.connect(sandbox_db)
    cur = conn.cursor()
    tables = [row[0] for row in cur.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
    assert "exam_topics" in tables, "Table 'exam_topics' not found in sandbox!"

    # Verify columns
    columns = [col[1] for col in cur.execute("PRAGMA table_info(exam_topics)").fetchall()]
    expected_cols = ["id", "exam_code", "topic_id", "curriculum_role", "inclusion_status", "verification_status", "created_at"]
    for col in expected_cols:
        assert col in columns, f"Column '{col}' missing from exam_topics!"

    # Verify unique index
    indexes = [idx[1] for idx in cur.execute("PRAGMA index_list(exam_topics)").fetchall()]
    assert "uq_exam_topics_link" in indexes or any("exam_topics" in idx for idx in indexes), f"Unique index missing! Found: {indexes}"
    conn.close()
    print("  [OK] Table 'exam_topics' schema and indexes verified.")

    # 4. Seed curriculum hierarchy on sandbox
    sandbox_url = f"sqlite:///{sandbox_db.as_posix()}"
    engine = create_engine(sandbox_url, future=True)
    Session = sessionmaker(bind=engine, autocommit=False, autoflush=False)

    print("\n3. Seeding Canonical Curriculum into sandbox...")
    session = Session()
    res_seed = seed_canonical_curriculum(session, dry_run=False, include_unreviewed=False)
    session.close()
    print(f"  [OK] Seeded {res_seed['chapters_created']} chapters and {res_seed['topics_created']} topics (quarantined: {res_seed['quarantined_count']}).")

    # 5. Test Exam-Topic Sync Dry Run
    print("\n4. Testing Exam-Topic Synchronization (Dry Run)...")
    session = Session()
    res_dry = sync_exam_topics(session, dry_run=True)
    session.close()
    assert res_dry["dry_run"] is True
    assert res_dry["links_created"] == 1377, f"Expected 1377 links_created in dry run, got {res_dry['links_created']}"
    assert res_dry["quarantined_count"] == 2
    assert res_dry["textbook_only_count"] == 2

    # Verify sandbox exam_topics table is still empty
    conn = sqlite3.connect(sandbox_db)
    cur = conn.cursor()
    cnt_after_dry = cur.execute("SELECT COUNT(*) FROM exam_topics").fetchone()[0]
    conn.close()
    assert cnt_after_dry == 0, "Dry run wrote to exam_topics table!"
    print("  [OK] Dry run verified with 0 table writes.")

    # 6. Test Exam-Topic Sync Live Run
    print("\n5. Testing Exam-Topic Synchronization (Live Run)...")
    session = Session()
    res_live = sync_exam_topics(session, dry_run=False)
    session.close()
    assert res_live["links_created"] == 1377
    assert res_live["quarantined_count"] == 2
    assert res_live["textbook_only_count"] == 2
    print(f"  [OK] Synchronized {res_live['links_created']} exam-topic associations.")

    # 7. Test Idempotency
    print("\n6. Testing Synchronization Idempotency...")
    session = Session()
    res_idem = sync_exam_topics(session, dry_run=False)
    session.close()
    assert res_idem["links_created"] == 0, f"Expected 0 inserts on rerun, got {res_idem['links_created']}"
    assert res_idem["links_existing"] == 1377, f"Expected 1377 unchanged on rerun, got {res_idem['links_existing']}"
    print("  [OK] Idempotency confirmed: 0 new inserts, 1,377 unchanged.")

    # 8. Query and Verify Applicability Distribution
    print("\n7. Validating Exam Scope & Domain Boundaries...")
    conn = sqlite3.connect(sandbox_db)
    cur = conn.cursor()

    jee_main_count = cur.execute("SELECT COUNT(*) FROM exam_topics WHERE exam_code='JEE_MAIN'").fetchone()[0]
    jee_adv_count = cur.execute("SELECT COUNT(*) FROM exam_topics WHERE exam_code='JEE_ADVANCED'").fetchone()[0]
    neet_count = cur.execute("SELECT COUNT(*) FROM exam_topics WHERE exam_code='NEET_UG'").fetchone()[0]

    print(f"  - JEE_MAIN associations:     {jee_main_count}")
    print(f"  - JEE_ADVANCED associations: {jee_adv_count}")
    print(f"  - NEET_UG associations:      {neet_count}")
    assert jee_main_count == 436, f"Expected 436 JEE Main links, got {jee_main_count}"
    assert jee_adv_count == 444, f"Expected 444 JEE Advanced links, got {jee_adv_count}"
    assert neet_count == 497, f"Expected 497 NEET links, got {neet_count}"

    # Verify NEET has 0 Math
    neet_math = cur.execute("""
        SELECT COUNT(*) FROM exam_topics et
        JOIN topics t ON et.topic_id = t.id
        JOIN chapters c ON t.chapter_id = c.id
        JOIN subjects s ON c.subject_id = s.id
        WHERE et.exam_code = 'NEET_UG' AND s.code IN ('MATH11', 'MATH12')
    """).fetchone()[0]
    assert neet_math == 0, f"NEET has {neet_math} Math topics!"
    print("  [OK] NEET UG has 0 Mathematics topics.")

    # Verify JEE has 0 Biology
    jee_bio = cur.execute("""
        SELECT COUNT(*) FROM exam_topics et
        JOIN topics t ON et.topic_id = t.id
        JOIN chapters c ON t.chapter_id = c.id
        JOIN subjects s ON c.subject_id = s.id
        WHERE et.exam_code IN ('JEE_MAIN', 'JEE_ADVANCED') AND s.code IN ('BIO11', 'BIO12')
    """).fetchone()[0]
    assert jee_bio == 0, f"JEE has {jee_bio} Biology topics!"
    print("  [OK] JEE Main & JEE Advanced have 0 Biology topics.")

    # Check PRAGMA integrity and foreign keys
    integrity = cur.execute("PRAGMA integrity_check").fetchall()
    assert integrity == [("ok",)], f"Integrity check failed: {integrity}"
    fk_violations = cur.execute("PRAGMA foreign_key_check").fetchall()
    assert len(fk_violations) == 0, f"FK violations: {fk_violations}"
    print("  [OK] PRAGMA integrity_check and foreign_key_check passed with 0 errors.")

    # Check legacy data
    std10_topics_post = cur.execute(
        "SELECT COUNT(*) FROM topics WHERE chapter_id IN (SELECT id FROM chapters WHERE subject_id IN (SELECT id FROM subjects WHERE standard_id IN (SELECT id FROM standards WHERE grade_number = 10)))"
    ).fetchone()[0]
    assert std10_topics_post == std10_topics_pre, "Legacy Std 10 topics changed!"
    print(f"  [OK] Legacy Std 10 topics preserved intact ({std10_topics_post} rows).")
    conn.close()

    # Clean up sandbox
    engine.dispose()
    if sandbox_db.exists():
        sandbox_db.unlink()
    print("  [OK] Sandbox database deleted.")

    # Re-verify persistent DB hash
    hash_post = compute_sha256(persistent_db)
    print(f"\nPersistent DB Hash (Post): {hash_post}")
    assert hash_post == PERSISTENT_BASELINE_HASH, f"Persistent DB was modified! Post hash: {hash_post}"
    print("  [PASSED] Persistent DB hash is UNCHANGED and strictly preserved.")

if __name__ == "__main__":
    main()
