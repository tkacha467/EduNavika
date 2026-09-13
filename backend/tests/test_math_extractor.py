import pytest
import os
from pathlib import Path
from backend.app.ingestion.math import (
    MathExtractor,
    MathEvaluator,
    MathQualityGate,
    MathValidationResult,
)

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
GT_PATH = PROJECT_ROOT / "backend" / "app" / "ingestion" / "math" / "ground_truth.json"

class MockMathExtractor(MathExtractor):
    @property
    def name(self) -> str:
        return "MockMathExtractor"

    def load_model(self) -> None:
        self.loaded = True

    def extract_page(self, pdf_path: str, page_num: int):
        return {
            "text": "The distance formula is \\sqrt{(x_2-x_1)^2+(y_2-y_1)^2}.",
            "execution_time_seconds": 0.01,
            "success": True,
            "error": None
        }

def test_math_extractor_contract():
    extractor = MockMathExtractor()
    assert extractor.name == "MockMathExtractor"
    extractor.load_model()
    assert extractor.loaded is True
    res = extractor.extract_page("dummy.pdf", 1)
    assert res["success"] is True
    assert "distance" in res["text"]

def test_math_evaluator_exact_match():
    evaluator = MathEvaluator(str(GT_PATH))
    
    gt_item = {
        "id": "test_eq",
        "type": "formula",
        "latex": "\\sqrt{(x_2-x_1)^2+(y_2-y_1)^2}",
        "expected_symbols": ["\\sqrt", "^", "_", "+", "-"],
        "has_fraction": False,
        "has_subscript": True,
        "has_superscript": True
    }
    
    # Verbatim match inside a paragraph
    page_text = "From Theorem 7.1, we have \\sqrt{(x_2-x_1)^2+(y_2-y_1)^2} as the Euclidean distance."
    metrics = evaluator.evaluate_formula(page_text, gt_item)
    assert metrics["exact_match"] == "PASS"
    assert metrics["semantic_accuracy"] == "HIGH"
    assert metrics["symbol_accuracy"] == "HIGH"
    assert metrics["subscript_superscript"] == "HIGH"

def test_math_evaluator_corrupted_formula():
    evaluator = MathEvaluator(str(GT_PATH))
    
    gt_item = {
        "id": "test_eq_frac",
        "type": "formula",
        "latex": "P = \\frac{1}{f}",
        "expected_symbols": ["\\frac"],
        "has_fraction": True,
        "has_subscript": False,
        "has_superscript": False
    }
    
    # Severely corrupted extraction where fraction became disconnected prose
    corrupted_text = "Power P equals 1 f without division"
    metrics = evaluator.evaluate_formula(corrupted_text, gt_item)
    assert metrics["exact_match"] == "FAIL"
    assert metrics["fraction_accuracy"] == "FAIL"
    assert metrics["semantic_accuracy"] == "FAIL"

def test_math_evaluator_summary_computation():
    benchmark_results = {
        "extractor": "TestEngine",
        "pages": [
            {
                "page": 1,
                "execution_time_seconds": 0.05,
                "evaluation": {
                    "eq_1": {
                        "exact_match": "PASS",
                        "symbol_accuracy": "HIGH",
                        "semantic_accuracy": "HIGH"
                    }
                }
            },
            {
                "page": 2,
                "execution_time_seconds": 0.05,
                "evaluation": {
                    "eq_2": {
                        "exact_match": "FAIL",
                        "symbol_accuracy": "MEDIUM",
                        "semantic_accuracy": "REVIEW"
                    }
                }
            }
        ]
    }
    summary = MathEvaluator.compute_summary(benchmark_results)
    assert summary["total_pages_evaluated"] == 2
    assert summary["total_formulas_evaluated"] == 2
    assert summary["exact_matches"] == 1
    assert summary["exact_match_rate"] == 0.5
    assert summary["semantic_high"] == 1
    assert summary["semantic_review"] == 1
    assert summary["semantic_fail"] == 0

