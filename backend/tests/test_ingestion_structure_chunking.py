import pytest
from backend.app.ingestion.structure import StructureParser
from backend.app.ingestion.chunker import StructureAwareChunker
from backend.app.ingestion.schemas import (
    CleanedPage,
    PageQualityStatus,
    DocumentIdentity,
)


def test_structure_parser_and_chunking():
    # Construct mock cleaned pages representing a chapter with 2 topics
    page1 = CleanedPage(
        document_id="doc_test123",
        pdf_page_number=1,
        cleaned_text="CHAPTER 1 Chemical Reactions and Equations\n\n1.1 Writing Chemical Equations\n\nA chemical equation represents a chemical reaction.",
        quality_status=PageQualityStatus.EXTRACTED,
    )
    page2 = CleanedPage(
        document_id="doc_test123",
        pdf_page_number=2,
        cleaned_text="1.2 Types of Chemical Reactions\n\nWe have learnt that during a chemical reaction atoms of one element do not change into those of another element.",
        quality_status=PageQualityStatus.EXTRACTED,
    )

    parser = StructureParser()
    chapters = parser.parse_structure([page1, page2])

    assert len(chapters) == 1
    assert chapters[0].chapter_number == 1
    assert "Chemical Reactions" in chapters[0].chapter_title
    assert len(chapters[0].topics) >= 1

    doc_id = DocumentIdentity(
        document_id="doc_test123",
        relative_path="STD-10th/test.pdf",
        filename="test.pdf",
        file_hash="a" * 64,
        file_size_bytes=1024,
        standard=10,
        subject="Science",
    )

    chunker = StructureAwareChunker()
    chunks = chunker.chunk_document(doc_id, [page1, page2], chapters)

    assert len(chunks) >= 1
    for chunk in chunks:
        assert chunk.chunk_id.startswith("chk_")
        assert chunk.document_id == "doc_test123"
        assert chunk.approx_token_count > 0
        assert chunk.heading_path is not None
        assert "Standard 10 > Science" in chunk.heading_path

    # Verify chunk determinism: running chunker again must yield same chunk_id
    chunks_rerun = chunker.chunk_document(doc_id, [page1, page2], chapters)
    assert [c.chunk_id for c in chunks] == [c.chunk_id for c in chunks_rerun]
