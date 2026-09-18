"""
Database Models Package.
All models are consolidated into 4 clean, cohesive modules:
- core_models: Base, User, StudentProfile, TeacherProfile
- curriculum_models: Standard, Subject, Chapter, Topic, LearningContent
- assessment_models: MCQQuestion, Assessment, Attempt, Answer
- adaptive_models: LearningEvent, TopicPerformance, ForgettingSignal, RevisionPlan, TeacherAction
"""

from backend.app.core.database import Base
from backend.app.models.core_models import (
    BaseModelMixin,
    generate_uuid,
    get_utc_now,
    User,
    StudentProfile,
    TeacherProfile,
    UserRole,
)
from backend.app.models.curriculum_models import (
    Standard,
    Subject,
    Chapter,
    Topic,
    LearningContent,
    ContentType,
)
from backend.app.models.assessment_models import (
    MCQQuestion,
    QuestionHistory,
    QuestionStatus,
    QuestionDifficulty,
    OptionKey,
    Assessment,
    AssessmentQuestion,
    AssessmentStatus,
    Attempt,
    Answer,
    AttemptStatus,
)
from backend.app.models.adaptive_models import (
    LearningEvent,
    EventType,
    TopicPerformance,
    RevisionPlan,
    RevisionPriority,
    RevisionCompletionState,
    ForgettingSignal,
    ForgettingSignalStatus,
    TeacherAction,
    TeacherActionType,
)

__all__ = [
    "Base",
    "BaseModelMixin",
    "generate_uuid",
    "get_utc_now",
    "User",
    "StudentProfile",
    "TeacherProfile",
    "UserRole",
    "Standard",
    "Subject",
    "Chapter",
    "Topic",
    "LearningContent",
    "ContentType",
    "MCQQuestion",
    "QuestionHistory",
    "QuestionStatus",
    "QuestionDifficulty",
    "OptionKey",
    "Assessment",
    "AssessmentQuestion",
    "AssessmentStatus",
    "Attempt",
    "Answer",
    "AttemptStatus",
    "LearningEvent",
    "EventType",
    "TopicPerformance",
    "RevisionPlan",
    "RevisionPriority",
    "RevisionCompletionState",
    "ForgettingSignal",
    "ForgettingSignalStatus",
    "TeacherAction",
    "TeacherActionType",
]
