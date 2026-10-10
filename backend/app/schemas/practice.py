from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from backend.app.domain.enums import MasteryLevel


class AdaptivePracticeQuestion(BaseModel):
    """
    Personalized practice question grounded in curriculum textbook material.
    Includes comprehensive provenance tracing back to GSEB/NCERT syllabus text.
    Note: correct_answer is excluded from student-facing payloads prior to submission.
    """
    id: str
    student_id: str
    topic_id: str
    topic_title: str
    subject: Optional[str] = None
    chapter: Optional[str] = None
    difficulty: str  # FOUNDATIONAL | GUIDED | APPLICATION | CHALLENGE
    question_type: str = "MCQ"  # MCQ or SHORT_ANSWER
    question: str
    options: List[str] = Field(default_factory=list)
    correct_answer: Optional[str] = None  # None when sent to student before submission
    explanation: Optional[str] = None
    source_document: Optional[str] = None
    source_page: Optional[int] = None
    source_chunk_id: Optional[str] = None
    source_text: Optional[str] = None
    skill_target: str
    personalization_reason: str


class AdaptivePracticeResponse(BaseModel):
    """
    Set of personalized practice questions delivered to the student.
    """
    student_id: str
    topic_id: str
    topic_title: str
    target_difficulty: str
    generation_mode: str  # LOCAL_LLM | DETERMINISTIC_FALLBACK
    model_name: Optional[str] = None
    total_questions: int
    questions: List[AdaptivePracticeQuestion]
    message: Optional[str] = None


class PracticeSubmissionRequest(BaseModel):
    """
    Student response submission for an adaptive practice question.
    """
    student_id: str
    question_id: str
    topic_id: str
    selected_answer: str
    response_time_ms: Optional[int] = Field(None, ge=0)
    hint_used: bool = False
    language: Optional[str] = "en"
    confidence_level: Optional[str] = None  # GUESSING | SOMEWHAT_CONFIDENT | VERY_CONFIDENT


class RemediationEvidence(BaseModel):
    """
    Evidence-grounded misconception remediation details extracted from verified local textbook chunks.
    """
    concept_target: str
    what_went_wrong: str
    concept_explanation: str
    textbook_excerpt: Optional[str] = None
    source_document: Optional[str] = None
    source_page: Optional[int] = None
    source_chunk_id: Optional[str] = None
    follow_up_question_id: Optional[str] = None
    follow_up_question_text: Optional[str] = None
    can_retry: bool = True


class PracticeSubmissionResponse(BaseModel):
    """
    Pedagogical feedback and updated learning state following practice submission.
    """
    correct: bool
    correct_answer: str
    selected_answer: str
    feedback: str
    explanation: str
    next_recommended_action: str
    updated_mastery: MasteryLevel
    updated_accuracy: float
    source_document: Optional[str] = None
    source_page: Optional[int] = None
    event_id: str
    remediation: Optional[RemediationEvidence] = None



class PracticeRecommendation(BaseModel):
    """
    Direct practice recommendation decision adhering to knowledge profile.
    """
    topic_id: str
    topic_title: str
    subject_name: Optional[str] = None
    mastery_level: MasteryLevel
    accuracy: float
    recent_accuracy: Optional[float] = None
    trend: str
    retention_risk: str
    recommended_action: str
    recommended_difficulty: str
    reason: str

