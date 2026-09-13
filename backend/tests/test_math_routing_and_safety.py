import pytest
from typing import Dict, Any

from backend.app.ingestion.math.base import MathExtractor
from backend.app.ingestion.math.detector import (
    MathPageDetector,
    MathPageClassification,
    MathDetectionResult,
)
from backend.app.ingestion.math.quality_gate import (
    MathQualityGate,
    MathValidationResult,
)
from backend.app.ingestion.math.router import (
    MathExtractionRouter,
    RoutedPageExtraction,
)
from backend.app.rag.context_builder import ContextBuilder
from backend.app.retrieval.service import RetrievalResult
from backend.app.ingestion.chunker import StructureAwareChunker
from backend.app.ingestion.schemas import (
    DocumentIdentity,
    CleanedPage,
    PageQualityStatus,
    ChapterCandidate,
    TopicCandidate,
)

# Mock Extractors
class MockStandardExtractor(MathExtractor):
    @property
    def name(self) -> str:
        return "MockStandardExtractor"

    def load_model(self) -> None:
        pass

    def extract_page(self, pdf_path: str, page_num: int) -> Dict[str, Any]:
        if page_num == 1:
            # Normal prose
            return {"text": "A Baker from Goa is a traditional portrait of village life.", "success": True}
        elif page_num == 2:
            # Math present
            return {"text": "Ohm's law states that V = IR where V is voltage.", "success": True}
        elif page_num == 3:
            # Math heavy, corrupted under standard extraction
            return {
                "text": "CH COOH CH CH OH CH C C CH CH H O3 3 2 3 2 3 2 Acid − + − − − − − + 11 (Ester)",
                "success": True
            }
        return {"text": "", "success": True}

class MockSpecializedExtractor(MathExtractor):
    @property
    def name(self) -> str:
        return "MockSpecializedExtractor"

    def load_model(self) -> None:
        pass

    def extract_page(self, pdf_path: str, page_num: int) -> Dict[str, Any]:
        # Specialized extractor returns clean LaTeX equations
        if page_num == 3:
            return {
                "text": "CH_3COOH + CH_3CH_2OH \\xrightarrow{Acid} CH_3COOCH_2CH_3 + H_2O",
                "success": True
            }
        return {
            "text": "\\int_0^1 x^2 dx = \\frac{1}{3} \\quad \\sum_{i=1}^n i = \\frac{n(n+1)}{2}",
            "success": True
        }


# Tests for Phase 3: Mathematical Page Detection
def test_math_detector_normal_page():
    detector = MathPageDetector()
    text = (
        "The bakers had a peculiar dress earlier known as the kabai. "
        "It was a single-piece long frock reaching down to the knees."
    )
    res = detector.detect(text)
    assert res.is_math is False
    assert res.classification == MathPageClassification.NORMAL
    assert res.score < 0.20
    assert len(res.signals) == 0

def test_math_detector_math_present_page():
    detector = MathPageDetector()
    text = (
        "In this electric circuit, we measure the potential difference V. "
        "By Ohm's law, V = IR. The resistance R is measured in ohms."
    )
    res = detector.detect(text)
    assert res.is_math is True
    assert res.classification in [MathPageClassification.MATH_PRESENT, MathPageClassification.MATH_HEAVY]
    assert res.score >= 0.20
    assert any("equation" in s or "operator" in s for s in res.signals)

def test_math_detector_math_heavy_page():
    detector = MathPageDetector()
    text = (
        "Calculate the sum of terms: S_n = \\frac{n}{2} [2a + (n-1)d]. "
        "Also verify that \\sqrt{(x_2-x_1)^2 + (y_2-y_1)^2} = d. "
        "For angles \\alpha, \\beta, \\theta, we have \\sin^2 \\theta + \\cos^2 \\theta = 1."
    )
    res = detector.detect(text)
    assert res.is_math is True
    assert res.classification == MathPageClassification.MATH_HEAVY
    assert res.score >= 0.55
    assert len(res.signals) >= 2


# Tests for Phase 4: Routing Policy
def test_router_normal_page_routing():
    router = MathExtractionRouter(
        standard_extractor=MockStandardExtractor(),
        specialized_extractor=MockSpecializedExtractor()
    )
    result = router.route_and_extract("dummy.pdf", 1)
    assert result.extraction_method == "MockStandardExtractor"
    assert result.detection_result.classification == MathPageClassification.NORMAL
    assert result.validation_result.status == "SAFE"
    assert result.fallback_triggered is False

