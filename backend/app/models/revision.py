from sqlalchemy import Column, String, Text, DateTime, Enum as SQLEnum, ForeignKey
from sqlalchemy.orm import relationship
from backend.app.core.database import Base
from backend.app.models.base import BaseModelMixin
from backend.app.domain.enums import RevisionPriority, RevisionCompletionState

# Re-export for backward compatibility
__all__ = ["RevisionPlan", "RevisionPriority", "RevisionCompletionState"]


class RevisionPlan(BaseModelMixin, Base):
    """
    Data model for future personalized revision scheduling.
    """
    __tablename__ = "revision_plans"

    student_id = Column(String(36), ForeignKey("student_profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    topic_id = Column(String(36), ForeignKey("topics.id", ondelete="CASCADE"), nullable=False, index=True)
    recommended_revision_at = Column(DateTime(timezone=True), nullable=False, index=True)
    priority = Column(SQLEnum(RevisionPriority), default=RevisionPriority.MEDIUM, nullable=False)
    reason = Column(Text, nullable=True)
    completion_state = Column(SQLEnum(RevisionCompletionState), default=RevisionCompletionState.PENDING, nullable=False, index=True)

    # Relationships
    student = relationship("StudentProfile", back_populates="revision_plans")
    topic = relationship("Topic", back_populates="revision_plans")
