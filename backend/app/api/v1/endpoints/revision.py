from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.app.core.database import get_db
from backend.app.models import StudentProfile
from backend.app.models import Topic
from backend.app.models import RevisionPlan, RevisionCompletionState
from backend.app.schemas.revision import RevisionPlanCreate, RevisionPlanResponse

router = APIRouter()


@router.get("/students/{id}/revision-plan", response_model=List[RevisionPlanResponse], summary="Get revision plans for a student")
@router.get("/revision/plans", response_model=List[RevisionPlanResponse], summary="Get revision plans query alias")
def get_student_revision_plan(
    id: Optional[str] = None,
    student_id: Optional[str] = None,
    completion_state: Optional[RevisionCompletionState] = None,
    db: Session = Depends(get_db)
):
    target_id = id or student_id
    if not target_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="student_id or id parameter required")

    student = db.query(StudentProfile).filter(StudentProfile.id == target_id).first()
    if not student:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student profile not found")

    query = db.query(RevisionPlan).filter(RevisionPlan.student_id == target_id)
    if completion_state:
        query = query.filter(RevisionPlan.completion_state == completion_state)

    plans = query.order_by(RevisionPlan.recommended_revision_at.asc()).all()

    # Enrich with human-readable topic and subject names
    enriched_results = []
    for p in plans:
        resp = RevisionPlanResponse.model_validate(p)
        if p.topic:
            resp.topic_title = p.topic.title
            if p.topic.chapter and p.topic.chapter.subject:
                resp.subject_name = p.topic.chapter.subject.name
            else:
                resp.subject_name = "Science"
        else:
            resp.topic_title = "Topic"
            resp.subject_name = "General"
        enriched_results.append(resp)

    return enriched_results


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
