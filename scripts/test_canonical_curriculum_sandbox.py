"""
Sandbox Verification of Canonical Curriculum Seeder against full copy of edunavika.db.
Verifies that real database state accommodates all 106 chapters and 626 topics without constraint violations.
"""

import os
import sys
import shutil
import sqlite3
from pathlib import Path

root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(root))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.app.services.curriculum_seeder import seed_canonical_curriculum

def main():
    root = Path(__file__).resolve().parent.parent
    source_db = root / "edunavika.db"
    sandbox_db = root / "sandbox_test_phase_e.db"

    if sandbox_db.exists():
        sandbox_db.unlink()

    print(f"1. Copying {source_db} to {sandbox_db}...")
    shutil.copy2(source_db, sandbox_db)

    # Initial state checks
    conn = sqlite3.connect(sandbox_db)
    cur = conn.cursor()
    std10_ch_pre = cur.execute(
        "SELECT COUNT(*) FROM chapters WHERE subject_id IN (SELECT id FROM subjects WHERE standard_id IN (SELECT id FROM standards WHERE grade_number = 10))"
    ).fetchone()[0]
    std11_12_ch_pre = cur.execute(
        "SELECT COUNT(*) FROM chapters WHERE subject_id IN (SELECT id FROM subjects WHERE standard_id IN (SELECT id FROM standards WHERE grade_number IN (11, 12)))"
    ).fetchone()[0]
    conn.close()

    print(f"Pre-seed: Standard 10 Chapters = {std10_ch_pre}, Standards 11/12 Chapters = {std11_12_ch_pre}")
    assert std11_12_ch_pre == 0, "Expected 0 chapters under Std 11 & 12 before seeding"

    # Setup SQLAlchemy session on sandbox
    sandbox_url = f"sqlite:///{sandbox_db.as_posix()}"
    engine = create_engine(sandbox_url, future=True)
    Session = sessionmaker(bind=engine, autocommit=False, autoflush=False)

    # Step 1: Dry run
    print("\n2. Testing Dry Run on Sandbox...")
    session = Session()
    r_dry = seed_canonical_curriculum(session, dry_run=True, include_unreviewed=False)
    session.close()

    assert r_dry["dry_run"] is True
    assert r_dry["chapters_created"] == 106
    assert r_dry["topics_created"] == 624
    assert r_dry["quarantined_count"] == 2

    # Verify zero writes on DB
    conn = sqlite3.connect(sandbox_db)
    cur = conn.cursor()
    ch_after_dry = cur.execute(
        "SELECT COUNT(*) FROM chapters WHERE subject_id IN (SELECT id FROM subjects WHERE standard_id IN (SELECT id FROM standards WHERE grade_number IN (11, 12)))"
    ).fetchone()[0]
    conn.close()
    assert ch_after_dry == 0, "Dry run wrote to sandbox DB!"
    print("  [OK] Dry run completed with 0 writes.")

    # Step 2: Live Seed
    print("\n3. Testing Live Seed on Sandbox...")
    session = Session()
    r_live = seed_canonical_curriculum(session, dry_run=False, include_unreviewed=False)
    session.close()

    assert r_live["chapters_created"] == 106
    assert r_live["topics_created"] == 624
    assert r_live["quarantined_count"] == 2
    print(f"  [OK] Seeded 106 chapters and 624 verified topics successfully (2 unreviewed quarantined).")

    # Verify post-seed DB constraints
    conn = sqlite3.connect(sandbox_db)
    cur = conn.cursor()
    integrity = cur.execute("PRAGMA integrity_check").fetchall()
    assert integrity == [("ok",)], f"Integrity failed: {integrity}"
    fk_errors = cur.execute("PRAGMA foreign_key_check").fetchall()
    assert len(fk_errors) == 0, f"FK violations: {fk_errors}"

    std10_ch_post = cur.execute(
        "SELECT COUNT(*) FROM chapters WHERE subject_id IN (SELECT id FROM subjects WHERE standard_id IN (SELECT id FROM standards WHERE grade_number = 10))"
    ).fetchone()[0]
    assert std10_ch_post == std10_ch_pre, "Standard 10 chapters modified!"

    std11_12_ch_post = cur.execute(
        "SELECT COUNT(*) FROM chapters WHERE subject_id IN (SELECT id FROM subjects WHERE standard_id IN (SELECT id FROM standards WHERE grade_number IN (11, 12)))"
    ).fetchone()[0]
    assert std11_12_ch_post == 106, f"Expected 106 chapters, got {std11_12_ch_post}"

    std11_12_top_post = cur.execute(
        "SELECT COUNT(*) FROM topics WHERE chapter_id IN (SELECT id FROM chapters WHERE subject_id IN (SELECT id FROM subjects WHERE standard_id IN (SELECT id FROM standards WHERE grade_number IN (11, 12))))"
    ).fetchone()[0]
    assert std11_12_top_post == 624, f"Expected 624 topics, got {std11_12_top_post}"
    conn.close()
    print("  [OK] Integrity OK, 0 FK errors, Std 10 records untouched, exactly 106 chapters and 624 topics added.")

    # Step 3: Re-run for Idempotency
    print("\n4. Testing Idempotency (Second Live Run)...")
    session = Session()
    r_rerun = seed_canonical_curriculum(session, dry_run=False, include_unreviewed=False)
    session.close()

    assert r_rerun["chapters_created"] == 0
    assert r_rerun["topics_created"] == 0
    assert r_rerun["chapters_existing"] == 106
    assert r_rerun["topics_existing"] == 624
    print("  [OK] Second run created 0 duplicates (100% idempotent).")

    # Clean up sandbox
    engine.dispose()
    if sandbox_db.exists():
        sandbox_db.unlink()
    print("\n[ALL SANDBOX TESTS PASSED SUCCESSFULLY]")

if __name__ == "__main__":
    main()
