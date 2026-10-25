"""
EduNavika — Competitive Examination & Assessment Engine API Endpoints.
Supports JEE Main, JEE Advanced, and NEET UG curriculum navigation,
previous-year paper exploration, 20-question coverage audits, and timed assessments.
"""

from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query, Body
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.models.competitive_models import (
    Examination,
    ExamSubject,
    ExamPaper,
    Question,
    QuestionOption,
    QuestionVerificationLog,
)
from backend.app.models.curriculum_models import Chapter, Topic, Subject, Standard
from backend.app.services.curriculum_coverage_service import CurriculumCoverageService
from backend.app.services.competitive_assessment_service import (
    CompetitiveAssessmentService,
    ACTIVE_ASSESSMENT_SESSIONS,
)
from backend.app.core.security import get_current_reviewer
from backend.app.models.core_models import User
from backend.app.services.question_verification_service import QuestionVerificationService



router = APIRouter(prefix="/competitive", tags=["Competitive Examination Platform"])


class StartAssessmentRequest(BaseModel):
    student_id: str = Field(default="e09699dd-0c64-44cc-82ef-ab41a832e072")
    exam_code: str = Field(default="JEE_MAIN", description="JEE_MAIN, JEE_ADVANCED, or NEET_UG")
    mode: str = Field(default="CHAPTER_MOCK", description="CHAPTER_MOCK, SUBJECT_MOCK, or FULL_MOCK")
    chapter_id: Optional[str] = None
    duration_minutes: int = Field(default=45, ge=1, le=360)
    total_questions: int = Field(default=20, ge=1, le=200)


class SaveResponseRequest(BaseModel):
    question_id: str
    selected_option: Optional[str] = None
    selected_options: Optional[List[str]] = None
    numerical_value: Optional[float] = None
    status: str = Field(default="ANSWERED", description="ANSWERED, UNANSWERED, MARKED_FOR_REVIEW")
    time_spent_seconds: int = Field(default=0, ge=0)


class SeedCoverageRequest(BaseModel):
    chapter_id: str
    target_count: int = Field(default=20, ge=1, le=50)


# 1. Competitive Examinations Master
@router.get("/exams", summary="List supported competitive examinations")
def list_examinations(db: Session = Depends(get_db)):
    exams = db.query(Examination).filter(Examination.is_active == True).all()
    results = []
    for e in exams:
        subjs = [es.subject.name for es in e.exam_subjects if es.subject]
        results.append({
            "code": e.code,
            "name": e.name,
            "conducting_body": e.conducting_body,
            "description": e.description,
            "subjects": sorted(list(set(subjs))),
            "total_exam_topics": len(e.exam_topics),
            "total_papers": len(e.exam_papers),
        })
    return results


# 2. Curriculum Coverage Audit
@router.get("/coverage", summary="Audit question coverage against 20-question target")
def get_curriculum_coverage(
    exam_code: Optional[str] = Query(None, description="Optional filter by JEE_MAIN, JEE_ADVANCED, NEET_UG"),
    db: Session = Depends(get_db)
):
    service = CurriculumCoverageService(db)
    return service.audit_full_curriculum_coverage(exam_code=exam_code)


