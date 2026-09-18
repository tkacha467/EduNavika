import pytest
from sqlalchemy import create_engine, event
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

import backend.app.models  # Ensure all SQLAlchemy models are registered with Base.metadata
from backend.app.core.database import Base, get_db
from backend.app.main import app
from backend.app.models import User, StudentProfile, TeacherProfile, UserRole
from backend.app.models import Standard, Subject, Chapter, Topic

# Single shared in-memory SQLite database using StaticPool
test_engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
    future=True
)

# Enforce SQLite foreign keys
@event.listens_for(test_engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine, future=True)


@pytest.fixture(scope="function")
def db_session():
    """Provides a clean database schema and session per test."""
    Base.metadata.create_all(bind=test_engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=test_engine)


@pytest.fixture(scope="function")
def client(db_session):
    """FastAPI TestClient with overridden get_db dependency."""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


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
