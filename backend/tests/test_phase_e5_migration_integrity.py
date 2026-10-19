"""
Phase E.5: Migration Integrity Verification Test
Tests Alembic revision chain, upgrade(), downgrade(), and re-upgrade on an isolated temporary copy of the pre-migration backup.
Checks SQLite compatibility, FKs, unique constraints, and indexes.
Never modifies D:\\EduNavika\\edunavika.db or the immutable backup.
"""

import os
import sys
import shutil
import sqlite3
import hashlib
import pytest
from pathlib import Path

root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(root))

from alembic.config import Config
from alembic import command
from alembic.script import ScriptDirectory

EXPECTED_BACKUP_HASH = "5df476e628c08569bd093aafa5ac4a4b3cbc9a7c77b63d0ef558a791128327fd"
BACKUP_PATH = root / "backups" / "edunavika_pre_phase_f_20261019_153342.db"
PERSISTENT_DB_PATH = root / "edunavika.db"
EXPECTED_PERSISTENT_HASH = "4c1c2a274ddb09e13b6d698b9b05b4bd4c241b43df466e2321fc6a4d2e98059d"

def compute_sha256(filepath: Path) -> str:
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest().lower()

def test_migration_chain():
    print("--- 1. Inspecting Alembic Revision Chain ---")
    alembic_cfg = Config(str(root / "backend" / "alembic.ini"))
    alembic_cfg.set_main_option("script_location", str(root / "backend" / "alembic"))

    script = ScriptDirectory.from_config(alembic_cfg)
    heads = script.get_heads()
    print(f"Alembic Script Heads: {heads}")
    assert heads == ["a1b2c3d4e5f6"], f"Unexpected heads: {heads}"

    rev_a1b = script.get_revision("a1b2c3d4e5f6")
    print(f"Revision: {rev_a1b.revision}, Down Revision: {rev_a1b.down_revision}")
    assert rev_a1b.down_revision == "f1e2d3c4b5a6", f"Parent mismatch: {rev_a1b.down_revision}"

    rev_f1e = script.get_revision("f1e2d3c4b5a6")
    print(f"Revision: {rev_f1e.revision}, Down Revision: {rev_f1e.down_revision}")
    assert rev_f1e.down_revision == "e025394444f5"

    rev_e02 = script.get_revision("e025394444f5")
    print(f"Revision: {rev_e02.revision}, Down Revision: {rev_e02.down_revision}")
    assert rev_e02.down_revision == "7bc787ffc064"

    rev_7bc = script.get_revision("7bc787ffc064")
    print(f"Revision: {rev_7bc.revision}, Down Revision: {rev_7bc.down_revision}")
    assert rev_7bc.down_revision is None
    print("[PASSED] Revision chain is single-parent linear and unbroken.")

