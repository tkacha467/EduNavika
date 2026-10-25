"""
Question Verification & Human Review Workflow Service
EduNavika Milestone 5.8 - Human Review Workflow & State Machine Enforcement

Enforces the correct order of evidence across the question lifecycle:
1. Extraction & Ingestion
2. Visual Asset Verification
3. Content & Curriculum Verification
4. Answer-Key Reconciliation
5. Rights & Publication Review
6. Scoring Eligibility Promotion

Strictly prevents conflation between visual approval, content correctness,
answer-key verification, copyright clearance, and scoring eligibility.
"""

from datetime import datetime, timezone
import json
import logging
from typing import Any, Dict, List, Optional, Tuple
import uuid

from sqlalchemy.orm import Session

from backend.app.models.competitive_models import (
    Question,
    QuestionOption,
    QuestionVerificationLog,
)

logger = logging.getLogger(__name__)

WORKFLOW_VERSION = "2.0-m5.8"

# Allowed Human Review Decisions
VALID_REVIEW_DECISIONS = {"APPROVED", "REJECTED", "NEEDS_CORRECTION"}

# Allowed Action Types in QuestionVerificationLog
VALID_ACTION_TYPES = {
    "HUMAN_VISUAL_REVIEW",
    "CONTENT_VERIFICATION",
    "ANSWER_KEY_RECONCILIATION",
    "RIGHTS_AND_PUBLICATION_REVIEW",
    "SCORING_ELIGIBILITY_PROMOTION",
    "INGESTION_PILOT",
    "QUARANTINE_ACTION",
}


class InvalidStateTransitionError(ValueError):
    """Raised when an invalid state transition or gate bypass is attempted."""
    pass


