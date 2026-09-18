from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from backend.app.models import LearningEvent
from backend.app.models import TopicPerformance
from backend.app.models import ForgettingSignal
from backend.app.models import RevisionPlan
from backend.app.domain.enums import RevisionPriority, RevisionCompletionState, ForgettingSignalStatus
from backend.app.domain.decay_engine.schemas import (
    DecayDetectionConfig,
    DecayDetectionResponse,
    AdaptiveScheduleResponse,
)
from backend.app.domain.decay_engine.detector import LongitudinalDecayDetector
from backend.app.domain.decay_engine.scheduler import SpacedRepetitionScheduler
from backend.app.domain.decay_engine.deduplication import SignalDeduplicator
from backend.app.domain.decay_engine.state_machine import SignalLifecycleStateMachine


class AdaptiveLearningService:
    """
    High-level orchestrator connecting the longitudinal LearningEvent stream,
    empirical decay detection, idempotent signal persistence, and spaced-repetition scheduling.
    """

    def __init__(self, config: Optional[DecayDetectionConfig] = None):
        self.config = config or DecayDetectionConfig()
        self.detector = LongitudinalDecayDetector(config=self.config)

    def detect_and_schedule_for_student(
        self,
        db: Session,
        student_id: str,
        topic_id: Optional[str] = None
    ) -> DecayDetectionResponse:
        """
        Executes idempotent longitudinal decay analysis and generates prioritized revision plans.
        """
        # 1. Fetch all events for the student
        events_query = db.query(LearningEvent).filter(LearningEvent.student_id == student_id)
        all_student_events = events_query.order_by(LearningEvent.timestamp.asc()).all()

        if topic_id:
            topics_to_eval = [topic_id]
        else:
            topics_to_eval = sorted(list({e.topic_id for e in all_student_events}))

        total_detected = 0
        total_created = 0
        total_deduped = 0
        total_scheduled = 0
        details: List[Dict[str, Any]] = []

        now = datetime.now(timezone.utc)

        for tid in topics_to_eval:
            # Topic performance snapshot
            topic_perf = (
                db.query(TopicPerformance)
                .filter(
                    TopicPerformance.student_id == student_id,
                    TopicPerformance.topic_id == tid
                )
                .first()
            )

            # Detect signals
            detected_drafts = self.detector.detect_for_topic(
                student_id=student_id,
                topic_id=tid,
                events=all_student_events,
                topic_perf=topic_perf,
                all_student_events=all_student_events,
            )

            total_detected += len(detected_drafts)

            for draft in detected_drafts:
                # Idempotency check
                is_dupe = SignalDeduplicator.is_duplicate_signal(
                    db=db,
                    student_id=student_id,
                    topic_id=tid,
                    fingerprint=draft.episode_fingerprint
                )

                if is_dupe:
                    total_deduped += 1
                    details.append({
                        "topic_id": tid,
                        "evidence_type": draft.evidence_type,
                        "action": "DEDUPLICATED",
                        "fingerprint": draft.episode_fingerprint
                    })
                    continue

                # Create persistent ForgettingSignal
                signal = ForgettingSignal(
                    student_id=student_id,
                    topic_id=tid,
                    detected_at=draft.detected_at,
                    evidence_type=draft.evidence_type,
                    evidence_strength=draft.evidence_strength,
                    prior_performance_reference=draft.prior_performance_reference,
                    later_performance_reference=draft.later_performance_reference,
                    status=ForgettingSignalStatus.UNRESOLVED,
                    evidence_metadata=draft.evidence_metadata,
                )
                db.add(signal)
                total_created += 1

                # Check if a pending plan already exists for this topic
                has_pending = SignalDeduplicator.has_pending_revision_plan(db, student_id, tid)
                if not has_pending:
                    plan_draft = SpacedRepetitionScheduler.schedule_from_signal(
                        signal=draft,
                        topic_perf=topic_perf,
                        now=now
                    )
                    revision_plan = RevisionPlan(
                        student_id=student_id,
                        topic_id=tid,
                        recommended_revision_at=plan_draft.recommended_revision_at,
                        priority=plan_draft.priority,
                        reason=plan_draft.reason,
                        completion_state=RevisionCompletionState.PENDING,
                    )
                    db.add(revision_plan)
                    total_scheduled += 1

                details.append({
                    "topic_id": tid,
                    "evidence_type": draft.evidence_type,
                    "evidence_strength": draft.evidence_strength,
                    "action": "SIGNAL_CREATED",
                    "plan_scheduled": not has_pending
                })

        db.commit()

        return DecayDetectionResponse(
            student_id=student_id,
            signals_detected=total_detected,
            signals_created=total_created,
            signals_deduplicated=total_deduped,
            plans_scheduled=total_scheduled,
            details=details,
        )

    @staticmethod
    def get_student_schedule(db: Session, student_id: str) -> AdaptiveScheduleResponse:
        """
        Retrieves active pending revision items for a student, ordered by priority and deadline.
        """
        plans = (
            db.query(RevisionPlan)
            .filter(
                RevisionPlan.student_id == student_id,
                RevisionPlan.completion_state == RevisionCompletionState.PENDING
            )
            .order_by(
                RevisionPlan.priority.desc(),
                RevisionPlan.recommended_revision_at.asc()
            )
            .all()
        )

        urgent = sum(1 for p in plans if p.priority == RevisionPriority.URGENT)
        high = sum(1 for p in plans if p.priority == RevisionPriority.HIGH)
        med = sum(1 for p in plans if p.priority == RevisionPriority.MEDIUM)
        low = sum(1 for p in plans if p.priority == RevisionPriority.LOW)

        items = [
            {
                "id": p.id,
                "topic_id": p.topic_id,
                "priority": p.priority.value,
                "recommended_revision_at": p.recommended_revision_at.isoformat(),
                "reason": p.reason,
                "completion_state": p.completion_state.value,
            }
            for p in plans
        ]

        return AdaptiveScheduleResponse(
            student_id=student_id,
            total_pending_revisions=len(plans),
            urgent_count=urgent,
            high_count=high,
            medium_count=med,
            low_count=low,
            revision_items=items,
        )

    @staticmethod
    def handle_revision_attempt(
        db: Session,
        student_id: str,
        topic_id: str,
        score: float,
        correctness: bool,
        response_time_ms: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Processes a completed revision attempt and drives the signal lifecycle.
        """
        result = SignalLifecycleStateMachine.process_revision_outcome(
            db=db,
            student_id=student_id,
            topic_id=topic_id,
            score=score,
            correctness=correctness,
            response_time_ms=response_time_ms
        )
        db.commit()
        return result
