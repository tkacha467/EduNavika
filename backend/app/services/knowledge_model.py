from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
from sqlalchemy.orm import Session

from backend.app.models import LearningEvent, TopicPerformance, ForgettingSignal, ForgettingSignalStatus
from backend.app.models import Topic, Chapter, Subject
from backend.app.domain.enums import MasteryLevel, PerformanceTrend, RetentionRiskLevel
from backend.app.schemas.knowledge_profile import TopicKnowledgeProfile, StudentKnowledgeProfileResponse


class KnowledgeModelService:
    """
    Computes reliable, evidence-grounded Student Knowledge Profiles per topic.
    Combines aggregated TopicPerformance metrics, recent longitudinal event trends,
    and active ForgettingSignal states.
    """

    @staticmethod
    def calculate_topic_profile(
        db: Session,
        student_id: str,
        topic: Topic,
    ) -> TopicKnowledgeProfile:
        """
        Calculates an individual topic knowledge profile for a student.
        """
        # 1. Fetch live TopicPerformance record
        perf = (
            db.query(TopicPerformance)
            .filter(
                TopicPerformance.student_id == student_id,
                TopicPerformance.topic_id == topic.id,
            )
            .first()
        )

        total_attempts = perf.total_attempts if perf else 0
        correct_attempts = perf.correct_attempts if perf else 0
        accuracy = perf.accuracy if perf else 0.0
        avg_resp_time = perf.average_response_time if (perf and perf.average_response_time > 0) else None
        hint_count = perf.hint_usage_count if perf else 0
        last_act = perf.last_activity_at if perf else None
        last_succ = perf.last_success_at if perf else None

        # 2. Determine 4-tier mastery level
        # NOVICE (< 50% or < 3 attempts), DEVELOPING (50-69%), PROFICIENT (70-84%), MASTERED (>= 85% with >= 5 attempts)
        if total_attempts == 0:
            mastery = MasteryLevel.UNASSESSED
        elif total_attempts >= 5 and accuracy >= 85.0:
            mastery = MasteryLevel.MASTERED
        elif total_attempts >= 3 and accuracy >= 70.0:
            mastery = MasteryLevel.PROFICIENT
        elif total_attempts >= 3 and accuracy >= 50.0:
            mastery = MasteryLevel.DEVELOPING
        else:
            mastery = MasteryLevel.NOVICE

        # 3. Retrieve recent evaluative events for trend & recent accuracy
        eval_events = (
            db.query(LearningEvent)
            .filter(
                LearningEvent.student_id == student_id,
                LearningEvent.topic_id == topic.id,
                LearningEvent.correctness.isnot(None),
            )
            .order_by(LearningEvent.timestamp.asc())
            .all()
        )

        recent_accuracy: Optional[float] = None
        trend = PerformanceTrend.INSUFFICIENT_DATA

        if eval_events:
            # Recent window: up to the last 5 events
            recent_window = eval_events[-5:]
            recent_correct = sum(1 for e in recent_window if e.correctness is True)
            recent_accuracy = round((recent_correct / len(recent_window)) * 100.0, 2)

            # Trend calculation requires at least 4 evaluative interactions
            if len(eval_events) >= 4:
                half = len(eval_events) // 2
                prior_half = eval_events[:half]
                recent_half = eval_events[half:]

                prior_acc = (sum(1 for e in prior_half if e.correctness is True) / len(prior_half)) * 100.0
                recent_acc = (sum(1 for e in recent_half if e.correctness is True) / len(recent_half)) * 100.0

                acc_diff = recent_acc - prior_acc
                if acc_diff >= 15.0:
                    trend = PerformanceTrend.IMPROVING
                elif acc_diff <= -15.0:
                    trend = PerformanceTrend.DECLINING
                else:
                    trend = PerformanceTrend.STABLE

        # 4. Determine Retention Risk Level
        # Grounded strictly in empirical data:
        # HIGH: Active unresolved decay signal exists, or recent accuracy <= 30% with >= 3 attempts
        # MODERATE: Weak decay indicator exists or accuracy between 30% and 55%
        # LOW: Accuracy >= 70% with no active forgetting signals
        # UNASSESSED: No attempts
        if total_attempts == 0:
            retention_risk = RetentionRiskLevel.UNASSESSED
        else:
            active_signal = (
                db.query(ForgettingSignal)
                .filter(
                    ForgettingSignal.student_id == student_id,
                    ForgettingSignal.topic_id == topic.id,
                    ForgettingSignal.status == ForgettingSignalStatus.UNRESOLVED,
                )
                .first()
            )

            if active_signal:
                if active_signal.evidence_strength in ("STRONG", "MODERATE"):
                    retention_risk = RetentionRiskLevel.HIGH
                else:
                    retention_risk = RetentionRiskLevel.MODERATE
            elif (recent_accuracy is not None and recent_accuracy <= 30.0) or accuracy <= 30.0:
                retention_risk = RetentionRiskLevel.HIGH
            elif accuracy < 60.0:
                retention_risk = RetentionRiskLevel.MODERATE
            else:
                retention_risk = RetentionRiskLevel.LOW

        # 5. Extract Subject Name
        subject_name = "Science & Technology"
        if topic.chapter and topic.chapter.subject:
            subject_name = topic.chapter.subject.name

        return TopicKnowledgeProfile(
            topic_id=topic.id,
            topic_title=topic.title,
            subject_name=subject_name,
            mastery_level=mastery,
            accuracy=accuracy,
            total_attempts=total_attempts,
            correct_attempts=correct_attempts,
            recent_accuracy=recent_accuracy,
            trend=trend,
            retention_risk=retention_risk,
            average_response_time_ms=avg_resp_time,
            hint_usage_count=hint_count,
            last_activity_at=last_act,
            last_success_at=last_succ,
            learning_pace=None,  # Intentionally null/unassessed until duration model baseline is calibrated
            current_difficulty=None,  # Intentionally null until question bank difficulty metadata is attached
        )

    @staticmethod
    def get_student_knowledge_profiles(
        db: Session,
        student_id: str,
        topic_id: Optional[str] = None,
    ) -> StudentKnowledgeProfileResponse:
        """
        Retrieves all active topic knowledge profiles for a student.
        If topic_id is provided, returns profile specifically for that topic.
        Otherwise, returns profiles for all topics with activity or across standard curriculum.
        """
        if topic_id:
            from backend.app.api.v1.endpoints.attempts import _resolve_topic
            resolved_topic = _resolve_topic(db, topic_id)
            topics_to_evaluate = [resolved_topic] if resolved_topic else []
        else:
            # First find topics that have activity for this student
            perf_topic_ids = [
                row[0] for row in
                db.query(TopicPerformance.topic_id)
                .filter(TopicPerformance.student_id == student_id)
                .all()
            ]
            if perf_topic_ids:
                topics_to_evaluate = (
                    db.query(Topic)
                    .filter(Topic.id.in_(perf_topic_ids))
                    .order_by(Topic.topic_order.asc())
                    .all()
                )
            else:
                topics_to_evaluate = []

        profiles = [
            KnowledgeModelService.calculate_topic_profile(db, student_id, t)
            for t in topics_to_evaluate
        ]

        return StudentKnowledgeProfileResponse(
            student_id=student_id,
            total_topics_tracked=len(profiles),
            profiles=profiles,
        )
