"""
EduNavika Competitive Examination Question Ingestion Service.
Supports JEE Main, JEE Advanced, and NEET UG with strict mathematical validation,
source provenance, rights management, dropped-item exclusion, and idempotent processing.
"""

import hashlib
import uuid
import re
import logging
from typing import List, Dict, Any, Optional, Tuple

from sqlalchemy.orm import Session
from sqlalchemy import text

from backend.app.models.competitive_models import (
    Examination,
    ExamPaper,
    Question,
    QuestionOption,
    QuestionVerificationLog,
)
from backend.app.models.curriculum_models import Topic

logger = logging.getLogger(__name__)


def compute_content_hash(
    question_text: str,
    options: List[Dict[str, Any]],
    correct_answer: Optional[str],
    stem_diagram_url: Optional[str] = None,
) -> str:
    """
    Computes deterministic SHA-256 hash for deduplication based on normalized text, diagrams, and options.
    Preserves exact backward compatibility for questions without diagram assets.
    """
    norm_text = re.sub(r'\s+', ' ', question_text.strip().lower())
    norm_stem_diag = (stem_diagram_url or "").strip().lower()
    norm_opts = []
    has_diagrams = bool(norm_stem_diag)
    for opt in sorted(options, key=lambda x: x.get("option_key", "")):
        key = opt.get("option_key", "").strip().upper()
        txt = re.sub(r'\s+', ' ', opt.get("option_text", "").strip().lower())
        diag = (opt.get("diagram_asset_url") or "").strip().lower()
        if diag:
            has_diagrams = True
            norm_opts.append(f"{key}:{txt}[diag:{diag}]")
        else:
            norm_opts.append(f"{key}:{txt}")
    norm_ans = (correct_answer or "").strip().upper()
    if has_diagrams:
        payload = f"{norm_text}|stem_diag:{norm_stem_diag}|{'#'.join(norm_opts)}|{norm_ans}"
    else:
        payload = f"{norm_text}|{'#'.join(norm_opts)}|{norm_ans}"
    return hashlib.sha256(payload.encode('utf-8')).hexdigest()



def validate_katex_syntax(text: str) -> bool:
    """Checks for balanced LaTeX inline ($) and display ($$) math delimiters."""
    # Count $$ (display blocks)
    display_matches = len(re.findall(r'\$\$', text))
    if display_matches % 2 != 0:
        return False
    # Remove display math and count remaining single $
    cleaned = re.sub(r'\$\$', '', text)
    inline_matches = len(re.findall(r'(?<!\\)\$', cleaned))
    return inline_matches % 2 == 0


