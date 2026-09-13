from pathlib import Path
from typing import List, Generator
import pypdf

from backend.app.ingestion.schemas import ExtractedPage, PageQualityStatus
from backend.app.ingestion.quality import PageQualityAnalyzer


class PDFExtractor:
    """
    Page-level deterministic PDF extractor using pypdf.
    Preserves exact physical page numbers (1-indexed), raw text, and extracts
    individual pages without loading the entire document into a single monolith.
    """

    @staticmethod
    def extract_pages(
        pdf_path: Path,
        document_id: str,
        quality_analyzer: PageQualityAnalyzer = None,
    ) -> List[ExtractedPage]:
        """
        Extract all pages from the target PDF document.
        """
        if quality_analyzer is None:
            quality_analyzer = PageQualityAnalyzer()

        pages: List[ExtractedPage] = []
        reader = pypdf.PdfReader(str(pdf_path))

        for idx, page in enumerate(reader.pages):
            pdf_page_number = idx + 1
            raw_text = ""
            try:
                extracted = page.extract_text()
                raw_text = extracted if extracted else ""
            except Exception:
                raw_text = ""

            metrics = quality_analyzer.analyze(raw_text)

            pages.append(
                ExtractedPage(
                    document_id=document_id,
                    pdf_page_number=pdf_page_number,
                    printed_page_number=None,  # Preserved as None unless reliably detected later
                    raw_text=raw_text,
                    extraction_method="pypdf",
                    character_count=metrics["character_count"],
                    word_count=metrics["word_count"],
                    alphabetic_ratio=metrics["alphabetic_ratio"],
                    whitespace_ratio=metrics["whitespace_ratio"],
                    quality_status=metrics["quality_status"],
                )
            )

        return pages

    @staticmethod
    def iter_extract_pages(
        pdf_path: Path,
        document_id: str,
        quality_analyzer: PageQualityAnalyzer = None,
    ) -> Generator[ExtractedPage, None, None]:
        """
        Streaming generator for memory-efficient extraction of large PDFs.
        """
        if quality_analyzer is None:
            quality_analyzer = PageQualityAnalyzer()

        reader = pypdf.PdfReader(str(pdf_path))
        for idx, page in enumerate(reader.pages):
            pdf_page_number = idx + 1
            raw_text = ""
            try:
                extracted = page.extract_text()
                raw_text = extracted if extracted else ""
            except Exception:
                raw_text = ""

            metrics = quality_analyzer.analyze(raw_text)

            yield ExtractedPage(
                document_id=document_id,
                pdf_page_number=pdf_page_number,
                printed_page_number=None,
                raw_text=raw_text,
                extraction_method="pypdf",
                character_count=metrics["character_count"],
                word_count=metrics["word_count"],
                alphabetic_ratio=metrics["alphabetic_ratio"],
                whitespace_ratio=metrics["whitespace_ratio"],
                quality_status=metrics["quality_status"],
            )
