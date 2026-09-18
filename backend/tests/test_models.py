import pytest
from sqlalchemy.exc import IntegrityError
from backend.app.models import User, StudentProfile, TeacherProfile, UserRole
from backend.app.models import Standard, Subject, Chapter, Topic
from backend.app.models import LearningContent, ContentType
from backend.app.models import MCQQuestion, QuestionHistory, QuestionStatus, QuestionDifficulty, OptionKey


def test_create_user_and_profiles(db_session):
    user = User(
        name="Test Student",
        email="student1@test.com",
        hashed_password="pw",
        role=UserRole.STUDENT,
    )
    db_session.add(user)
    db_session.commit()

    assert user.id is not None
    assert user.created_at is not None
    assert user.role == UserRole.STUDENT

    profile = StudentProfile(user_id=user.id, division="B")
    db_session.add(profile)
    db_session.commit()

    assert profile.id is not None
    assert profile.user.email == "student1@test.com"


def test_unique_email_constraint(db_session):
    u1 = User(name="User 1", email="same@test.com", hashed_password="pw", role=UserRole.STUDENT)
    u2 = User(name="User 2", email="same@test.com", hashed_password="pw", role=UserRole.STUDENT)
    db_session.add(u1)
    db_session.commit()

    db_session.add(u2)
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()


def test_curriculum_hierarchy_and_cascade(db_session, seed_data):
    standard = seed_data["standard"]
    subject = seed_data["subject"]
    chapter = seed_data["chapter"]
    topic = seed_data["topic"]

    assert topic.chapter.subject.standard.grade_number == 10

    # Add content to topic
    content = LearningContent(
        topic_id=topic.id,
        content_type=ContentType.DEFINITION,
        title="Combination Reaction Definition",
        content_text="A reaction in which a single product is formed from two or more reactants.",
        source_document="Std-10_Science_English Medium.pdf",
        source_page=6,
        chunk_identifier="std10_sci_ch1_chunk_004",
    )
    db_session.add(content)
    db_session.commit()

    assert content.id is not None
    assert content.topic.title == "Types of Chemical Reactions"

    # Verify cascade delete
    db_session.delete(chapter)
    db_session.commit()

    # Topic and its content should be deleted
    assert db_session.query(Topic).filter(Topic.id == topic.id).first() is None
    assert db_session.query(LearningContent).filter(LearningContent.id == content.id).first() is None


def test_foreign_key_enforcement(db_session):
    # Creating a subject with non-existent standard_id should fail
    bad_subject = Subject(
        standard_id="non-existent-uuid",
        name="Bad Subject",
        code="BAD-01"
    )
    db_session.add(bad_subject)
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()
