"""
EduNavika — Milestone 5.2: Official Answer-Key Reconciliation Service.
Provides auditable, deterministic matching of extracted competitive questions to
authoritative official answer keys (NTA / IIT JEE).
Maintains full audit trails, supports revised keys, dropped/bonus items,
multiple-correct options, and numerical answer tolerances without fabricating data.
"""

import re
import uuid
import logging
from typing import Dict, Any, List, Optional, Tuple, Set
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from backend.app.models.competitive_models import (
    Examination,
    ExamPaper,
    Question,
    QuestionOption,
    QuestionVerificationLog,
)

logger = logging.getLogger(__name__)


class ReconciliationError(Exception):
    """Raised when answer-key reconciliation encounters unresolvable ambiguities."""
    pass


class AnswerKeyReconciliationService:
    def __init__(self, db: Session):
        self.db = db

    @staticmethod
    def validate_manifest_schema(manifest: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validates that an answer-key manifest conforms to the required provenance schema.
        Must declare authority, exam, year, paper code/session, key version, and item answers.
        """
        errors = []
        required_fields = [
            "manifest_version",
            "exam_code",
            "exam_year",
            "paper_session",
            "authority",
            "official_document_ref",
            "key_version",
            "answers",
        ]
        for f in required_fields:
            if not manifest.get(f):
                errors.append(f"Missing required manifest field: '{f}'")

        exam_code = manifest.get("exam_code")
        if exam_code not in ("JEE_MAIN", "JEE_ADVANCED", "NEET_UG"):
            errors.append(f"Invalid exam_code: '{exam_code}'")

        answers = manifest.get("answers", {})
        if not isinstance(answers, dict) or len(answers) == 0:
            errors.append("Manifest 'answers' must be a non-empty dictionary keyed by question number")

        return len(errors) == 0, errors

    @staticmethod
    def normalize_official_answer(
        raw_answer: Any,
        question_type: str,
        official_status: str = "REGULAR",
    ) -> Dict[str, Any]:
        """
        Normalizes raw answer key strings into standardized representations:
        - SCQ: single uppercase letter 'A', 'B', 'C', or 'D'.
        - MCQ_MULTI: sorted list of valid letters, e.g. ['A', 'C'].
        - NUMERICAL: min_val, max_val, and precision bounds.
        - DROPPED/BONUS: flags official status without forcing an option key.
        """
        status_clean = (official_status or "REGULAR").upper().strip()
        if status_clean in ("DROPPED", "BONUS", "CANCELLED", "WITHDRAWN"):
            return {
                "normalized_answer": None,
                "correct_options": [],
                "is_dropped": True,
                "official_status": "DROPPED" if status_clean != "BONUS" else "BONUS",
                "numerical_min": None,
                "numerical_max": None,
                "tolerance_epsilon": None,
                "notes": f"Item officially marked as {status_clean} by conducting authority.",
            }

        # 1. SCQ Normalization
        if question_type in ("SCQ", "ASSERTION_REASON", "MATCH"):
            val_str = str(raw_answer).strip().upper()
            # Handle numeric option keys (e.g. 1 -> A, 2 -> B in NEET)
            num_map = {"1": "A", "2": "B", "3": "C", "4": "D"}
            norm_key = num_map.get(val_str, val_str)
            if norm_key not in ("A", "B", "C", "D"):
                raise ValueError(f"Invalid SCQ official answer representation: '{raw_answer}'")
            return {
                "normalized_answer": norm_key,
                "correct_options": [norm_key],
                "is_dropped": False,
                "official_status": "REGULAR",
                "numerical_min": None,
                "numerical_max": None,
                "tolerance_epsilon": None,
                "notes": f"Single correct option: [{norm_key}]",
            }

        # 2. MCQ_MULTI Normalization
        elif question_type == "MCQ_MULTI":
            if isinstance(raw_answer, list):
                raw_opts = raw_answer
            elif isinstance(raw_answer, str):
                # Split on comma, slash, space, or 'or'
                cleaned_str = raw_answer.replace("OR", ",").replace("/", ",")
                raw_opts = [part.strip().upper() for part in cleaned_str.split(",") if part.strip()]
            else:
                raw_opts = [str(raw_answer).strip().upper()]

            num_map = {"1": "A", "2": "B", "3": "C", "4": "D"}
            norm_opts = sorted(list(set(num_map.get(o, o) for o in raw_opts if o)))
            for o in norm_opts:
                if o not in ("A", "B", "C", "D"):
                    raise ValueError(f"Invalid option key '{o}' in MCQ_MULTI answer: '{raw_answer}'")

            if len(norm_opts) == 0:
                raise ValueError("MCQ_MULTI answer must specify at least one correct option")

            return {
                "normalized_answer": ", ".join(norm_opts),
                "correct_options": norm_opts,
                "is_dropped": False,
                "official_status": "REGULAR",
                "numerical_min": None,
                "numerical_max": None,
                "tolerance_epsilon": None,
                "notes": f"Multiple correct options: {norm_opts}",
            }

        # 3. NUMERICAL Normalization
        elif question_type == "NUMERICAL":
            if isinstance(raw_answer, dict):
                min_v = float(raw_answer.get("min_val", raw_answer.get("value", 0.0)))
                max_v = float(raw_answer.get("max_val", raw_answer.get("value", 0.0)))
                eps = float(raw_answer.get("epsilon", 0.01))
            elif isinstance(raw_answer, (int, float)):
                min_v = float(raw_answer)
                max_v = float(raw_answer)
                eps = 0.01
            elif isinstance(raw_answer, str):
                # Check for range: e.g. "12.4 to 12.6" or "12.4 - 12.6"
                m_range = re.search(r'([\d\.\-]+)\s*(?:to|-)\s*([\d\.\-]+)', raw_answer)
                if m_range:
                    min_v = float(m_range.group(1))
                    max_v = float(m_range.group(2))
                    eps = 0.01
                else:
                    val = float(raw_answer.strip())
                    min_v = val
                    max_v = val
                    eps = 0.01
            else:
                raise ValueError(f"Invalid NUMERICAL official answer representation: '{raw_answer}'")

            if min_v > max_v:
                raise ValueError(f"numerical min_val ({min_v}) cannot exceed max_val ({max_v})")

            norm_str = f"{min_v:.2f}" if min_v == max_v else f"[{min_v:.2f}, {max_v:.2f}]"
            return {
                "normalized_answer": norm_str,
                "correct_options": [],
                "is_dropped": False,
                "official_status": "REGULAR",
                "numerical_min": min_v,
                "numerical_max": max_v,
                "tolerance_epsilon": eps,
                "notes": f"Numerical acceptable range: {norm_str}",
            }

        return {
            "normalized_answer": str(raw_answer).strip(),
            "correct_options": [],
            "is_dropped": False,
            "official_status": "REGULAR",
            "numerical_min": None,
            "numerical_max": None,
            "tolerance_epsilon": None,
            "notes": "Standard answer recorded",
        }

    def reconcile_question_record(
        self,
        question: Question,
        manifest_entry: Dict[str, Any],
        manifest_meta: Dict[str, Any],
        reviewer: str = "pipeline:official_key_reconciler",
    ) -> Dict[str, Any]:
        """
        Reconciles a single extracted Question with its corresponding official answer-key entry.
        Transitions state, updates options, creates audit log, and resolves scoring eligibility.
        """
        raw_ans = manifest_entry.get("official_raw_answer")
        declared_q_type = manifest_entry.get("question_type", question.question_type)
        declared_status = manifest_entry.get("action", "REGULAR")

        # 1. Structural Compatibility Check
        structural_mismatch = False
        if declared_q_type != question.question_type:
            # If extracted structure conflicts fundamentally (e.g. SCQ with 4 options vs NUMERICAL in key)
            if (declared_q_type == "NUMERICAL" and len(question.options) > 0) or \
               (declared_q_type in ("SCQ", "MCQ_MULTI") and len(question.options) == 0):
                structural_mismatch = True

        if structural_mismatch:
            prev_status = question.verification_status
            question.quarantine_status = "FLAGGED_MALFORMED"
            question.quarantine_reason = f"STRUCTURAL_MISMATCH: Extracted as {question.question_type}, official key expects {declared_q_type}"
            question.eligibility_for_scoring = "INELIGIBLE_MALFORMED"
            question.verification_status = "PENDING_OFFICIAL_KEY_RECONCILIATION"

            log = QuestionVerificationLog(
                id=str(uuid.uuid4()),
                question_id=question.id,
                verified_by=reviewer,
                previous_status=prev_status,
                new_status="FLAGGED_MALFORMED",
                action_type="RECONCILIATION_FLAGGED",
                review_notes=question.quarantine_reason,
                reviewed_at=datetime.now(timezone.utc),
            )
            self.db.add(log)
            return {
                "question_id": question.id,
                "status": "FLAGGED_STRUCTURAL_MISMATCH",
                "details": question.quarantine_reason,
            }

        # 2. Normalize Answer Representation
        norm = self.normalize_official_answer(raw_ans, question.question_type, declared_status)

        prev_answer = question.correct_answer_raw
        prev_eligibility = question.eligibility_for_scoring
        is_revision = (question.answer_verification_status != "UNVERIFIED" and prev_answer != norm["normalized_answer"])

        # 3. Update Question Entity
        question.correct_answer_raw = norm["normalized_answer"]
        question.scoring_policy_version = manifest_meta.get("key_version", "OFFICIAL_FINAL_V1")
        question.scoring_policy_source = manifest_meta.get("official_document_ref", "Official Conducting Authority Key")
        question.official_status = norm["official_status"]

        if norm["numerical_min"] is not None:
            question.numerical_min_val = norm["numerical_min"]
            question.numerical_max_val = norm["numerical_max"]
            question.numerical_tolerance_epsilon = norm["tolerance_epsilon"]

        # 4. Synchronize Option Correctness
        if len(question.options) > 0 and norm["correct_options"]:
            corr_set = set(norm["correct_options"])
            for opt in question.options:
                opt.is_correct = (opt.option_key in corr_set)

        # 5. Evaluate Eligibility for Scoring
        if norm["is_dropped"]:
            question.answer_verification_status = "OFFICIAL_KEY_VERIFIED"
            question.eligibility_for_scoring = "INELIGIBLE_DROPPED"
            question.verification_status = "VERIFIED"
            action_type = "ITEM_DROPPED_NOTICE"
            review_note = f"Authority declared question as {norm['official_status']}. Ineligible for standard scoring."
        elif question.quarantine_status == "CLEAN":
            question.answer_verification_status = "OFFICIAL_KEY_VERIFIED"
            # State Machine Guard: Question content must be verified before scoring promotion
            content_is_verified = question.verification_status in (
                "CONTENT_VERIFIED", "VERIFIED", "HUMAN_VERIFIED", "ALGORITHMICALLY_VERIFIED"
            )
            if content_is_verified:
                question.eligibility_for_scoring = "ELIGIBLE_FOR_SCORING"
                question.verification_status = "VERIFIED"
                action_type = "KEY_REVISED" if is_revision else "OFFICIAL_KEY_RECONCILED"
                review_note = f"Matched against {manifest_meta.get('authority', 'Authority')} Key {manifest_meta.get('key_version', 'v1')}. Normalized answer: {norm['normalized_answer']}."
            else:
                question.eligibility_for_scoring = "INELIGIBLE_UNVERIFIED_CONTENT"
                action_type = "KEY_RECONCILED_AWAITING_CONTENT_VERIFICATION"
                review_note = f"Key confirmed ({norm['normalized_answer']}), but content verification is pending ({question.verification_status}). Ineligible for scoring."
        else:
            question.answer_verification_status = "OFFICIAL_KEY_VERIFIED"
            question.eligibility_for_scoring = "INELIGIBLE_MALFORMED"
            action_type = "KEY_RECONCILED_QUARANTINED"
            review_note = f"Key confirmed ({norm['normalized_answer']}), but question remains quarantined: {question.quarantine_reason}."

        # 6. Audit Trail: QuestionVerificationLog
        log_entry = QuestionVerificationLog(
            id=str(uuid.uuid4()),
            question_id=question.id,
            verified_by=f"{reviewer}:{manifest_meta.get('authority', 'Authority')}",
            previous_status=f"ANS:{prev_answer or 'NONE'}|ELIG:{prev_eligibility}",
            new_status=f"ANS:{question.correct_answer_raw}|ELIG:{question.eligibility_for_scoring}",
            action_type=action_type,
            review_notes=review_note,
            reviewed_at=datetime.now(timezone.utc),
        )
        self.db.add(log_entry)
        self.db.flush()

        return {
            "question_id": question.id,
            "status": "SUCCESS",
            "action_type": action_type,
            "normalized_answer": norm["normalized_answer"],
            "eligibility_for_scoring": question.eligibility_for_scoring,
            "is_revision": is_revision,
        }

    def reconcile_paper_batch(
        self,
        paper_id: str,
        manifest: Dict[str, Any],
        reviewer: str = "pipeline:official_key_reconciler",
        dry_run: bool = True,
    ) -> Dict[str, Any]:
        """
        Reconciles all questions of an ExamPaper against an official answer-key manifest.
        Strictly rejects ambiguous booklet-code or numbering mismatches.
        If dry_run=True, rolls back all database mutations.
        """
        is_valid, errors = self.validate_manifest_schema(manifest)
        if not is_valid:
            raise ValueError(f"Invalid answer-key manifest: {'; '.join(errors)}")

        paper = self.db.query(ExamPaper).filter(ExamPaper.id == paper_id).first()
        if not paper:
            raise ValueError(f"ExamPaper with ID '{paper_id}' not found.")

        # 1. Provenance & Booklet Code Verification
        if paper.exam_code != manifest["exam_code"]:
            raise ValueError(f"Exam code mismatch: Paper is '{paper.exam_code}', manifest is '{manifest['exam_code']}'")

        if paper.exam_year != manifest["exam_year"]:
            raise ValueError(f"Exam year mismatch: Paper is {paper.exam_year}, manifest is {manifest['exam_year']}")

        # Booklet code check (prevent permuted question numbering cross-contamination)
        paper_code = manifest.get("paper_code")
        if paper_code and paper.paper_code and paper.paper_code != paper_code:
            raise ReconciliationError(
                f"AMBIGUOUS_BOOKLET_CODE: Paper has booklet code '{paper.paper_code}', "
                f"manifest specifies '{paper_code}'. Permuted question sets must not be cross-matched."
            )

        manifest_answers = manifest["answers"]
        questions = self.db.query(Question).filter(Question.exam_paper_id == paper_id).all()

        results = {
            "dry_run": dry_run,
            "paper_id": paper_id,
            "paper_identifier": paper.paper_identifier,
            "total_questions_in_paper": len(questions),
            "manifest_items_count": len(manifest_answers),
            "reconciled_count": 0,
            "unmatched_count": 0,
            "revised_count": 0,
            "dropped_count": 0,
            "promoted_to_eligible_count": 0,
            "quarantined_count": 0,
            "detailed_reports": [],
        }

        for q in questions:
            q_num_str = str(q.paper_question_number)
            if q_num_str in manifest_answers:
                item_spec = manifest_answers[q_num_str]
                res = self.reconcile_question_record(
                    question=q,
                    manifest_entry=item_spec,
                    manifest_meta=manifest,
                    reviewer=reviewer,
                )
                results["reconciled_count"] += 1
                if res.get("is_revision"):
                    results["revised_count"] += 1
                if res.get("eligibility_for_scoring") == "ELIGIBLE_FOR_SCORING":
                    results["promoted_to_eligible_count"] += 1
                elif res.get("eligibility_for_scoring") == "INELIGIBLE_DROPPED":
                    results["dropped_count"] += 1
                elif res.get("status") == "FLAGGED_STRUCTURAL_MISMATCH":
                    results["quarantined_count"] += 1
                results["detailed_reports"].append(res)
            else:
                # Question has no match in official key -> MUST remain unverified
                results["unmatched_count"] += 1
                results["detailed_reports"].append({
                    "question_id": q.id,
                    "paper_question_number": q.paper_question_number,
                    "status": "UNMATCHED_NO_OFFICIAL_KEY_SPECIFIED",
                })

        if dry_run:
            self.db.rollback()
        else:
            self.db.commit()

        return results
