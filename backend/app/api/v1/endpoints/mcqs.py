from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from backend.app.core.database import get_db
from backend.app.models.curriculum import Topic
from backend.app.models.content import LearningContent
from backend.app.models.mcq import MCQQuestion, QuestionStatus, QuestionDifficulty
from backend.app.schemas.mcq import (
    MCQCreate,
    MCQUpdateStatus,
    MCQResponse,
    DuplicateCheckResult,
)
from backend.app.services.duplicate_detection import ExactDuplicateDetector

router = APIRouter()


@router.post("/mcqs/check-duplicate", response_model=DuplicateCheckResult, summary="Check if question text is an exact duplicate")
def check_duplicate(question_text: str = Query(..., min_length=5), db: Session = Depends(get_db)):
    return ExactDuplicateDetector.check_duplicate(db, question_text)


@router.post("/mcqs", response_model=MCQResponse, status_code=status.HTTP_201_CREATED, summary="Create a new MCQ with provenance and duplicate check")
def create_mcq(payload: MCQCreate, force: bool = Query(False, description="Bypass duplicate check if true"), db: Session = Depends(get_db)):
    # 1. Validate topic existence
    topic = db.query(Topic).filter(Topic.id == payload.topic_id).first()
    if not topic:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Referenced topic does not exist")

    # 2. Validate source content if provided
    if payload.source_content_id:
        content = db.query(LearningContent).filter(LearningContent.id == payload.source_content_id).first()
        if not content:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Referenced source content does not exist")

    # 3. Duplicate check
    dup_result = ExactDuplicateDetector.check_duplicate(db, payload.question_text)
    if dup_result.is_exact_duplicate and not force:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "message": "Exact duplicate question already exists in repository history.",
                "existing_question_id": dup_result.existing_question_id,
                "text_hash": dup_result.text_hash,
            }
        )

    # 4. Create question
    mcq = MCQQuestion(**payload.model_dump())
    db.add(mcq)
    db.flush()  # populate mcq.id

    # 5. Record question history
    ExactDuplicateDetector.record_history(db, mcq)

    db.commit()
    db.refresh(mcq)
    return mcq


@router.get("/mcqs/{id}", response_model=MCQResponse, summary="Get MCQ by ID")
def get_mcq(id: str, db: Session = Depends(get_db)):
    mcq = db.query(MCQQuestion).filter(MCQQuestion.id == id).first()
    if not mcq:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="MCQ not found")
    return mcq


@router.get("/topics/{id}/mcqs", response_model=List[MCQResponse], summary="List MCQs for a topic")
def get_topic_mcqs(
    id: str,
    status_filter: Optional[QuestionStatus] = Query(None, alias="status"),
    difficulty: Optional[QuestionDifficulty] = None,
    db: Session = Depends(get_db)
):
    topic = db.query(Topic).filter(Topic.id == id).first()
    if not topic:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Topic not found")
    
    query = db.query(MCQQuestion).filter(MCQQuestion.topic_id == id)
    if status_filter:
        query = query.filter(MCQQuestion.status == status_filter)
    if difficulty:
        query = query.filter(MCQQuestion.difficulty == difficulty)

    return query.order_by(MCQQuestion.created_at.desc()).all()


@router.patch("/mcqs/{id}/status", response_model=MCQResponse, summary="Update MCQ approval/lifecycle status")
def update_mcq_status(id: str, payload: MCQUpdateStatus, db: Session = Depends(get_db)):
    mcq = db.query(MCQQuestion).filter(MCQQuestion.id == id).first()
    if not mcq:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="MCQ not found")
    mcq.status = payload.status
    db.commit()
    db.refresh(mcq)
    return mcq


from pydantic import BaseModel, Field
from backend.app.models.user import StudentProfile
from backend.app.models.learning_event import EventType
from backend.app.domain.enums import OptionKey
from backend.app.services.event_recorder import EventRecorderService


class MCQPracticeSubmit(BaseModel):
    student_id: str
    selected_option: OptionKey
    response_time_ms: Optional[int] = Field(None, ge=0)
    hint_used: bool = False
    session_id: Optional[str] = None
    idempotency_key: Optional[str] = None


class MCQPracticeResponse(BaseModel):
    question_id: str
    selected_option: OptionKey
    is_correct: bool
    correct_option: OptionKey
    explanation: Optional[str] = None
    event_id: str


@router.post("/mcqs/{id}/practice", response_model=MCQPracticeResponse, summary="Submit a formative practice answer on an MCQ (PRACTICE event)")
def submit_practice_answer(id: str, payload: MCQPracticeSubmit, db: Session = Depends(get_db)):
    mcq = db.query(MCQQuestion).filter(MCQQuestion.id == id).first()
    if not mcq:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="MCQ not found")

    student = db.query(StudentProfile).filter(StudentProfile.id == payload.student_id).first()
    if not student:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student profile not found")

    is_correct = (payload.selected_option == mcq.correct_option)
    score_val = 100.0 if is_correct else 0.0

    event = EventRecorderService.record_event(
        db=db,
        student_id=payload.student_id,
        topic_id=mcq.topic_id,
        event_type=EventType.PRACTICE,
        score=score_val,
        correctness=is_correct,
        response_time_ms=payload.response_time_ms,
        hint_used=payload.hint_used,
        session_id=payload.session_id,
        event_metadata={
            "question_id": mcq.id,
            "selected_option": payload.selected_option.value if hasattr(payload.selected_option, "value") else str(payload.selected_option),
            "difficulty": mcq.difficulty.value if hasattr(mcq.difficulty, "value") else str(mcq.difficulty),
        },
        idempotency_key=payload.idempotency_key,
        auto_commit=True,
    )

    return MCQPracticeResponse(
        question_id=mcq.id,
        selected_option=payload.selected_option,
        is_correct=is_correct,
        correct_option=mcq.correct_option,
        explanation=mcq.explanation,
        event_id=event.id,
    )

