from sqlalchemy import Column, String, Text, Integer, Float, DateTime, Enum as SQLEnum, ForeignKey, UniqueConstraint, CheckConstraint
from sqlalchemy.orm import relationship
from backend.app.core.database import Base
from backend.app.models.base import BaseModelMixin
from backend.app.domain.enums import AssessmentStatus

# Re-export for backward compatibility
__all__ = ["Assessment", "AssessmentQuestion", "AssessmentStatus"]


class Assessment(BaseModelMixin, Base):
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
