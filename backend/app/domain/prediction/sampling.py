from datetime import datetime, timezone, timedelta
from typing import List, Optional, Dict, Any, Tuple, Set
from collections import defaultdict
import uuid

from backend.app.models.learning_event import LearningEvent
from backend.app.domain.prediction.schemas import (
    PointInTimeFeatures,
    DatasetSample,
    CausalDatasetMatrix,
    CutoffSelectionConfig,
)
from backend.app.domain.prediction.extractor import PointInTimeFeatureExtractor, _ensure_utc


class RejectionReason:
    NO_FUTURE_TARGET = "NO_FUTURE_TARGET"
    TARGET_AT_OR_BEFORE_CUTOFF = "TARGET_AT_OR_BEFORE_CUTOFF"
    MISSING_TARGET_CORRECTNESS = "MISSING_TARGET_CORRECTNESS"
    DUPLICATE_OBSERVATION_TARGET = "DUPLICATE_OBSERVATION_TARGET"
    MALFORMED_TEMPORAL_ORDERING = "MALFORMED_TEMPORAL_ORDERING"
    INSUFFICIENT_HISTORY = "INSUFFICIENT_HISTORY"
    LEAD_TIME_BELOW_MINIMUM = "LEAD_TIME_BELOW_MINIMUM"


class SampleAuditRecord:
    def __init__(
        self,
        student_id: str,
        topic_id: str,
        cutoff_timestamp: Optional[datetime],
        target_event_id: Optional[str],
        target_timestamp: Optional[datetime],
        status: str,
        rejection_reason: Optional[str] = None,
    ):
        self.student_id = student_id
        self.topic_id = topic_id
        self.cutoff_timestamp = cutoff_timestamp
        self.target_event_id = target_event_id
        self.target_timestamp = target_timestamp
        self.status = status  # "ACCEPTED" | "REJECTED"
        self.rejection_reason = rejection_reason

    def to_dict(self) -> Dict[str, Any]:
        return {
            "student_id": self.student_id,
            "topic_id": self.topic_id,
            "cutoff_timestamp": self.cutoff_timestamp.isoformat() if self.cutoff_timestamp else None,
            "target_event_id": self.target_event_id,
            "target_timestamp": self.target_timestamp.isoformat() if self.target_timestamp else None,
            "status": self.status,
            "rejection_reason": self.rejection_reason,
        }


class ObservationSamplingAudit:
    """Audit log tracking accepted vs rejected candidate observations."""
    def __init__(self):
        self.total_candidates_evaluated: int = 0
        self.accepted_samples_count: int = 0
        self.rejected_samples_count: int = 0
        self.rejections_by_reason: Dict[str, int] = defaultdict(int)
        self.records: List[SampleAuditRecord] = []

    def record_rejection(
        self,
        student_id: str,
        topic_id: str,
        reason: str,
        cutoff_timestamp: Optional[datetime] = None,
        target_event_id: Optional[str] = None,
        target_timestamp: Optional[datetime] = None,
    ):
        self.total_candidates_evaluated += 1
        self.rejected_samples_count += 1
        self.rejections_by_reason[reason] += 1
        self.records.append(
            SampleAuditRecord(
                student_id=student_id,
                topic_id=topic_id,
                cutoff_timestamp=cutoff_timestamp,
                target_event_id=target_event_id,
                target_timestamp=target_timestamp,
                status="REJECTED",
                rejection_reason=reason,
            )
        )

    def record_acceptance(
        self,
        student_id: str,
        topic_id: str,
        cutoff_timestamp: datetime,
        target_event_id: str,
        target_timestamp: datetime,
    ):
        self.total_candidates_evaluated += 1
        self.accepted_samples_count += 1
        self.records.append(
            SampleAuditRecord(
                student_id=student_id,
                topic_id=topic_id,
                cutoff_timestamp=cutoff_timestamp,
                target_event_id=target_event_id,
                target_timestamp=target_timestamp,
                status="ACCEPTED",
            )
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "total_candidates_evaluated": self.total_candidates_evaluated,
            "accepted_samples_count": self.accepted_samples_count,
            "rejected_samples_count": self.rejected_samples_count,
            "rejections_by_reason": dict(self.rejections_by_reason),
        }


