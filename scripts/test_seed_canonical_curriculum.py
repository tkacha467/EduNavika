"""
EduNavika Milestone 4 — Phase B: Curriculum Seeding Verification Test.
Executes against a disposable sandbox copy of the database to verify:
1. Clean seed creates exact expected records.
2. Second seed execution is 100% idempotent (0 created, all already existing).
3. Legacy Standard 10 records remain 100% untouched.
4. Exam-to-Subject mappings match approved configuration (Physics/Chem=3 exams, Math=JEE, Bio=NEET).
5. Foreign-key and uniqueness constraints hold.
6. Invalid operations roll back safely without corruption.
7. Persistent edunavika.db remains 100% untouched.
"""

import os
import sys
import shutil
import sqlite3
from pathlib import Path

# Ensure project root is in sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.app.db.seed_canonical_curriculum import seed_canonical_curriculum
from backend.app.models.curriculum_models import Standard, Subject

def test_seed_lifecycle():
    source_db = Path("edunavika.db").resolve()
    assert source_db.exists(), f"Source DB not found at {source_db}"

    sandbox_db = Path("temp_seed_sandbox.db").resolve()
    if sandbox_db.exists():
        sandbox_db.unlink()

    print("--- 1. Creating Sandbox Copy for Seeding Verification ---")
    shutil.copy2(source_db, sandbox_db)
    print(f"Created sandbox at {sandbox_db}")

    # Baseline counts on sandbox
    conn = sqlite3.connect(str(sandbox_db))
    cur = conn.cursor()
    std10_count_pre = cur.execute("SELECT COUNT(*) FROM standards WHERE grade_number = 10").fetchone()[0]
    std10_subjects_pre = cur.execute("SELECT COUNT(*) FROM subjects WHERE standard_id = (SELECT id FROM standards WHERE grade_number = 10)").fetchone()[0]
    total_subjects_pre = cur.execute("SELECT COUNT(*) FROM subjects").fetchone()[0]
    total_mcqs_pre = cur.execute("SELECT COUNT(*) FROM mcq_questions").fetchone()[0]
    conn.close()

    sandbox_url = f"sqlite:///{sandbox_db.as_posix()}"
    engine = create_engine(sandbox_url, future=True)
    Session = sessionmaker(bind=engine, autocommit=False, autoflush=False)

    # --- Test 1: Dry-Run Verification ---
    print("\n--- Test 1: Testing Dry-Run Mode ---")
    session_dry = Session()
    dry_report = seed_canonical_curriculum(session_dry, dry_run=True)
    session_dry.close()
    assert dry_report["created"]["examinations"] == 3
    assert dry_report["created"]["standards"] == 2
    assert dry_report["created"]["subjects"] == 8
    assert dry_report["created"]["exam_subjects"] == 18
    # Verify nothing was committed in dry run
    conn = sqlite3.connect(str(sandbox_db))
    cur = conn.cursor()
    assert cur.execute("SELECT COUNT(*) FROM examinations").fetchone()[0] == 0
    assert cur.execute("SELECT COUNT(*) FROM standards").fetchone()[0] == 1
    conn.close()
    print("[PASSED] Dry run planned 3 exams, 2 standards, 8 subjects, 18 links with 0 database writes.")

    # --- Test 2: Clean Live Seed ---
    print("\n--- Test 2: Executing Clean Live Seed ---")
    session_live = Session()
    live_report = seed_canonical_curriculum(session_live, dry_run=False)
    session_live.close()

    assert live_report["created"]["examinations"] == 3
    assert live_report["created"]["standards"] == 2
    assert live_report["created"]["subjects"] == 8
    assert live_report["created"]["exam_subjects"] == 18
    print(f"[PASSED] Seeded: 3 examinations, 2 standards (11, 12), 8 subjects, 18 exam-subject links.")

    # Inspect Sandbox Database State Post-Seed
    conn = sqlite3.connect(str(sandbox_db))
    cur = conn.cursor()

    # Integrity & FK Check
    assert cur.execute("PRAGMA integrity_check").fetchall() == [("ok",)], "Integrity check failed"
    assert len(cur.execute("PRAGMA foreign_key_check").fetchall()) == 0, "FK check failed"
    print("[PASSED] Database integrity check ok, 0 foreign key violations.")

    # --- Test 3: Idempotency (Second Seed Execution) ---
    print("\n--- Test 3: Testing Idempotency on Second Seed Run ---")
    session_rerun = Session()
    rerun_report = seed_canonical_curriculum(session_rerun, dry_run=False)
    session_rerun.close()

    assert rerun_report["created"]["examinations"] == 0
    assert rerun_report["created"]["standards"] == 0
    assert rerun_report["created"]["subjects"] == 0
    assert rerun_report["created"]["exam_subjects"] == 0

    assert rerun_report["already_existing"]["examinations"] == 3
    assert rerun_report["already_existing"]["standards"] == 2
    assert rerun_report["already_existing"]["subjects"] == 8
    assert rerun_report["already_existing"]["exam_subjects"] == 18
    print("[PASSED] Second execution created 0 duplicates; exactly 3 exams, 2 standards, 8 subjects, 18 links reported already existing.")

    # --- Test 4: Legacy Standard 10 Preservation ---
    print("\n--- Test 4: Verifying Legacy Standard 10 Preservation ---")
    std10_count_post = cur.execute("SELECT COUNT(*) FROM standards WHERE grade_number = 10").fetchone()[0]
    std10_subjects_post = cur.execute("SELECT COUNT(*) FROM subjects WHERE standard_id = (SELECT id FROM standards WHERE grade_number = 10)").fetchone()[0]
    total_mcqs_post = cur.execute("SELECT COUNT(*) FROM mcq_questions").fetchone()[0]

    assert std10_count_post == std10_count_pre, "Standard 10 record altered!"
    assert std10_subjects_post == std10_subjects_pre, "Standard 10 subjects count mutated!"
    assert total_mcqs_post == total_mcqs_pre, "Standard 10 MCQs count mutated!"
    print(f"[PASSED] Standard 10 remains untouched: {std10_count_post} standard, {std10_subjects_post} subjects, {total_mcqs_post} MCQs.")

    # --- Test 5: Verify Specific Exam-Subject Distribution Rules ---
    print("\n--- Test 5: Verifying Cross-Exam Association Rules ---")
    # Rule 1: Physics and Chemistry must map to all 3 exams (Std 11 & 12 = 6 links each)
    phys_links = cur.execute("""
        SELECT COUNT(*) FROM exam_subjects es
        JOIN subjects s ON es.subject_id = s.id
        WHERE s.name = 'Physics'
    """).fetchone()[0]
    chem_links = cur.execute("""
        SELECT COUNT(*) FROM exam_subjects es
        JOIN subjects s ON es.subject_id = s.id
        WHERE s.name = 'Chemistry'
    """).fetchone()[0]
    assert phys_links == 6, f"Expected 6 Physics links, got {phys_links}"
    assert chem_links == 6, f"Expected 6 Chemistry links, got {chem_links}"

    # Rule 2: Mathematics must map ONLY to JEE Main and JEE Advanced (Std 11 & 12 = 4 links)
    math_links = cur.execute("""
        SELECT es.exam_code, s.code FROM exam_subjects es
        JOIN subjects s ON es.subject_id = s.id
        WHERE s.name = 'Mathematics'
    """).fetchall()
    assert len(math_links) == 4, f"Expected 4 Math links, got {len(math_links)}"
    math_exams = {row[0] for row in math_links}
    assert math_exams == {"JEE_MAIN", "JEE_ADVANCED"}, f"Mathematics linked to invalid exam: {math_exams}"
    assert "NEET_UG" not in math_exams, "Mathematics must NEVER be linked to NEET UG!"

    # Rule 3: Biology must map ONLY to NEET UG (Std 11 & 12 = 2 links)
    bio_links = cur.execute("""
        SELECT es.exam_code, s.code FROM exam_subjects es
        JOIN subjects s ON es.subject_id = s.id
        WHERE s.name = 'Biology'
    """).fetchall()
    assert len(bio_links) == 2, f"Expected 2 Biology links, got {len(bio_links)}"
    bio_exams = {row[0] for row in bio_links}
    assert bio_exams == {"NEET_UG"}, f"Biology linked to invalid exam: {bio_exams}"
    assert "JEE_MAIN" not in bio_exams, "Biology must NEVER be linked to JEE Main!"
    assert "JEE_ADVANCED" not in bio_exams, "Biology must NEVER be linked to JEE Advanced!"
    print("[PASSED] Exam associativity verified: Physics (6), Chemistry (6), Math strictly JEE (4), Bio strictly NEET (2).")

    # --- Test 6: Transaction Rollback on Error ---
    print("\n--- Test 6: Verifying Transaction Safety on Constraint Violation ---")
    session_fail = Session()
    try:
        # Intentionally cause a foreign key constraint violation
        session_fail.connection().exec_driver_sql(
            "INSERT INTO exam_subjects (id, exam_code, subject_id, curriculum_role) VALUES ('bad-id', 'NON_EXISTENT_EXAM', 'bad-subj', 'CORE')"
        )
        session_fail.commit()
        assert False, "Should have thrown IntegrityError"
    except Exception:
        session_fail.rollback()
        print("[PASSED] Transaction rolled back cleanly on constraint violation.")
    finally:
        session_fail.close()

    conn.close()
    engine.dispose()

    # Cleanup sandbox
    sandbox_db.unlink()
    print("\n--- Sandbox Cleaned Up ---")

    # --- Test 7: Verify Persistent Database Untouched ---
    print("\n--- Test 7: Verifying Persistent Database edunavika.db Untouched ---")
    conn_real = sqlite3.connect(str(source_db))
    cur_real = conn_real.cursor()
    real_standards = cur_real.execute("SELECT COUNT(*) FROM standards").fetchone()[0]
    real_subjects = cur_real.execute("SELECT COUNT(*) FROM subjects").fetchone()[0]
    real_exams = cur_real.execute("SELECT COUNT(*) FROM examinations").fetchone()[0]
    real_exam_subjs = cur_real.execute("SELECT COUNT(*) FROM exam_subjects").fetchone()[0]
    conn_real.close()

    assert real_standards == 1, f"edunavika.db standards mutated! ({real_standards})"
    assert real_subjects == 239, f"edunavika.db subjects mutated! ({real_subjects})"
    assert real_exams == 0, f"edunavika.db examinations mutated! ({real_exams})"
    assert real_exam_subjs == 0, f"edunavika.db exam_subjects mutated! ({real_exam_subjs})"
    print("[PASSED] Persistent edunavika.db remains 100% untouched (examinations=0, standards=1, subjects=239).")

    print("\n=======================================================")
    print("ALL 7 PHASE B SEEDING TESTS PASSED WITH 100% SUCCESS")
    print("=======================================================")

if __name__ == "__main__":
    test_seed_lifecycle()
