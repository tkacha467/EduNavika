from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.schemas.retrieval import RetrievalSearchRequest, RetrievalSearchResponse
from backend.app.services.curriculum_retrieval import CurriculumRetrievalService

router = APIRouter(prefix="/retrieval", tags=["Curriculum Retrieval"])


@router.post(
    "/search",
    response_model=RetrievalSearchResponse,
    status_code=status.HTTP_200_OK,
    summary="Retrieve grounded curriculum textbook material by query and topic"
)
def search_curriculum(
    payload: RetrievalSearchRequest,
    db: Session = Depends(get_db)
):
    """
    Topic-aware curriculum retrieval service.
    Exposes verified textbook learning materials with page numbers and source document provenance.
    """
    return CurriculumRetrievalService.search(db=db, request=payload)
