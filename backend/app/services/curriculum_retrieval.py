import re
import math
from collections import Counter
from typing import List, Optional, Dict, Any, Tuple
from sqlalchemy.orm import Session

from backend.app.models import LearningContent, Topic, Chapter, Subject, StudentProfile
from backend.app.schemas.retrieval import (
    RetrievalSearchRequest,
    RetrievedContentItem,
    RetrievalSearchResponse,
)
from backend.app.services.recommendation_engine import RecommendationEngineService
from backend.app.services.topic_resolver import resolve_topic as _resolve_topic


class CurriculumRetrievalService:
    """
    Deterministic Local Lexical (BM25) Retrieval Service for Grounded Curriculum Content.
    Constrains results to verified pedagogical curriculum topics (e.g. Chemical Reactions and Equations),
    rejecting synthetic or unrelated placeholder topics.
    """

    @staticmethod
    def _tokenize(text: str) -> List[str]:
        """Simple, robust tokenization supporting alphanumeric words."""
        return re.findall(r"\b[a-zA-Z0-9_]+\b", text.lower())

    @staticmethod
    def _bm25_score(
        query_tokens: List[str],
        docs: List[LearningContent],
        k1: float = 1.5,
        b: float = 0.75,
    ) -> List[Tuple[float, LearningContent]]:
        """
        Computes standard BM25 Okapi scores over the target document collection.
        Deterministic, pure-python, zero extra native dependency.
        """
        if not docs:
            return []

        doc_tokens = [CurriculumRetrievalService._tokenize(d.content_text) for d in docs]
        N = len(docs)
        avgdl = sum(len(dt) for dt in doc_tokens) / N if N > 0 else 1.0

        # Document frequency per token
        df = Counter()
        for dt in doc_tokens:
            for token in set(dt):
                df[token] += 1

        scored: List[Tuple[float, LearningContent]] = []
        for idx, dt in enumerate(doc_tokens):
            score = 0.0
            doc_len = len(dt)
            tf = Counter(dt)
            for qt in query_tokens:
                if qt in df:
                    n_qi = df[qt]
                    # Standard BM25 IDF formulation
                    idf = math.log((N - n_qi + 0.5) / (n_qi + 0.5) + 1.0)
                    freq = tf[qt]
                    numerator = freq * (k1 + 1)
                    denominator = freq + k1 * (1 - b + b * (doc_len / avgdl))
                    score += idf * (numerator / denominator)
            scored.append((round(score, 4), docs[idx]))

        # Sort descending by score; tie-break by source page ascending if available
        scored.sort(key=lambda item: (item[0], -(item[1].source_page or 9999)), reverse=True)
        return scored

    @staticmethod
    def search(
        db: Session,
        request: RetrievalSearchRequest,
    ) -> RetrievalSearchResponse:
        """
        Executes grounded topic-aware curriculum content retrieval.
        """
        query_text = (request.query or "").strip()
        student = None
        if request.student_id:
            student = db.query(StudentProfile).filter(StudentProfile.id == request.student_id).first()

        # 1. Topic Resolution & Validation
        target_topic: Optional[Topic] = None
        if request.topic_id:
            target_topic = _resolve_topic(db, request.topic_id)
            if not target_topic:
                # Return empty response if topic cannot be found
                return RetrievalSearchResponse(
                    query=query_text,
                    topic_id=request.topic_id,
                    topic_title=None,
                    total_results=0,
                    results=[],
                )

            # Check curriculum eligibility
            if not RecommendationEngineService.is_eligible_curriculum_topic(db, student, target_topic):
                # Never return synthetic placeholder or standard-mismatched topics
                return RetrievalSearchResponse(
                    query=query_text,
                    topic_id=target_topic.id,
                    topic_title=target_topic.title,
                    total_results=0,
                    results=[],
                )

        # 2. Collect Candidate Learning Content
        content_query = db.query(LearningContent).join(LearningContent.topic)

        if target_topic:
            content_query = content_query.filter(LearningContent.topic_id == target_topic.id)
        else:
            # If no topic specified, restrict to eligible curriculum topics
            content_query = content_query.filter(
                ~Topic.title.ilike("%general content%"),
                ~Topic.title.ilike("%general curriculum%"),
            )
            if student and student.standard_id:
                content_query = (
                    content_query.join(Topic.chapter)
                    .join(Chapter.subject)
                    .filter(Subject.standard_id == student.standard_id)
                )

        candidate_contents: List[LearningContent] = content_query.all()
        if not candidate_contents:
            return RetrievalSearchResponse(
                query=query_text,
                topic_id=target_topic.id if target_topic else None,
                topic_title=target_topic.title if target_topic else None,
                total_results=0,
                results=[],
            )

        # 3. Handle Empty Query
        query_tokens = CurriculumRetrievalService._tokenize(query_text)
        if not query_tokens:
            # If query is blank, return first top_k curriculum chunks ordered by page
            sorted_by_page = sorted(candidate_contents, key=lambda c: c.source_page or 9999)[: request.top_k]
            results = [
                RetrievedContentItem(
                    content_id=c.id,
                    topic_id=c.topic_id,
                    topic_title=c.topic.title,
                    chapter_title=c.topic.chapter.title if c.topic and c.topic.chapter else None,
                    subject_name=c.topic.chapter.subject.name if (c.topic and c.topic.chapter and c.topic.chapter.subject) else None,
                    content_type=c.content_type.value if hasattr(c.content_type, "value") else str(c.content_type),
                    source_document=c.source_document,
                    source_page=c.source_page,
                    source_reference=c.source_reference,
                    content_text=c.content_text,
                    score=1.0,
                )
                for c in sorted_by_page
            ]
            return RetrievalSearchResponse(
                query=query_text,
                topic_id=target_topic.id if target_topic else None,
                topic_title=target_topic.title if target_topic else None,
                total_results=len(results),
                results=results,
            )

        # 4. Compute BM25 Relevance Scores
        scored_docs = CurriculumRetrievalService._bm25_score(query_tokens, candidate_contents)

        # Filter strictly positive scores; fallback to top page chunks if all 0
        positive_results = [(s, d) for s, d in scored_docs if s > 0.0]
        if not positive_results:
            selected_docs = [(0.0, d) for d in candidate_contents[: request.top_k]]
        else:
            selected_docs = positive_results[: request.top_k]

        results = [
            RetrievedContentItem(
                content_id=doc.id,
                topic_id=doc.topic_id,
                topic_title=doc.topic.title,
                chapter_title=doc.topic.chapter.title if doc.topic and doc.topic.chapter else None,
                subject_name=doc.topic.chapter.subject.name if (doc.topic and doc.topic.chapter and doc.topic.chapter.subject) else None,
                content_type=doc.content_type.value if hasattr(doc.content_type, "value") else str(doc.content_type),
                source_document=doc.source_document,
                source_page=doc.source_page,
                source_reference=doc.source_reference,
                content_text=doc.content_text,
                score=score,
            )
            for score, doc in selected_docs
        ]

        return RetrievalSearchResponse(
            query=query_text,
            topic_id=target_topic.id if target_topic else None,
            topic_title=target_topic.title if target_topic else None,
            total_results=len(results),
            results=results,
        )
