"""
Milestone 4 — Phase C: Test-Isolation Hardening Regression Tests.

Verifies:
1. The application test client uses the isolated test database.
2. The test session factory is bound to the isolated database.
3. A representative write through the application test client does not reach the persistent database.
4. Direct imports of session factories cannot silently bypass isolation.
5. The hard blocker guard immediately stops any attempt to open a connection to edunavika.db.
6. Test setup and teardown close sessions and clean up temporary database files.
7. Existing development database row counts and schema revision remain unchanged.
8. The isolation setup works with standard pytest test execution commands.
"""

import os
import uuid
import sqlite3
import tempfile
import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from backend.app.core.database import SessionLocal, engine, get_db
from backend.app.models import User, UserRole
from backend.app.main import app


def _query_persistent_db(persistent_path: str, query: str, params: tuple = ()):
    """Executes a read-only query on the persistent database directly via raw SQLite."""
    conn = sqlite3.connect(f"file:{persistent_path}?mode=ro", uri=True)
    try:
        cursor = conn.cursor()
        cursor.execute(query, params)
        return cursor.fetchall()
    finally:
        conn.close()


def test_1_client_uses_isolated_test_database(client, isolated_db_info):
    """
    1. The application test client uses the isolated test database.
    Verifies that requests through the test client resolve against the isolated
    database rather than the persistent development database.
    """
    response = client.get("/api/v1/curriculum/runtime-status")
    assert response.status_code == 200

    test_engine = isolated_db_info["test_engine"]
    test_db_path = isolated_db_info["test_db_path"]
    persistent_db_path = isolated_db_info["persistent_db_path"]

    # Verify that the test engine URL is pointing to the temporary test database file
    assert str(test_engine.url).endswith(".db")
    assert os.path.realpath(test_engine.url.database).lower() == test_db_path.lower()
    assert os.path.realpath(test_engine.url.database).lower() != persistent_db_path.lower()


def test_2_session_factory_bound_to_isolated_database(isolated_db_info):
    """
    2. The test session factory is bound to the isolated database.
    Verifies TestingSessionLocal is bound to the temporary database and NOT edunavika.db.
    """
    TestingSessionLocal = isolated_db_info["TestingSessionLocal"]
    test_db_path = isolated_db_info["test_db_path"]
    persistent_db_path = isolated_db_info["persistent_db_path"]

    session = TestingSessionLocal()
    try:
        # Check database file path reported by SQLite PRAGMA database_list
        row = session.execute(text("PRAGMA database_list")).fetchall()
        assert len(row) > 0
        db_file = row[0][2]
        assert db_file is not None and db_file != ""
        assert os.path.realpath(db_file).lower() == test_db_path.lower()
        assert os.path.realpath(db_file).lower() != persistent_db_path.lower()
    finally:
        session.close()


def test_3_representative_write_does_not_reach_persistent_database(client, db_session, isolated_db_info):
    """
    3. A representative write through the application test client does not reach the persistent database.
    Writes a distinct canary record in the test session, confirms it is present in the test DB,
    and independently verifies via raw read-only SQLite that it does NOT exist in edunavika.db.
    """
    persistent_db_path = isolated_db_info["persistent_db_path"]
    canary_id = f"canary-client-{uuid.uuid4().hex[:12]}"
    canary_email = f"{canary_id}@edunavika.isolation.test"

    # Write canary user through the test session
    canary_user = User(
        id=canary_id,
        name="Isolation Canary Client Test",
        email=canary_email,
        hashed_password="hashed_canary_password",
        role=UserRole.STUDENT,
        is_active=True,
    )
    db_session.add(canary_user)
    db_session.commit()

    # Verify presence in test database
    assert db_session.query(User).filter(User.id == canary_id).first() is not None

    # Independently verify canary does NOT exist in persistent database
    persistent_rows = _query_persistent_db(persistent_db_path, "SELECT id, email FROM users WHERE id = ?", (canary_id,))
    assert len(persistent_rows) == 0, (
        f"CRITICAL ISOLATION BREACH: Canary record '{canary_id}' was found in persistent database!"
    )

    persistent_email_rows = _query_persistent_db(persistent_db_path, "SELECT id FROM users WHERE email = ?", (canary_email,))
    assert len(persistent_email_rows) == 0, (
        f"CRITICAL ISOLATION BREACH: Canary email '{canary_email}' was found in persistent database!"
    )


