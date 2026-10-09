from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class RetrievalSearchRequest(BaseModel):
    """
    Request model for local curriculum content retrieval.
    """
    student_id: Optional[str] = Field(None, description="Student requesting curriculum content")
    topic_id: Optional[str] = Field(None, description="Target topic ID or name to constrain retrieval")
    query: str = Field(..., description="Query terms or concept to search for in curriculum content")
    top_k: int = Field(5, ge=1, le=20, description="Maximum number of curriculum chunks to retrieve")


class RetrievedContentItem(BaseModel):
    """
    Individual curriculum chunk with full provenance and source traceability.
    """
    content_id: str
    topic_id: str
    topic_title: str
    chapter_title: Optional[str] = None
    subject_name: Optional[str] = None
    content_type: str
    source_document: Optional[str] = None
    source_page: Optional[int] = None
    source_reference: Optional[str] = None
    content_text: str
    score: float


class RetrievalSearchResponse(BaseModel):
    """
    Response model containing grounded curriculum learning materials.
    """
    query: str
    topic_id: Optional[str] = None
    topic_title: Optional[str] = None
    total_results: int
    results: List[RetrievedContentItem]
