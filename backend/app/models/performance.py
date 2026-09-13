from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey, UniqueConstraint, CheckConstraint
from sqlalchemy.orm import relationship
from backend.app.core.database import Base
from backend.app.models.base import BaseModelMixin


class TopicPerformance(BaseModelMixin, Base):
    """
    Topic-level evidence aggregation layer.
    Summarizes student interaction metrics for quick application dashboard lookups,
    WITHOUT replacing raw longitudinal event logs.
    This is an application-facing evidence layer, NOT a research-grade ML predictor.
    """
    __tablename__ = "topic_performances"
    __table_args__ = (
        UniqueConstraint("student_id", "topic_id", name="uq_student_topic_performance"),
        CheckConstraint("total_attempts >= 0", name="chk_topic_perf_total_attempts_non_negative"),
        CheckConstraint("correct_attempts >= 0", name="chk_topic_perf_correct_attempts_non_negative"),
        CheckConstraint("accuracy >= 0 AND accuracy <= 100", name="chk_topic_perf_accuracy_range"),
        CheckConstraint("practice_count >= 0", name="chk_topic_perf_practice_count_non_negative"),
        CheckConstraint("revision_count >= 0", name="chk_topic_perf_revision_count_non_negative"),
        CheckConstraint("hint_usage_count >= 0", name="chk_topic_perf_hint_usage_count_non_negative"),
        CheckConstraint("average_response_time >= 0", name="chk_topic_perf_avg_time_non_negative"),
    )

    student_id = Column(String(36), ForeignKey("student_profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    topic_id = Column(String(36), ForeignKey("topics.id", ondelete="CASCADE"), nullable=False, index=True)
    
    total_attempts = Column(Integer, default=0, nullable=False)
    correct_attempts = Column(Integer, default=0, nullable=False)
    accuracy = Column(Float, default=0.0, nullable=False)
    
    last_activity_at = Column(DateTime(timezone=True), nullable=True)
    last_success_at = Column(DateTime(timezone=True), nullable=True)
    
    practice_count = Column(Integer, default=0, nullable=False)
    revision_count = Column(Integer, default=0, nullable=False)
    average_response_time = Column(Float, default=0.0, nullable=False)
    hint_usage_count = Column(Integer, default=0, nullable=False)
    
    # Application-facing heuristic state (UNASSESSED, NOVICE, PRACTICING, MASTERED)
    mastery_state = Column(String(50), default="UNASSESSED", nullable=False)

    # Relationships
    student = relationship("StudentProfile", back_populates="topic_performances")
    topic = relationship("Topic", back_populates="topic_performances")
