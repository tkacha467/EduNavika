import logging
from datetime import datetime, timezone
from typing import List, Optional
import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, OperationalError
from backend.app.core.database import get_db
from backend.app.models import StudentProfile, User, UserRole, Topic, Chapter
from backend.app.models import Assessment, AssessmentQuestion, AssessmentStatus
from backend.app.models import Attempt, Answer, AttemptStatus
from backend.app.models import MCQQuestion
from backend.app.models import EventType
from backend.app.schemas.attempt import (
    AttemptCreate,
    AnswerSubmit,
    AttemptSubmit,
    AnswerResponse,
    AttemptResponse,
    AttemptDetailResponse,
)
from backend.app.services.event_recorder import EventRecorderService

logger = logging.getLogger(__name__)

router = APIRouter()


def _get_or_create_student_profile(db: Session, student_id: str) -> Optional[StudentProfile]:
    """Finds or auto-provisions a StudentProfile for the student."""
    # 1. Direct match by StudentProfile.id
    student = db.query(StudentProfile).filter(StudentProfile.id == student_id).first()
    if student:
        return student

    # 2. Match by StudentProfile.user_id
    student = db.query(StudentProfile).filter(StudentProfile.user_id == student_id).first()
    if student:
        return student

    # 3. Match User by ID or student role
    user = db.query(User).filter(User.id == student_id).first()
    if not user:
        user = db.query(User).filter(User.role == UserRole.STUDENT).first()
    if not user:
        user = db.query(User).filter(User.email == "kachatushar108@gmail.com").first()

    if user:
        existing_profile = db.query(StudentProfile).filter(StudentProfile.user_id == user.id).first()
        if existing_profile:
            return existing_profile

        try:
            new_profile = StudentProfile(
                id=student_id if (len(student_id) <= 36 and not student_id.startswith("http")) else None,
                user_id=user.id,
                enrollment_number=f"EN-{user.id[:8]}",
                division="A",
            )
            db.add(new_profile)
            db.commit()
            db.refresh(new_profile)
            return new_profile
        except (IntegrityError, OperationalError):
            db.rollback()
            return db.query(StudentProfile).filter(StudentProfile.user_id == user.id).first()

    return None


def _resolve_topic(db: Session, topic_id: Optional[str]) -> Optional[Topic]:
    """
    Robustly resolves a topic by:
    1. Exact UUID match on Topic.id
    2. Exact title match on Topic.title (case-insensitive)
    3. Normalized title match (e.g. '&' -> 'and', '—' -> '-')
    4. Substring / partial match on Topic.title
    5. Chapter title match -> returns primary topic under that chapter
    Returns None if no matching topic is found. Never falls back to unrelated topics.
    """
    if not topic_id:
        return None

    # 1. Exact ID
    topic = db.query(Topic).filter(Topic.id == topic_id).first()
    if topic:
        return topic

    # 2. Exact Title
    topic = db.query(Topic).filter(func.lower(Topic.title) == func.lower(topic_id)).first()
    if topic:
        return topic

    # 3. Normalized Title
    norm = topic_id.replace('&', 'and').replace('—', '-').strip()
    topic = db.query(Topic).filter(func.lower(Topic.title) == func.lower(norm)).first()
    if topic:
        return topic

    # 4. Partial Title Match
    topic = db.query(Topic).filter(Topic.title.ilike(f"%{norm}%")).first()
    if topic:
        return topic

    # 5. Reverse Substring Match (e.g. "Chemical Reactions" matching "Chemical Reactions and Equations")
    all_topics = db.query(Topic).all()
    norm_lower = norm.lower()
    for t in all_topics:
        t_clean = t.title.replace('&', 'and').replace('—', '-').lower().strip()
        if (len(t_clean) >= 4 and t_clean in norm_lower) or (len(norm_lower) >= 4 and norm_lower in t_clean):
            return t

    # 6. Chapter match: check if a chapter matches the topic_id / name
    all_chapters = db.query(Chapter).all()
    for c in all_chapters:
        c_clean = c.title.replace('&', 'and').replace('—', '-').lower().strip()
        if (len(c_clean) >= 4 and c_clean in norm_lower) or (len(norm_lower) >= 4 and norm_lower in c_clean):
            first_top = (
                db.query(Topic)
                .filter(Topic.chapter_id == c.id)
                .order_by(Topic.topic_order.asc())
                .first()
            )
            if first_top:
                return first_top

    return None


