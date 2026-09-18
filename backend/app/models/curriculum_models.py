"""
Curriculum & Content database models: Standard, Subject, Chapter, Topic, LearningContent.
"""

from sqlalchemy import Column, String, Integer, Text, Boolean, Enum as SQLEnum, ForeignKey, JSON, UniqueConstraint, CheckConstraint
from sqlalchemy.orm import relationship

from backend.app.core.database import Base
from backend.app.models.core_models import BaseModelMixin
from backend.app.domain.enums import ContentType

__all__ = ["Standard", "Subject", "Chapter", "Topic", "LearningContent", "ContentType"]


class Standard(BaseModelMixin, Base):
    """School grade level (e.g. Standard 9, 10, 11, 12)."""
    __tablename__ = "standards"
    __table_args__ = (
        CheckConstraint("grade_number >= 1 AND grade_number <= 12", name="chk_standard_grade_number_range"),
    )

    grade_number = Column(Integer, unique=True, index=True, nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)

    # Relationships
    subjects = relationship("Subject", back_populates="standard", cascade="all, delete-orphan")
    students = relationship("StudentProfile", back_populates="standard")


class Subject(BaseModelMixin, Base):
    """Academic subject under a Standard (e.g. Mathematics, Science)."""
    __tablename__ = "subjects"
    __table_args__ = (
        UniqueConstraint("standard_id", "code", name="uq_subject_standard_code"),
    )

    standard_id = Column(String(36), ForeignKey("standards.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(150), nullable=False)
    code = Column(String(50), nullable=False, index=True)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)

    # Relationships
    standard = relationship("Standard", back_populates="subjects")
    chapters = relationship("Chapter", back_populates="subject", cascade="all, delete-orphan")


class Chapter(BaseModelMixin, Base):
    """Textbook chapter under a Subject."""
    __tablename__ = "chapters"
    __table_args__ = (
        UniqueConstraint("subject_id", "chapter_number", name="uq_chapter_subject_order"),
        CheckConstraint("chapter_number >= 1", name="chk_chapter_number_positive"),
    )

    subject_id = Column(String(36), ForeignKey("subjects.id", ondelete="CASCADE"), nullable=False, index=True)
    chapter_number = Column(Integer, nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    source_reference = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)

    # Relationships
    subject = relationship("Subject", back_populates="chapters")
    topics = relationship("Topic", back_populates="chapter", cascade="all, delete-orphan")


class Topic(BaseModelMixin, Base):
    """Subtopic within a Chapter."""
    __tablename__ = "topics"
    __table_args__ = (
        UniqueConstraint("chapter_id", "topic_order", name="uq_topic_chapter_order"),
        CheckConstraint("topic_order >= 1", name="chk_topic_order_positive"),
    )

    chapter_id = Column(String(36), ForeignKey("chapters.id", ondelete="CASCADE"), nullable=False, index=True)
    topic_order = Column(Integer, nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    learning_objectives = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)

    # Relationships
    chapter = relationship("Chapter", back_populates="topics")
    learning_contents = relationship("LearningContent", back_populates="topic", cascade="all, delete-orphan")
    mcqs = relationship("MCQQuestion", back_populates="topic", cascade="all, delete-orphan")
    learning_events = relationship("LearningEvent", back_populates="topic", cascade="all, delete-orphan")
    topic_performances = relationship("TopicPerformance", back_populates="topic", cascade="all, delete-orphan")
    revision_plans = relationship("RevisionPlan", back_populates="topic", cascade="all, delete-orphan")
    forgetting_signals = relationship("ForgettingSignal", back_populates="topic", cascade="all, delete-orphan")
    teacher_actions = relationship("TeacherAction", back_populates="topic", cascade="all, delete-orphan")


class LearningContent(BaseModelMixin, Base):
    """Granular chunk of textbook learning material with exact page provenance."""
    __tablename__ = "learning_contents"
    __table_args__ = (
        CheckConstraint("source_page IS NULL OR source_page >= 1", name="chk_content_source_page_positive"),
    )

    topic_id = Column(String(36), ForeignKey("topics.id", ondelete="CASCADE"), nullable=False, index=True)
    content_type = Column(SQLEnum(ContentType), default=ContentType.TEXT, nullable=False)
    title = Column(String(255), nullable=False)
    content_text = Column(Text, nullable=False)
    source_document = Column(String(255), nullable=True, index=True)
    source_page = Column(Integer, nullable=True)
    source_reference = Column(String(255), nullable=True)
    chunk_identifier = Column(String(100), nullable=True, index=True)
    content_metadata = Column(JSON, nullable=True)

    # Relationships
    topic = relationship("Topic", back_populates="learning_contents")
    derived_mcqs = relationship("MCQQuestion", back_populates="source_content")
