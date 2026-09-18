"""
Assessment database models: Questions, History, Assessments, Attempts, and Answers.
"""

from sqlalchemy import Column, String, Integer, Float, Boolean, Text, DateTime, JSON, Enum as SQLEnum, ForeignKey, UniqueConstraint, CheckConstraint
from sqlalchemy.orm import relationship

from backend.app.core.database import Base
from backend.app.models.core_models import BaseModelMixin, get_utc_now
from backend.app.domain.enums import QuestionStatus, QuestionDifficulty, OptionKey, AssessmentStatus, AttemptStatus

__all__ = [
    "MCQQuestion",
    "QuestionHistory",
    "QuestionStatus",
    "QuestionDifficulty",
    "OptionKey",
    "Assessment",
    "AssessmentQuestion",
    "AssessmentStatus",
    "Attempt",
    "Answer",
    "AttemptStatus",
]


class MCQQuestion(BaseModelMixin, Base):
    """Multiple Choice Question with 4 options and verified syllabus grounding."""
    __tablename__ = "mcq_questions"

    topic_id = Column(String(36), ForeignKey("topics.id", ondelete="CASCADE"), nullable=False, index=True)
    question_text = Column(Text, nullable=False)
    option_a = Column(Text, nullable=False)
    option_b = Column(Text, nullable=False)
    option_c = Column(Text, nullable=False)
    option_d = Column(Text, nullable=False)
    correct_option = Column(SQLEnum(OptionKey), nullable=False)
    explanation = Column(Text, nullable=True)
    difficulty = Column(SQLEnum(QuestionDifficulty), default=QuestionDifficulty.MEDIUM, nullable=False)
    
    # Provenance tracking
    source_content_id = Column(String(36), ForeignKey("learning_contents.id", ondelete="SET NULL"), nullable=True, index=True)
    generation_model = Column(String(100), nullable=True)
    generation_version = Column(String(50), nullable=True)
    status = Column(SQLEnum(QuestionStatus), default=QuestionStatus.DRAFT, nullable=False, index=True)

    # Relationships
    topic = relationship("Topic", back_populates="mcqs")
    source_content = relationship("LearningContent", back_populates="derived_mcqs")
    history = relationship("QuestionHistory", back_populates="question", uselist=False, cascade="all, delete-orphan")
    assessment_links = relationship("AssessmentQuestion", back_populates="question", cascade="all, delete-orphan")
    answers = relationship("Answer", back_populates="question")


class QuestionHistory(BaseModelMixin, Base):
    """Deduplication and vector embedding reference for generated questions."""
    __tablename__ = "question_history"

    question_id = Column(String(36), ForeignKey("mcq_questions.id", ondelete="CASCADE"), unique=True, index=True, nullable=False)
    normalized_question_text = Column(Text, nullable=False)
    text_hash = Column(String(64), index=True, nullable=False)  # SHA-256 hex digest
    embedding_reference = Column(String(255), nullable=True)     # Pointer to vector storage
    generation_metadata = Column(JSON, nullable=True)

    # Relationships
    question = relationship("MCQQuestion", back_populates="history")


class Assessment(BaseModelMixin, Base):
    """Teacher-curated or automated assessment package."""
    __tablename__ = "assessments"

    teacher_id = Column(String(36), ForeignKey("teacher_profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    topic_id = Column(String(36), ForeignKey("topics.id", ondelete="SET NULL"), nullable=True, index=True)
    status = Column(SQLEnum(AssessmentStatus), default=AssessmentStatus.DRAFT, nullable=False, index=True)
    scheduled_at = Column(DateTime(timezone=True), nullable=True)
    published_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    teacher = relationship("TeacherProfile", back_populates="assessments")
    topic = relationship("Topic")
    question_links = relationship("AssessmentQuestion", back_populates="assessment", cascade="all, delete-orphan", order_by="AssessmentQuestion.question_order")
    attempts = relationship("Attempt", back_populates="assessment", cascade="all, delete-orphan")


class AssessmentQuestion(BaseModelMixin, Base):
    """Ordered junction linking questions to an assessment."""
    __tablename__ = "assessment_questions"
    __table_args__ = (
        UniqueConstraint("assessment_id", "question_id", name="uq_assessment_question"),
        CheckConstraint("question_order >= 1", name="chk_assessment_question_order_positive"),
        CheckConstraint("points >= 0", name="chk_assessment_question_points_non_negative"),
    )

    assessment_id = Column(String(36), ForeignKey("assessments.id", ondelete="CASCADE"), nullable=False, index=True)
    question_id = Column(String(36), ForeignKey("mcq_questions.id", ondelete="CASCADE"), nullable=False, index=True)
    question_order = Column(Integer, default=1, nullable=False)
    points = Column(Float, default=1.0, nullable=False)

    # Relationships
    assessment = relationship("Assessment", back_populates="question_links")
    question = relationship("MCQQuestion", back_populates="assessment_links")


class Attempt(BaseModelMixin, Base):
    """Student attempt session on an assessment."""
    __tablename__ = "attempts"
    __table_args__ = (
        CheckConstraint("total_score >= 0", name="chk_attempt_total_score_non_negative"),
        CheckConstraint("percentage >= 0 AND percentage <= 100", name="chk_attempt_percentage_range"),
        CheckConstraint("duration_seconds IS NULL OR duration_seconds >= 0", name="chk_attempt_duration_non_negative"),
    )

    student_id = Column(String(36), ForeignKey("student_profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    assessment_id = Column(String(36), ForeignKey("assessments.id", ondelete="CASCADE"), nullable=False, index=True)
    started_at = Column(DateTime(timezone=True), default=get_utc_now, nullable=False)
    submitted_at = Column(DateTime(timezone=True), nullable=True)
    total_score = Column(Float, default=0.0, nullable=False)
    percentage = Column(Float, default=0.0, nullable=False)
    duration_seconds = Column(Integer, nullable=True)
    status = Column(SQLEnum(AttemptStatus), default=AttemptStatus.STARTED, nullable=False, index=True)

    # Relationships
    student = relationship("StudentProfile", back_populates="attempts")
    assessment = relationship("Assessment", back_populates="attempts")
    answers = relationship("Answer", back_populates="attempt", cascade="all, delete-orphan")
    learning_events = relationship("LearningEvent", back_populates="attempt")


class Answer(BaseModelMixin, Base):
    """Individual question answer submitted during a student attempt."""
    __tablename__ = "answers"
    __table_args__ = (
        UniqueConstraint("attempt_id", "question_id", name="uq_attempt_question_answer"),
        CheckConstraint("response_time_ms >= 0", name="chk_answer_response_time_non_negative"),
    )

    attempt_id = Column(String(36), ForeignKey("attempts.id", ondelete="CASCADE"), nullable=False, index=True)
    question_id = Column(String(36), ForeignKey("mcq_questions.id", ondelete="CASCADE"), nullable=False, index=True)
    selected_option = Column(SQLEnum(OptionKey), nullable=False)
    is_correct = Column(Boolean, nullable=False)
    response_time_ms = Column(Integer, nullable=False)
    hint_used = Column(Boolean, default=False, nullable=False)
    answered_at = Column(DateTime(timezone=True), default=get_utc_now, nullable=False)

    # Relationships
    attempt = relationship("Attempt", back_populates="answers")
    question = relationship("MCQQuestion", back_populates="answers")
