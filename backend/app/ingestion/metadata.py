from pathlib import Path
from typing import Dict, Any, Optional
import pypdf
from backend.app.ingestion.schemas import DocumentIdentity


class MetadataExtractor:
    """
    Extracts embedded PDF metadata (title, author, creation date, page count)
    supplementary to the authoritative curriculum manifest.
    """

    @staticmethod
    def extract_pdf_metadata(file_path: Path, doc_identity: DocumentIdentity) -> Dict[str, Any]:
        result = {
            "document_id": doc_identity.document_id,
            "filename": doc_identity.filename,
            "file_size_bytes": doc_identity.file_size_bytes,
            "file_hash": doc_identity.file_hash,
            "standard": doc_identity.standard,
            "subject": doc_identity.subject,
            "category": doc_identity.category,
            "curriculum_relevance": doc_identity.curriculum_relevance,
            "ocr_requirement": doc_identity.ocr_requirement,
            "pdf_embedded_title": None,
            "pdf_author": None,
            "pdf_creator": None,
            "pdf_producer": None,
            "pdf_creation_date": None,
            "page_count": doc_identity.page_count,
        }

        try:
            reader = pypdf.PdfReader(str(file_path))
            result["page_count"] = len(reader.pages)

            if reader.metadata:
                m = reader.metadata
                result["pdf_embedded_title"] = str(m.title) if m.title else None
                result["pdf_author"] = str(m.author) if m.author else None
                result["pdf_creator"] = str(m.creator) if m.creator else None
                result["pdf_producer"] = str(m.producer) if m.producer else None
                result["pdf_creation_date"] = str(m.creation_date) if m.creation_date else None
        except Exception as e:
            result["metadata_extraction_warning"] = str(e)

        return result
