from datetime import datetime, timedelta, timezone
from typing import List, Optional
from backend.app.domain.enums import RevisionPriority
from backend.app.domain.constants import (
    EVIDENCE_STRENGTH_STRONG,
    EVIDENCE_STRENGTH_MODERATE,
    EVIDENCE_STRENGTH_WEAK,
)
from backend.app.domain.decay_engine.schemas import DecaySignalDraft, RevisionScheduleDraft
from backend.app.models.performance import TopicPerformance


class SpacedRepetitionScheduler:
    """
    Computes personalized revision schedules using an initial deterministic baseline policy.
    
    IMPORTANT RESEARCH NOTE:
    The interval progression [1d, 3d, 7d, 14d, 30d] is an initial deterministic operational
    baseline, NOT an empirically calibrated optimal cognitive schedule. It provides an
    auditable, reproducible reference policy for longitudinal comparison and optimization.
    """

    BASELINE_INTERVALS_DAYS = [1, 3, 7, 14, 30]

    @classmethod
    def schedule_from_signal(
        cls,
        signal: DecaySignalDraft,
        topic_perf: Optional[TopicPerformance] = None,
        now: Optional[datetime] = None
    ) -> RevisionScheduleDraft:
        now = now or datetime.now(timezone.utc)

        # Map derived evidence strength to baseline urgency and scheduling offset
        if signal.evidence_strength == EVIDENCE_STRENGTH_STRONG:
            priority = RevisionPriority.URGENT
            offset_days = 1
            reason = (
                f"Urgent revision recommended due to strong empirical decay evidence "
                f"({signal.evidence_type}) with substantial performance deterioration."
            )
        elif signal.evidence_strength == EVIDENCE_STRENGTH_MODERATE:
            priority = RevisionPriority.HIGH
            offset_days = 3
            reason = (
                f"High priority revision recommended due to moderate decay evidence "
                f"({signal.evidence_type}) after an extended inactive interval."
            )
        else:
            priority = RevisionPriority.MEDIUM
            offset_days = 7
            reason = (
                f"Medium priority revision recommended based on preliminary or weak decay indicators "
                f"({signal.evidence_type})."
            )

        recommended_at = now + timedelta(days=offset_days)

        return RevisionScheduleDraft(
            student_id=signal.student_id,
            topic_id=signal.topic_id,
            recommended_revision_at=recommended_at,
            priority=priority,
            reason=f"[Baseline Policy] {reason}",
            signal_fingerprint=signal.episode_fingerprint,
        )

    @classmethod
    def schedule_baseline_maintenance(
        cls,
        student_id: str,
        topic_id: str,
        topic_perf: TopicPerformance,
        now: Optional[datetime] = None
    ) -> RevisionScheduleDraft:
        """
        Schedules next routine review step in the initial deterministic [1, 3, 7, 14, 30] sequence.
        """
        now = now or datetime.now(timezone.utc)
        step_idx = min(topic_perf.revision_count, len(cls.BASELINE_INTERVALS_DAYS) - 1)
        interval_days = cls.BASELINE_INTERVALS_DAYS[step_idx]

        priority = RevisionPriority.LOW if step_idx >= 3 else RevisionPriority.MEDIUM
        recommended_at = now + timedelta(days=interval_days)

        return RevisionScheduleDraft(
            student_id=student_id,
            topic_id=topic_id,
            recommended_revision_at=recommended_at,
            priority=priority,
            reason=(
                f"[Baseline Policy] Scheduled maintenance review step {step_idx + 1} "
                f"({interval_days}-day interval) for topic in {topic_perf.mastery_state} state."
            ),
        )