@router.post("/attempts", response_model=AttemptResponse, status_code=status.HTTP_201_CREATED, summary="Start an assessment attempt or record formative practice telemetry")
def create_attempt(payload: AttemptCreate, db: Session = Depends(get_db)):
    student = _get_or_create_student_profile(db, payload.student_id)
    if not student:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student profile not found")

    # Flow A: Formal assessment attempt start
    if payload.assessment_id:
        assessment = db.query(Assessment).filter(Assessment.id == payload.assessment_id).first()
        if not assessment:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assessment not found")

        if assessment.status != AssessmentStatus.PUBLISHED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot attempt an assessment that is not in PUBLISHED status"
            )

        attempt = Attempt(
            student_id=student.id,
            assessment_id=payload.assessment_id,
            started_at=datetime.now(timezone.utc),
            status=AttemptStatus.STARTED,
            total_score=0.0,
            percentage=0.0,
        )
        db.add(attempt)
        db.commit()
        db.refresh(attempt)
        return attempt

    # Flow B: Formative practice question telemetry
    topic = _resolve_topic(db, payload.topic_id)
    if not topic:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Topic could not be resolved from identifier '{payload.topic_id}'. Valid curriculum topic required."
        )

    now = datetime.now(timezone.utc)
    score = float(payload.score) if payload.score is not None else (100.0 if payload.is_correct else 0.0)
    is_correct = payload.is_correct if payload.is_correct is not None else (score > 0)
    response_time = max(0, payload.response_time_ms or 0)

    idempotency_key = f"practice_{student.id}_{payload.mcq_id}_{int(now.timestamp())}" if payload.mcq_id else None
    event = EventRecorderService.record_event(
        db=db,
        student_id=student.id,
        topic_id=topic.id,
        event_type=EventType.PRACTICE,
        timestamp=now,
        score=score,
        correctness=is_correct,
        response_time_ms=response_time,
        hint_used=bool(payload.hint_requested),
        idempotency_key=idempotency_key,
        event_metadata={
            "mcq_id": payload.mcq_id,
            "selected_option": payload.selected_option,
            "client_topic_id": payload.topic_id,
            "resolved_topic_title": topic.title,
        },
        auto_commit=True,
    )
    event_id = event.id

    return AttemptResponse(
        id=event_id,
        student_id=student.id,
        assessment_id=None,
        started_at=now,
        submitted_at=now,
        total_score=score,
        percentage=score,
        duration_seconds=int(response_time / 1000),
        status=AttemptStatus.SUBMITTED,
        created_at=now,
        updated_at=now,
        mcq_id=payload.mcq_id,
        topic_id=topic.id if topic else payload.topic_id,
        selected_option=payload.selected_option,
        is_correct=is_correct,
        score=score,
        response_time_ms=response_time,
        hint_requested=bool(payload.hint_requested),
    )


@router.post("/attempts/{id}/answers", response_model=AnswerResponse, status_code=status.HTTP_201_CREATED, summary="Submit an answer during an attempt")
def submit_answer(id: str, payload: AnswerSubmit, db: Session = Depends(get_db)):
    attempt = db.query(Attempt).filter(Attempt.id == id).first()
    if not attempt:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Attempt not found")

    if attempt.status != AttemptStatus.STARTED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot submit answers to an attempt in {attempt.status.value} status"
        )

    # Check if question is in the assessment
    aq = (
        db.query(AssessmentQuestion)
        .filter(
            AssessmentQuestion.assessment_id == attempt.assessment_id,
            AssessmentQuestion.question_id == payload.question_id
        )
        .first()
    )
    if not aq:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The specified question does not belong to this assessment"
        )

    # Check duplicate answer in attempt
    existing_answer = (
        db.query(Answer)
        .filter(Answer.attempt_id == id, Answer.question_id == payload.question_id)
        .first()
    )
    if existing_answer:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Answer for this question in this attempt has already been submitted"
        )

    mcq = db.query(MCQQuestion).filter(MCQQuestion.id == payload.question_id).first()
    if not mcq:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Question not found")

    now = datetime.now(timezone.utc)
    is_correct = (payload.selected_option == mcq.correct_option)

    # Create answer
    answer = Answer(
        attempt_id=id,
        question_id=payload.question_id,
        selected_option=payload.selected_option,
        is_correct=is_correct,
        response_time_ms=payload.response_time_ms,
        hint_used=payload.hint_used,
        answered_at=now,
    )
    db.add(answer)

    # Record longitudinal learning event and update topic performance evidence
    EventRecorderService.record_event(
        db=db,
        student_id=attempt.student_id,
        topic_id=mcq.topic_id,
        event_type=EventType.MCQ_ATTEMPT,
        timestamp=now,
        session_id=attempt.id,
        attempt_id=attempt.id,
        score=aq.points if is_correct else 0.0,
        correctness=is_correct,
        response_time_ms=payload.response_time_ms,
        hint_used=payload.hint_used,
        idempotency_key=f"attempt_{id}_q_{payload.question_id}",
        auto_commit=False,
    )

    db.commit()
    db.refresh(answer)
    return answer