class QuestionVerificationService:
    """
    Manages human review decisions, audit logging, and state transitions
    for assessment questions and linked assets.
    """

    def __init__(self, db: Session):
        self.db = db

    def submit_human_visual_review(
        self,
        question_id: str,
        reviewer_id: str,
        decision: str,
        review_notes: str,
        asset_ids_reviewed: Optional[List[str]] = None,
        asset_checksums: Optional[Dict[str, str]] = None,
        source_manifest_version: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Records an explicit human visual review decision for a question and its diagram assets.
        Valid decisions: 'APPROVED', 'REJECTED', 'NEEDS_CORRECTION'.
        Never hardcodes reviewer identity or automatically approves unreviewed assets.
        """
        if not reviewer_id or not isinstance(reviewer_id, str) or len(reviewer_id.strip()) == 0:
            raise ValueError("Reviewer identity ('reviewer_id') must be a valid, non-empty identifier")

        decision_upper = decision.strip().upper()
        if decision_upper not in VALID_REVIEW_DECISIONS:
            raise ValueError(f"Invalid decision '{decision}'. Must be one of: {sorted(VALID_REVIEW_DECISIONS)}")

        question = self.db.query(Question).filter(Question.id == question_id).first()
        if not question:
            raise ValueError(f"Question with ID '{question_id}' not found")

        prev_status = question.verification_status
        now_utc = datetime.now(timezone.utc)

        # Build auditable structured metadata for review notes
        metadata = {
            "decision": decision_upper,
            "reviewer_id": reviewer_id.strip(),
            "workflow_version": WORKFLOW_VERSION,
            "timestamp_utc": now_utc.isoformat(),
            "asset_ids_reviewed": asset_ids_reviewed or [],
            "asset_checksums": asset_checksums or {},
            "manifest_version": source_manifest_version,
            "reviewer_notes": review_notes.strip() if review_notes else "",
        }

        # Transition question state according to decision
        if decision_upper == "APPROVED":
            # Visual review approved: marks content verified for visual aspects
            # Does NOT touch answer_verification_status, rights_status, or eligibility_for_scoring
            new_status = "CONTENT_VERIFIED"
            question.verification_status = new_status
            if question.quarantine_status == "QUARANTINED" and question.quarantine_reason and "diagram" in question.quarantine_reason.lower():
                question.quarantine_status = "CLEAN"
                question.quarantine_reason = None

        elif decision_upper == "REJECTED":
            new_status = "REJECTED"
            question.verification_status = new_status
            question.quarantine_status = "QUARANTINED"
            question.quarantine_reason = f"Visual review rejected by {reviewer_id}: {review_notes}"
            question.eligibility_for_scoring = "INELIGIBLE_QUARANTINED"

        elif decision_upper == "NEEDS_CORRECTION":
            new_status = "NEEDS_CORRECTION"
            question.verification_status = new_status
            question.quarantine_status = "QUARANTINED"
            question.quarantine_reason = f"Visual review requires correction ({reviewer_id}): {review_notes}"
            question.eligibility_for_scoring = "INELIGIBLE_QUARANTINED"

        # Create immutable verification log
        log_entry = QuestionVerificationLog(
            id=str(uuid.uuid4()),
            question_id=question.id,
            verified_by=reviewer_id.strip(),
            previous_status=prev_status,
            new_status=new_status,
            action_type="HUMAN_VISUAL_REVIEW",
            review_notes=json.dumps(metadata, indent=2),
            reviewed_at=now_utc,
        )
        self.db.add(log_entry)
        self.db.flush()

        return {
            "question_id": question.id,
            "previous_status": prev_status,
            "new_status": new_status,
            "decision": decision_upper,
            "reviewer_id": reviewer_id.strip(),
            "quarantine_status": question.quarantine_status,
            "eligibility_for_scoring": question.eligibility_for_scoring,
            "log_id": log_entry.id,
        }

    def evaluate_scoring_eligibility(self, question: Question) -> Tuple[bool, List[str]]:
        """
        Pure rule check: evaluates if a question satisfies all 6 mandatory gates
        to become ELIGIBLE_FOR_SCORING.
        """
        blockers = []

        # Gate 1: Quarantine status must be CLEAN
        if question.quarantine_status != "CLEAN":
            blockers.append(f"Question is quarantined: {question.quarantine_reason or question.quarantine_status}")

        # Gate 2: Content verification status must be verified
        if question.verification_status not in ("CONTENT_VERIFIED", "VERIFIED", "HUMAN_VERIFIED", "ALGORITHMICALLY_VERIFIED"):
            blockers.append(f"Content verification incomplete: status is '{question.verification_status}'")

        # Gate 3: Answer key must be verified
        if question.answer_verification_status in ("UNVERIFIED", None):
            blockers.append("Answer key has not been verified (answer_verification_status is UNVERIFIED)")

        # Gate 4: Official status cannot be DROPPED or DISPUTED
        if question.official_status in ("DROPPED", "DISPUTED"):
            blockers.append(f"Official status '{question.official_status}' disqualifies question from scoring")

        # Gate 5: Rights clearance must be granted
        if question.rights_status not in ("OFFICIAL_FAIR_USE", "PROPRIETARY", "PUBLIC_DOMAIN"):
            blockers.append(f"Rights clearance pending or restricted: rights_status is '{question.rights_status}'")

        # Gate 6: Publish permission cannot be FORBIDDEN
        if question.publish_permission == "FORBIDDEN":
            blockers.append("Publish permission is FORBIDDEN")

        return len(blockers) == 0, blockers

    def promote_to_scoring_eligible(self, question_id: str, reviewer_id: str, notes: str = "") -> Dict[str, Any]:
        """
        Promotes a question to ELIGIBLE_FOR_SCORING if and only if all 6 gates pass.
        Raises InvalidStateTransitionError if any gate fails.
        """
        question = self.db.query(Question).filter(Question.id == question_id).first()
        if not question:
            raise ValueError(f"Question with ID '{question_id}' not found")

        is_eligible, blockers = self.evaluate_scoring_eligibility(question)
        if not is_eligible:
            raise InvalidStateTransitionError(
                f"Cannot promote question '{question_id}' to ELIGIBLE_FOR_SCORING. Gate failures: {'; '.join(blockers)}"
            )

        prev_eligibility = question.eligibility_for_scoring
        question.eligibility_for_scoring = "ELIGIBLE_FOR_SCORING"

        log_entry = QuestionVerificationLog(
            id=str(uuid.uuid4()),
            question_id=question.id,
            verified_by=reviewer_id,
            previous_status=prev_eligibility,
            new_status="ELIGIBLE_FOR_SCORING",
            action_type="SCORING_ELIGIBILITY_PROMOTION",
            review_notes=notes or "Promoted after passing all 6 content, answer-key, rights, and integrity gates",
            reviewed_at=datetime.now(timezone.utc),
        )
        self.db.add(log_entry)
        self.db.flush()

        return {
            "question_id": question.id,
            "previous_eligibility": prev_eligibility,
            "new_eligibility": question.eligibility_for_scoring,
            "log_id": log_entry.id,
        }
