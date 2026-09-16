from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Optional, Dict, Any, List, Union


@dataclass
class PointInTimeFeatures:
    """
    Point-in-time historical feature vector derived strictly from LearningEvent
    records with timestamp <= cutoff_timestamp.
    
    CRITICAL CONTRACT:
    Must NEVER read from mutable live tables (e.g. TopicPerformance).
    Preserves explicit missing-data indicators rather than silently imputing.
    """
    # Identification & Cutoff Context
    student_id: str
    topic_id: str
    cutoff_timestamp: datetime

    # 1. Temporal Recency & Spacing
    delta_t_topic_days: Optional[float] = None
    delta_t_topic_seconds: Optional[float] = None
    has_prior_topic_interaction: bool = False
    delta_t_success_days: Optional[float] = None
    has_prior_topic_success: bool = False
    delta_t_global_days: Optional[float] = None
    has_prior_global_interaction: bool = False

    # 2. Cumulative Exposure / Volume
    cumulative_topic_attempts: int = 0
    cumulative_topic_exposures: int = 0
    cumulative_topic_correct_count: int = 0
    cumulative_revision_count: int = 0
    cumulative_practice_count: int = 0
    cumulative_mcq_attempt_count: int = 0
    cumulative_global_attempts: int = 0
    cumulative_global_exposures: int = 0

    # 3. Historical Accuracy
    cumulative_topic_accuracy: Optional[float] = None
    topic_accuracy_is_missing: bool = True
    cumulative_global_accuracy: Optional[float] = None
    global_accuracy_is_missing: bool = True

    # 4. EWMA Accuracy (Exponentially Weighted Moving Average)
    ewma_topic_accuracy: Optional[float] = None
    ewma_accuracy_is_missing: bool = True
    ewma_alpha: float = 0.3

    # 5. Response Time Statistics & Trend
    mean_response_time_ms: Optional[float] = None
    median_response_time_ms: Optional[float] = None
    last_response_time_ms: Optional[float] = None
    latency_trend_ratio: Optional[float] = None
    latency_is_missing: bool = True
    latency_winsorized_count: int = 0

    # 6. Hint Usage & Scaffolding
    cumulative_hint_count: int = 0
    hint_rate: Optional[float] = None
    last_attempt_hint_used: Optional[bool] = None
    hint_data_is_missing: bool = True

    # 7. Intervening Interference (Between last topic event and cutoff T)
    intervening_event_count: int = 0
    intervening_distinct_topics_count: int = 0
    intervening_evaluative_count: int = 0
    is_first_topic_attempt: bool = True

    # 8. Static Curriculum Context
    grade_level: Optional[int] = None
    subject_code: Optional[str] = None
    chapter_number: Optional[int] = None
    topic_order: Optional[int] = None
    curriculum_context_is_missing: bool = True

    def to_dict(self) -> Dict[str, Any]:
        """Returns feature dataclass as a python dictionary."""
        d = asdict(self)
        d["cutoff_timestamp"] = self.cutoff_timestamp.isoformat()
        return d

    def to_flat_feature_dict(self, prefix: str = "") -> Dict[str, Any]:
        """
        Returns numeric/categorical flat feature dictionary suitable
        for tabular ML consumption, excluding entity identifiers.
        """
        raw = self.to_dict()
        # Strip entity/timestamp identifiers from numeric vector
        exclude = {"student_id", "topic_id", "cutoff_timestamp"}
        return {
            f"{prefix}{k}": v for k, v in raw.items() if k not in exclude
        }


@dataclass
class CutoffSelectionConfig:
    """Configuration governing prediction cutoff selection."""
    min_prior_topic_attempts: int = 0
    min_prior_global_events: int = 0
    min_lead_time_seconds: float = 0.0
    require_evaluative_target: bool = True
    max_latency_ms: int = 180000  # 3 minutes cap (winsorization bound)


@dataclass
class DatasetSample:
    """
    A single point-in-time supervised training instance.
    Features X(T) strictly precede target Y(T_target).
    """
    sample_id: str
    student_id: str
    topic_id: str
    cutoff_timestamp: datetime
    target_event_id: str
    target_timestamp: datetime
    lead_time_seconds: float
    target_correctness: int  # 1 if True, 0 if False (Target Option A)
    target_score: Optional[float]
    target_response_time_ms: Optional[int]
    target_event_type: str
    features: PointInTimeFeatures

    def to_dict(self) -> Dict[str, Any]:
        return {
            "sample_id": self.sample_id,
            "student_id": self.student_id,
            "topic_id": self.topic_id,
            "cutoff_timestamp": self.cutoff_timestamp.isoformat(),
            "target_event_id": self.target_event_id,
            "target_timestamp": self.target_timestamp.isoformat(),
            "lead_time_seconds": self.lead_time_seconds,
            "target_correctness": self.target_correctness,
            "target_score": self.target_score,
            "target_response_time_ms": self.target_response_time_ms,
            "target_event_type": self.target_event_type,
            **self.features.to_flat_feature_dict(prefix="feat_"),
        }


@dataclass
class CausalDatasetMatrix:
    """Collection of validated, leakage-free supervised learning instances."""
    samples: List[DatasetSample] = field(default_factory=list)
    target_name: str = "target_correctness"

    @property
    def total_samples(self) -> int:
        return len(self.samples)

    @property
    def positive_target_count(self) -> int:
        return sum(1 for s in self.samples if s.target_correctness == 1)

    @property
    def negative_target_count(self) -> int:
        return sum(1 for s in self.samples if s.target_correctness == 0)

    @property
    def positive_rate(self) -> float:
        if not self.samples:
            return 0.0
        return round(self.positive_target_count / len(self.samples), 4)

    def to_records(self) -> List[Dict[str, Any]]:
        """Returns flattened records for dataframes / csv export."""
        return [s.to_dict() for s in self.samples]