class ObservationSampler:
    """
    Deterministic observation and cutoff sampling engine.
    Scans chronological student event histories, verifies point-safe causality,
    and rejects invalid or leaking candidate observation pairs.
    """

    def __init__(self, config: Optional[CutoffSelectionConfig] = None):
        self.config = config or CutoffSelectionConfig()

    def sample_observations(
        self,
        events: List[LearningEvent],
        curriculum_map: Optional[Dict[str, Dict[str, Any]]] = None,
        db: Optional[Any] = None,
    ) -> Tuple[CausalDatasetMatrix, ObservationSamplingAudit]:
        """
        Samples valid (X(T), Y(T_target)) instances with complete audit tracking.
        """
        audit = ObservationSamplingAudit()
        seen_pairs: Set[Tuple[str, str, str, str]] = set()

        # Group by student
        by_student: Dict[str, List[LearningEvent]] = defaultdict(list)
        for e in events:
            by_student[e.student_id].append(e)

        samples: List[DatasetSample] = []

        for student_id, stud_events in by_student.items():
            # Check for malformed ordering in raw stream
            # Sort explicitly by timestamp ASC
            stud_events_sorted = sorted(
                stud_events,
                key=lambda x: (_ensure_utc(x.timestamp), getattr(x, "created_at", _ensure_utc(x.timestamp)), getattr(x, "id", ""))
            )

            # Group student's events by topic
            by_topic: Dict[str, List[LearningEvent]] = defaultdict(list)
            for e in stud_events_sorted:
                by_topic[e.topic_id].append(e)

            for topic_id, topic_events in by_topic.items():
                curriculum_meta = curriculum_map.get(topic_id) if curriculum_map else None

                # Iterate through all topic events to evaluate valid transitions
                for i, target_event in enumerate(topic_events):
                    target_id = getattr(target_event, "id", str(uuid.uuid4()))
                    target_dt = _ensure_utc(target_event.timestamp)

                    # Rejection Check 1: Missing target correctness
                    if target_event.correctness is None:
                        audit.record_rejection(
                            student_id=student_id,
                            topic_id=topic_id,
                            reason=RejectionReason.MISSING_TARGET_CORRECTNESS,
                            target_event_id=target_id,
                            target_timestamp=target_dt,
                        )
                        continue

                    # Define cutoff: immediately preceding target interaction
                    cutoff_dt = target_dt - timedelta(milliseconds=1)

                    # Rejection Check 2: Target at or before cutoff
                    lead_time = (target_dt - cutoff_dt).total_seconds()
                    if lead_time <= 0:
                        audit.record_rejection(
                            student_id=student_id,
                            topic_id=topic_id,
                            reason=RejectionReason.TARGET_AT_OR_BEFORE_CUTOFF,
                            cutoff_timestamp=cutoff_dt,
                            target_event_id=target_id,
                            target_timestamp=target_dt,
                        )
                        continue

                    # Rejection Check 3: Lead time below configured threshold
                    if lead_time < self.config.min_lead_time_seconds:
                        audit.record_rejection(
                            student_id=student_id,
                            topic_id=topic_id,
                            reason=RejectionReason.LEAD_TIME_BELOW_MINIMUM,
                            cutoff_timestamp=cutoff_dt,
                            target_event_id=target_id,
                            target_timestamp=target_dt,
                        )
                        continue

                    # Rejection Check 4: Duplicate observation pair
                    pair_key = (student_id, topic_id, cutoff_dt.isoformat(), target_id)
                    if pair_key in seen_pairs:
                        audit.record_rejection(
                            student_id=student_id,
                            topic_id=topic_id,
                            reason=RejectionReason.DUPLICATE_OBSERVATION_TARGET,
                            cutoff_timestamp=cutoff_dt,
                            target_event_id=target_id,
                            target_timestamp=target_dt,
                        )
                        continue

                    # Rejection Check 5: Insufficient prior history if required
                    prior_topic_evals = sum(
                        1 for e in topic_events[:i]
                        if e.correctness is not None and _ensure_utc(e.timestamp) <= cutoff_dt
                    )
                    if prior_topic_evals < self.config.min_prior_topic_attempts:
                        audit.record_rejection(
                            student_id=student_id,
                            topic_id=topic_id,
                            reason=RejectionReason.INSUFFICIENT_HISTORY,
                            cutoff_timestamp=cutoff_dt,
                            target_event_id=target_id,
                            target_timestamp=target_dt,
                        )
                        continue

                    prior_global_events = sum(
                        1 for e in stud_events_sorted
                        if _ensure_utc(e.timestamp) <= cutoff_dt
                    )
                    if prior_global_events < self.config.min_prior_global_events:
                        audit.record_rejection(
                            student_id=student_id,
                            topic_id=topic_id,
                            reason=RejectionReason.INSUFFICIENT_HISTORY,
                            cutoff_timestamp=cutoff_dt,
                            target_event_id=target_id,
                            target_timestamp=target_dt,
                        )
                        continue

                    # Sample is valid and accepted
                    seen_pairs.add(pair_key)
                    audit.record_acceptance(
                        student_id=student_id,
                        topic_id=topic_id,
                        cutoff_timestamp=cutoff_dt,
                        target_event_id=target_id,
                        target_timestamp=target_dt,
                    )

                    features = PointInTimeFeatureExtractor.extract(
                        student_id=student_id,
                        topic_id=topic_id,
                        cutoff_timestamp=cutoff_dt,
                        events=stud_events_sorted,
                        curriculum_meta=curriculum_meta,
                        db=db,
                        max_latency_ms=self.config.max_latency_ms,
                    )

                    sample_id = f"smp_{target_id}"
                    target_correctness_int = 1 if target_event.correctness is True else 0

                    samples.append(
                        DatasetSample(
                            sample_id=sample_id,
                            student_id=student_id,
                            topic_id=topic_id,
                            cutoff_timestamp=cutoff_dt,
                            target_event_id=target_id,
                            target_timestamp=target_dt,
                            lead_time_seconds=round(lead_time, 4),
                            target_correctness=target_correctness_int,
                            target_score=target_event.score,
                            target_response_time_ms=target_event.response_time_ms,
                            target_event_type=str(target_event.event_type.value if hasattr(target_event.event_type, "value") else target_event.event_type),
                            features=features,
                        )
                    )

        # Deterministic sort
        samples.sort(key=lambda s: (s.cutoff_timestamp, s.student_id, s.topic_id, s.target_event_id))

        return CausalDatasetMatrix(samples=samples), audit