def test_math_quality_gate_clean_and_corrupted():
    gate = MathQualityGate()

    # Clean prose
    clean_prose = "The baker was a friend and companion to the children in the village of Goa."
    res = gate.validate_chunk(clean_prose)
    assert res.is_safe is True
    assert res.has_math is False
    assert res.status == "SAFE"

    # Clean math
    clean_math = "The quadratic formula states that for ax^2 + bx + c = 0, x = (-b +- sqrt(D)) / 2a."
    res = gate.validate_chunk(clean_math)
    assert res.is_safe is True
    assert res.has_math is True
    assert res.status == "SAFE"

    # Corrupted chemical text from standard extraction
    corrupted_chemistry = (
        "CH COOH CH CH OH CH C C CH CH H O3 3 2 3 2 3 2\n"
        "Acid − + − − − − − + 11 (Ethanol) (Ester)"
    )
    res = gate.validate_chunk(corrupted_chemistry)
    assert res.is_safe is False
    assert res.status == "CORRUPTED"
    assert len(res.detected_issues) > 0


def test_specialized_extractor_adapters_contract():
    from backend.app.ingestion.math import (
        PyPDFium2Extractor,
        PyPDFExtractor,
        HeuristicMathExtractor,
        RapidOCRExtractor,
    )

    pdfium = PyPDFium2Extractor()
    assert pdfium.name == "PyPDFium2Extractor"
    pdfium.load_model()
    # Non-existent file should gracefully return success=False and error
    res_err = pdfium.extract_page("non_existent_file.pdf", 1)
    assert res_err["success"] is False
    assert res_err["error"] is not None

    pypdf_ext = PyPDFExtractor()
    assert pypdf_ext.name == "PyPDFExtractor"
    pypdf_ext.load_model()
    res_err2 = pypdf_ext.extract_page("non_existent_file.pdf", 1)
    assert res_err2["success"] is False

    heuristic = HeuristicMathExtractor()
    assert heuristic.name == "HeuristicMathExtractor"
    heuristic.load_model()
    cleaned = heuristic.clean_math_text("x 2 + y 2 = r 2, x1, y1, radical √")
    assert "x^2" in cleaned
    assert "y^2" in cleaned
    assert "x_1" in cleaned
    assert "\\sqrt" in cleaned

    rapid = RapidOCRExtractor()
    assert rapid.name == "RapidOCRExtractor"


def test_math_evaluator_unicode_and_boundary_normalization():
    evaluator = MathEvaluator(str(GT_PATH))

    # Formula with Unicode equivalents (superscript 2, radical, minus sign)
    gt_poly = {
        "id": "test_poly",
        "type": "formula",
        "latex": "x^2 - 3 = (x - \\sqrt{3})(x + \\sqrt{3})",
        "expected_symbols": ["\\sqrt", "^", "=", "-", "+"],
        "has_fraction": False,
        "has_subscript": False,
        "has_superscript": True
    }

    # Extracted with Unicode symbols (e.g. from OCR or clean text)
    unicode_text = "The roots are given by x² − 3 = (x − √3)(x + √3) as shown."
    res = evaluator.evaluate_formula(unicode_text, gt_poly)
    assert res["exact_match"] == "PASS"
    assert res["semantic_accuracy"] == "HIGH"
    assert res["symbol_accuracy"] == "HIGH"

    # Short token boundary check: '-OH' should not match embedded inside 'alcohol'
    gt_short = {
        "id": "test_short",
        "type": "formula",
        "latex": "-OH",
        "expected_symbols": ["-"],
        "has_fraction": False,
        "has_subscript": False,
        "has_superscript": False
    }
    # Text without standalone '-OH'
    text_embedded = "Alcoholic beverages contain ethanol."
    res_short = evaluator.evaluate_formula(text_embedded, gt_short)
    assert res_short["exact_match"] == "FAIL"

    # Text with standalone '-OH'
    text_standalone = "The alcohol functional group is -OH."
    res_standalone = evaluator.evaluate_formula(text_standalone, gt_short)
    assert res_standalone["exact_match"] == "PASS"

