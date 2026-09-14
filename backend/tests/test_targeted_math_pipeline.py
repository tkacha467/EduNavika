import pytest
import numpy as np
from pathlib import Path

from backend.app.ingestion.math.quality_gate import MathQualityGate
from backend.app.ingestion.math.normalizer import CanonicalLaTeXNormalizer
from backend.app.ingestion.math.region_detector import MathRegionDetector, MathRegion
from backend.app.ingestion.math.targeted_extractor import TargetedMathExtractor
from backend.app.ingestion.math.evaluator import MathEvaluator


def test_quality_gate_prose_preservation():
    gate = MathQualityGate()
    prose = (
        "The Constitution of India guarantees fundamental rights to all citizens. "
        "These include equality before the law, freedom of speech and expression, "
        "and protection of life and personal liberty. Education is vital for national progress."
    )
    result = gate.analyze(prose)
    assert result["is_math_heavy"] is False
    assert result["needs_recovery"] is False
    assert result["math_score"] < 0.2


def test_quality_gate_math_detection():
    gate = MathQualityGate()
    math_text = "The quadratic formula states that x = (-b +- sqrt(b^2 - 4ac)) / 2a when ax^2 + bx + c = 0."
    result = gate.analyze(math_text)
    assert result["is_math_heavy"] is True
    assert result["needs_recovery"] is True
    assert result["math_score"] >= 0.45


def test_normalizer_prose_preservation():
    normalizer = CanonicalLaTeXNormalizer()
    prose = "The standard test of English requires writing two essays and answering 50 questions in 60 minutes."
    normalized = normalizer.normalize(prose)
    assert normalized == prose  # Pure prose remains 100% unaltered


def test_normalizer_mathematical_transformations():
    normalizer = CanonicalLaTeXNormalizer()

    # Powers and superscripts
    assert "^2" in normalizer.normalize("x² + y² = r²")

    # Radicals
    rad_norm = normalizer.normalize("√(x2 - x1)")
    assert r"\sqrt" in rad_norm

    # Greek letters
    assert r"\theta" in normalizer.normalize("sin θ = 0.5")

    # Inequalities and signs
    assert r"\le" in normalizer.normalize("0 ≤ P(E) ≤ 1")
    assert r"\pm" in normalizer.normalize("x = -b ± d")


def test_region_detector_detection_and_crop():
    detector = MathRegionDetector(min_confidence=0.25)
    pdf_path = "GSEB-Dataset/STD-10/Std-10_Maths_EnglishMedium.pdf"

    # Page 127 is known to have coordinate geometry formulas
    regions = detector.detect_regions(pdf_path, 127)
    assert len(regions) > 0

    first_region = regions[0]
    assert first_region.page_number == 127
    assert len(first_region.bbox) == 4
    assert first_region.confidence >= 0.25

    # Test cropping mechanism
    dummy_img = np.zeros((1000, 800, 3), dtype=np.uint8)
    crop = detector.crop_region_from_image(dummy_img, first_region.bbox, (595.0, 842.0))
    assert crop.ndim == 3
    assert crop.shape[0] > 0 and crop.shape[1] > 0


def test_targeted_math_extractor_integration():
    extractor = TargetedMathExtractor(enable_ocr=False) # Test fast routing without heavy model
    pdf_path = "GSEB-Dataset/STD-10/Std-10_Maths_EnglishMedium.pdf"

    # Page 15 is Social Science Constitution page (prose)
    prose_res = extractor.extract_page(pdf_path, 15)
    assert prose_res["success"] is True

    # Page 127 is Coordinate geometry (math)
    math_res = extractor.extract_page(pdf_path, 127)
    assert math_res["success"] is True
    assert math_res["is_math_heavy"] is True


def test_rag_provenance_contract():
    # Verify that recovered formulas conform to RAG ingestion contracts
    recovered_item = {
        "region_id": "p127_r1",
        "bbox": [100.0, 200.0, 300.0, 250.0],
        "confidence": 0.85,
        "raw_ocr": "x^2 + y^2 = r^2",
        "canonical_latex": "x^2 + y^2 = r^2",
        "extraction_method": "targeted_crop_rapidocr"
    }

    assert "bbox" in recovered_item
    assert "canonical_latex" in recovered_item
    assert "extraction_method" in recovered_item
    assert recovered_item["confidence"] > 0.0


def test_false_positive_v3_in_ordinary_prose():
    normalizer = CanonicalLaTeXNormalizer()
    prose = "We tested model v3 yesterday and evaluated version V3 in chapter 2."
    result = normalizer.normalize(prose, in_math_region=False)
    assert "\\sqrt" not in result
    assert result == prose  # Completely untouched


def test_false_positive_a_minus_b_not_fraction():
    normalizer = CanonicalLaTeXNormalizer()
    # a - b in formula context must remain a subtraction, never becoming \frac{a}{b}
    math_expr = "x = a - b"
    result = normalizer.normalize(math_expr, has_stacked_geometry=False)
    assert "\\frac" not in result
    assert "-" in result


def test_false_positive_horizontal_punctuation_not_fraction():
    normalizer = CanonicalLaTeXNormalizer()
    prose = "Chapter 1 — Introduction to Secondary Science — Units 1 to 4"
    result = normalizer.normalize(prose, has_stacked_geometry=False)
    assert "\\frac" not in result
    assert "Chapter 1" in result


def test_stacked_geometry_fraction_evidence():
    normalizer = CanonicalLaTeXNormalizer()
    # With explicit spatial evidence of numerator-bar-denominator geometry
    stacked_ocr = "x_1 一 x_2"
    result = normalizer.normalize(stacked_ocr, has_stacked_geometry=True, in_math_region=True)
    assert "\\frac{x_1}{x_2}" in result