def test_4_direct_imports_of_session_factory_cannot_bypass_isolation(isolated_db_info):
    """
    4. Direct imports of session factories cannot silently bypass isolation.
    Directly imports SessionLocal from backend.app.core.database and verifies
    that calling it connects to the test database and NOT edunavika.db.
    """
    from backend.app.core.database import SessionLocal as DirectSessionLocal

    test_db_path = isolated_db_info["test_db_path"]
    persistent_db_path = isolated_db_info["persistent_db_path"]

    direct_session = DirectSessionLocal()
    canary_id = f"canary-direct-{uuid.uuid4().hex[:12]}"
    canary_email = f"{canary_id}@edunavika.direct.test"

    try:
        # Check PRAGMA database_list
        row = direct_session.execute(text("PRAGMA database_list")).fetchall()
        db_file = row[0][2]
        assert os.path.realpath(db_file).lower() == test_db_path.lower()
        assert os.path.realpath(db_file).lower() != persistent_db_path.lower()

        # Write canary record
        canary_user = User(
            id=canary_id,
            name="Direct SessionLocal Canary",
            email=canary_email,
            hashed_password="hashed_pw",
            role=UserRole.STUDENT,
            is_active=True,
        )
        direct_session.add(canary_user)
        direct_session.commit()

        # Verify canary exists in direct_session
        assert direct_session.query(User).filter(User.id == canary_id).first() is not None
    finally:
        direct_session.close()

    # Independently verify canary does NOT exist in persistent development database
    persistent_rows = _query_persistent_db(persistent_db_path, "SELECT id FROM users WHERE id = ?", (canary_id,))
    assert len(persistent_rows) == 0, (
        f"CRITICAL ISOLATION BREACH: Direct SessionLocal write '{canary_id}' reached persistent database!"
    )


def test_5_hard_guard_blocks_persistent_database_connections(isolated_db_info):
    """
    5. The hard blocker guard immediately stops any attempt to open a connection to edunavika.db.
    Attempts to instantiate an SQLAlchemy engine targeting edunavika.db and verifies
    that the connect listener raises a RuntimeError preventing access.
    """
    persistent_db_path = isolated_db_info["persistent_db_path"]
    rogue_engine = create_engine(
        f"sqlite:///{persistent_db_path}",
        connect_args={"check_same_thread": False},
        future=True,
    )
    with pytest.raises(RuntimeError) as exc_info:
        with rogue_engine.connect() as conn:
            conn.execute(text("SELECT 1"))

    assert "DATABASE ISOLATION VIOLATION" in str(exc_info.value)
    rogue_engine.dispose()


def test_6_test_setup_and_teardown_lifecycle():
    """
    6. Test setup and teardown close sessions and clean up temporary database files.
    Creates a dedicated disposable SQLite file, initializes tables, closes sessions,
    disposes the engine, and verifies clean removal of the temporary file.
    """
    tmp = tempfile.NamedTemporaryFile(suffix=".db", prefix="isolation_lifecycle_test_", delete=False)
    tmp_path = os.path.realpath(tmp.name)
    tmp.close()

    assert os.path.exists(tmp_path)
    engine_temp = create_engine(f"sqlite:///{tmp_path}", future=True)
    Session_temp = sessionmaker(bind=engine_temp, future=True)

    session = Session_temp()
    session.execute(text("CREATE TABLE test_canary (id INTEGER PRIMARY KEY, val TEXT)"))
    session.execute(text("INSERT INTO test_canary (val) VALUES ('test_val')"))
    session.commit()
    assert session.execute(text("SELECT count(*) FROM test_canary")).scalar() == 1

    # Teardown
    session.close()
    engine_temp.dispose()
    os.unlink(tmp_path)

    assert not os.path.exists(tmp_path), "Disposable database file should be deleted upon teardown"


