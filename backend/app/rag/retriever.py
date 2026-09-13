from typing import List, Dict, Any, Optional
from backend.app.retrieval.service import RetrievalService, RetrievalResult
from backend.app.rag.schemas import MCQGenerationRequest

class RAGRetriever:
    """
    Adapter that bridges the RAG pipeline with the frozen RetrievalService.
    """
    def __init__(self, retrieval_service: RetrievalService):
        self.retrieval_service = retrieval_service

    def fetch_context(self, request: MCQGenerationRequest, top_k: int = 15) -> List[RetrievalResult]:
        """
        Translates a teacher's generation request into curriculum filters
        and retrieves the most relevant chunks.
        """
        # Build strict filters based on teacher's request
        filters = {
            "standard": request.grade,
            "subject": request.subject
        }
        if request.chapter:
            filters["chapter"] = request.chapter
        if request.topic:
            filters["topic"] = request.topic
            
        # We synthesize a search query from the request parameters
        # In a real scenario, this could be more sophisticated or use a generic "overview" query
        query_parts = [f"Grade {request.grade} {request.subject}"]
        if request.chapter:
            query_parts.append(request.chapter)
        if request.topic:
            query_parts.append(request.topic)
            
        search_query = " ".join(query_parts)
        
        # Retrieve chunks
        # We fetch a larger pool (e.g. 15) so the ContextBuilder can down-select within the token budget
        return self.retrieval_service.retrieve(query=search_query, filters=filters, top_k=top_k)
