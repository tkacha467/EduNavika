"""
EduNavika Milestone 4 — Gate 1 Native SQLite Backup & Verification Script.
Uses Python's native sqlite3.Connection.backup() API to ensure an atomic,
consistent snapshot accounting for active WAL journals.
"""

import os
import sys
import sqlite3
from pathlib import Path
from datetime import datetime, timezone

def perform_verified_backup():
    source_db_path = Path("edunavika.db").resolve()
    if not source_db_path.exists():
        print(f"ERROR: Source database not found at {source_db_path}", file=sys.stderr)
        sys.exit(1)

    backup_dir = Path("backups/milestone_4_pre_migration").resolve()
    backup_dir.mkdir(parents=True, exist_ok=True)
    backup_db_path = backup_dir / "edunavika_pre_m4.db"

    print(f"--- Starting SQLite Native Backup ---")
    print(f"Timestamp (UTC): {datetime.now(timezone.utc).isoformat()}")
    print(f"Source Database: {source_db_path} (Size: {source_db_path.stat().st_size} bytes)")
    print(f"Target Backup:   {backup_db_path}")

    # Check for WAL files
    wal_path = Path(f"{source_db_path}-wal")
    shm_path = Path(f"{source_db_path}-shm")
    print(f"WAL journal present: {wal_path.exists()} (Size: {wal_path.stat().st_size if wal_path.exists() else 0} bytes)")
    print(f"SHM index present:   {shm_path.exists()}")

    # 1. Connect to source with WAL pragmas
    source_conn = sqlite3.connect(str(source_db_path))
    source_cur = source_conn.cursor()

    # Flush WAL to disk before backup if possible
    try:
        source_cur.execute("PRAGMA wal_checkpoint(PASSIVE)")
        checkpoint_res = source_cur.fetchone()
        print(f"Passive WAL checkpoint result: {checkpoint_res}")
    except Exception as e:
        print(f"WAL checkpoint note: {e}")

    # 2. Connect to destination backup database
    if backup_db_path.exists():
        backup_db_path.unlink()

    dest_conn = sqlite3.connect(str(backup_db_path))

    # 3. Perform native SQLite backup
    print("Executing sqlite3.Connection.backup()...")
    source_conn.backup(dest_conn, pages=100)
    print("Native backup completed successfully.")

    # 4. Close destination connection
    dest_conn.close()

    # 5. Independent Verification of Backup
    print("\n--- Independent Backup Verification ---")
    verify_conn = sqlite3.connect(str(backup_db_path))
    verify_cur = verify_conn.cursor()

    # Integrity Check
    integrity = verify_cur.execute("PRAGMA integrity_check").fetchall()
    print(f"Integrity check: {integrity}")
    assert integrity == [("ok",)], f"Backup integrity check failed: {integrity}"

    # Foreign Key Check
    fk_check = verify_cur.execute("PRAGMA foreign_key_check").fetchall()
    print(f"Foreign key violations count: {len(fk_check)}")
    if fk_check:
        print(f"Foreign key violations (first 5): {fk_check[:5]}")

    # Alembic Revision
    alembic_rev = verify_cur.execute("SELECT version_num FROM alembic_version").fetchone()
    print(f"Alembic revision in backup: {alembic_rev[0] if alembic_rev else 'NONE'}")

    # Compare Tables and Row Counts
    source_tables = [r[0] for r in source_cur.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name").fetchall()]
    backup_tables = [r[0] for r in verify_cur.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name").fetchall()]

    assert source_tables == backup_tables, f"Table list mismatch: {set(source_tables) ^ set(backup_tables)}"
    print(f"\nTable Count Matches: Exactly {len(backup_tables)} tables present in both.")

    print(f"{'Table Name':<30} | {'Source Count':<12} | {'Backup Count':<12} | {'Match'}")
    print("-" * 65)

    all_matched = True
    row_summary = {}
    for table in backup_tables:
        s_count = source_cur.execute(f'SELECT COUNT(*) FROM "{table}"').fetchone()[0]
        b_count = verify_cur.execute(f'SELECT COUNT(*) FROM "{table}"').fetchone()[0]
        match = (s_count == b_count)
        if not match:
            all_matched = False
        row_summary[table] = (s_count, b_count)
        print(f"{table:<30} | {s_count:<12} | {b_count:<12} | {'YES' if match else 'NO'}")

    assert all_matched, "Row count discrepancy detected between source and backup!"
    print("\n[SUCCESS] All table row counts match 100% exactly.")

    source_conn.close()
    verify_conn.close()

    print(f"Backup file size: {backup_db_path.stat().st_size} bytes")
    print("--- Gate 1 Verified Database Backup Complete ---\n")

if __name__ == "__main__":
    perform_verified_backup()