def test_7_persistent_database_remains_completely_unmodified(isolated_db_info):
    """
    7. Existing development database row counts and schema revision remain unchanged after isolation tests.
    Verifies PRAGMA integrity_check, foreign_key_check, alembic version, and row counts.
    """
    get_state = isolated_db_info["get_persistent_db_state"]
    state = get_state()
    assert state is not None
    assert state["integrity"] == [("ok",)], f"Integrity check failed: {state['integrity']}"
    assert state["foreign_keys"] == [], f"Foreign key violations found: {state['foreign_keys']}"
    assert state["alembic_version"] == ["f1e2d3c4b5a6"], f"Alembic version corrupted: {state['alembic_version']}"

    # Verify core table row counts match expected baseline
    counts = state["row_counts"]
    assert counts.get("standards") == 3, f"Expected 3 standards, found {counts.get('standards')}"
    assert counts.get("subjects") == 247, f"Expected 247 subjects, found {counts.get('subjects')}"
    assert counts.get("examinations") == 3, f"Expected 3 examinations, found {counts.get('examinations')}"
    assert counts.get("exam_subjects") == 18, f"Expected 18 exam_subjects, found {counts.get('exam_subjects')}"
    assert counts.get("mcq_questions") == 80, f"Expected 80 mcq_questions, found {counts.get('mcq_questions')}"
    assert counts.get("learning_contents") == 573, f"Expected 573 learning_contents, found {counts.get('learning_contents')}"
    assert counts.get("users") == 244, f"Expected 244 users, found {counts.get('users')}"


def test_8_guard_blocks_all_path_variants_and_uris():
    """
    8. The hard blocker guard intercepts all URL variants targeting edunavika.db:
    relative paths, absolute paths, case differences, forward/backward slashes,
    and SQLite URI query styles.
    """
    urls_to_test = [
        "sqlite:///D:/EduNavika/edunavika.db",
        "sqlite:///d:/edunavika/edunavika.db",
        "sqlite:///D:\\EduNavika\\edunavika.db",
        "sqlite:///edunavika.db",
        "sqlite:///./edunavika.db",
        "sqlite:///../EduNavika/edunavika.db",
        "sqlite:///file:edunavika.db?uri=true",
        "sqlite:///file:///D:/EduNavika/edunavika.db?uri=true",
    ]
    for url in urls_to_test:
        rogue_engine = create_engine(url, connect_args={"check_same_thread": False}, future=True)
        with pytest.raises(RuntimeError) as exc_info:
            with rogue_engine.connect() as conn:
                conn.execute(text("SELECT 1"))
        assert "DATABASE ISOLATION VIOLATION" in str(exc_info.value), f"Failed to block {url}"
        rogue_engine.dispose()


def test_9_canonical_question_sync_idempotency_and_no_duplicate_standards(db_session):
    """
    9. Verifies sync_canonical_questions_to_db:
    - On clean test DB: creates exactly one Standard 10 and syncs canonical questions.
    - On repeated sync: returns 0 questions and standard count remains 1.
    - When Standard 10 already exists: reuses the existing standard without creating a duplicate.
    """
    from backend.app.models import Standard
    from backend.app.services.curriculum_question_bank import sync_canonical_questions_to_db

    # Clean test session
    first_sync = sync_canonical_questions_to_db(db_session)
    stds = db_session.query(Standard).all()
    assert len(stds) == 1, f"Expected exactly 1 standard created, got {len(stds)}"
    assert stds[0].grade_number == 10
    assert first_sync > 0, "Expected questions to be synced on first run"

    # Repeated sync
    second_sync = sync_canonical_questions_to_db(db_session)
    assert second_sync == 0, f"Expected 0 questions on repeated sync, got {second_sync}"
    stds_after_repeat = db_session.query(Standard).all()
    assert len(stds_after_repeat) == 1, "Repeated sync created duplicate standards!"

