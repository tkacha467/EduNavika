from typing import Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from backend.app.core.database import get_db
from backend.app.models import StudentProfile
from backend.app.domain.decay_engine import (
    AdaptiveLearningService,
    DecayDetectionResponse,
    AdaptiveScheduleResponse,
)
from backend.app.schemas.knowledge_profile import StudentKnowledgeProfileResponse
from backend.app.schemas.recommendation import RecommendationResponse
from backend.app.schemas.explanation import ExplanationRequest, ExplanationResponse

router = APIRouter(prefix="/adaptive")
adaptive_service = AdaptiveLearningService()


from backend.app.models import EventType
from backend.app.services.event_recorder import EventRecorderService


class RevisionOutcomeRequest(BaseModel):
    student_id: str
    topic_id: str
    score: float = Field(..., ge=0.0, le=100.0)
    correctness: bool
    response_time_ms: Optional[int] = Field(None, ge=0)
    session_id: Optional[str] = None
    idempotency_key: Optional[str] = None



@router.post(
    "/detect-decay/{student_id}",
    response_model=DecayDetectionResponse,
    summary="Trigger longitudinal decay analysis and idempotent revision scheduling"
)
def detect_decay_for_student(
    student_id: str,
    topic_id: Optional[str] = Query(None, description="Optional topic filter"),
    db: Session = Depends(get_db)
):
    student = db.query(StudentProfile).filter(StudentProfile.id == student_id).first()
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Student profile {student_id} not found"
        )

    return adaptive_service.detect_and_schedule_for_student(
        db=db,
        student_id=student_id,
        topic_id=topic_id
    )


@router.get(
    "/schedule/{student_id}",
    response_model=AdaptiveScheduleResponse,
    summary="Get prioritized adaptive revision queue for a student"
)
def get_adaptive_schedule(
    student_id: str,
    db: Session = Depends(get_db)
):
    student = db.query(StudentProfile).filter(StudentProfile.id == student_id).first()
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Student profile {student_id} not found"
        )

    return adaptive_service.get_student_schedule(db=db, student_id=student_id)


@router.get(
    "/knowledge-profile/{student_id}",
    response_model=StudentKnowledgeProfileResponse,
    summary="Get reliable adaptive knowledge profiles per topic for a student"
)
def get_student_knowledge_profile(
    student_id: str,
    topic_id: Optional[str] = Query(None, description="Optional topic filter"),
    db: Session = Depends(get_db)
):
    from backend.app.api.v1.endpoints.attempts import _get_or_create_student_profile
    from backend.app.services.knowledge_model import KnowledgeModelService

    student = _get_or_create_student_profile(db, student_id)
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Student profile {student_id} not found"
        )

    return KnowledgeModelService.get_student_knowledge_profiles(
        db=db,
        student_id=student.id,
        topic_id=topic_id,
    )


@router.get(
    "/recommendations/{student_id}",
    response_model=RecommendationResponse,
    summary="Get explainable next-step recommendations prioritized by urgency"
)
def get_student_recommendations(
    student_id: str,
    limit: int = Query(10, ge=1, le=50, description="Max recommendations to return"),
    language: Optional[str] = Query(None, description="Language code (en, hi, gu)"),
    db: Session = Depends(get_db)
):
    from backend.app.api.v1.endpoints.attempts import _get_or_create_student_profile
    from backend.app.services.recommendation_engine import RecommendationEngineService

    student = _get_or_create_student_profile(db, student_id)
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Student profile {student_id} not found"
        )

    target_lang = language or student.preferred_language or "en"

    return RecommendationEngineService.generate_recommendations(
        db=db,
        student_id=student.id,
        limit=limit,
        language=target_lang,
    )


@router.post(
    "/explanation",
    response_model=ExplanationResponse,
    summary="Generate personalized, curriculum-grounded explanation locally"
)
def get_personalized_explanation(
    payload: ExplanationRequest,
    db: Session = Depends(get_db)
):
    from backend.app.api.v1.endpoints.attempts import _get_or_create_student_profile
    from backend.app.services.personalized_explanation import personalized_explanation_service

    student = _get_or_create_student_profile(db, payload.student_id)
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Student profile {payload.student_id} not found"
        )

    try:
        return personalized_explanation_service.generate_explanation(db=db, request=payload)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post(
    "/revision-outcome",
    summary="Process a completed revision attempt and drive signal lifecycle"
)
def process_revision_outcome(
    payload: RevisionOutcomeRequest,
    db: Session = Depends(get_db)
):
    student = db.query(StudentProfile).filter(StudentProfile.id == payload.student_id).first()
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Student profile {payload.student_id} not found"
        )

    # Record longitudinal REVISION learning event
    event = EventRecorderService.record_event(
        db=db,
        student_id=payload.student_id,
        topic_id=payload.topic_id,
        event_type=EventType.REVISION,
        score=payload.score,
        correctness=payload.correctness,
        response_time_ms=payload.response_time_ms,
        session_id=payload.session_id,
        idempotency_key=payload.idempotency_key,
        event_metadata={"revision_flow": True},
        auto_commit=False,
    )

    result = adaptive_service.handle_revision_attempt(
        db=db,
        student_id=payload.student_id,
        topic_id=payload.topic_id,
        score=payload.score,
        correctness=payload.correctness,
        response_time_ms=payload.response_time_ms
    )
    return {"status": "SUCCESS", "lifecycle_update": result, "event_id": event.id}


class CompleteAssessmentRequest(BaseModel):
    student_id: str
    topic_id: str
    score: float = Field(..., ge=0.0, le=100.0)
    total_questions: int = Field(5, ge=1)
    correct_answers: int = Field(..., ge=0)


