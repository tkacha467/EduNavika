import enum


class UserRole(str, enum.Enum):
    STUDENT = "STUDENT"
    TEACHER = "TEACHER"
    ADMIN = "ADMIN"


class ContentType(str, enum.Enum):
    TEXT = "TEXT"
    EXAMPLE = "EXAMPLE"
    DEFINITION = "DEFINITION"
    FORMULA = "FORMULA"
    EXPLANATION = "EXPLANATION"
    QUESTION_REFERENCE = "QUESTION_REFERENCE"


class QuestionStatus(str, enum.Enum):
    DRAFT = "DRAFT"
    PENDING_REVIEW = "PENDING_REVIEW"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    PUBLISHED = "PUBLISHED"
    ARCHIVED = "ARCHIVED"


class QuestionDifficulty(str, enum.Enum):
    EASY = "EASY"
    MEDIUM = "MEDIUM"
    HARD = "HARD"


class OptionKey(str, enum.Enum):
    A = "A"
    B = "B"
    C = "C"
    D = "D"


class AssessmentStatus(str, enum.Enum):
    DRAFT = "DRAFT"
    SCHEDULED = "SCHEDULED"
    PUBLISHED = "PUBLISHED"
    COMPLETED = "COMPLETED"
    ARCHIVED = "ARCHIVED"


class AttemptStatus(str, enum.Enum):
    STARTED = "STARTED"
    SUBMITTED = "SUBMITTED"
    ABANDONED = "ABANDONED"


class EventType(str, enum.Enum):
    LEARN = "LEARN"
    PRACTICE = "PRACTICE"
    MCQ_ATTEMPT = "MCQ_ATTEMPT"
    REVISION = "REVISION"
    REVIEW = "REVIEW"


class RevisionPriority(str, enum.Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    URGENT = "URGENT"


class RevisionCompletionState(str, enum.Enum):
    PENDING = "PENDING"
    COMPLETED = "COMPLETED"
    DISMISSED = "DISMISSED"
    OVERDUE = "OVERDUE"


class ForgettingSignalStatus(str, enum.Enum):
    UNRESOLVED = "UNRESOLVED"
    ADDRESSED_BY_REVISION = "ADDRESSED_BY_REVISION"
    DISMISSED = "DISMISSED"


class TeacherActionType(str, enum.Enum):
    RECOMMEND_REVISION = "RECOMMEND_REVISION"
    ASSIGN_PRACTICE = "ASSIGN_PRACTICE"
    FLAG_TOPIC = "FLAG_TOPIC"
    REVIEW_PERFORMANCE = "REVIEW_PERFORMANCE"
