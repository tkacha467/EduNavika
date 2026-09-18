from datetime import datetime, timezone
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.app.core.database import get_db
from backend.app.models import TeacherProfile
from backend.app.models import Assessment, AssessmentQuestion, AssessmentStatus
from backend.app.models import MCQQuestion
from backend.app.schemas.assessment import (
    AssessmentCreate,
    AssessmentPublish,
    AssessmentResponse,
    AssessmentDetailResponse,
)

router = APIRouter()


@router.post("/assessments", response_model=AssessmentDetailResponse, status_code=status.HTTP_201_CREATED, summary="Create an assessment with optional questions")
def create_assessment(payload: AssessmentCreate, db: Session = Depends(get_db)):
    teacher = db.query(TeacherProfile).filter(TeacherProfile.id == payload.teacher_id).first()
    if not teacher:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Referenced teacher profile does not exist")

    assessment_data = payload.model_dump(exclude={"questions"})
    assessment = Assessment(**assessment_data)
    db.add(assessment)
    db.flush()

    if payload.questions:
        for q_item in payload.questions:
            # Validate question exists
            mcq = db.query(MCQQuestion).filter(MCQQuestion.id == q_item.question_id).first()
            if not mcq:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Referenced question {q_item.question_id} does not exist"
                )
            link = AssessmentQuestion(
                assessment_id=assessment.id,
                question_id=q_item.question_id,
                question_order=q_item.question_order,
                points=q_item.points,
            )
            db.add(link)

    db.commit()
    db.refresh(assessment)
    return assessment


@router.get("/assessments/{id}", response_model=AssessmentDetailResponse, summary="Get assessment details and questions")
def get_assessment(id: str, db: Session = Depends(get_db)):
    assessment = db.query(Assessment).filter(Assessment.id == id).first()
    if not assessment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assessment not found")
    return assessment


@router.post("/assessments/{id}/publish", response_model=AssessmentResponse, summary="Publish an assessment")
def publish_assessment(id: str, payload: Optional[AssessmentPublish] = None, db: Session = Depends(get_db)):
    assessment = db.query(Assessment).filter(Assessment.id == id).first()
    if not assessment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assessment not found")
    
    assessment.status = AssessmentStatus.PUBLISHED
    if payload and payload.published_at:
        assessment.published_at = payload.published_at
    else:
        assessment.published_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(assessment)
    return assessment
