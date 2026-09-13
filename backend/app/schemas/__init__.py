from backend.app.schemas.common import (
    PaginatedResponse,
    ResponseMetadata,
    MessageResponse,
    ErrorResponse,
    ErrorDetail,
)
from backend.app.schemas.user import (
    UserCreate,
    UserUpdate,
    UserResponse,
    StudentProfileCreate,
    StudentProfileResponse,
    TeacherProfileCreate,
    TeacherProfileResponse,
)
from backend.app.schemas.curriculum import (
    StandardCreate,
    StandardResponse,
    SubjectCreate,
    SubjectResponse,
    ChapterCreate,
    ChapterResponse,
    TopicCreate,
    TopicResponse,
)
from backend.app.schemas.content import (
    LearningContentCreate,
    LearningContentResponse,
)
from backend.app.schemas.mcq import (
    MCQCreate,
    MCQUpdateStatus,
    MCQResponse,
    QuestionHistoryResponse,
    DuplicateCheckResult,
)
from backend.app.schemas.assessment import (
    AssessmentQuestionCreate,
    AssessmentQuestionResponse,
    AssessmentCreate,
    AssessmentPublish,
    AssessmentResponse,
    AssessmentDetailResponse,
)
from backend.app.schemas.attempt import (
    AttemptCreate,
    AnswerSubmit,
    AttemptSubmit,
    AnswerResponse,
    AttemptResponse,
    AttemptDetailResponse,
)
from backend.app.schemas.learning_event import (
    LearningEventCreate,
    LearningEventResponse,
)
from backend.app.schemas.performance import (
    TopicPerformanceResponse,
)
from backend.app.schemas.revision import (
    RevisionPlanCreate,
    RevisionPlanResponse,
)
from backend.app.schemas.forgetting import (
    ForgettingSignalCreate,
    ForgettingSignalResponse,
)
from backend.app.schemas.teacher_action import (
    TeacherActionCreate,
    TeacherActionResponse,
)

__all__ = [
    "PaginatedResponse",
    "ResponseMetadata",
    "MessageResponse",
    "ErrorResponse",
    "ErrorDetail",
    "UserCreate",
    "UserUpdate",
    "UserResponse",
    "StudentProfileCreate",
    "StudentProfileResponse",
    "TeacherProfileCreate",
    "TeacherProfileResponse",
    "StandardCreate",
    "StandardResponse",
    "SubjectCreate",
    "SubjectResponse",
    "ChapterCreate",
    "ChapterResponse",
    "TopicCreate",
    "TopicResponse",
    "LearningContentCreate",
    "LearningContentResponse",
    "MCQCreate",
    "MCQUpdateStatus",
    "MCQResponse",
    "QuestionHistoryResponse",
    "DuplicateCheckResult",
    "AssessmentQuestionCreate",
    "AssessmentQuestionResponse",
    "AssessmentCreate",
    "AssessmentPublish",
    "AssessmentResponse",
    "AssessmentDetailResponse",
    "AttemptCreate",
    "AnswerSubmit",
    "AttemptSubmit",
    "AnswerResponse",
    "AttemptResponse",
    "AttemptDetailResponse",
    "LearningEventCreate",
    "LearningEventResponse",
    "TopicPerformanceResponse",
    "RevisionPlanCreate",
    "RevisionPlanResponse",
    "ForgettingSignalCreate",
    "ForgettingSignalResponse",
    "TeacherActionCreate",
    "TeacherActionResponse",
]
