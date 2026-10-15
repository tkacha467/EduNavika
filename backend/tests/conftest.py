import os
import tempfile
import atexit
import sqlite3
import hashlib
import pytest
from sqlalchemy import create_engine, event, Engine, text
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

# ---------------------------------------------------------------------------
# 1. Early Environment Injection & Disposable Database Lifecycle
# ---------------------------------------------------------------------------
_TEST_DB_FILE = tempfile.NamedTemporaryFile(suffix=".db", prefix="edunavika_test_", delete=False)
TEST_DB_PATH = os.path.realpath(_TEST_DB_FILE.name)
_TEST_DB_FILE.close()
TEST_DATABASE_URL = f"sqlite:///{TEST_DB_PATH}"

# Force test database URL in environment before application modules load
os.environ["DATABASE_URL"] = TEST_DATABASE_URL
os.environ["ENV"] = "testing"

# Target persistent DB path to guard (canonical realpath)
PERSISTENT_DB_PATH = os.path.realpath(r"D:\EduNavika\edunavika.db").lower()

# ---------------------------------------------------------------------------
# 2. Hard Persistent Database Access Blocker Guard
# ---------------------------------------------------------------------------
@event.listens_for(Engine, "connect")
def guard_against_persistent_db(dbapi_connection, connection_record):
    """
    Prevents ANY database connection from touching the persistent development DB.
    Inspects PRAGMA database_list on every newly opened connection and raises
    RuntimeError immediately if the path points to edunavika.db.
    """
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA database_list")
    for row in cursor.fetchall():
        db_file = row[2]
        if db_file:
            real_file = os.path.realpath(db_file).lower()
            if real_file == PERSISTENT_DB_PATH or (real_file.endswith("edunavika.db") and "test" not in real_file):
                cursor.close()
                raise RuntimeError(
                    f"DATABASE ISOLATION VIOLATION: Test process attempted to open connection "
                    f"to persistent development database: {db_file}"
                )
    cursor.close()

# ---------------------------------------------------------------------------
# 3. Test Engine & Session Creation
# ---------------------------------------------------------------------------
test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    future=True
)

@event.listens_for(test_engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.execute("PRAGMA busy_timeout=30000")
    cursor.close()

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine, future=True)

# ---------------------------------------------------------------------------
# 4. Central Rebinding of Application Database Symbols
# ---------------------------------------------------------------------------
import backend.app.models  # Ensure all SQLAlchemy models are registered with Base.metadata
from backend.app.core.database import Base, get_db
import backend.app.core.database as app_db
import backend.app.core.config as app_config
import backend.app.main as app_main
from backend.app.main import app
from backend.app.models import User, StudentProfile, TeacherProfile, UserRole
from backend.app.models import Standard, Subject, Chapter, Topic

# Redirect core database symbols so direct imports resolve to isolated test DB
app_config.settings.DATABASE_URL = TEST_DATABASE_URL
app_db.engine = test_engine
app_db.SessionLocal = TestingSessionLocal
app_main.engine = test_engine
app_main.SessionLocal = TestingSessionLocal

# Also ensure default FastAPI dependency override
def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

# ---------------------------------------------------------------------------
# 5. Global Cleanup Hook for Disposable Database File
# ---------------------------------------------------------------------------
def _cleanup_test_db():
    try:
        test_engine.dispose()
    except Exception:
        pass
    for path in [TEST_DB_PATH, f"{TEST_DB_PATH}-wal", f"{TEST_DB_PATH}-shm"]:
        if os.path.exists(path):
            try:
                os.unlink(path)
            except Exception:
                pass

atexit.register(_cleanup_test_db)

# ---------------------------------------------------------------------------
# 6. Persistent Database Invariant Monitor Fixture
# ---------------------------------------------------------------------------
def _get_persistent_db_state():
    """Inspects persistent development DB via raw read-only connection without mutating."""
    if not os.path.exists(PERSISTENT_DB_PATH):
        return None
    with open(PERSISTENT_DB_PATH, "rb") as f:
        file_bytes = f.read()
    sha256 = hashlib.sha256(file_bytes).hexdigest()
    size = len(file_bytes)

    conn = sqlite3.connect(f"file:{PERSISTENT_DB_PATH}?mode=ro", uri=True)
    c = conn.cursor()
    c.execute("PRAGMA integrity_check")
    integrity = c.fetchall()
    c.execute("PRAGMA foreign_key_check")
    fk_check = c.fetchall()
    c.execute("SELECT version_num FROM alembic_version")
    rev = [r[0] for r in c.fetchall()]
    c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name")
    tables = [r[0] for r in c.fetchall()]
    counts = {}
    for t in tables:
        c.execute(f'SELECT count(*) FROM "{t}"')
        counts[t] = c.fetchone()[0]
    conn.close()
    return {
        "sha256": sha256,
        "size": size,
        "integrity": integrity,
        "foreign_keys": fk_check,
        "alembic_version": rev,
        "row_counts": counts,
    }


