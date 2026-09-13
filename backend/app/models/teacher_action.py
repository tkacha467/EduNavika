from sqlalchemy import Column, String, Text, DateTime, Enum as SQLEnum, ForeignKey
from sqlalchemy.orm import relationship
from backend.app.core.database import Base
from backend.app.models.base import BaseModelMixin
from backend.app.domain.enums import TeacherActionType

# Re-export for backward compatibility
__all__ = ["TeacherAction", "TeacherActionType"]


class TeacherAction(BaseModelMixin, Base):
    """
    Teacher intervention tracking for longitudinal efficacy studies.
    """
    __tablename__ = "teacher_actions"

    teacher_id = Column(String(36), ForeignKey("teacher_profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    student_id = Column(String(36), ForeignKey("student_profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    topic_id = Column(String(36), ForeignKey("topics.id", ondelete="CASCADE"), nullable=False, index=True)
    action_type = Column(SQLEnum(TeacherActionType), nullable=False, index=True)
    note = Column(Text, nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    teacher = relationship("TeacherProfile", back_populates="actions_created")
    student = relationship("StudentProfile", back_populates="interventions_received")
    topic = relationship("Topic", back_populates="teacher_actions")