@router.post("/attempts/{id}/submit", response_model=AttemptDetailResponse, summary="Finalize and score an assessment attempt")
def finalize_attempt(id: str, payload: Optional[AttemptSubmit] = None, db: Session = Depends(get_db)):
    attempt = db.query(Attempt).filter(Attempt.id == id).first()
    if not attempt:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Attempt not found")

    if attempt.status != AttemptStatus.STARTED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Attempt is already {attempt.status.value}"
        )

    now = payload.submitted_at if payload and payload.submitted_at else datetime.now(timezone.utc)
    attempt.submitted_at = now
    attempt.status = AttemptStatus.SUBMITTED

    if attempt.started_at:
        started = attempt.started_at
        if started.tzinfo is None and now.tzinfo is not None:
            started = started.replace(tzinfo=timezone.utc)
        elif started.tzinfo is not None and now.tzinfo is None:
            now = now.replace(tzinfo=timezone.utc)
        attempt.duration_seconds = max(0, int((now - started).total_seconds()))

    # Calculate score
    assessment_questions = (
        db.query(AssessmentQuestion)
        .filter(AssessmentQuestion.assessment_id == attempt.assessment_id)
        .all()
    )
    total_possible_points = sum(q.points for q in assessment_questions) if assessment_questions else 0.0
    question_points_map = {q.question_id: q.points for q in assessment_questions}

    answers = db.query(Answer).filter(Answer.attempt_id == id).all()
    earned_score = sum(
        question_points_map.get(ans.question_id, 1.0)
        for ans in answers
        if ans.is_correct
    )

    attempt.total_score = earned_score
    if total_possible_points > 0:
        attempt.percentage = round((earned_score / total_possible_points) * 100.0, 2)
    else:
        attempt.percentage = 0.0

    db.commit()
    db.refresh(attempt)
    return attempt


@router.get("/attempts/{id}", response_model=AttemptDetailResponse, summary="Get attempt details and answers")
def get_attempt(id: str, db: Session = Depends(get_db)):
    attempt = db.query(Attempt).filter(Attempt.id == id).first()
    if not attempt:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Attempt not found")
    return attempt


from pydantic import BaseModel, Field


class AttemptReviewRequest(BaseModel):
    student_id: str
    session_id: Optional[str] = None
    review_duration_ms: Optional[int] = Field(None, ge=0)
    topic_id: Optional[str] = None
    idempotency_key: Optional[str] = None


@router.post("/attempts/{id}/review", summary="Record a student review of an assessment attempt (REVIEW event)")
def review_attempt(id: str, payload: AttemptReviewRequest, db: Session = Depends(get_db)):
    attempt = db.query(Attempt).filter(Attempt.id == id).first()
    if not attempt:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Attempt not found")

    if attempt.student_id != payload.student_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Attempt does not belong to this student")

    # Determine topic: use payload or assessment topic or first question's topic
    target_topic_id = payload.topic_id
    if not target_topic_id and attempt.assessment and attempt.assessment.topic_id:
        target_topic_id = attempt.assessment.topic_id
    elif not target_topic_id:
        first_q = db.query(AssessmentQuestion).filter(AssessmentQuestion.assessment_id == attempt.assessment_id).first()
        if first_q and first_q.question:
            target_topic_id = first_q.question.topic_id

    if not target_topic_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot determine topic for attempt review")

    event = EventRecorderService.record_event(
        db=db,
        student_id=payload.student_id,
        topic_id=target_topic_id,
        event_type=EventType.REVIEW,
        score=attempt.percentage,
        correctness=None,
        response_time_ms=payload.review_duration_ms,
        session_id=payload.session_id or attempt.id,
        attempt_id=id,
        idempotency_key=payload.idempotency_key or f"review_attempt_{id}",
        event_metadata={
            "attempt_id": id,
            "attempt_score": attempt.total_score,
            "percentage": attempt.percentage,
        },
        auto_commit=True,
    )

    return {"status": "REVIEW_RECORDED", "attempt_id": id, "event_id": event.id}

