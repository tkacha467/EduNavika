from typing import List, Optional
from sqlalchemy.orm import Session

from backend.app.models import LearningEvent, Topic, StudentProfile
from backend.app.schemas.explanation import ExplanationRequest, ExplanationResponse
from backend.app.schemas.retrieval import RetrievalSearchRequest
from backend.app.services.knowledge_model import KnowledgeModelService
from backend.app.services.recommendation_engine import RecommendationEngineService
from backend.app.services.curriculum_retrieval import CurriculumRetrievalService
from backend.app.services.explanation_engine import (
    ExplanationEngineInterface,
    DeterministicExplanationEngine,
    OnDeviceLLMExplanationEngine,
)
from backend.app.api.v1.endpoints.attempts import _resolve_topic


class PersonalizedExplanationService:
    """
    Orchestrates the complete personalized learning explanation pipeline:
    Student Profile + Topic Recommendation + Curriculum Retrieval -> ExplanationEngine -> Response
    """

    def __init__(self, engine: Optional[ExplanationEngineInterface] = None):
        self.engine = engine or OnDeviceLLMExplanationEngine()

    def generate_explanation(
        self,
        db: Session,
        request: ExplanationRequest,
    ) -> ExplanationResponse:
        student_id = request.student_id
        student = db.query(StudentProfile).filter(StudentProfile.id == student_id).first()

        # 1. Resolve & Validate Topic
        resolved_topic = _resolve_topic(db, request.topic_id)
        if not resolved_topic:
            raise ValueError(f"Topic '{request.topic_id}' could not be resolved.")

        # Check curriculum eligibility (prevent placeholder/unrelated topics)
        if not RecommendationEngineService.is_eligible_curriculum_topic(db, student, resolved_topic):
            raise ValueError(f"Topic '{resolved_topic.title}' is not an eligible curriculum topic for this student.")

        # 2. Retrieve Student Knowledge Profile for this topic
        prof_resp = KnowledgeModelService.get_student_knowledge_profiles(db, student_id, topic_id=resolved_topic.id)
        if prof_resp.profiles:
            knowledge_profile = prof_resp.profiles[0]
        else:
            knowledge_profile = KnowledgeModelService.calculate_topic_profile(db, student_id, resolved_topic)

        # 3. Retrieve Recommendation context
        rec_resp = RecommendationEngineService.generate_recommendations(db, student_id)
        rec = next((r for r in rec_resp.recommendations if r.topic_id == resolved_topic.id), None)

        # 4. Retrieve Grounded Curriculum Material
        search_query = request.query or f"{resolved_topic.title} key concepts"
        ret_req = RetrievalSearchRequest(
            student_id=student_id,
            topic_id=resolved_topic.id,
            query=search_query,
            top_k=request.top_k,
        )
        ret_res = CurriculumRetrievalService.search(db, ret_req)

        # 5. Extract Recent Student Error Context (if any recorded in events)
        error_events = (
            db.query(LearningEvent)
            .filter(
                LearningEvent.student_id == student_id,
                LearningEvent.topic_id == resolved_topic.id,
                LearningEvent.correctness == False,
            )
            .order_by(LearningEvent.timestamp.desc())
            .limit(3)
            .all()
        )
        error_notes: List[str] = []
        for e in error_events:
            if e.event_metadata and e.event_metadata.get("mcq_id"):
                error_notes.append(f"Question {e.event_metadata.get('mcq_id')}")

        # 6. Delegate to Local Explanation Engine
        target_lang = (
            request.language
            or (student.preferred_language if student and hasattr(student, "preferred_language") else None)
            or "en"
        ).lower()

        return self.engine.generate(
            student_id=student_id,
            topic_id=resolved_topic.id,
            topic_title=resolved_topic.title,
            knowledge_profile=knowledge_profile,
            recommendation=rec,
            retrieved_contexts=ret_res.results,
            student_query=request.query,
            recent_error_notes=error_notes if error_notes else None,
            language=target_lang,
        )


# Global default service instance
personalized_explanation_service = PersonalizedExplanationService()