@router.post(
    "/complete-assessment",
    summary="Evaluate completed assessment performance and trigger formative revision if needed"
)
def complete_assessment(
    payload: CompleteAssessmentRequest,
    db: Session = Depends(get_db)
):
    from backend.app.api.v1.endpoints.attempts import _get_or_create_student_profile, _resolve_topic

    student = _get_or_create_student_profile(db, payload.student_id)
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Student profile {payload.student_id} not found"
        )

    topic = _resolve_topic(db, payload.topic_id)
    if not topic:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Topic '{payload.topic_id}' could not be resolved"
        )

    revision_plan = adaptive_service.evaluate_assessment_performance(
        db=db,
        student_id=student.id,
        topic_id=topic.id,
        score=payload.score,
        total_questions=payload.total_questions,
        correct_answers=payload.correct_answers,
    )

    return {
        "status": "SUCCESS",
        "student_id": student.id,
        "topic_id": topic.id,
        "score": payload.score,
        "revision_required": revision_plan is not None,
        "revision_plan_id": revision_plan.id if revision_plan else None,
        "priority": revision_plan.priority.value if revision_plan else None,
        "reason": revision_plan.reason if revision_plan else None,
    }


# ==================================================
# Phase 7: Adaptive Practice & Personalized Feedback
# ==================================================
from backend.app.schemas.practice import (
    AdaptivePracticeResponse,
    PracticeSubmissionRequest,
    PracticeSubmissionResponse,
    PracticeRecommendation,
)
from backend.app.services.adaptive_practice import adaptive_practice_service


@router.get(
    "/next-practice/{student_id}",
    response_model=PracticeRecommendation,
    summary="Get next practice recommendation and difficulty adapted to student knowledge model"
)
def get_next_practice_recommendation(
    student_id: str,
    topic_id: Optional[str] = Query(None, description="Optional target topic ID or title"),
    language: Optional[str] = Query(None, description="Language code (en, hi, gu)"),
    db: Session = Depends(get_db),
):
    try:
        return adaptive_practice_service.recommend_next_practice(
            db=db,
            student_id=student_id,
            topic_id=topic_id,
            language=language,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Practice recommendation failed: {str(e)}"
        )


@router.get(
    "/practice/{student_id}",
    response_model=AdaptivePracticeResponse,
    summary="Retrieve personalized, curriculum-grounded practice questions adapted to student mastery"
)
def get_adaptive_practice_questions(
    student_id: str,
    topic_id: str = Query(..., description="Target curriculum topic ID or title"),
    count: int = Query(3, ge=1, le=10, description="Number of questions to generate"),
    language: Optional[str] = Query(None, description="Language code (en, hi, gu)"),
    db: Session = Depends(get_db),
):
    try:
        return adaptive_practice_service.generate_practice_questions(
            db=db,
            student_id=student_id,
            topic_id=topic_id,
            count=count,
            language=language,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Adaptive practice generation failed: {str(e)}"
        )


@router.post(
    "/practice/submit",
    response_model=PracticeSubmissionResponse,
    summary="Submit answer to practice question, record learning event, and receive personalized feedback"
)
def submit_practice_answer(
    payload: PracticeSubmissionRequest,
    db: Session = Depends(get_db),
):
    try:
        return adaptive_practice_service.submit_practice_answer(
            db=db,
            submission=payload,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Practice submission failed: {str(e)}"
        )


# ==================================================
# Phase 14: Student Progress Tracking & Learning Journey
# ==================================================
from backend.app.schemas.progress import StudentProgressResponse
from backend.app.services.progress_service import student_progress_service


@router.get(
    "/progress/{student_id}",
    response_model=StudentProgressResponse,
    summary="Get complete empirical progress, mastery distribution, strengths/weaknesses, and learning journey for a student"
)
def get_student_progress(
    student_id: str,
    subject_id: Optional[str] = Query(None, description="Optional subject id, code, name, or 'all' to scope curriculum progress"),
    language: Optional[str] = Query(None, description="Language code (en, hi, gu)"),
    db: Session = Depends(get_db),
):
    try:
        return student_progress_service.get_student_progress(
            db=db,
            student_id=student_id,
            subject_id=subject_id,
            language=language,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Progress tracking failed: {str(e)}"
        )


# ==================================================
# Phase 16: Automated Personalized Revision Planning
# ==================================================
from backend.app.schemas.revision_plan import RevisionPlanResponse
from backend.app.services.revision_planner import revision_planner_service


@router.get(
    "/revision-plan/{student_id}",
    response_model=RevisionPlanResponse,
    summary="Get automated, personalized revision plan with spaced intervals and explainable reasons"
)
def get_student_revision_plan(
    student_id: str,
    subject_id: Optional[str] = Query(None, description="Optional subject id, code, or 'all' to scope revision plan"),
    language: Optional[str] = Query(None, description="Language code for presentation: en, hi, gu"),
    db: Session = Depends(get_db),
):
    try:
        return revision_planner_service.get_or_create_revision_plan(
            db=db,
            student_id=student_id,
            subject_id=subject_id,
            language=language,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Revision planning failed: {str(e)}"
        )


# ==================================================
# Phase 17: Educational Gamification MVP
# ==================================================
from backend.app.schemas.gamification import GamificationResponse
from backend.app.services.gamification_service import gamification_service


@router.get(
    "/gamification/{student_id}",
    response_model=GamificationResponse,
    summary="Get personalized educational gamification profile: XP, level, streak, daily goal, and badges"
)
def get_student_gamification(
    student_id: str,
    language: Optional[str] = Query(None, description="Language code for presentation: en, hi, gu"),
    db: Session = Depends(get_db),
):
    try:
        return gamification_service.get_student_gamification(
            db=db,
            student_id=student_id,
            language=language,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Gamification retrieval failed: {str(e)}"
        )





