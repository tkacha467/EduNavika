from backend.app.core.database import Base
from backend.app.models.base import BaseModelMixin, generate_uuid, get_utc_now
from backend.app.models.user import User, StudentProfile, TeacherProfile, UserRole
from backend.app.models.curriculum import Standard, Subject, Chapter, Topic
from backend.app.models.content import LearningContent, ContentType
from backend.app.models.mcq import MCQQuestion, QuestionHistory, QuestionStatus, QuestionDifficulty, OptionKey
from backend.app.models.assessment import Assessment, AssessmentQuestion, AssessmentStatus
from backend.app.models.attempt import Attempt, Answer, AttemptStatus
from backend.app.models.learning_event import LearningEvent, EventType
from backend.app.models.performance import TopicPerformance
from backend.app.models.revision import RevisionPlan, RevisionPriority, RevisionCompletionState
from backend.app.models.forgetting import ForgettingSignal, ForgettingSignalStatus
from backend.app.models.teacher_action import TeacherAction, TeacherActionType

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
