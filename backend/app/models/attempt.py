from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, Enum as SQLEnum, ForeignKey, UniqueConstraint, CheckConstraint
from sqlalchemy.orm import relationship
from backend.app.core.database import Base
from backend.app.models.base import BaseModelMixin, get_utc_now
from backend.app.domain.enums import AttemptStatus, OptionKey

# Re-export for backward compatibility
__all__ = ["Attempt", "Answer", "AttemptStatus", "OptionKey"]


class Attempt(BaseModelMixin, Base):
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
    __tablename__ = "answers"
    __table_args__ = (
        UniqueConstraint("attempt_id", "question_id", name="uq_attempt_question_answer"),
        CheckConstraint("response_time_ms >= 0", name="chk_answer_response_time_non_negative"),
    )

    attempt_id = Column(String(36), ForeignKey("attempts.id", ondelete="CASCADE"), nullable=False, index=True)
    question_id = Column(String(36), ForeignKey("mcq_questions.id", ondelete="CASCADE"), nullable=False, index=True)
    selected_option = Column(SQLEnum(OptionKey), nullable=False)
    is_correct = Column(Boolean, nullable=False)
    response_time_ms = Column(Integer, nullable=False)  # Captured server-side or verified
    hint_used = Column(Boolean, default=False, nullable=False)
    answered_at = Column(DateTime(timezone=True), default=get_utc_now, nullable=False)

    # Relationships
    attempt = relationship("Attempt", back_populates="answers")
    question = relationship("MCQQuestion", back_populates="answers")
