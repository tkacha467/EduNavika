"""
EduNavika Curriculum Ingestion Package (Milestone 2)
Provides reproducible, deterministic, provenance-preserving ingestion
of GSEB textbook PDFs into the normalized curriculum schema.
"""

from backend.app.ingestion.schemas import (
    DocumentIdentity,
    ExtractedPage,
    CleanedPage,
    ChapterCandidate,
    TopicCandidate,
    ContentChunk,
    DocumentDiagnostic,
    IngestionSummaryReport,
    PageQualityStatus,
    StructureConfidence,
    DetectionSource,
)
from backend.app.ingestion.scanner import DocumentScanner
from backend.app.ingestion.metadata import MetadataExtractor
from backend.app.ingestion.pdf_extractor import PDFExtractor
from backend.app.ingestion.quality import PageQualityAnalyzer
from backend.app.ingestion.cleaner import DeterministicCleaner
from backend.app.ingestion.structure import StructureParser
from backend.app.ingestion.chunker import StructureAwareChunker
from backend.app.ingestion.mapper import DatabaseCurriculumMapper
from backend.app.ingestion.validator import IngestionValidator
from backend.app.ingestion.pipeline import IngestionPipeline

__all__ = [
    "DocumentIdentity",
    "ExtractedPage",
    "CleanedPage",
    "ChapterCandidate",
    "TopicCandidate",
    "ContentChunk",
    "DocumentDiagnostic",
    "IngestionSummaryReport",
    "PageQualityStatus",
    "StructureConfidence",
    "DetectionSource",
    "DocumentScanner",
    "MetadataExtractor",
    "PDFExtractor",
    "PageQualityAnalyzer",
    "DeterministicCleaner",
    "StructureParser",
    "StructureAwareChunker",
    "DatabaseCurriculumMapper",
    "IngestionValidator",
    "IngestionPipeline",
]
