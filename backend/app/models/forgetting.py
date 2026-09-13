from sqlalchemy import Column, String, DateTime, Enum as SQLEnum, ForeignKey, JSON
from sqlalchemy.orm import relationship
from backend.app.core.database import Base
from backend.app.models.base import BaseModelMixin, get_utc_now
from backend.app.domain.enums import ForgettingSignalStatus

# Re-export for backward compatibility
__all__ = ["ForgettingSignal", "ForgettingSignalStatus"]


class ForgettingSignal(BaseModelMixin, Base):
    """
    Longitudinal evidence of performance decay across temporal observations.
    Preserves comparative empirical evidence without inventing an unvalidated decay formula or probability.
    
    Fields:
    - evidence_type: Categorization of observed divergence (e.g. ACCURACY_DROP_POST_DELAY, LATENCY_SPIKE)
    - evidence_strength: Categorical strength of empirical evidence (e.g. WEAK, MODERATE, STRONG). NOT a calibrated probability.
    - prior_performance_reference: Snapshot/reference of prior successful state
    - later_performance_reference: Snapshot/reference of degraded subsequent state
    - evidence_metadata: Empirical observation context (e.g. elapsed_days, sample_size)
    """
    __tablename__ = "forgetting_signals"

    student_id = Column(String(36), ForeignKey("student_profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    topic_id = Column(String(36), ForeignKey("topics.id", ondelete="CASCADE"), nullable=False, index=True)
    detected_at = Column(DateTime(timezone=True), default=get_utc_now, nullable=False, index=True)
    
    # Evidence categorization & strength (NOT a probability)
    evidence_type = Column(String(100), nullable=False)
    evidence_strength = Column(String(50), default="MODERATE", nullable=True)
    prior_performance_reference = Column(JSON, nullable=True)
    later_performance_reference = Column(JSON, nullable=True)
    status = Column(SQLEnum(ForgettingSignalStatus), default=ForgettingSignalStatus.UNRESOLVED, nullable=False, index=True)
    evidence_metadata = Column(JSON, nullable=True)

    # Relationships
    student = relationship("StudentProfile", back_populates="forgetting_signals")
    topic = relationship("Topic", back_populates="forgetting_signals")

    # Backward-compatible property aliases
    @property
    def prior_performance_ref(self):
        return self.prior_performance_reference

    @prior_performance_ref.setter
    def prior_performance_ref(self, value):
        self.prior_performance_reference = value

    @property
    def later_performance_ref(self):
        return self.later_performance_reference

    @later_performance_ref.setter
    def later_performance_ref(self, value):
        self.later_performance_reference = value

    @property
    def confidence_metadata(self):
        return self.evidence_metadata

    @confidence_metadata.setter
    def confidence_metadata(self, value):
        self.evidence_metadata = value