class QuestionIngestionService:
    def __init__(self, db: Session):
        self.db = db

    def validate_question_data(self, q: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Runs the 10-Point Automated Validation Gate on a raw question dictionary.
        Returns (is_valid, list_of_errors).
        """
        errors = []
        q_text = q.get("question_text", "")
        q_type = q.get("question_type", "SCQ")
        options = q.get("options", [])
        correct_ans = q.get("correct_answer_raw")
        ans_ver_status = q.get("answer_verification_status", "UNVERIFIED")
        official_status = q.get("official_status", "REGULAR")
        quarantine_status = q.get("quarantine_status", "CLEAN")
        rights_status = q.get("rights_status", "PENDING_LEGAL_REVIEW")
        publish_permission = q.get("publish_permission", "FORBIDDEN")
        eligibility = q.get("eligibility_for_scoring", "INELIGIBLE_UNVERIFIED_KEY")

        # 1. Stem non-empty
        if len(q_text.strip()) < 10:
            errors.append("Question text length must be >= 10 characters")

        # 2. KaTeX syntax valid
        if not validate_katex_syntax(q_text):
            errors.append("Unbalanced LaTeX/KaTeX math delimiters ($ or $$)")

        for opt in options:
            if not validate_katex_syntax(opt.get("option_text", "")):
                errors.append(f"Unbalanced LaTeX in option {opt.get('option_key')}")

        # 3. Options cardinality and content completeness
        if q_type in ("SCQ", "ASSERTION_REASON"):
            if len(options) != 4:
                errors.append(f"{q_type} requires exactly 4 options, found {len(options)}")
            else:
                for opt in options:
                    opt_text = opt.get("option_text", "").strip()
                    opt_diag = opt.get("diagram_asset_url")
                    if len(opt_text) == 0 and not opt_diag:
                        errors.append(f"Option {opt.get('option_key')} text cannot be empty (missing diagram/formula drawing)")

        elif q_type == "NUMERICAL":
            if len(options) > 0:
                errors.append(f"NUMERICAL questions must have 0 options, found {len(options)}")

        # 4. Correct answer bounded
        if official_status == "REGULAR" and ans_ver_status != "UNVERIFIED":
            if q_type in ("SCQ", "ASSERTION_REASON") and correct_ans not in ("A", "B", "C", "D"):
                errors.append(f"Invalid correct_answer_raw for {q_type}: {correct_ans}")

        # 5. Numerical tolerance bounds
        if q_type == "NUMERICAL":
            min_v = q.get("numerical_min_val")
            max_v = q.get("numerical_max_val")
            if min_v is not None and max_v is not None and min_v > max_v:
                errors.append(f"numerical_min_val ({min_v}) cannot exceed numerical_max_val ({max_v})")

        # 6. Scoring Eligibility Rules
        if ans_ver_status == "UNVERIFIED" and eligibility == "ELIGIBLE_FOR_SCORING":
            errors.append("CRITICAL: Unverified answer key CANNOT be marked ELIGIBLE_FOR_SCORING")

        if official_status in ("DROPPED", "DISPUTED") and eligibility == "ELIGIBLE_FOR_SCORING":
            errors.append(f"CRITICAL: {official_status} question CANNOT be marked ELIGIBLE_FOR_SCORING")

        if quarantine_status != "CLEAN" and eligibility == "ELIGIBLE_FOR_SCORING":
            errors.append(f"CRITICAL: {quarantine_status} question CANNOT be marked ELIGIBLE_FOR_SCORING")

        ver_status = q.get("verification_status", "INGESTED")
        if eligibility == "ELIGIBLE_FOR_SCORING" and ver_status not in (
            "CONTENT_VERIFIED", "VERIFIED", "HUMAN_VERIFIED", "ALGORITHMICALLY_VERIFIED"
        ):
            errors.append(f"CRITICAL: Question with unverified content status '{ver_status}' CANNOT be marked ELIGIBLE_FOR_SCORING")

        # 7. Rights & Publication Permission Rules
        if rights_status not in ("OFFICIAL_FAIR_USE", "PROPRIETARY", "PUBLIC_DOMAIN") and publish_permission != "FORBIDDEN":
            errors.append(f"CRITICAL: Rights status '{rights_status}' requires publish_permission='FORBIDDEN'")

        return (len(errors) == 0, errors)

    def ingest_paper_batch(
        self,
        paper_info: Dict[str, Any],
        questions_data: List[Dict[str, Any]],
        dry_run: bool = False,
    ) -> Dict[str, Any]:
        """
        Idempotently ingests an exam paper and its associated questions.
        If dry_run=True, executes validation and planning without persistent DB writes.
        """
        metrics = {
            "dry_run": dry_run,
            "total_submitted": len(questions_data),
            "valid_count": 0,
            "invalid_count": 0,
            "inserted_count": 0,
            "skipped_duplicate_count": 0,
            "quarantined_count": 0,
            "dropped_count": 0,
            "eligible_for_scoring_count": 0,
            "validation_errors": {},
            "question_hashes": [],
        }

        # 1. Ensure Exam exists
        exam_code = paper_info["exam_code"]
        exam = self.db.query(Examination).filter(Examination.code == exam_code).first()
        if not exam and not dry_run:
            raise ValueError(f"Examination '{exam_code}' does not exist in examinations table")

        # 2. Get or create ExamPaper
        paper_id = paper_info.get("id") or str(uuid.uuid4())
        paper_identifier = paper_info["paper_identifier"]
        
        paper = self.db.query(ExamPaper).filter(ExamPaper.paper_identifier == paper_identifier).first()
        if not paper and not dry_run:
            from datetime import date, datetime
            raw_date = paper_info.get("exam_date")
            parsed_date = None
            if isinstance(raw_date, str):
                try:
                    parsed_date = datetime.strptime(raw_date, "%Y-%m-%d").date()
                except Exception:
                    parsed_date = None
            elif isinstance(raw_date, date):
                parsed_date = raw_date

            paper = ExamPaper(
                id=paper_id,
                paper_identifier=paper_identifier,
                exam_code=exam_code,
                exam_year=paper_info["exam_year"],
                session_or_shift=paper_info["session_or_shift"],
                paper_code=paper_info.get("paper_code"),
                exam_date=parsed_date,
                total_questions=paper_info.get("total_questions", len(questions_data)),
                source_pdf_path=paper_info.get("source_pdf_path"),
                source_pdf_hash=paper_info.get("source_pdf_hash"),
            )
            self.db.add(paper)
            self.db.flush()


        # 3. Process questions
        for idx, q_dict in enumerate(questions_data):
            q_num = q_dict.get("paper_question_number", idx + 1)
            is_valid, errors = self.validate_question_data(q_dict)

            if not is_valid:
                metrics["invalid_count"] += 1
                metrics["validation_errors"][f"Q{q_num}"] = errors
                continue

            metrics["valid_count"] += 1

            # Compute content hash
            content_hash = compute_content_hash(
                q_dict["question_text"],
                q_dict.get("options", []),
                q_dict.get("correct_answer_raw"),
                stem_diagram_url=q_dict.get("diagram_asset_url"),
            )
            metrics["question_hashes"].append(content_hash)

            # Check for existing duplicate by content hash
            existing_q = self.db.query(Question).filter(Question.content_hash == content_hash).first()
            if existing_q:
                metrics["skipped_duplicate_count"] += 1
                continue

            # Check quarantine and dropped statuses
            if q_dict.get("quarantine_status") not in (None, "CLEAN"):
                metrics["quarantined_count"] += 1

            if q_dict.get("official_status") in ("DROPPED", "BONUS"):
                metrics["dropped_count"] += 1

            if q_dict.get("eligibility_for_scoring") == "ELIGIBLE_FOR_SCORING":
                metrics["eligible_for_scoring_count"] += 1

            if dry_run:
                metrics["inserted_count"] += 1
                continue

            # Ensure Topic ID exists (if uncertain, route to quarantine)
            topic_id = q_dict.get("topic_id")
            topic = self.db.query(Topic).filter(Topic.id == topic_id).first() if topic_id else None
            
            quarantine_status = q_dict.get("quarantine_status", "CLEAN")
            orig_reason = q_dict.get("quarantine_reason")
            quarantine_reason = orig_reason
            eligibility = q_dict.get("eligibility_for_scoring", "INELIGIBLE_UNVERIFIED_KEY")

            if not topic:
                quarantine_status = "QUARANTINED"
                quarantine_reason = f"{orig_reason} (Topic ID '{topic_id}' unmapped)" if orig_reason else f"Topic ID '{topic_id}' not found in curriculum hierarchy"
                eligibility = "INELIGIBLE_QUARANTINED"

                # Use a sentinel/fallback topic or require existing topic
                # To satisfy NOT NULL foreign key on questions.topic_id, query first topic or raise
                first_topic = self.db.query(Topic).first()
                if not first_topic:
                    raise ValueError("Cannot persist question: no topics exist in database")
                topic_id = first_topic.id

            q_id = q_dict.get("id") or str(uuid.uuid4())
            new_question = Question(
                id=q_id,
                exam_paper_id=paper.id if paper else None,
                paper_question_number=q_num,
                topic_id=topic_id,
                question_type=q_dict.get("question_type", "SCQ"),
                question_text=q_dict["question_text"],
                diagram_asset_url=q_dict.get("diagram_asset_url"),
                correct_answer_raw=q_dict.get("correct_answer_raw"),
                answer_verification_status=q_dict.get("answer_verification_status", "UNVERIFIED"),
                solution_text=q_dict.get("solution_text"),
                ncert_citation=q_dict.get("ncert_citation"),
                evaluation_policy=q_dict.get("evaluation_policy", "UNRESOLVED_POLICY"),
                numerical_precision_type=q_dict.get("numerical_precision_type", "NOT_APPLICABLE"),
                numerical_min_val=q_dict.get("numerical_min_val"),
                numerical_max_val=q_dict.get("numerical_max_val"),
                numerical_tolerance_epsilon=q_dict.get("numerical_tolerance_epsilon"),
                scoring_policy_version=q_dict.get("scoring_policy_version"),
                scoring_policy_source=q_dict.get("scoring_policy_source"),
                difficulty_tier=q_dict.get("difficulty_tier", "MEDIUM"),
                cognitive_level=q_dict.get("cognitive_level", "APPLYING"),
                estimated_seconds=q_dict.get("estimated_seconds", 120),
                source_type=q_dict.get("source_type", "OFFICIAL_PYQ"),
                rights_status=q_dict.get("rights_status", "PENDING_LEGAL_REVIEW"),
                publish_permission=q_dict.get("publish_permission", "FORBIDDEN"),
                rights_review_notes=q_dict.get("rights_review_notes"),
                official_status=q_dict.get("official_status", "REGULAR"),
                official_status_evidence=q_dict.get("official_status_evidence"),
                quarantine_status=quarantine_status,
                quarantine_reason=quarantine_reason,
                eligibility_for_scoring=eligibility,
                verification_status=q_dict.get("verification_status", "INGESTED"),
                content_hash=content_hash,
            )
            self.db.add(new_question)
            self.db.flush()

            # Insert Options
            for o_idx, opt in enumerate(q_dict.get("options", [])):
                opt_row = QuestionOption(
                    id=str(uuid.uuid4()),
                    question_id=new_question.id,
                    option_key=opt["option_key"],
                    option_text=opt.get("option_text", ""),
                    diagram_asset_url=opt.get("diagram_asset_url"),
                    is_correct=opt.get("is_correct", False),
                    explanation=opt.get("explanation"),
                    sort_order=opt.get("sort_order", o_idx),
                )
                self.db.add(opt_row)

            # Insert Initial Verification Log
            v_log = QuestionVerificationLog(
                id=str(uuid.uuid4()),
                question_id=new_question.id,
                verified_by=q_dict.get("verified_by", "AUTOMATED_INGESTION_PIPELINE"),
                previous_status="NONE",
                new_status=new_question.verification_status,
                action_type="INGESTION_PILOT",
                review_notes=f"Pilot ingestion. Rights: {new_question.rights_status}. Eligibility: {new_question.eligibility_for_scoring}",
            )
            self.db.add(v_log)
            metrics["inserted_count"] += 1

        if not dry_run:
            self.db.commit()

        return metrics
