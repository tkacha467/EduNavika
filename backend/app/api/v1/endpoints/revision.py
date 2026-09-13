from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.app.core.database import get_db
from backend.app.models.user import StudentProfile
from backend.app.models.curriculum import Topic
from backend.app.models.revision import RevisionPlan, RevisionCompletionState
from backend.app.schemas.revision import RevisionPlanCreate, RevisionPlanResponse

router = APIRouter()


@router.get("/students/{id}/revision-plan", response_model=List[RevisionPlanResponse], summary="Get revision plans for a student")
def get_student_revision_plan(
    id: str,
    completion_state: Optional[RevisionCompletionState] = None,
    db: Session = Depends(get_db)
):
    student = db.query(StudentProfile).filter(StudentProfile.id == id).first()
    if not student:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student profile not found")

    query = db.query(RevisionPlan).filter(RevisionPlan.student_id == id)
    if completion_state:
        query = query.filter(RevisionPlan.completion_state == completion_state)

    return query.order_by(RevisionPlan.recommended_revision_at.asc()).all()


@router.post("/revision-plans", response_model=RevisionPlanResponse, status_code=status.HTTP_201_CREATED, summary="Create a revision plan entry")
def create_revision_plan(payload: RevisionPlanCreate, db: Session = Depends(get_db)):
    student = db.query(StudentProfile).filter(StudentProfile.id == payload.student_id).first()
    if not student:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student profile not found")

    topic = db.query(Topic).filter(Topic.id == payload.topic_id).first()
    if not topic:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Topic not found")

    plan = RevisionPlan(**payload.model_dump())
    db.add(plan)
    db.commit()
    db.refresh(plan)
    return plan