def test_router_math_heavy_page_routing():
    router = MathExtractionRouter(
        standard_extractor=MockStandardExtractor(),
        specialized_extractor=MockSpecializedExtractor()
    )
    # Page 3 under standard is corrupted math-heavy; router switches or falls back to specialized
    result = router.route_and_extract("dummy.pdf", 3)
    assert result.extraction_method == "MockSpecializedExtractor"
    assert result.validation_result.status == "SAFE"
    assert "CH_3COOH" in result.text


# Tests for Phase 5: MathQualityGate States
def test_quality_gate_safe_review_corrupted_states():
    gate = MathQualityGate()

    # SAFE
    safe_res = gate.validate_chunk("The velocity is v = d / t where d is distance and t is time.")
    assert safe_res.status == "SAFE"
    assert safe_res.is_safe is True

    # NEEDS_REVIEW (minor bracket imbalance)
    review_res = gate.validate_chunk("Note the open set (x, y with positive slope.")
    assert review_res.status in ["SAFE", "NEEDS_REVIEW"]

    # CORRUPTED (disordered bond chain + detached digits)
    corrupt_res = gate.validate_chunk("CH COOH CH CH OH CH C C CH CH H O3 3 2 3 2 3 2 − + − − − − − + 11")
    assert corrupt_res.status == "CORRUPTED"
    assert corrupt_res.is_safe is False
    assert len(corrupt_res.detected_issues) > 0


# Tests for Phase 6 & Phase 7: Metadata Preservation and RAG Safety Firewall
def test_corrupted_chunk_blocked_by_context_builder():
    builder = ContextBuilder(max_tokens=1000, filter_corrupted_math=True)

    # 1. Clean prose chunk
    r1 = RetrievalResult(
        chunk_id="chk_clean_prose",
        score=0.95,
        rank=1,
        content="Photosynthesis is the process by which green plants make food.",
        retrieval_method="hybrid"
    )

    # 2. Corrupted mathematical chunk (e.g. jumbled formulas)
    r2 = RetrievalResult(
        chunk_id="chk_corrupt_math",
        score=0.90,
        rank=2,
        content="CH COOH CH CH OH CH C C CH CH H O3 3 2 3 2 3 2 Acid − + − − − − − + 11",
        retrieval_method="hybrid"
    )

    # 3. Clean math chunk
    r3 = RetrievalResult(
        chunk_id="chk_clean_math",
        score=0.85,
        rank=3,
        content="The quadratic formula is x = (-b +- sqrt(b^2 - 4ac)) / (2a).",
        retrieval_method="hybrid"
    )

    context_str, included_ids = builder.build_context([r1, r2, r3])

    # Assertions
    assert "chk_clean_prose" in included_ids
    assert "chk_clean_math" in included_ids
    assert "chk_corrupt_math" not in included_ids  # BLOCKED!
    assert "chk_corrupt_math" in builder.blocked_chunks
    assert "O3 3 2 3 2" not in context_str

def test_metadata_preservation_in_chunker():
    chunker = StructureAwareChunker()
    doc_id = DocumentIdentity(
        document_id="doc_test123",
        relative_path="STD-10th/test.pdf",
        filename="test.pdf",
        file_hash="abc123hash",
        file_size_bytes=1024,
        standard=10,
        subject="Mathematics"
    )
    pages = [
        CleanedPage(
            document_id="doc_test123",
            pdf_page_number=1,
            cleaned_text="The theorem states that a^2 + b^2 = c^2 for right triangles.\n\nSection 1.1 Complete.",
            quality_status=PageQualityStatus.EXTRACTED
        )
    ]
    chapters = [
        ChapterCandidate(
            chapter_number=1,
            chapter_title="Triangles",
            start_pdf_page=1,
            end_pdf_page=1,
            topics=[
                TopicCandidate(
                    topic_order=1,
                    topic_title="Pythagoras Theorem",
                    start_pdf_page=1,
                    end_pdf_page=1
                )
            ]
        )
    ]

    chunks = chunker.chunk_document(doc_id, pages, chapters)
    assert len(chunks) >= 1
    chunk = chunks[0]

    # Verify math metadata is present and populated
    assert "math_detected" in chunk.metadata
    assert "math_validity_status" in chunk.metadata
    assert chunk.metadata["math_detected"] is True
    assert chunk.metadata["math_validity_status"] == "SAFE"

def test_deterministic_routing_reproducibility():
    detector = MathPageDetector()
    sample_text = "The roots of ax^2 + bx + c = 0 are given by x = \\frac{-b \\pm \\sqrt{b^2 - 4ac}}{2a}."

    results = [detector.detect(sample_text) for _ in range(10)]
    first = results[0]
    for r in results[1:]:
        assert r.is_math == first.is_math
        assert r.classification == first.classification
        assert r.score == first.score
        assert r.signals == first.signals
        assert r.feature_counts == first.feature_counts
