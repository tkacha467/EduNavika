import json
import pytest
from backend.app.ingestion.math.base import MathExtractor
from backend.app.ingestion.math.evaluator import MathEvaluator


class SampleExtractor(MathExtractor):
    @property
    def name(self) -> str:
        return "SampleExtractor"

    def load_model(self) -> None:
        self.loaded = True

    def extract_page(self, pdf_path: str, page_num: int):
        return {
            "text": "E = mc^2",
            "execution_time_seconds": 0.01,
            "success": True,
            "error": None
        }


@pytest.fixture
def temp_gt_file(tmp_path):
    gt_data = [
        {
            "document": "STD-10/Math.pdf",
            "page": 10,
            "chapter": "Polynomials",
            "split": "dev",
            "items": [
                {
                    "id": "eq_quad",
                    "type": "formula",
                    "category": "ALGEBRA",
                    "latex": "ax^2 + bx + c = 0",
                    "expected_symbols": ["^", "+", "="],
                    "has_fraction": False,
                    "has_subscript": False,
                    "has_superscript": True
                },
                {
                    "id": "eq_frac",
                    "type": "formula",
                    "category": "ALGEBRA",
                    "latex": "\\frac{a}{b}",
                    "expected_symbols": ["\\frac"],
                    "has_fraction": True,
                    "has_subscript": False,
                    "has_superscript": False
                }
            ]
        },
        {
            "document": "STD-10/Science.pdf",
            "page": 10,
            "chapter": "Chemical Reactions",
            "split": "test",
            "items": [
                {
                    "id": "chem_1",
                    "type": "formula",
                    "category": "CHEMICAL",
                    "latex": "2H_2 + O_2 \\rightarrow 2H_2O",
                    "expected_symbols": ["_", "\\rightarrow"],
                    "has_fraction": False,
                    "has_subscript": True,
                    "has_superscript": False
                }
            ]
        }
    ]
    gt_file = tmp_path / "test_gt.json"
    gt_file.write_text(json.dumps(gt_data), encoding="utf-8")
    return str(gt_file)


def test_math_extractor_interface():
    extractor = SampleExtractor()
    assert extractor.name == "SampleExtractor"
    extractor.load_model()
    assert extractor.loaded is True
    res = extractor.extract_page("fake_path.pdf", 1)
    assert res["success"] is True
    assert res["text"] == "E = mc^2"


def test_evaluator_exact_match(temp_gt_file):
    evaluator = MathEvaluator(temp_gt_file)
    gt_item = {
        "id": "eq_test",
        "category": "ALGEBRA",
        "latex": "y = mx + c",
        "expected_symbols": ["="],
        "has_fraction": False,
        "has_subscript": False,
        "has_superscript": False
    }

    result = evaluator.evaluate_formula("  Y = mx + C  ", gt_item)
    assert result["exact_match"] == "PASS"
    assert result["semantic_accuracy"] == "HIGH"
    assert result["symbol_accuracy"] == "HIGH"
    assert result["structural_accuracy"] == "HIGH"
    assert result["category"] == "ALGEBRA"
    assert result["track"] == "CORE"


def test_evaluator_semantic_equivalence(temp_gt_file):
    evaluator = MathEvaluator(temp_gt_file)
    gt_item = {
        "id": "eq_pyth",
        "category": "ALGEBRA",
        "latex": "x^2 + y^2 = r^2",
        "expected_symbols": ["^", "+", "="],
        "has_superscript": True
    }

    # Unicode powers vs standard LaTeX markup
    result = evaluator.evaluate_formula("x² + y² = r²", gt_item)
    assert result["exact_match"] == "FAIL"  # Differs in string encoding
    assert result["semantic_accuracy"] == "HIGH"  # Mathematically equivalent
    assert result["structural_accuracy"] == "HIGH"


