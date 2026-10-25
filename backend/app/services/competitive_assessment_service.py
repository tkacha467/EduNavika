"""
EduNavika — Competitive Assessment & Server-Authoritative Timing Engine.
Implements exam-specific scoring (JEE Main +4/-1; JEE Advanced multi-correct partial marking; NEET UG +4/-1).
Provides countdown tracking, server-side timer enforcement, save-and-resume, and secure response evaluation.
"""

import uuid
import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timezone, timedelta
from sqlalchemy.orm import Session

from backend.app.models.competitive_models import (
    Question,
    QuestionOption,
    ExamPaper,
    Examination,
    ExamSubject,
)
from backend.app.models.curriculum_models import Chapter, Topic, Subject

logger = logging.getLogger(__name__)

# Active session store (in-memory for instant high-speed responsive tests)
ACTIVE_ASSESSMENT_SESSIONS: Dict[str, Dict[str, Any]] = {}

# Server grace period for latency on submission (seconds)
LATENCY_GRACE_PERIOD_SECONDS = 15


class CompetitiveScoringEngine:
    """
    Computes points for an individual question attempt based on verified exam marking rules.
    """

    @staticmethod
    def evaluate_scq(
        selected_option: Optional[str],
        correct_option: Optional[str],
        exam_code: str = "JEE_MAIN",
    ) -> Tuple[float, bool]:
        """
        Evaluates Single Choice Question (SCQ).
        Returns (points_awarded, is_correct).
        """
        if not selected_option:
            return 0.0, False

        sel = selected_option.strip().upper()
        corr = (correct_option or "").strip().upper()

        if sel == corr:
            if exam_code == "JEE_ADVANCED":
                return 3.0, True
            else:  # JEE_MAIN, NEET_UG
                return 4.0, True
        else:
            if exam_code in ("JEE_MAIN", "JEE_ADVANCED", "NEET_UG"):
                return -1.0, False
            return 0.0, False

    @staticmethod
    def evaluate_mcq_multi_jee_advanced(
        selected_options: List[str],
        correct_options: List[str],
    ) -> Tuple[float, bool]:
        """
        Evaluates JEE Advanced Multiple Choice Question with Partial Marking Scheme:
        - Full marks (+4): If only all correct options are chosen.
        - Partial marks (+3): If 4 options are correct, but only 3 chosen and no incorrect chosen.
        - Partial marks (+2): If 3 or more options are correct, but only 2 chosen and no incorrect chosen.
        - Partial marks (+1): If 2 or more options are correct, but only 1 chosen and no incorrect chosen.
        - Zero marks (0): If none of the options are chosen (unattempted).
        - Negative marks (-2): If ANY incorrect option is chosen.
        """
        if not selected_options:
            return 0.0, False

        sel_set = set(o.strip().upper() for o in selected_options)
        corr_set = set(o.strip().upper() for o in correct_options)

        # Check for any incorrect options chosen
        incorrect_chosen = sel_set - corr_set
        if len(incorrect_chosen) > 0:
            return -2.0, False

        # Only correct options chosen
        num_chosen = len(sel_set)
        total_correct = len(corr_set)

        if sel_set == corr_set:
            return 4.0, True
        elif total_correct == 4 and num_chosen == 3:
            return 3.0, False
        elif total_correct >= 3 and num_chosen == 2:
            return 2.0, False
        elif total_correct >= 2 and num_chosen == 1:
            return 1.0, False

        return 0.0, False

    @staticmethod
    def evaluate_numerical(
        user_value: Optional[float],
        min_val: Optional[float],
        max_val: Optional[float],
        epsilon: Optional[float] = 0.01,
        exam_code: str = "JEE_MAIN",
    ) -> Tuple[float, bool]:
        """
        Evaluates Numerical Question within acceptable bounds or precision epsilon.
        """
        if user_value is None:
            return 0.0, False

        is_correct = False
        if min_val is not None and max_val is not None:
            is_correct = (min_val <= user_value <= max_val)
        elif min_val is not None:
            is_correct = abs(user_value - min_val) <= (epsilon or 0.01)

        if is_correct:
            points = 3.0 if exam_code == "JEE_ADVANCED" else 4.0
            return points, True
        else:
            # Negative marking for numericals: -1 for JEE Main recent policy, 0 for classical
            return 0.0, False


