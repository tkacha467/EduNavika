import abc
import hashlib
import re
from typing import Optional, Tuple
from sqlalchemy.orm import Session
from backend.app.models.mcq import QuestionHistory, MCQQuestion
from backend.app.schemas.mcq import DuplicateCheckResult


def normalize_text(text: str) -> str:
    """
    Normalizes text for consistent hashing:
    - Lowercase
    - Strip leading/trailing whitespace
    - Replace multiple whitespaces/newlines with single space
    - Strip non-alphanumeric punctuation characters
    """
    if not text:
        return ""
    text = text.lower().strip()
    text = re.sub(r"[^\w\s]", "", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def compute_text_hash(text: str) -> str:
    """
    Computes a SHA-256 hash of the normalized text.
    """
    normalized = normalize_text(text)
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


class SemanticDuplicateDetectorInterface(abc.ABC):
    """
    Clean abstraction / interface for future vector embedding duplicate detection.
    Will be implemented when vector store infrastructure (e.g. pgvector / Chroma)
    is integrated into the pipeline.
    """

    @abc.abstractmethod
    def check_semantic_duplicate(
        self,
        db: Session,
        normalized_text: str,
        threshold: float = 0.85
    ) -> Optional[Tuple[str, float]]:
        """
        Returns (existing_question_id, similarity_score) if a semantic duplicate is found,
        otherwise None.
        """
        pass


class ExactDuplicateDetector:
    """
    Deterministic exact duplicate detection using SHA-256 hash comparison
    over normalized question text.
    """

    @staticmethod
    def check_duplicate(db: Session, question_text: str) -> DuplicateCheckResult:
        normalized = normalize_text(question_text)
        text_hash = compute_text_hash(question_text)

        existing = db.query(QuestionHistory).filter(QuestionHistory.text_hash == text_hash).first()
        if existing:
            return DuplicateCheckResult(
                is_exact_duplicate=True,
                existing_question_id=existing.question_id,
                text_hash=text_hash,
                similarity_score=1.0,
                duplicate_type="EXACT",
            )
        
        return DuplicateCheckResult(
            is_exact_duplicate=False,
            existing_question_id=None,
            text_hash=text_hash,
            similarity_score=0.0,
            duplicate_type="NONE",
        )

    @staticmethod
    def record_history(
        db: Session,
        question: MCQQuestion,
        embedding_reference: Optional[str] = None
    ) -> QuestionHistory:
        """
        Records question text hash and normalization into QuestionHistory.
        """
        normalized = normalize_text(question.question_text)
        text_hash = compute_text_hash(question.question_text)

        history = QuestionHistory(
            question_id=question.id,
            normalized_question_text=normalized,
            text_hash=text_hash,
            embedding_reference=embedding_reference,
            generation_metadata={
                "model": question.generation_model,
                "version": question.generation_version,
                "difficulty": question.difficulty.value if question.difficulty else None,
            }
        )
        db.add(history)
        return history