def test_evaluator_partial_match_review(temp_gt_file):
    evaluator = MathEvaluator(temp_gt_file)
    gt_item = {
        "id": "eq_quad",
        "category": "ALGEBRA",
        "latex": "ax^2 + bx + c = 0",
        "expected_symbols": ["^", "+", "="],
        "has_fraction": False,
        "has_subscript": False,
        "has_superscript": True
    }

    extracted = "Quadratic is ax^2 + bx + c = 0 where a is non-zero"
    result = evaluator.evaluate_formula(extracted, gt_item)
    assert result["exact_match"] == "FAIL"
    assert result["symbol_accuracy"] == "HIGH"
    assert result["subscript_superscript"] == "MEDIUM"
    assert result["semantic_accuracy"] == "REVIEW"


def test_evaluator_fraction_and_radical_handling(temp_gt_file):
    evaluator = MathEvaluator(temp_gt_file)
    gt_item = {
        "id": "eq_rad_frac",
        "category": "ALGEBRA",
        "latex": "\\frac{1}{\\sqrt{2}}",
        "expected_symbols": ["\\frac", "\\sqrt"],
        "has_fraction": True
    }

    # Extracted with slash and radical
    res_slash = evaluator.evaluate_formula("value is 1/√2", gt_item)
    assert res_slash["fraction_accuracy"] == "MEDIUM"
    assert res_slash["radical_accuracy"] == "MEDIUM"
    assert res_slash["structural_accuracy"] == "MEDIUM"

    # Extracted without radical
    res_norad = evaluator.evaluate_formula("value is 1/2", gt_item)
    assert res_norad["radical_accuracy"] == "FAIL"
    assert res_norad["structural_accuracy"] == "FAIL"


def test_evaluator_page_evaluation_and_document_disambiguation(temp_gt_file):
    evaluator = MathEvaluator(temp_gt_file)

    math_res = evaluator.evaluate_page(10, "ax^2 + bx + c = 0 and \\frac{a}{b}", document="STD-10/Math.pdf")
    assert "eq_quad" in math_res
    assert "eq_frac" in math_res
    assert "chem_1" not in math_res

    sci_res = evaluator.evaluate_page(10, "2H_2 + O_2 -> 2H_2O", document="STD-10/Science.pdf")
    assert "chem_1" in sci_res
    assert "eq_quad" not in sci_res
    assert sci_res["chem_1"]["track"] == "DIAGNOSTIC"


def test_test_manifest_verification():
    # Verify the real test manifest generated by build_stratified_math_gt.py
    is_valid = MathEvaluator.verify_test_manifest(
        manifest_path="data/processed/reports/test_manifest.json",
        test_path="data/processed/reports/math_ground_truth_test.json"
    )
    assert is_valid is True


def test_aggregate_metrics_reporting():
    evals = [
        {
            "id": "1", "category": "ALGEBRA", "track": "CORE",
            "exact_match": "PASS", "semantic_accuracy": "HIGH",
            "structural_accuracy": "HIGH", "symbol_accuracy": "HIGH"
        },
        {
            "id": "2", "category": "GEOMETRY", "track": "CORE",
            "exact_match": "FAIL", "semantic_accuracy": "REVIEW",
            "structural_accuracy": "MEDIUM", "symbol_accuracy": "HIGH"
        },
        {
            "id": "3", "category": "CHEMICAL", "track": "DIAGNOSTIC",
            "exact_match": "FAIL", "semantic_accuracy": "FAIL",
            "structural_accuracy": "FAIL", "symbol_accuracy": "FAIL"
        }
    ]

    report = MathEvaluator.aggregate_metrics(evals)
    assert "CORE" in report
    assert "DIAGNOSTIC" in report
    assert "OVERALL" in report

    assert report["CORE"]["count"] == 2
    assert report["CORE"]["exact_match"] == "1/2 (50.00%)"
    assert report["CORE"]["structural_accuracy"] == "2/2 (100.00%)"

    assert report["DIAGNOSTIC"]["count"] == 1
    assert report["DIAGNOSTIC"]["exact_match"] == "0/1 (0.00%)"

    assert report["OVERALL"]["count"] == 3
    assert report["OVERALL"]["exact_match"] == "1/3 (33.33%)"