def test_upgrade_downgrade_sandbox(tmp_path: Path):
    print("\n--- 2. Testing Upgrade and Downgrade on Isolated Temporary Copy of Pre-Migration Backup ---")

    # 1. Verify immutable source backup exists and matches exact documented SHA-256
    if not BACKUP_PATH.exists():
        pytest.fail(f"Verified pre-migration backup file not found at: {BACKUP_PATH}")

    backup_hash_pre = compute_sha256(BACKUP_PATH)
    assert backup_hash_pre == EXPECTED_BACKUP_HASH, (
        f"Source backup hash mismatch! Expected {EXPECTED_BACKUP_HASH}, got {backup_hash_pre}"
    )
    print(f"[OK] Source backup verified at {BACKUP_PATH.name} (SHA-256: {backup_hash_pre})")

    # Record persistent database hash if present to ensure 0 mutations
    persistent_hash_pre = None
    if PERSISTENT_DB_PATH.exists():
        persistent_hash_pre = compute_sha256(PERSISTENT_DB_PATH)

    # 2. Copy the backup to a unique pytest temporary directory fixture
    sandbox_db = tmp_path / "sandbox_audit_migration.db"
    shutil.copy2(BACKUP_PATH, sandbox_db)
    assert sandbox_db.exists(), "Failed to create temporary sandbox database"
    print(f"[OK] Cloned pre-migration backup to temporary sandbox: {sandbox_db}")

    # 3. Configure Alembic with strict URL targeting only the temporary sandbox
    sandbox_url = f"sqlite:///{sandbox_db.as_posix()}"
    old_env = os.environ.get("DATABASE_URL")
    os.environ["DATABASE_URL"] = sandbox_url

    alembic_cfg = Config(str(root / "backend" / "alembic.ini"))
    alembic_cfg.set_main_option("script_location", str(root / "backend" / "alembic"))
    alembic_cfg.set_main_option("sqlalchemy.url", sandbox_url)

    # Ensure safe isolation before executing any migration commands
    assert sandbox_url != old_env, "Sandbox URL must not match persistent database URL"

    try:
        # 4. Verify initial revision in sandbox is the pre-migration baseline f1e2d3c4b5a6
        conn = sqlite3.connect(sandbox_db)
        cur = conn.cursor()
        v_init = cur.execute("SELECT version_num FROM alembic_version").fetchone()[0]
        cur.execute("PRAGMA integrity_check;")
        assert cur.fetchall() == [("ok",)], "Sandbox initial integrity check failed"
        cur.execute("PRAGMA foreign_key_check;")
        assert cur.fetchall() == [], "Sandbox initial foreign key check failed"
        conn.close()
        print(f"  [OK] Initial sandbox revision verified: {v_init}")
        assert v_init == "f1e2d3c4b5a6", f"Sandbox expected f1e2d3c4b5a6, got {v_init}"

        # 5. Test UPGRADE to a1b2c3d4e5f6 on isolated copy
        print("Executing upgrade to a1b2c3d4e5f6 on isolated copy...")
        command.upgrade(alembic_cfg, "a1b2c3d4e5f6")

        conn = sqlite3.connect(sandbox_db)
        cur = conn.cursor()
        v_up = cur.execute("SELECT version_num FROM alembic_version").fetchone()[0]
        tables_up = [r[0] for r in cur.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
        cols_up = [r[1] for r in cur.execute("PRAGMA table_info(exam_topics)").fetchall()]
        idxs_up = [r[1] for r in cur.execute("PRAGMA index_list(exam_topics)").fetchall()]
        cur.execute("PRAGMA integrity_check;")
        assert cur.fetchall() == [("ok",)], "Post-upgrade integrity check failed"
        cur.execute("PRAGMA foreign_key_check;")
        assert cur.fetchall() == [], "Post-upgrade foreign key check failed"
        conn.close()

        assert v_up == "a1b2c3d4e5f6", f"Upgrade failed, version is {v_up}"
        assert "exam_topics" in tables_up, "exam_topics table missing!"
        for req_col in ["id", "exam_code", "topic_id", "curriculum_role", "inclusion_status", "verification_status", "created_at"]:
            assert req_col in cols_up, f"Column {req_col} missing in exam_topics"
        for req_idx in ["ix_exam_topics_exam_code", "ix_exam_topics_topic_id", "idx_exam_topics_lookup"]:
            assert req_idx in idxs_up, f"Index {req_idx} missing on exam_topics"
        print("  [OK] Upgrade applied cleanly: revision a1b2c3d4e5f6, table, columns, and indexes verified.")

        # 6. Test DOWNGRADE to f1e2d3c4b5a6
        print("Executing downgrade to f1e2d3c4b5a6 on isolated copy...")
        command.downgrade(alembic_cfg, "f1e2d3c4b5a6")

        conn = sqlite3.connect(sandbox_db)
        cur = conn.cursor()
        v_down = cur.execute("SELECT version_num FROM alembic_version").fetchone()[0]
        tables_down = [r[0] for r in cur.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
        cur.execute("PRAGMA integrity_check;")
        assert cur.fetchall() == [("ok",)], "Post-downgrade integrity check failed"
        cur.execute("PRAGMA foreign_key_check;")
        assert cur.fetchall() == [], "Post-downgrade foreign key check failed"
        conn.close()

        assert v_down == "f1e2d3c4b5a6", f"Downgrade failed, version is {v_down}"
        assert "exam_topics" not in tables_down, "exam_topics table still present after downgrade!"
        print("  [OK] Downgrade applied cleanly: version reverted, table dropped.")

        # 7. Test RE-UPGRADE to a1b2c3d4e5f6
        print("Executing re-upgrade to a1b2c3d4e5f6 on isolated copy...")
        command.upgrade(alembic_cfg, "a1b2c3d4e5f6")

        conn = sqlite3.connect(sandbox_db)
        cur = conn.cursor()
        v_reup = cur.execute("SELECT version_num FROM alembic_version").fetchone()[0]
        tables_reup = [r[0] for r in cur.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
        cur.execute("PRAGMA integrity_check;")
        assert cur.fetchall() == [("ok",)], "Post-reupgrade integrity check failed"
        cur.execute("PRAGMA foreign_key_check;")
        assert cur.fetchall() == [], "Post-reupgrade foreign key check failed"
        conn.close()

        assert v_reup == "a1b2c3d4e5f6"
        assert "exam_topics" in tables_reup
        print("  [OK] Re-upgrade succeeded cleanly: revision is a1b2c3d4e5f6, table recreated.")

    finally:
        # Restore environment variable
        if old_env is not None:
            os.environ["DATABASE_URL"] = old_env
        else:
            os.environ.pop("DATABASE_URL", None)

    # 8. Verify the immutable backup hash remains completely unchanged
    backup_hash_post = compute_sha256(BACKUP_PATH)
    assert backup_hash_post == EXPECTED_BACKUP_HASH, (
        f"CRITICAL: Immutable backup was modified! Expected {EXPECTED_BACKUP_HASH}, got {backup_hash_post}"
    )
    print(f"[PASSED] Immutable backup hash verified unchanged: {backup_hash_post}")

    # 9. Verify persistent database was not touched
    if persistent_hash_pre is not None and PERSISTENT_DB_PATH.exists():
        persistent_hash_post = compute_sha256(PERSISTENT_DB_PATH)
        assert persistent_hash_post == persistent_hash_pre, "CRITICAL: Persistent database was modified during migration test!"
        print(f"[PASSED] Persistent DB hash verified unchanged: {persistent_hash_post}")

if __name__ == "__main__":
    test_migration_chain()