class CompetitiveAssessmentService:
    def __init__(self, db: Session):
        self.db = db

    def start_assessment_session(
        self,
        student_id: str,
        exam_code: str = "JEE_MAIN",
        mode: str = "CHAPTER_MOCK",
        chapter_id: Optional[str] = None,
        duration_minutes: int = 45,
        total_questions: int = 20,
    ) -> Dict[str, Any]:
        """
        Starts a server-authoritative timed assessment session.
        Hides answer keys until explicit submission or time expiry.
        """
        now = datetime.now(timezone.utc)
        duration_seconds = duration_minutes * 60
        expires_at = now + timedelta(seconds=duration_seconds)

        # Select questions based on mode
        q_query = self.db.query(Question).filter(
            Question.eligibility_for_scoring == "ELIGIBLE_FOR_SCORING",
            Question.answer_verification_status != "UNVERIFIED",
            Question.quarantine_status == "CLEAN",
            Question.publish_permission != "FORBIDDEN",
        )

        if chapter_id:
            topics = self.db.query(Topic).filter(Topic.chapter_id == chapter_id).all()
            topic_ids = [t.id for t in topics]
            q_query = q_query.filter(Question.topic_id.in_(topic_ids))

        questions = q_query.limit(total_questions).all()

        if not questions:
            raise ValueError(
                f"No eligible verified questions available for assessment in '{exam_code}' "
                f"{f'for chapter {chapter_id}' if chapter_id else ''}. "
                f"Cannot create an empty or fabricated assessment session."
            )

        session_id = str(uuid.uuid4())
        session_questions = []

        for idx, q in enumerate(questions):
            opts = [
                {
                    "option_key": o.option_key,
                    "option_text": o.option_text,
                    "diagram_asset_url": o.diagram_asset_url,
                }
                for o in q.options
            ]
            session_questions.append({
                "question_id": q.id,
                "order": idx + 1,
                "question_type": q.question_type,
                "question_text": q.question_text,
                "diagram_asset_url": q.diagram_asset_url,
                "options": opts,
                "topic_title": q.topic.title if q.topic else "General",
                "subject_name": q.topic.chapter.subject.name if q.topic and q.topic.chapter and q.topic.chapter.subject else "Science",
                # Secret fields for grading:
                "_correct_answer_raw": q.correct_answer_raw,
                "_correct_options": [o.option_key for o in q.options if o.is_correct],
                "_min_val": q.numerical_min_val,
                "_max_val": q.numerical_max_val,
                "_epsilon": q.numerical_tolerance_epsilon,
                "_solution": q.solution_text,
                "_ncert_citation": q.ncert_citation,
            })

        session_record = {
            "session_id": session_id,
            "student_id": student_id,
            "exam_code": exam_code,
            "mode": mode,
            "chapter_id": chapter_id,
            "started_at": now,
            "expires_at": expires_at,
            "duration_seconds": duration_seconds,
            "status": "IN_PROGRESS",
            "questions": session_questions,
            "responses": {
                sq["question_id"]: {
                    "selected_option": None,
                    "selected_options": [],
                    "numerical_value": None,
                    "status": "UNANSWERED",
                    "time_spent_seconds": 0,
                }
                for sq in session_questions
            },
            "submission": None,
        }

        ACTIVE_ASSESSMENT_SESSIONS[session_id] = session_record

        # Return client payload (without secret answers)
        return self._format_client_session(session_record)

    def _format_client_session(self, session: Dict[str, Any]) -> Dict[str, Any]:
        """Strips secret answer fields from client-facing session."""
        now = datetime.now(timezone.utc)
        remaining = max(0, int((session["expires_at"] - now).total_seconds()))

        safe_questions = []
        for q in session["questions"]:
            safe_questions.append({
                "question_id": q["question_id"],
                "order": q["order"],
                "question_type": q["question_type"],
                "question_text": q["question_text"],
                "diagram_asset_url": q["diagram_asset_url"],
                "options": q["options"],
                "topic_title": q["topic_title"],
                "subject_name": q["subject_name"],
            })

        return {
            "session_id": session["session_id"],
            "exam_code": session["exam_code"],
            "mode": session["mode"],
            "status": session["status"],
            "started_at": session["started_at"].isoformat(),
            "expires_at": session["expires_at"].isoformat(),
            "duration_seconds": session["duration_seconds"],
            "remaining_seconds": remaining,
            "total_questions": len(safe_questions),
            "questions": safe_questions,
            "responses": session["responses"],
        }

    def save_response(
        self,
        session_id: str,
        question_id: str,
        selected_option: Optional[str] = None,
        selected_options: Optional[List[str]] = None,
        numerical_value: Optional[float] = None,
        status: str = "ANSWERED",
        time_spent_seconds: int = 0,
    ) -> Dict[str, Any]:
        """
        Saves student response during an active timed session (save-and-resume).
        Enforces server expiry check.
        """
        session = ACTIVE_ASSESSMENT_SESSIONS.get(session_id)
        if not session:
            raise ValueError(f"Session '{session_id}' not found.")

        now = datetime.now(timezone.utc)
        if now > (session["expires_at"] + timedelta(seconds=LATENCY_GRACE_PERIOD_SECONDS)):
            # Auto-submit on expiry
            return self.submit_assessment(session_id, auto_expired=True)

        if question_id in session["responses"]:
            session["responses"][question_id] = {
                "selected_option": selected_option,
                "selected_options": selected_options or ([selected_option] if selected_option else []),
                "numerical_value": numerical_value,
                "status": status,
                "time_spent_seconds": time_spent_seconds,
            }

        return {
            "session_id": session_id,
            "saved": True,
            "remaining_seconds": max(0, int((session["expires_at"] - now).total_seconds())),
        }

    def submit_assessment(
        self,
        session_id: str,
        auto_expired: bool = False,
    ) -> Dict[str, Any]:
        """
        Submits assessment session, calculates final score with exam-specific marking rules,
        and unlocks answer solutions for student review.
        """
        session = ACTIVE_ASSESSMENT_SESSIONS.get(session_id)
        if not session:
            raise ValueError(f"Session '{session_id}' not found.")

        if session["status"] == "SUBMITTED" and session["submission"]:
            return session["submission"]

        now = datetime.now(timezone.utc)
        exam_code = session["exam_code"]
        questions = session["questions"]
        responses = session["responses"]

        total_score = 0.0
        max_possible_score = 0.0
        correct_count = 0
        incorrect_count = 0
        unattempted_count = 0
        total_time_spent = 0

        subject_scores: Dict[str, Dict[str, float]] = {}
        review_items = []

        for q in questions:
            qid = q["question_id"]
            q_type = q["question_type"]
            subj = q["subject_name"]
            resp = responses.get(qid, {})

            if subj not in subject_scores:
                subject_scores[subj] = {"score": 0.0, "max_score": 0.0, "correct": 0, "total": 0}

            subject_scores[subj]["total"] += 1

            # Standard max points per question
            max_pts = 4.0 if exam_code != "JEE_ADVANCED" else 3.0
            if q_type == "MCQ_MULTI":
                max_pts = 4.0
            max_possible_score += max_pts
            subject_scores[subj]["max_score"] += max_pts

            sel_opt = resp.get("selected_option")
            sel_opts = resp.get("selected_options") or ([sel_opt] if sel_opt else [])
            num_val = resp.get("numerical_value")
            time_spent = resp.get("time_spent_seconds", 0)
            total_time_spent += time_spent

            is_attempted = bool(sel_opt or sel_opts or num_val is not None)

            if not is_attempted:
                unattempted_count += 1
                points = 0.0
                is_correct = False
            else:
                if q_type == "SCQ":
                    points, is_correct = CompetitiveScoringEngine.evaluate_scq(
                        sel_opt, q["_correct_answer_raw"], exam_code
                    )
                elif q_type == "MCQ_MULTI":
                    points, is_correct = CompetitiveScoringEngine.evaluate_mcq_multi_jee_advanced(
                        sel_opts, q["_correct_options"]
                    )
                elif q_type == "NUMERICAL":
                    points, is_correct = CompetitiveScoringEngine.evaluate_numerical(
                        num_val, q["_min_val"], q["_max_val"], q["_epsilon"], exam_code
                    )
                else:
                    points, is_correct = CompetitiveScoringEngine.evaluate_scq(
                        sel_opt, q["_correct_answer_raw"], exam_code
                    )

                if is_correct:
                    correct_count += 1
                    subject_scores[subj]["correct"] += 1
                elif points < 0:
                    incorrect_count += 1

            total_score += points
            subject_scores[subj]["score"] += points

            review_items.append({
                "question_id": qid,
                "order": q["order"],
                "question_text": q["question_text"],
                "diagram_asset_url": q.get("diagram_asset_url"),
                "question_type": q_type,
                "options": q["options"],
                "subject_name": subj,
                "topic_title": q["topic_title"],
                "user_selected_option": sel_opt,
                "user_selected_options": sel_opts,
                "user_numerical_value": num_val,
                "correct_answer": q["_correct_answer_raw"] or ",".join(q["_correct_options"]),
                "points_awarded": points,
                "max_points": max_pts,
                "is_correct": is_correct,
                "is_attempted": is_attempted,
                "time_spent_seconds": time_spent,
                "solution_text": q["_solution"] or "Explanation available in NCERT reference.",
                "ncert_citation": q["_ncert_citation"],
            })

        percentage = round((max(0.0, total_score) / max(1.0, max_possible_score)) * 100, 1)

        submission_result = {
            "session_id": session_id,
            "status": "EXPIRED" if auto_expired else "SUBMITTED",
            "auto_expired": auto_expired,
            "exam_code": exam_code,
            "mode": session["mode"],
            "total_score": round(total_score, 1),
            "max_possible_score": round(max_possible_score, 1),
            "percentage": percentage,
            "total_questions": len(questions),
            "correct_count": correct_count,
            "incorrect_count": incorrect_count,
            "unattempted_count": unattempted_count,
            "total_time_spent_seconds": total_time_spent,
            "subject_breakdown": subject_scores,
            "questions_review": review_items,
            "submitted_at": now.isoformat(),
        }

        session["status"] = "SUBMITTED"
        session["submission"] = submission_result

        return submission_result
