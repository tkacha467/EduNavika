from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from backend.app.domain.enums import RevisionPriority, ForgettingSignalStatus


@dataclass
class DecayDetectionConfig:
    """
    Heuristic operational parameters for automated decay detection.
    These are operational definitions for automated triage, NOT cognitive-science laws.
    """
    min_prior_attempts: int = 3
    min_delay_days: float = 7.0
    baseline_accuracy_min: float = 70.0
    post_delay_accuracy_max: float = 60.0
    latency_spike_ratio_threshold: float = 2.0
    consecutive_failures_threshold: int = 2


@dataclass
class EvidenceProfile:
    """
    Observable empirical metrics extracted from longitudinal event history.
    Used for multi-factor qualitative evidence strength derivation.
    """
    prior_attempts: int
    baseline_accuracy: float
    post_delay_attempts: int
    post_delay_accuracy: float
    delay_days: float
    baseline_avg_latency_ms: Optional[float] = None
    post_delay_avg_latency_ms: Optional[float] = None
    latency_ratio: Optional[float] = None
    prior_mastery_state: str = "UNASSESSED"
    is_consecutive_failure: bool = False
    consecutive_failures_count: int = 0
    # Strictly observational metadata (NOT causal evidence)
    observational_intervening_activities: int = 0
    observational_intervening_topics: List[str] = field(default_factory=list)


@dataclass
class DecaySignalDraft:
    """
    Structured empirical evidence of temporal performance divergence,
    ready for idempotent persistence into the ForgettingSignal table.
    """
    student_id: str
    topic_id: str
    evidence_type: str
    evidence_strength: str  # WEAK, MODERATE, STRONG (qualitative categorical)
    prior_performance_reference: Dict[str, Any]
    later_performance_reference: Dict[str, Any]
    evidence_metadata: Dict[str, Any]
    detected_at: datetime
    episode_fingerprint: str


@dataclass
class RevisionScheduleDraft:
    """
    Initial deterministic baseline spaced-repetition recommendation.
    """
    student_id: str
    topic_id: str
    recommended_revision_at: datetime
    priority: RevisionPriority
    reason: str
    signal_fingerprint: Optional[str] = None


class DecayDetectionRequest(BaseModel):
    student_id: str
    topic_id: Optional[str] = None


class DecayDetectionResponse(BaseModel):
    student_id: str
    signals_detected: int
    signals_created: int
    signals_deduplicated: int
    plans_scheduled: int
    details: List[Dict[str, Any]] = Field(default_factory=list)


class AdaptiveScheduleResponse(BaseModel):
    student_id: str
    total_pending_revisions: int
    urgent_count: int
    high_count: int
    medium_count: int
    low_count: int
    revision_items: List[Dict[str, Any]] = Field(default_factory=list)
