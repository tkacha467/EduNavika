import hashlib
from typing import Optional
from sqlalchemy.orm import Session
from backend.app.models.forgetting import ForgettingSignal
from backend.app.models.revision import RevisionPlan
from backend.app.domain.enums import ForgettingSignalStatus, RevisionCompletionState


class SignalDeduplicator:
    """
    Ensures idempotency in longitudinal decay analysis.
    Prevents duplicate ForgettingSignal and RevisionPlan records when
    detection is invoked multiple times over identical event histories.
    """

    @staticmethod
    def generate_fingerprint(
        student_id: str,
        topic_id: str,
        evidence_type: str,
        latest_event_iso: str
    ) -> str:
        raw = f"{student_id}:{topic_id}:{evidence_type}:{latest_event_iso}"
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]

    @staticmethod
    def is_duplicate_signal(
        db: Session,
        student_id: str,
        topic_id: str,
        fingerprint: str
    ) -> bool:
        """
        Returns True if an unresolved signal with this fingerprint
        or an unresolved active signal for the same topic already exists.
        """
        # 1. Direct fingerprint match in metadata
        existing_signals = (
            db.query(ForgettingSignal)
            .filter(
                ForgettingSignal.student_id == student_id,
                ForgettingSignal.topic_id == topic_id,
                ForgettingSignal.status == ForgettingSignalStatus.UNRESOLVED
            )
            .all()
        )
        
        for sig in existing_signals:
            meta = sig.evidence_metadata or {}
            if meta.get("episode_fingerprint") == fingerprint:
                return True
            # Also deduplicate if there's already an active unresolved signal for the same topic
            # that was detected within the same temporal episode
            if meta.get("latest_event_iso") == fingerprint.split(":")[-1]:
                return True

        return False

    @staticmethod
    def has_pending_revision_plan(
        db: Session,
        student_id: str,
        topic_id: str
    ) -> bool:
        """
        Checks if a pending revision plan already exists for this student and topic.
        Prevents flooding the student's queue with multiple pending plans for the same topic.
        """
        pending = (
            db.query(RevisionPlan)
            .filter(
                RevisionPlan.student_id == student_id,
                RevisionPlan.topic_id == topic_id,
                RevisionPlan.completion_state == RevisionCompletionState.PENDING
            )
            .first()
        )
        return pending is not None