@router.get("/coverage/chapters/{chapter_id}", summary="Audit coverage for single chapter")
def get_chapter_coverage(
    chapter_id: str,
    exam_code: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    service = CurriculumCoverageService(db)
    try:
        return service.audit_chapter_coverage(chapter_id, exam_code=exam_code)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post("/coverage/seed", summary="Seed verified textbook practice to meet 20-question target")
def seed_chapter_coverage(
    payload: SeedCoverageRequest,
    db: Session = Depends(get_db)
):
    service = CurriculumCoverageService(db)
    return service.seed_supplementary_chapter_practice(
        chapter_id=payload.chapter_id,
        target_count=payload.target_count,
    )


# 3. Previous-Year Papers (PYQ Browser)
@router.get("/papers", summary="List previous-year examination papers")
def list_exam_papers(
    exam_code: Optional[str] = Query(None, description="Filter by JEE_ADVANCED, NEET_UG, etc."),
    year: Optional[int] = Query(None),
    db: Session = Depends(get_db)
):
    q = db.query(ExamPaper)
    if exam_code:
        q = q.filter(ExamPaper.exam_code == exam_code)
    if year:
        q = q.filter(ExamPaper.exam_year == year)
    papers = q.order_by(ExamPaper.exam_year.desc()).all()

    return [
        {
            "id": p.id,
            "paper_identifier": p.paper_identifier,
            "exam_code": p.exam_code,
            "exam_year": p.exam_year,
            "session_or_shift": p.session_or_shift,
            "paper_code": p.paper_code,
            "total_questions": p.total_questions,
            "has_pdf": bool(p.source_pdf_path),
            "questions_count": len(p.questions),
        }
        for p in papers
    ]


@router.get("/papers/{paper_id}/questions", summary="Get questions for an authentic exam paper")
def get_paper_questions(paper_id: str, db: Session = Depends(get_db)):
    paper = db.query(ExamPaper).filter(ExamPaper.id == paper_id).first()
    if not paper:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Paper not found")

    questions = (
        db.query(Question)
        .filter(
            Question.exam_paper_id == paper_id,
            Question.publish_permission != "FORBIDDEN",
        )
        .order_by(Question.paper_question_number)
        .all()
    )

    return {
        "paper_identifier": paper.paper_identifier,
        "exam_code": paper.exam_code,
        "exam_year": paper.exam_year,
        "session_or_shift": paper.session_or_shift,
        "total_questions": len(questions),
        "questions": [
            {
                "id": q.id,
                "paper_question_number": q.paper_question_number,
                "question_type": q.question_type,
                "question_text": q.question_text,
                "diagram_asset_url": q.diagram_asset_url,
                "options": [
                    {
                        "option_key": o.option_key,
                        "option_text": o.option_text,
                        "diagram_asset_url": o.diagram_asset_url,
                    }
                    for o in q.options
                ],
                "answer_verification_status": q.answer_verification_status,
                "source_type": q.source_type,
                "difficulty_tier": q.difficulty_tier,
                "solution_text": q.solution_text,
            }
            for q in questions
        ]
    }


# 4. Chapter-wise Questions & Practice
@router.get("/chapters/{chapter_id}/questions", summary="List questions for a chapter")
def get_chapter_questions(
    chapter_id: str,
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    topics = db.query(Topic).filter(Topic.chapter_id == chapter_id).all()
    topic_ids = [t.id for t in topics]

    questions = (
        db.query(Question)
        .filter(
            Question.topic_id.in_(topic_ids),
            Question.quarantine_status == "CLEAN",
            Question.publish_permission != "FORBIDDEN",
        )
        .limit(limit)
        .all()
    )

    return [
        {
            "id": q.id,
            "question_type": q.question_type,
            "question_text": q.question_text,
            "options": [
                {"option_key": o.option_key, "option_text": o.option_text}
                for o in q.options
            ],
            "topic_title": q.topic.title if q.topic else None,
            "source_type": q.source_type,
            "difficulty_tier": q.difficulty_tier,
            "ncert_citation": q.ncert_citation,
        }
        for q in questions
    ]


# 5. Timed Competitive Assessment Engine
@router.post("/assessments/start", summary="Start a server-authoritative timed assessment session")
def start_assessment(payload: StartAssessmentRequest, db: Session = Depends(get_db)):
    service = CompetitiveAssessmentService(db)
    try:
        return service.start_assessment_session(
            student_id=payload.student_id,
            exam_code=payload.exam_code,
            mode=payload.mode,
            chapter_id=payload.chapter_id,
            duration_minutes=payload.duration_minutes,
            total_questions=payload.total_questions,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))


@router.get("/assessments/{session_id}", summary="Get active assessment session status and time remaining")
def get_assessment_status(session_id: str):
    session = ACTIVE_ASSESSMENT_SESSIONS.get(session_id)
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assessment session not found")
    from backend.app.services.competitive_assessment_service import CompetitiveAssessmentService
    dummy_service = CompetitiveAssessmentService(None)
    return dummy_service._format_client_session(session)


@router.post("/assessments/{session_id}/save", summary="Save question answer during active test")
def save_assessment_answer(
    session_id: str,
    payload: SaveResponseRequest,
    db: Session = Depends(get_db)
):
    service = CompetitiveAssessmentService(db)
    try:
        return service.save_response(
            session_id=session_id,
            question_id=payload.question_id,
            selected_option=payload.selected_option,
            selected_options=payload.selected_options,
            numerical_value=payload.numerical_value,
            status=payload.status,
            time_spent_seconds=payload.time_spent_seconds,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post("/assessments/{session_id}/submit", summary="Submit assessment and compute exam-specific score")
def submit_assessment(session_id: str, db: Session = Depends(get_db)):
    service = CompetitiveAssessmentService(db)
    try:
        return service.submit_assessment(session_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


import json


class HumanReviewRequest(BaseModel):
    reviewer_id: Optional[str] = Field(default=None, description="Optional; overridden by authenticated reviewer session")
    decision: str = Field(..., description="APPROVED, REJECTED, or NEEDS_CORRECTION")
    review_notes: str = Field(default="", description="Reviewer comments and rationales")
    asset_ids_reviewed: Optional[List[str]] = Field(default=None)
    asset_checksums: Optional[Dict[str, str]] = Field(default=None)
    manifest_version: Optional[str] = Field(default="1.0")


# 6. Authenticated Human Content & Visual Verification Endpoints (Reviewer-Facing)
@router.post("/questions/{question_id}/review", summary="Submit explicit human visual/content review decision")
def submit_question_review(
    question_id: str,
    payload: HumanReviewRequest,
    current_reviewer: User = Depends(get_current_reviewer),
    db: Session = Depends(get_db)
):
    """
    Submits an auditable reviewer decision for a question and its diagram assets.
    Server-side authorization strictly binds the verified reviewer identity to the authenticated user.
    Requires meaningful review notes (min 5 chars) for REJECTED or NEEDS_CORRECTION.
    """
    decision_clean = payload.decision.strip().upper()
    if decision_clean in ("REJECTED", "NEEDS_CORRECTION") and len((payload.review_notes or "").strip()) < 5:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"A meaningful review note (minimum 5 characters) is required when submitting decision '{decision_clean}'.",
        )

    # Server-verified reviewer identity bound to authenticated user
    verified_reviewer_id = current_reviewer.email or current_reviewer.name or current_reviewer.id

    service = QuestionVerificationService(db)
    try:
        result = service.submit_human_visual_review(
            question_id=question_id,
            reviewer_id=verified_reviewer_id,
            decision=decision_clean,
            review_notes=payload.review_notes,
            asset_ids_reviewed=payload.asset_ids_reviewed,
            asset_checksums=payload.asset_checksums,
            source_manifest_version=payload.manifest_version,
        )
        db.commit()
        return result
    except ValueError as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/review/unverified", summary="List questions requiring human verification (Reviewer-facing)")
def list_unverified_questions(
    exam_code: Optional[str] = Query(None),
    year: Optional[int] = Query(None),
    subject: Optional[str] = Query(None),
    question_number: Optional[int] = Query(None),
    review_state: Optional[str] = Query(None, description="ALL, INGESTED, NEEDS_CORRECTION, REJECTED, CONTENT_VERIFIED"),
    issue_type: Optional[str] = Query(None, description="ALL, QUARANTINED, CLEAN, DIAGRAM_MISSING, GRAPHICAL_OPTIONS"),
    paper_id: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    current_reviewer: User = Depends(get_current_reviewer),
    db: Session = Depends(get_db)
):
    """
    Returns questions awaiting or subject to review for authorized reviewers.
    Protected by role-based authorization (TEACHER, ADMIN, REVIEWER).
    """
    q = db.query(Question)

    # Filter review state
    if review_state and review_state.upper() != "ALL":
        q = q.filter(Question.verification_status == review_state.upper())
    else:
        q = q.filter(Question.verification_status.in_(["INGESTED", "NEEDS_CORRECTION", "PENDING_HUMAN_REVIEW", "REJECTED"]))

    # Filter exam paper
    if paper_id:
        q = q.filter(Question.exam_paper_id == paper_id)
    if exam_code or year:
        q = q.join(ExamPaper, Question.exam_paper_id == ExamPaper.id)
        if exam_code:
            q = q.filter(ExamPaper.exam_code == exam_code.upper())
        if year:
            q = q.filter(ExamPaper.exam_year == year)

    # Filter question number
    if question_number is not None:
        q = q.filter(Question.paper_question_number == question_number)

    # Filter issue type
    if issue_type:
        issue_clean = issue_type.upper()
        if issue_clean == "QUARANTINED":
            q = q.filter(Question.quarantine_status != "CLEAN")
        elif issue_clean == "CLEAN":
            q = q.filter(Question.quarantine_status == "CLEAN")
        elif issue_clean == "DIAGRAM_MISSING":
            q = q.filter(Question.quarantine_reason.ilike("%diagram%"))
        elif issue_clean == "GRAPHICAL_OPTIONS":
            q = q.filter(Question.quarantine_reason.ilike("%option%"))

    questions = q.order_by(Question.paper_question_number.asc()).offset(offset).limit(limit).all()

    return [
        {
            "id": item.id,
            "paper_question_number": item.paper_question_number,
            "exam_code": item.exam_paper.exam_code if item.exam_paper else None,
            "exam_year": item.exam_paper.exam_year if item.exam_paper else None,
            "paper_code": item.exam_paper.paper_code if item.exam_paper else None,
            "question_type": item.question_type,
            "question_text": item.question_text,
            "diagram_asset_url": item.diagram_asset_url,
            "verification_status": item.verification_status,
            "quarantine_status": item.quarantine_status,
            "quarantine_reason": item.quarantine_reason,
            "answer_verification_status": item.answer_verification_status,
            "rights_status": item.rights_status,
            "publish_permission": item.publish_permission,
            "eligibility_for_scoring": item.eligibility_for_scoring,
            "options": [
                {
                    "option_key": o.option_key,
                    "option_text": o.option_text,
                    "diagram_asset_url": o.diagram_asset_url,
                }
                for o in sorted(item.options, key=lambda x: x.sort_order)
            ],
            "verification_logs_count": len(item.verification_logs),
        }
        for item in questions
    ]


@router.get("/questions/{question_id}/detail", summary="Get question details and verification logs for reviewer")
def get_question_review_detail(
    question_id: str,
    current_reviewer: User = Depends(get_current_reviewer),
    db: Session = Depends(get_db)
):
    """
    Returns full question structure, options, diagrams, curriculum anchor, and immutable audit logs.
    """
    q = db.query(Question).filter(Question.id == question_id).first()
    if not q:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Question not found")

    logs = (
        db.query(QuestionVerificationLog)
        .filter(QuestionVerificationLog.question_id == question_id)
        .order_by(QuestionVerificationLog.reviewed_at.desc())
        .all()
    )
    formatted_logs = []
    for log in logs:
        parsed_notes = None
        if log.review_notes:
            try:
                parsed_notes = json.loads(log.review_notes)
            except Exception:
                parsed_notes = log.review_notes
        formatted_logs.append({
            "id": log.id,
            "actor": log.verified_by,
            "verified_by": log.verified_by,
            "action": log.action_type,
            "action_type": log.action_type,
            "previous_status": log.previous_status,
            "new_status": log.new_status,
            "created_at": log.reviewed_at.isoformat() if log.reviewed_at else None,
            "reviewed_at": log.reviewed_at.isoformat() if log.reviewed_at else None,
            "notes": str(parsed_notes.get("reviewer_notes", parsed_notes) if isinstance(parsed_notes, dict) else parsed_notes),
            "review_notes": parsed_notes,
        })

    paper = q.exam_paper
    topic_title = q.topic.title if q.topic else None
    chapter_title = q.topic.chapter.title if q.topic and q.topic.chapter else None
    subject_name = q.topic.chapter.subject.name if q.topic and q.topic.chapter and q.topic.chapter.subject else None

    return {
        "id": q.id,
        "question_number": q.paper_question_number,
        "paper_question_number": q.paper_question_number,
        "exam_code": paper.exam_code if paper else None,
        "exam_year": paper.exam_year if paper else None,
        "paper_code": paper.paper_code if paper else None,
        "paper_identifier": paper.paper_identifier if paper else None,
        "subject_name": subject_name,
        "chapter_title": chapter_title,
        "topic_title": topic_title,
        "question_type": q.question_type,
        "question_text": q.question_text,
        "diagram_asset_url": q.diagram_asset_url,
        "options": [
            {
                "id": o.id,
                "option_key": o.option_key,
                "option_text": o.option_text,
                "diagram_asset_url": o.diagram_asset_url,
                "is_correct": o.is_correct,
                "explanation": o.explanation,
                "sort_order": o.sort_order,
            }
            for o in sorted(q.options, key=lambda x: x.sort_order)
        ],
        "correct_answer_raw": q.correct_answer_raw,
        "answer_verification_status": q.answer_verification_status,
        "solution_text": q.solution_text,
        "ncert_citation": q.ncert_citation,
        "official_status": q.official_status,
        "official_status_evidence": q.official_status_evidence,
        "quarantine_status": q.quarantine_status,
        "quarantine_reason": q.quarantine_reason,
        "rights_status": q.rights_status,
        "publish_permission": q.publish_permission,
        "eligibility_for_scoring": q.eligibility_for_scoring,
        "verification_status": q.verification_status,
        "content_hash": q.content_hash,
        "verification_logs": formatted_logs,
        "audit_history": formatted_logs,
    }


