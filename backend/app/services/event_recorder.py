from datetime import datetime, timezone
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from backend.app.models import LearningEvent, EventType
from backend.app.models import TopicPerformance


class EventRecorderService:
    """
    Handles recording of atomic longitudinal LearningEvents and maintains
    the aggregated TopicPerformance evidence layer.
    """

    @staticmethod
    def record_event(
        db: Session,
        student_id: str,
        topic_id: str,
        event_type: EventType,
        timestamp: Optional[datetime] = None,
        session_id: Optional[str] = None,
        attempt_id: Optional[str] = None,
        score: Optional[float] = None,
        correctness: Optional[bool] = None,
        response_time_ms: Optional[int] = None,
        hint_used: bool = False,
        attempt_number: int = 1,
        event_metadata: Optional[Dict[str, Any]] = None,
        idempotency_key: Optional[str] = None,
        auto_commit: bool = False
    ) -> LearningEvent:
        if timestamp is None:
            timestamp = datetime.now(timezone.utc)

        # Validation safeguards
        if score is not None and score < 0:
            raise ValueError(f"Event score cannot be negative, got {score}")
        if response_time_ms is not None and response_time_ms < 0:
            raise ValueError(f"Event response_time_ms cannot be negative, got {response_time_ms}")
        if attempt_number is not None and attempt_number < 1:
            raise ValueError(f"Event attempt_number must be >= 1, got {attempt_number}")

        # Semantic normalization by event_type
        if event_type == EventType.LEARN:
            correctness = None
            score = None
        elif event_type == EventType.REVIEW:
            correctness = None

        meta = dict(event_metadata) if event_metadata else {}
        if idempotency_key:
            meta["idempotency_key"] = idempotency_key

        effective_idempotency_key = meta.get("idempotency_key")
        if effective_idempotency_key:
            # Check for existing event with identical idempotency_key
            existing = (
                db.query(LearningEvent)
                .filter(
                    LearningEvent.student_id == student_id,
                    LearningEvent.topic_id == topic_id,
                    LearningEvent.event_type == event_type,
                )
                .all()
            )
            for ev in existing:
                if ev.event_metadata and ev.event_metadata.get("idempotency_key") == effective_idempotency_key:
                    return ev

        # 1. Store immutable raw learning event
        event = LearningEvent(
            student_id=student_id,
            topic_id=topic_id,
            event_type=event_type,
            timestamp=timestamp,
            session_id=session_id,
            attempt_id=attempt_id,
            score=score,
            correctness=correctness,
            response_time_ms=response_time_ms,
            hint_used=hint_used,
            attempt_number=attempt_number,
            event_metadata=meta if meta else None,
        )
        db.add(event)

        # 2. Update TopicPerformance evidence aggregation
        EventRecorderService._update_topic_performance(
            db=db,
            student_id=student_id,
            topic_id=topic_id,
            event_type=event_type,
            timestamp=timestamp,
            correctness=correctness,
            response_time_ms=response_time_ms,
            hint_used=hint_used,
        )

        if auto_commit:
            db.commit()
            db.refresh(event)

        return event


    @staticmethod
    def _update_topic_performance(
        db: Session,
        student_id: str,
        topic_id: str,
        event_type: EventType,
        timestamp: datetime,
        correctness: Optional[bool],
        response_time_ms: Optional[int],
        hint_used: bool,
    ) -> TopicPerformance:
        perf = (
            db.query(TopicPerformance)
            .filter(
                TopicPerformance.student_id == student_id,
                TopicPerformance.topic_id == topic_id
            )
            .first()
        )

        if not perf:
            perf = TopicPerformance(
                student_id=student_id,
                topic_id=topic_id,
                total_attempts=0,
                correct_attempts=0,
                accuracy=0.0,
                practice_count=0,
                revision_count=0,
                average_response_time=0.0,
                hint_usage_count=0,
                mastery_state="UNASSESSED",
            )
            db.add(perf)

        perf.last_activity_at = timestamp

        if hint_used:
            perf.hint_usage_count += 1

        if event_type == EventType.PRACTICE:
            perf.practice_count += 1
        elif event_type == EventType.REVISION:
            perf.revision_count += 1

        # If question/assessment attempt occurred
        if correctness is not None:
            prev_total = perf.total_attempts
            perf.total_attempts += 1
            if correctness:
                perf.correct_attempts += 1
                perf.last_success_at = timestamp

            perf.accuracy = round((perf.correct_attempts / perf.total_attempts) * 100.0, 2)

            if response_time_ms is not None:
                current_avg = perf.average_response_time
                perf.average_response_time = round(
                    ((current_avg * prev_total) + response_time_ms) / perf.total_attempts, 2
                )

            # Update evidence-based mastery state
            if perf.total_attempts >= 5 and perf.accuracy >= 80.0:
                perf.mastery_state = "MASTERED"
            elif perf.total_attempts >= 3 and perf.accuracy >= 50.0:
                perf.mastery_state = "PRACTICING"
            elif perf.total_attempts >= 1:
                perf.mastery_state = "NOVICE"

        return perf
