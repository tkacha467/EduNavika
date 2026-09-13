from datetime import datetime, timezone
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.app.core.database import get_db
from backend.app.models.user import StudentProfile
from backend.app.models.assessment import Assessment, AssessmentQuestion, AssessmentStatus
from backend.app.models.attempt import Attempt, Answer, AttemptStatus
from backend.app.models.mcq import MCQQuestion
from backend.app.models.learning_event import EventType
from backend.app.schemas.attempt import (
    AttemptCreate,
    AnswerSubmit,
    AttemptSubmit,
    AnswerResponse,
    AttemptResponse,
    AttemptDetailResponse,
)
from backend.app.services.event_recorder import EventRecorderService

router = APIRouter()


@router.post("/attempts", response_model=AttemptResponse, status_code=status.HTTP_201_CREATED, summary="Start a student assessment attempt")
def create_attempt(payload: AttemptCreate, db: Session = Depends(get_db)):
    student = db.query(StudentProfile).filter(StudentProfile.id == payload.student_id).first()
    if not student:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student profile not found")

    assessment = db.query(Assessment).filter(Assessment.id == payload.assessment_id).first()
    if not assessment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assessment not found")

    if assessment.status != AssessmentStatus.PUBLISHED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot attempt an assessment that is not in PUBLISHED status"
        )

    attempt = Attempt(
        student_id=payload.student_id,
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
