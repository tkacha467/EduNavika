from datetime import datetime, timezone, timedelta
from typing import List, Optional, Dict, Any
from collections import defaultdict
import uuid
from sqlalchemy.orm import Session

from backend.app.models import LearningEvent
from backend.app.domain.prediction.schemas import (
    PointInTimeFeatures,
    DatasetSample,
    CausalDatasetMatrix,
    CutoffSelectionConfig,
)
from backend.app.domain.prediction.extractor import PointInTimeFeatureExtractor, _ensure_utc


class CausalDatasetGenerator:
    """
    Generates point-in-time supervised learning dataset matrices from
    chronological student learning event histories.
    
    GUARANTEES:
    1. Cutoff ordering is strictly temporal: T_cutoff < T_target.
    2. Feature vector X(T) is derived solely from events with timestamp <= T_cutoff.
    3. Target Y is obtained exclusively from evaluative events with timestamp >= T_target.
    4. Rejects any sample where future information leaks or target is not strictly future.
    """

    def __init__(self, config: Optional[CutoffSelectionConfig] = None):
        self.config = config or CutoffSelectionConfig()

    def generate_from_events(
        self,
        events: List[LearningEvent],
        curriculum_map: Optional[Dict[str, Dict[str, Any]]] = None,
        db: Optional[Session] = None,
    ) -> CausalDatasetMatrix:
        """
        Scans an in-memory collection of LearningEvents, partitions by student,
        and extracts valid causal (X(T), Y(T_target)) samples.
        """
        # Group events by student
        by_student: Dict[str, List[LearningEvent]] = defaultdict(list)
        for e in events:
            by_student[e.student_id].append(e)

        samples: List[DatasetSample] = []

        for student_id, stud_events in by_student.items():
            # Chronological sort across all events for this student
            stud_events.sort(key=lambda x: (_ensure_utc(x.timestamp), getattr(x, "created_at", _ensure_utc(x.timestamp)), getattr(x, "id", "")))

            # Group student's events by topic to track topic-level history
            by_topic: Dict[str, List[LearningEvent]] = defaultdict(list)
            for e in stud_events:
                by_topic[e.topic_id].append(e)

            # For each topic, iterate through evaluative events as potential target points
            for topic_id, topic_events in by_topic.items():
                curriculum_meta = curriculum_map.get(topic_id) if curriculum_map else None

                evaluative_indices = [
                    idx for idx, e in enumerate(topic_events)
                    if e.correctness is not None
                ]

                for eval_idx in evaluative_indices:
                    target_event = topic_events[eval_idx]
                    target_dt = _ensure_utc(target_event.timestamp)

                    # Determine cutoff timestamp T
                    # Case 1: If there are prior topic events, cutoff is placed after the immediately preceding topic event
                    # or at a small delta before target_dt (e.g. 1 second before target)
                    if eval_idx > 0:
                        prev_topic_event = topic_events[eval_idx - 1]
                        prev_dt = _ensure_utc(prev_topic_event.timestamp)
                        # Cutoff is placed halfway or at least 1 millisecond after prev event and before target
                        # To simulate predicting right before the attempt:
                        # T = min(target_dt - timedelta(milliseconds=1), prev_dt + (target_dt - prev_dt) / 2)
                        # Standard convention: prediction immediately preceding the upcoming attempt:
                        cutoff_dt = target_dt - timedelta(milliseconds=1)
                    else:
                        # First attempt on this topic (cold start on topic)
                        cutoff_dt = target_dt - timedelta(milliseconds=1)

                    # Verify strict causal condition
                    lead_time = (target_dt - cutoff_dt).total_seconds()
                    if lead_time <= self.config.min_lead_time_seconds:
                        continue  # Reject: target is not genuinely future

                    # Check prior attempt filters
                    prior_topic_eval_count = eval_idx
                    if prior_topic_eval_count < self.config.min_prior_topic_attempts:
                        continue  # Skip if insufficient prior attempts required by config

                    prior_global_count = sum(
                        1 for e in stud_events
                        if _ensure_utc(e.timestamp) <= cutoff_dt
                    )
                    if prior_global_count < self.config.min_prior_global_events:
                        continue

                    # Extract point-in-time features strictly at cutoff_dt
                    features = PointInTimeFeatureExtractor.extract(
                        student_id=student_id,
                        topic_id=topic_id,
                        cutoff_timestamp=cutoff_dt,
                        events=stud_events,
                        curriculum_meta=curriculum_meta,
                        db=db,
                        max_latency_ms=self.config.max_latency_ms,
                    )

                    target_correctness_int = 1 if target_event.correctness is True else 0

                    sample_id = f"smp_{getattr(target_event, 'id', str(uuid.uuid4()))}"

                    samples.append(
                        DatasetSample(
                            sample_id=sample_id,
                            student_id=student_id,
                            topic_id=topic_id,
                            cutoff_timestamp=cutoff_dt,
                            target_event_id=getattr(target_event, "id", sample_id),
                            target_timestamp=target_dt,
                            lead_time_seconds=round(lead_time, 4),
                            target_correctness=target_correctness_int,
                            target_score=target_event.score,
                            target_response_time_ms=target_event.response_time_ms,
                            target_event_type=str(target_event.event_type.value if hasattr(target_event.event_type, "value") else target_event.event_type),
                            features=features,
                        )
                    )

        # Sort all generated samples chronologically by cutoff timestamp
        samples.sort(key=lambda s: (s.cutoff_timestamp, s.student_id, s.topic_id))

        return CausalDatasetMatrix(
            samples=samples,
            target_name="target_correctness",
        )

    def generate_from_db(
        self,
        db: Session,
        student_id: Optional[str] = None,
        topic_id: Optional[str] = None,
    ) -> CausalDatasetMatrix:
        """
        Extracts all LearningEvents from the DB and generates a causal dataset.
        """
        query = db.query(LearningEvent)
        if student_id:
            query = query.filter(LearningEvent.student_id == student_id)
        if topic_id:
            query = query.filter(LearningEvent.topic_id == topic_id)

        events = query.order_by(LearningEvent.timestamp.asc()).all()
        return self.generate_from_events(events=events, db=db)
