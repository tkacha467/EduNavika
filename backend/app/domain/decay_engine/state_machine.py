from datetime import datetime, timezone
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy.orm.attributes import flag_modified
from backend.app.models import ForgettingSignal
from backend.app.models import RevisionPlan
from backend.app.models import TopicPerformance
from backend.app.domain.enums import ForgettingSignalStatus, RevisionCompletionState


class SignalLifecycleStateMachine:
    """
    Manages the lifecycle transitions of ForgettingSignal and RevisionPlan records.
    
    IMPORTANT RESEARCH SAFEGUARD:
    Explicitly separates immediate *successful retrieval* from *durable retention*.
    A single revision score >= 80% marks the immediate revision task as completed,
    but signal resolution requires documented retrieval success and maintains
    the longitudinal evidence trail.
    """

    @staticmethod
    def process_revision_outcome(
        db: Session,
        student_id: str,
        topic_id: str,
        score: float,
        correctness: bool,
        response_time_ms: Optional[int] = None,
        now: Optional[datetime] = None
    ) -> Dict[str, Any]:
        now = now or datetime.now(timezone.utc)
        result = {
            "plans_updated": 0,
            "signals_resolved": 0,
            "signals_retained_unresolved": 0,
            "retrieval_success": correctness and (score >= 80.0),
        }

        # 1. Update pending RevisionPlans for this student & topic
        pending_plans = (
            db.query(RevisionPlan)
            .filter(
                RevisionPlan.student_id == student_id,
                RevisionPlan.topic_id == topic_id,
                RevisionPlan.completion_state == RevisionCompletionState.PENDING
            )
            .all()
        )

        for plan in pending_plans:
            plan.completion_state = RevisionCompletionState.COMPLETED
            plan.reason = (
                f"{plan.reason or ''} | Revision executed on {now.strftime('%Y-%m-%d')}: "
                f"score={score}%, correct={correctness} (Retrieval session completed)."
            )
            result["plans_updated"] += 1

        # 2. Evaluate active UNRESOLVED ForgettingSignals
        unresolved_signals = (
            db.query(ForgettingSignal)
            .filter(
                ForgettingSignal.student_id == student_id,
                ForgettingSignal.topic_id == topic_id,
                ForgettingSignal.status == ForgettingSignalStatus.UNRESOLVED
            )
            .all()
        )

        for sig in unresolved_signals:
            meta = sig.evidence_metadata or {}
            resolution_log = meta.get("resolution_history", [])
            resolution_log.append({
                "timestamp": now.isoformat(),
                "score": score,
                "correctness": correctness,
                "response_time_ms": response_time_ms,
                "assessment": "SUCCESSFUL_RETRIEVAL" if result["retrieval_success"] else "FAILED_RETRIEVAL",
            })
            meta["resolution_history"] = resolution_log

            # Only transition to ADDRESSED_BY_REVISION if retrieval was successful
            if result["retrieval_success"]:
                sig.status = ForgettingSignalStatus.ADDRESSED_BY_REVISION
                meta["resolved_at"] = now.isoformat()
                meta["resolution_notes"] = (
                    "Addressed via successful retrieval revision session. "
                    "Longitudinal stability subject to ongoing observation."
                )
                result["signals_resolved"] += 1
            else:
                # Retain UNRESOLVED; retrieval failed during revision
                sig.status = ForgettingSignalStatus.UNRESOLVED
                meta["latest_failed_revision_at"] = now.isoformat()
                result["signals_retained_unresolved"] += 1

            sig.evidence_metadata = dict(meta)
            flag_modified(sig, "evidence_metadata")

        db.flush()
        return result