@pytest.fixture(scope="session", autouse=True)
def persistent_database_guard_session():
    """Session-scoped fixture verifying D:\\EduNavika\\edunavika.db is never mutated by test suite."""
    baseline = _get_persistent_db_state()
    yield
    post = _get_persistent_db_state()
    if baseline and post:
        assert baseline["sha256"] == post["sha256"], (
            f"Persistent database SHA-256 changed during tests!\n"
            f"Before: {baseline['sha256']}\nAfter:  {post['sha256']}"
        )
        assert baseline["row_counts"] == post["row_counts"], (
            f"Persistent database row counts changed during tests!\n"
            f"Diff: {set(post['row_counts'].items()) - set(baseline['row_counts'].items())}"
        )


# ---------------------------------------------------------------------------
# 7. Pre-test Schema Ensure Fixture
# ---------------------------------------------------------------------------
@pytest.fixture(autouse=True)
def ensure_db_schema():
    """Ensure all tables exist in test database prior to each test."""
    Base.metadata.create_all(bind=test_engine)
    yield


@pytest.fixture(scope="session")
def isolated_db_info():
    """Provides test and persistent DB paths and inspection utilities to isolation tests."""
    return {
        "test_engine": test_engine,
        "test_db_path": TEST_DB_PATH,
        "persistent_db_path": PERSISTENT_DB_PATH,
        "get_persistent_db_state": _get_persistent_db_state,
        "TestingSessionLocal": TestingSessionLocal,
    }


@pytest.fixture(scope="function")
def db_session():
    """Provides a clean database schema and session per test."""
    Base.metadata.create_all(bind=test_engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        # Clean up rows rather than dropping tables, avoiding SQLite schema cache churn
        with test_engine.begin() as conn:
            for table in reversed(Base.metadata.sorted_tables):
                try:
                    conn.execute(table.delete())
                except Exception:
                    pass


@pytest.fixture(scope="function")
def client(db_session):
    """FastAPI TestClient with overridden get_db dependency."""
    def _override():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = _override
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides[get_db] = override_get_db


@pytest.fixture
def seed_data(db_session):
    """Common fixture providing pre-seeded hierarchy: Teacher, Student, Standard 10, Subject, Chapter, Topic."""
    # 1. Teacher User & Profile
    teacher_user = User(
        name="Prof. Sharma",
        email="sharma@edunavika.org",
        hashed_password="hashed_pw_test",
        role=UserRole.TEACHER,
        is_active=True,
    )
    db_session.add(teacher_user)
    db_session.flush()

    teacher_profile = TeacherProfile(
        user_id=teacher_user.id,
        employee_id="T-1001",
    )
    db_session.add(teacher_profile)

    # 2. Student User & Profile
    student_user = User(
        name="Aarav Patel",
        email="aarav@edunavika.org",
        hashed_password="hashed_pw_test",
        role=UserRole.STUDENT,
        is_active=True,
    )
    db_session.add(student_user)
    db_session.flush()

    student_profile = StudentProfile(
        user_id=student_user.id,
        division="A",
        enrollment_number="ST-2026-09",
    )
    db_session.add(student_profile)

    # 3. Standard
    standard = Standard(
        grade_number=10,
        name="Standard 10",
        description="GSEB Secondary Certificate Class 10",
    )
    db_session.add(standard)
    db_session.flush()

    student_profile.standard_id = standard.id

    # 4. Subject
    subject = Subject(
        standard_id=standard.id,
        name="Science",
        code="SCI-10",
        description="GSEB Standard 10 Science",
    )
    db_session.add(subject)
    db_session.flush()

    # 5. Chapter
    chapter = Chapter(
        subject_id=subject.id,
        chapter_number=1,
        title="Chemical Reactions and Equations",
        source_reference="Std-10_Science_English Medium.pdf",
    )
    db_session.add(chapter)
    db_session.flush()

    # 6. Topic
    topic = Topic(
        chapter_id=chapter.id,
        topic_order=1,
        title="Types of Chemical Reactions",
        learning_objectives="Identify combination, decomposition, displacement, and double displacement reactions.",
    )
    db_session.add(topic)
    db_session.commit()

    return {
        "teacher_user": teacher_user,
        "teacher_profile": teacher_profile,
        "student_user": student_user,
        "student_profile": student_profile,
        "standard": standard,
        "subject": subject,
        "chapter": chapter,
        "topic": topic,
    }
