from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from backend.app.retrieval.hybrid import HybridRetriever

class RetrievalResult(BaseModel):
    chunk_id: str
    score: float
    rank: int
    content: str
    standard: Optional[int] = None
    subject: Optional[str] = None
    chapter: Optional[str] = None
    topic: Optional[str] = None
    source_document: Optional[str] = None
    source_page: Optional[int] = None
    source_reference: Optional[str] = None
    retrieval_method: str

class RetrievalService:
    def __init__(self, retriever: Any):
        """
        Initialize with a retriever (e.g., HybridRetriever).
        """
        self.retriever = retriever

    def retrieve(self, query: str, filters: Optional[Dict[str, Any]] = None, top_k: int = 5) -> List[RetrievalResult]:
        """
        Retrieve relevant chunks based on a query and optional filters.
        """
        raw_results = self.retriever.search(query, top_k=top_k, filters=filters)
        
        results = []
        for rank, res in enumerate(raw_results, start=1):
            meta = res.get("metadata", {})
            
            result = RetrievalResult(
                chunk_id=res["chunk_id"],
                score=res["score"],
                rank=rank,
                content=meta.get("content", ""),
                standard=meta.get("standard"),
                subject=meta.get("subject"),
                chapter=meta.get("chapter"),
                topic=meta.get("topic"),
                source_document=meta.get("source_document"),
                source_page=meta.get("source_page"),
                source_reference=meta.get("source_reference"),
                retrieval_method=res.get("retrieval_method", "hybrid")
            )
            results.append(result)
            
        return results
