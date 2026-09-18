from typing import Optional, Any, Dict
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field
from backend.app.models import QuestionStatus, QuestionDifficulty, OptionKey


class MCQBase(BaseModel):
    topic_id: str
    question_text: str
    option_a: str
    option_b: str
    option_c: str
    option_d: str
    correct_option: OptionKey
    explanation: Optional[str] = None
    difficulty: QuestionDifficulty = QuestionDifficulty.MEDIUM
    source_content_id: Optional[str] = None
    generation_model: Optional[str] = None
    generation_version: Optional[str] = None
    status: QuestionStatus = QuestionStatus.DRAFT


class MCQCreate(MCQBase):
    pass


class MCQUpdateStatus(BaseModel):
    status: QuestionStatus


class QuestionHistoryResponse(BaseModel):
    id: str
    question_id: str
    normalized_question_text: str
    text_hash: str
    embedding_reference: Optional[str] = None
    generation_metadata: Optional[Dict[str, Any]] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class MCQResponse(MCQBase):
    id: str
    created_at: datetime
    updated_at: datetime
    history: Optional[QuestionHistoryResponse] = None

    model_config = ConfigDict(from_attributes=True)


class DuplicateCheckResult(BaseModel):
    is_exact_duplicate: bool
    existing_question_id: Optional[str] = None
    text_hash: str
    similarity_score: Optional[float] = None
    duplicate_type: str = "NONE"  # NONE, EXACT, SEMANTIC
