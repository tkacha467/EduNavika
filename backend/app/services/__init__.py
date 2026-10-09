from backend.app.services.duplicate_detection import (
    ExactDuplicateDetector,
    SemanticDuplicateDetectorInterface,
    normalize_text,
    compute_text_hash,
)
from backend.app.services.event_recorder import EventRecorderService
from backend.app.services.knowledge_model import KnowledgeModelService
from backend.app.services.recommendation_engine import RecommendationEngineService
from backend.app.services.curriculum_retrieval import CurriculumRetrievalService
from backend.app.services.explanation_engine import (
    ExplanationEngineInterface,
    DeterministicExplanationEngine,
)
from backend.app.services.personalized_explanation import (
    PersonalizedExplanationService,
    personalized_explanation_service,
)
from backend.app.services.adaptive_practice import (
    AdaptivePracticeService,
    adaptive_practice_service,
)

__all__ = [
    "ExactDuplicateDetector",
    "SemanticDuplicateDetectorInterface",
    "normalize_text",
    "compute_text_hash",
    "EventRecorderService",
    "KnowledgeModelService",
    "RecommendationEngineService",
    "CurriculumRetrievalService",
    "ExplanationEngineInterface",
    "DeterministicExplanationEngine",
    "PersonalizedExplanationService",
    "personalized_explanation_service",
    "AdaptivePracticeService",
    "adaptive_practice_service",
    "GamificationService",
    "gamification_service",
]
from backend.app.services.gamification_service import (
    GamificationService,
    gamification_service,
)


