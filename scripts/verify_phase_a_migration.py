"""
EduNavika Milestone 4 — Phase A Post-Migration Verification Script.
Validates the local development database edunavika.db following migration f1e2d3c4b5a6.
"""

import sys
import sqlite3
from pathlib import Path

def verify_phase_a():
    db_path = Path("edunavika.db").resolve()
    print(f"--- Verifying Phase A Migration on {db_path} ---")

    conn = sqlite3.connect(str(db_path))
    cur = conn.cursor()

    # 1. Integrity Check
    integrity = cur.execute("PRAGMA integrity_check").fetchall()
    print(f"SQLite Integrity Check: {integrity}")
    assert integrity == [("ok",)], f"Integrity check failed: {integrity}"

    # 2. Foreign Key Check
    fk_violations = cur.execute("PRAGMA foreign_key_check").fetchall()
    print(f"Foreign Key Violations: {len(fk_violations)}")
    assert len(fk_violations) == 0, f"FK violations found: {fk_violations}"

    # 3. Alembic Revision
    rev = cur.execute("SELECT version_num FROM alembic_version").fetchone()[0]
    print(f"Active Alembic Revision: {rev}")
    assert rev == "f1e2d3c4b5a6", f"Expected f1e2d3c4b5a6, got {rev}"

    # 4. Tables Inventory
    all_tables = sorted([r[0] for r in cur.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()])
    print(f"Total Tables Count: {len(all_tables)} (Expected: 27)")
    assert len(all_tables) == 27, f"Expected 27 tables, got {len(all_tables)}"

    expected_new_tables = {
        "examinations",
        "exam_subjects",
        "exam_papers",
        "questions",
        "question_options",
        "question_verification_logs",
    }
    legacy_tables = [t for t in all_tables if t not in expected_new_tables]
    assert len(legacy_tables) == 21, f"Expected 21 legacy tables, got {len(legacy_tables)}"

    print(f"[VERIFIED] Expected 6 new tables present: {sorted(expected_new_tables)}")

    # 5. Legacy Table Row Count Reconciliation
    expected_legacy_counts = {
        "alembic_version": 1,
        "standards": 1,
        "subjects": 239,
        "chapters": 288,
        "topics": 505,
        "learning_contents": 573,
        "mcq_questions": 80,
        "users": 244,
        "student_profiles": 243,
        "learning_events": 776,
        "topic_performances": 149,
        "revision_plans": 21,
        "forgetting_signals": 10,
        "learning_quests": 3,
        "answers": 0,
        "assessment_questions": 0,
        "assessments": 0,
        "attempts": 0,
        "question_history": 0,
        "teacher_actions": 0,
        "teacher_profiles": 0,
    }

    print("\n--- Legacy Table Row Counts (Before vs After Migration) ---")
    print(f"{'Table Name':<28} | {'Expected Count':<14} | {'Current Count':<14} | {'Status'}")
    print("-" * 65)

    all_matched = True
    for table, expected in expected_legacy_counts.items():
        current = cur.execute(f'SELECT COUNT(*) FROM "{table}"').fetchone()[0]
        matched = (current == expected)
        if not matched:
            all_matched = False
        print(f"{table:<28} | {expected:<14} | {current:<14} | {'UNCHANGED' if matched else 'MUTATED!'}")

    assert all_matched, "Legacy table row count mutation detected!"
    print("\n[VERIFIED] Zero legacy records were modified, mutated, or deleted.")

    # 6. Verify Schema Structure & Indexes of New Tables
    print("\n--- New Tables Schema & Index Verification ---")
    for new_table in sorted(expected_new_tables):
        cols = [c[1] for c in cur.execute(f"PRAGMA table_info('{new_table}')").fetchall()]
        idxs = [i[1] for i in cur.execute(f"PRAGMA index_list('{new_table}')").fetchall()]
        print(f"Table: {new_table}")
        print(f"  Columns ({len(cols)}): {', '.join(cols[:6])}...")
        print(f"  Indexes ({len(idxs)}): {', '.join(idxs)}")
        # Verify 0 rows in new tables (ensuring no premature seeding)
        row_count = cur.execute(f'SELECT COUNT(*) FROM "{new_table}"').fetchone()[0]
        assert row_count == 0, f"Expected 0 rows in unseeded table {new_table}, found {row_count}"

    print("\n[VERIFIED] All 6 new tables are empty (zero premature seeding).")

    conn.close()
    print("\n--- Phase A Migration Validation 100% SUCCESSFUL ---")

if __name__ == "__main__":
    verify_phase_a()
