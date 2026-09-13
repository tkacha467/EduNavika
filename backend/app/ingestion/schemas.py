import enum
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, ConfigDict, Field


class PageQualityStatus(str, enum.Enum):
    EXTRACTED = "EXTRACTED"
    LOW_QUALITY = "LOW_QUALITY"
    NEEDS_OCR = "NEEDS_OCR"
    EMPTY = "EMPTY"


class StructureConfidence(str, enum.Enum):
    CONFIDENT = "CONFIDENT"
    LOW_CONFIDENCE = "LOW_CONFIDENCE"
    AMBIGUOUS = "AMBIGUOUS"
    UNRESOLVED = "UNRESOLVED"


class DetectionSource(str, enum.Enum):
    TOC = "TOC"
    HEADING = "HEADING"
    NUMBERING = "NUMBERING"
    LAYOUT = "LAYOUT"
    HEURISTIC = "HEURISTIC"


class DocumentIdentity(BaseModel):
    document_id: str = Field(..., description="Deterministic document ID, e.g. doc_<hash[:12]>")
    relative_path: str
    filename: str
    file_hash: str = Field(..., description="SHA-256 hex digest of source PDF")
    file_size_bytes: int
    standard: int = Field(..., description="Grade number, e.g. 9, 10, 11, 12")
    subject: str = Field(..., description="Normalized subject name from manifest")
    category: str = Field(default="CORE_TEXTBOOK")
    curriculum_relevance: str = Field(default="HIGH")
    ocr_requirement: str = Field(default="NONE")
    page_count: Optional[int] = None
    manifest_matched: bool = True

    model_config = ConfigDict(from_attributes=True)


class ExtractedPage(BaseModel):
    document_id: str
    pdf_page_number: int = Field(..., ge=1, description="Physical 1-indexed PDF page index")
    printed_page_number: Optional[int] = Field(None, description="Actual printed page number if reliably detected, else None")
    raw_text: str
    extraction_method: str = "pypdf"
    character_count: int
    word_count: int
    alphabetic_ratio: float
    whitespace_ratio: float
    quality_status: PageQualityStatus

    model_config = ConfigDict(from_attributes=True)


class CleanedPage(BaseModel):
    document_id: str
    pdf_page_number: int
    printed_page_number: Optional[int] = None
    cleaned_text: str
    quality_status: PageQualityStatus
    removed_header: Optional[str] = None
    removed_footer: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class TopicCandidate(BaseModel):
    topic_order: int = Field(..., ge=1)
    topic_title: str
    start_pdf_page: int
    end_pdf_page: int
    confidence: StructureConfidence = StructureConfidence.CONFIDENT
    detection_method: DetectionSource = DetectionSource.HEADING
    learning_objectives: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class ChapterCandidate(BaseModel):
    chapter_number: int = Field(..., ge=1)
    chapter_title: str
    start_pdf_page: int
    end_pdf_page: int
    confidence: StructureConfidence = StructureConfidence.CONFIDENT
    detection_method: DetectionSource = DetectionSource.HEADING
    source_reference: Optional[str] = None
    topics: List[TopicCandidate] = []

    model_config = ConfigDict(from_attributes=True)


class ContentChunk(BaseModel):
    chunk_id: str = Field(..., description="Deterministic chunk ID, e.g. chk_<hash[:16]>")
    document_id: str
    standard_id: Optional[str] = None
    subject_id: Optional[str] = None
    chapter_id: Optional[str] = None
    topic_id: Optional[str] = None
    pdf_page_start: int
    pdf_page_end: int
    printed_page_start: Optional[int] = None
    printed_page_end: Optional[int] = None
    source_file: str
    content_type: str = "TEXT"
    chunk_index: int
    text: str
    approx_token_count: int = Field(..., description="Approximate token count (~4 chars / token). Not an exact model tokenizer.")
    heading_path: Optional[str] = None
    section_title: Optional[str] = None
    extraction_method: str = "pypdf"
    quality_status: str = "EXTRACTED"
    metadata: Dict[str, Any] = {}

    model_config = ConfigDict(from_attributes=True)


class DocumentDiagnostic(BaseModel):
    document_id: str
    relative_path: str
    filename: str
    total_pages: int = 0
    extracted_pages: int = 0
    ocr_required_pages: int = 0
    low_quality_pages: int = 0
    empty_pages: int = 0
    chapters_detected: int = 0
    topics_detected: int = 0
    ambiguous_topics: int = 0
    chunks_generated: int = 0
    chunks_inserted: int = 0
    status: str = "SUCCESS"  # SUCCESS, FAILED, SKIPPED
    warnings: List[str] = []
    errors: List[str] = []

    model_config = ConfigDict(from_attributes=True)


class IngestionSummaryReport(BaseModel):
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    total_pdfs_discovered: int = 0
    total_pdfs_expected_from_manifest: int = 0
    manifest_mismatches: List[str] = []
    successfully_processed_pdfs: int = 0
    failed_pdfs: int = 0
    skipped_unchanged_pdfs: int = 0
    total_pages: int = 0
    pages_extracted: int = 0
    pages_needing_ocr: int = 0
    low_quality_pages: int = 0
    chapters_detected: int = 0
    topics_detected: int = 0
    ambiguous_topics: int = 0
    chunks_generated: int = 0
    chunks_inserted: int = 0
    duplicate_chunks_skipped: int = 0
    warnings: List[str] = []
    errors: List[str] = []
    processing_duration_seconds: float = 0.0
    document_diagnostics: List[DocumentDiagnostic] = []

    model_config = ConfigDict(from_attributes=True)
