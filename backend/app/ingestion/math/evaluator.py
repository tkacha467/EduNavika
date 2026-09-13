import json
import re
import os
import hashlib
from typing import Dict, Any, List, Optional


class MathEvaluator:
    CORE_CATEGORIES = {"ALGEBRA", "GEOMETRY", "TRIGONOMETRY", "PHYSICS"}
    DIAGNOSTIC_CATEGORIES = {"CHEMICAL", "NUMERIC_EXPRESSION"}

    def __init__(self, ground_truth_path: str):
        self.ground_truth_path = ground_truth_path
        with open(ground_truth_path, 'r', encoding='utf-8') as f:
            self.gt_data = json.load(f)

    @staticmethod
    def verify_test_manifest(
        manifest_path: str = "data/processed/reports/test_manifest.json",
        test_path: str = "data/processed/reports/math_ground_truth_test.json"
    ) -> bool:
        """
        Cryptographically verifies that the held-out test ground truth matches
        the frozen SHA-256 manifest before evaluation.
        """
        if not os.path.exists(manifest_path) or not os.path.exists(test_path):
            return False
        with open(manifest_path, "r", encoding="utf-8") as f:
            manifest = json.load(f)
        with open(test_path, "rb") as f:
            computed_hash = hashlib.sha256(f.read()).hexdigest()
        return computed_hash == manifest.get("sha256")

    def _normalize(self, text: str) -> str:
        """Basic normalization: strip whitespace and lowercase."""
        if not text:
            return ""
        return re.sub(r'\s+', '', text).lower()

    def _canonicalize_semantic(self, text: str) -> str:
        """
        Level 3 semantic mathematical equivalence canonicalization:
        Normalizes Unicode superscripts/subscripts, operators, and formatting
        to test mathematical equivalence rather than strict string equality.
        """
        if not text:
            return ""
        s = text.lower()
        # Superscripts
        s = s.replace("²", "^2").replace("³", "^3").replace("⁴", "^4")
        s = s.replace("^{2}", "^2").replace("^{3}", "^3").replace("^{4}", "^4")
        # Subscripts
        s = s.replace("₁", "_1").replace("₂", "_2").replace("₃", "_3")
        s = s.replace("_{1}", "_1").replace("_{2}", "_2").replace("_{3}", "_3")
        # Multiplication & operators
        s = s.replace("\\times", "*").replace("\\cdot", "*")
        s = s.replace("\\le", "<=").replace("\\ge", ">=").replace("\\ne", "!=")
        s = s.replace("\\rightarrow", "->").replace("\\xrightarrow{\\delta}", "->")
        s = s.replace("\\pm", "+/-")
        # Whitespace and formatting tags
        s = re.sub(r'\\text\{([^}]+)\}', r'\1', s)
        s = re.sub(r'\\quad', '', s)
        s = re.sub(r'\s+', '', s)
        return s

    def evaluate_formula(self, extracted: str, gt_item: Dict[str, Any]) -> Dict[str, Any]:
        """
        Three-Tier Evaluation Framework:
          Level 1: Canonical Exact Match (strict string equality after basic normalization)
          Level 2: Structural Accuracy (operators, fractions, radicals, powers, subscripts)
          Level 3: Semantic Mathematical Equivalence (canonicalized equivalence)
        """
        gt_latex = gt_item.get("latex", "")
        norm_ext = self._normalize(extracted)
        norm_gt = self._normalize(gt_latex)
        category = gt_item.get("category", "UNKNOWN")

        metrics = {
            "category": category,
            "track": "CORE" if category in self.CORE_CATEGORIES else "DIAGNOSTIC",
            "exact_match": "FAIL",
            "structural_accuracy": "FAIL",
            "semantic_accuracy": "FAIL",
            "symbol_accuracy": "FAIL",
            "fraction_accuracy": "N/A",
            "subscript_superscript": "N/A",
            "radical_accuracy": "N/A"
        }

        # Level 1: Canonical Exact Match
        if norm_ext == norm_gt:
            metrics["exact_match"] = "PASS"
            metrics["structural_accuracy"] = "HIGH"
            metrics["semantic_accuracy"] = "HIGH"
            metrics["symbol_accuracy"] = "HIGH"
            if gt_item.get("has_subscript") or gt_item.get("has_superscript"):
                metrics["subscript_superscript"] = "HIGH"
            if gt_item.get("has_fraction"):
                metrics["fraction_accuracy"] = "HIGH"
            if "\\sqrt" in gt_latex:
                metrics["radical_accuracy"] = "HIGH"
            return metrics

        if not extracted or len(extracted) < 3:
            return metrics

        # Level 3: Semantic Mathematical Equivalence
        sem_ext = self._canonicalize_semantic(extracted)
        sem_gt = self._canonicalize_semantic(gt_latex)
        if sem_ext and sem_ext == sem_gt:
            metrics["semantic_accuracy"] = "HIGH"
            metrics["structural_accuracy"] = "HIGH"
            metrics["symbol_accuracy"] = "HIGH"
            if gt_item.get("has_subscript") or gt_item.get("has_superscript"):
                metrics["subscript_superscript"] = "HIGH"
            if gt_item.get("has_fraction"):
                metrics["fraction_accuracy"] = "HIGH"
            if "\\sqrt" in gt_latex:
                metrics["radical_accuracy"] = "HIGH"
            return metrics

        # Level 2: Structural Elements Checks
        # Symbol accuracy
        expected_symbols = gt_item.get("expected_symbols", [])
        if expected_symbols:
            symbols_found = sum(
                1 for sym in expected_symbols
                if sym in extracted or sym.replace("\\", "") in extracted or sym.replace("{", "").replace("}", "") in extracted
            )
            if symbols_found == len(expected_symbols):
                metrics["symbol_accuracy"] = "HIGH"
            elif symbols_found > 0:
                metrics["symbol_accuracy"] = "MEDIUM"

        # Subscript & Superscript
        if gt_item.get("has_superscript") or gt_item.get("has_subscript"):
            if "^" in extracted or "_" in extracted or any(c in extracted for c in ['²', '³', '⁴', '₁', '₂', '₃']):
                metrics["subscript_superscript"] = "MEDIUM"
            else:
                metrics["subscript_superscript"] = "FAIL"

        # Fraction
        if gt_item.get("has_fraction"):
            if "\\frac" in extracted or "/" in extracted:
                metrics["fraction_accuracy"] = "MEDIUM"
            else:
                metrics["fraction_accuracy"] = "FAIL"

        # Radical
        if "\\sqrt" in gt_latex:
            if "\\sqrt" in extracted or "√" in extracted:
                metrics["radical_accuracy"] = "MEDIUM"
            else:
                metrics["radical_accuracy"] = "FAIL"

        # Aggregate Structural Accuracy
        struct_flags = [
            metrics.get("fraction_accuracy"),
            metrics.get("subscript_superscript"),
            metrics.get("radical_accuracy")
        ]
        active_flags = [f for f in struct_flags if f != "N/A"]
        if active_flags:
            if all(f in ["HIGH", "MEDIUM"] for f in active_flags):
                metrics["structural_accuracy"] = "MEDIUM"
            else:
                metrics["structural_accuracy"] = "FAIL"
        else:
            # If no special structural flags, relies on symbol accuracy
            metrics["structural_accuracy"] = metrics["symbol_accuracy"]

        # Aggregate Semantic Accuracy
        if metrics["symbol_accuracy"] in ["HIGH", "MEDIUM"] and metrics["structural_accuracy"] != "FAIL":
            metrics["semantic_accuracy"] = "REVIEW"

        return metrics

    def evaluate_page(self, page_num: int, extracted_text: str, document: Optional[str] = None) -> Dict[str, Any]:
        """
        Evaluate a single page's extraction against its Ground Truth.
        Uses unique key (document, page) for disambiguation across textbooks.
        """
        if document:
            norm_doc = document.replace("\\", "/").strip()
            gt_page = next((item for item in self.gt_data if item["page"] == page_num and item.get("document", "").replace("\\", "/").strip() == norm_doc), None)
        else:
            gt_page = next((item for item in self.gt_data if item["page"] == page_num), None)

        if not gt_page:
            return {"error": f"No ground truth for page {page_num}" + (f" in {document}" if document else "")}

        results = {}
        for item in gt_page.get("items", []):
            if item.get("type") == "formula":
                results[item["id"]] = self.evaluate_formula(extracted_text, item)

        return results

    @classmethod
    def aggregate_metrics(cls, evaluations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Computes partitioned metrics (CORE, DIAGNOSTIC, OVERALL)
        with both numerator/denominator counts and percentages.
        """
        tracks = {"CORE": [], "DIAGNOSTIC": [], "OVERALL": evaluations}
        for ev in evaluations:
            track = ev.get("track", "CORE")
            if track in tracks:
                tracks[track].append(ev)

        report = {}
        for track_name, items in tracks.items():
            total = len(items)
            if total == 0:
                report[track_name] = {"count": 0}
                continue

            exact_count = sum(1 for it in items if it.get("exact_match") == "PASS")
            semantic_high = sum(1 for it in items if it.get("semantic_accuracy") == "HIGH")
            semantic_valid = sum(1 for it in items if it.get("semantic_accuracy") in ("HIGH", "REVIEW"))
            struct_valid = sum(1 for it in items if it.get("structural_accuracy") in ("HIGH", "MEDIUM"))
            symbol_valid = sum(1 for it in items if it.get("symbol_accuracy") in ("HIGH", "MEDIUM"))

            report[track_name] = {
                "count": total,
                "exact_match": f"{exact_count}/{total} ({100.0 * exact_count / total:.2f}%)",
                "semantic_high": f"{semantic_high}/{total} ({100.0 * semantic_high / total:.2f}%)",
                "semantic_valid": f"{semantic_valid}/{total} ({100.0 * semantic_valid / total:.2f}%)",
                "structural_accuracy": f"{struct_valid}/{total} ({100.0 * struct_valid / total:.2f}%)",
                "symbol_accuracy": f"{symbol_valid}/{total} ({100.0 * symbol_valid / total:.2f}%)"
            }

        return report
