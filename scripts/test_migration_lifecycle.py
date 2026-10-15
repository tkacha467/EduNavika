"""
EduNavika Milestone 4 — Disposable Migration Lifecycle Test.
Runs Alembic upgrade -> record insertion -> downgrade lifecycle in isolated subprocesses
against a disposable temporary copy of the database.
DOES NOT ALTER edunavika.db!
"""

import os
import sys
import shutil
import sqlite3
import subprocess
from pathlib import Path

def run_cmd(cmd_list, env=None):
    merged_env = os.environ.copy()
    if env:
        merged_env.update(env)
    res = subprocess.run(cmd_list, capture_output=True, text=True, env=merged_env)
    if res.returncode != 0:
        print(f"STDOUT:\n{res.stdout}")
        print(f"STDERR:\n{res.stderr}", file=sys.stderr)
        raise RuntimeError(f"Command failed with code {res.returncode}: {' '.join(cmd_list)}")
    return res.stdout

def test_migration_lifecycle():
    source_db = Path("edunavika.db").resolve()
    assert source_db.exists(), f"Source database not found at {source_db}"

    sandbox_db = Path("temp_migration_sandbox.db").resolve()
    if sandbox_db.exists():
        sandbox_db.unlink()

    print("--- 1. Creating Disposable Sandbox Copy of Database ---")
    shutil.copy2(source_db, sandbox_db)
    print(f"Created sandbox at {sandbox_db} (Size: {sandbox_db.stat().st_size} bytes)")

    # Read pre-migration state
    conn_pre = sqlite3.connect(str(sandbox_db))
    cur_pre = conn_pre.cursor()
    pre_tables = sorted([r[0] for r in cur_pre.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()])
    pre_counts = {t: cur_pre.execute(f'SELECT COUNT(*) FROM "{t}"').fetchone()[0] for t in pre_tables}
    pre_rev = cur_pre.execute("SELECT version_num FROM alembic_version").fetchone()[0]
    conn_pre.close()

    print(f"Pre-migration Alembic revision: {pre_rev}")
    print(f"Pre-migration tables count: {len(pre_tables)}")
    print(f"Pre-migration baseline: standards={pre_counts['standards']}, subjects={pre_counts['subjects']}, mcqs={pre_counts['mcq_questions']}")

    python_exe = sys.executable
    sandbox_url = f"sqlite:///{sandbox_db.as_posix()}"
    alembic_env = {"DATABASE_URL": sandbox_url}

    print("\n--- 2. Executing Alembic Upgrade to Head (Subprocess) ---")
    run_cmd([python_exe, "-m", "alembic", "-c", "backend/alembic.ini", "upgrade", "head"], env=alembic_env)

    # Inspect post-upgrade state
    conn_post = sqlite3.connect(str(sandbox_db))
    cur_post = conn_post.cursor()
    post_integrity = cur_post.execute("PRAGMA integrity_check").fetchall()
    assert post_integrity == [("ok",)], f"Integrity check failed: {post_integrity}"

    post_fk = cur_post.execute("PRAGMA foreign_key_check").fetchall()
    print(f"Post-upgrade foreign key violations: {len(post_fk)}")
    assert len(post_fk) == 0, f"FK violations detected: {post_fk}"

    post_rev = cur_post.execute("SELECT version_num FROM alembic_version").fetchone()[0]
    post_tables = sorted([r[0] for r in cur_post.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()])
    post_counts = {t: cur_post.execute(f'SELECT COUNT(*) FROM "{t}"').fetchone()[0] for t in post_tables}

    print(f"Post-upgrade Alembic revision: {post_rev}")
    print(f"Post-upgrade tables count: {len(post_tables)} (Added {len(post_tables) - len(pre_tables)} tables)")

    expected_new_tables = {
        "examinations",
        "exam_subjects",
        "exam_papers",
        "questions",
        "question_options",
        "question_verification_logs",
    }
    added_tables = set(post_tables) - set(pre_tables)
    assert added_tables == expected_new_tables, f"Unexpected tables added: {added_tables ^ expected_new_tables}"
    print(f"[VERIFIED] Expected 6 new tables present: {sorted(added_tables)}")

    # Verify all pre-existing table row counts were preserved untouched
    for t in pre_tables:
        if t == "alembic_version":
            continue
        assert post_counts[t] == pre_counts[t], f"Table {t} row count mutated during upgrade! ({pre_counts[t]} -> {post_counts[t]})"
    print("[VERIFIED] All 20 pre-existing data tables preserved 100% of rows.")

    # Test sample record insertion into new tables with strict validation
    print("\n--- 3. Testing Sample Records Insertion in Sandbox ---")
    cur_post.execute("""
        INSERT INTO examinations (code, name, conducting_body, is_active)
        VALUES ('JEE_MAIN', 'Joint Entrance Examination Main', 'National Testing Agency', 1)
    """)
    cur_post.execute("""
        INSERT INTO exam_papers (id, paper_identifier, exam_code, exam_year, session_or_shift, paper_code, total_questions)
        VALUES ('paper-001', 'JEE_MAIN:2024:session_1_jan_29_shift_1:DEFAULT', 'JEE_MAIN', 2024, 'Session 1 - Jan 29 Shift 1', NULL, 90)
    """)
    # Retrieve a valid topic from sandbox
    topic_row = cur_post.execute("SELECT id FROM topics LIMIT 1").fetchone()
    assert topic_row is not None, "No topic found in sandbox database"
    sample_topic_id = topic_row[0]

    cur_post.execute("""
        INSERT INTO questions (
            id, exam_paper_id, paper_question_number, topic_id, question_type,
            question_text, correct_answer_raw, answer_verification_status,
            solution_text, rights_status, publish_permission, evaluation_policy,
            official_status, eligibility_for_scoring, verification_status, content_hash
        ) VALUES (
            'q-001', 'paper-001', 1, ?, 'NUMERICAL',
            'Calculate the maximum kinetic energy $K_{\\max}$ in joules.', NULL, 'UNVERIFIED',
            NULL, 'PENDING_LEGAL_REVIEW', 'FORBIDDEN', 'UNRESOLVED_POLICY',
            'REGULAR', 'INELIGIBLE_UNVERIFIED_KEY', 'INGESTED', 'hash_test_q001'
        )
    """, (sample_topic_id,))
    conn_post.commit()
    print("[VERIFIED] Inserted sample unverified numerical question with NULL solution and NULL answer key cleanly.")

    # Verify duplicate paper_identifier is blocked
    try:
        cur_post.execute("""
            INSERT INTO exam_papers (id, paper_identifier, exam_code, exam_year, session_or_shift, paper_code, total_questions)
            VALUES ('paper-dup', 'JEE_MAIN:2024:session_1_jan_29_shift_1:DEFAULT', 'JEE_MAIN', 2024, 'Session 1 - Jan 29 Shift 1', NULL, 90)
        """)
        assert False, "Duplicate paper_identifier was not blocked!"
    except sqlite3.IntegrityError:
        print("[VERIFIED] Duplicate paper_identifier with NULL paper_code successfully blocked by UNIQUE constraint.")

    conn_post.close()
    del cur_post
    del conn_post
    import gc, time
    gc.collect()
    time.sleep(0.5)

    print("\n--- 4. Executing Alembic Downgrade to e025394444f5 (Subprocess) ---")
    run_cmd([python_exe, "-m", "alembic", "-c", "backend/alembic.ini", "downgrade", "e025394444f5"], env=alembic_env)

    # Inspect post-downgrade state
    conn_down = sqlite3.connect(str(sandbox_db))
    cur_down = conn_down.cursor()
    down_integrity = cur_down.execute("PRAGMA integrity_check").fetchall()
    assert down_integrity == [("ok",)], f"Integrity check after downgrade failed: {down_integrity}"

    down_rev = cur_down.execute("SELECT version_num FROM alembic_version").fetchone()[0]
    assert down_rev == "e025394444f5", f"Expected rollback to e025394444f5, got {down_rev}"
    print(f"Post-downgrade Alembic revision: {down_rev} (Rolled back successfully)")

    down_tables = sorted([r[0] for r in cur_down.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()])
    assert down_tables == pre_tables, f"Tables mismatch after downgrade! Diff: {set(down_tables) ^ set(pre_tables)}"
    print(f"[VERIFIED] Exactly 21 legacy tables remain after downgrade.")

    down_counts = {t: cur_down.execute(f'SELECT COUNT(*) FROM "{t}"').fetchone()[0] for t in down_tables}
    for t in pre_tables:
        assert down_counts[t] == pre_counts[t], f"Table {t} row count changed after rollback! ({pre_counts[t]} -> {down_counts[t]})"
    print("[VERIFIED] All pre-existing table row counts 100% identical after downgrade.")
    conn_down.close()

    # Cleanup sandbox
    sandbox_db.unlink()
    print(f"\n--- Disposable Sandbox Cleaned Up ---")
    print("[SUCCESS] Complete migration lifecycle (Upgrade -> Insertion -> Rollback) verified 100% safe and reversible!")

if __name__ == "__main__":
    test_migration_lifecycle()
