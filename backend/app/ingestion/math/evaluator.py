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

    def _normalize_predeclared(self, text: str) -> str:
        """
        Level 1 pre-declared canonical LaTeX normalization for Exact Match.
        Standardizes spacing tags and pre-declared ASCII/LaTeX operator equivalents.
        """
        if not text:
            return ""
        s = text.lower()
        s = re.sub(r'\\text\{([^}]+)\}', r'\1', s)
        s = re.sub(r'\\(?:quad|qquad|;|:|,|!)', '', s)
        s = s.replace("\\times", "*").replace("\\cdot", "*")
        s = s.replace("\\le", "<=").replace("\\ge", ">=").replace("\\ne", "!=")
        s = s.replace("\\rightarrow", "->").replace("\\xrightarrow{\\delta}", "->")
        s = s.replace("−", "-").replace("–", "-")
        s = re.sub(r'\s+', '', s)
        return s

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
        s = re.sub(r'\\(?:quad|qquad|;|:|,|!)', '', s)
        s = re.sub(r'\s+', '', s)
        return s

    def evaluate_formula(
        self,
        extracted: Any,
        gt_item: Dict[str, Any],
        localization_status: str = "UNLOCALIZED",
        bbox: Optional[List[float]] = None
    ) -> Dict[str, Any]:
        """
        Three-Tier Evaluation Framework:
          Level 1: Canonical Exact Match (pre-declared normalization rules)
          Level 2: Structural Accuracy (operators, fractions, radicals, powers, subscripts)
          Level 3: Semantic Mathematical Equivalence (canonicalized equivalence)

        Maintains strict separation between:
          - raw_extracted: raw extraction output
          - normalized_extracted: normalization output
          - localization_status: LOCALIZED (with spatial bbox) vs UNLOCALIZED
          - evaluation metrics: exact match, structural, semantic, and symbol
        """
        if isinstance(extracted, dict):
            raw_text = extracted.get("raw_ocr") or extracted.get("raw_text") or extracted.get("text", "")
            norm_text = extracted.get("canonical_latex") or extracted.get("normalized_text") or extracted.get("text", "")
            bbox = extracted.get("bbox", bbox)
            loc_status = extracted.get("localization_status", "LOCALIZED" if bbox else localization_status)
        else:
            raw_text = str(extracted or "")
            norm_text = str(extracted or "")
            loc_status = "LOCALIZED" if bbox else localization_status

        gt_latex = gt_item.get("latex", "")
        category = gt_item.get("category", "UNKNOWN")

        metrics = {
            "category": category,
            "track": "CORE" if category in self.CORE_CATEGORIES else "DIAGNOSTIC",
            "localization_status": loc_status,
            "bbox": bbox,
            "raw_extracted": raw_text,
            "normalized_extracted": norm_text,
            "exact_match": "FAIL",
            "structural_accuracy": "FAIL",
            "semantic_accuracy": "FAIL",
            "symbol_accuracy": "FAIL",
            "fraction_accuracy": "N/A",
            "subscript_superscript": "N/A",
            "radical_accuracy": "N/A"
        }

        if not norm_text or len(norm_text.strip()) == 0:
            return metrics

        # Level 1: Canonical Exact Match under pre-declared normalization rules
        dec_ext = self._normalize_predeclared(norm_text)
        dec_gt = self._normalize_predeclared(gt_latex)
        if dec_ext and dec_ext == dec_gt:
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

        if len(norm_text.strip()) < 2:
            return metrics

        # Level 3: Semantic Mathematical Equivalence
        sem_ext = self._canonicalize_semantic(norm_text)
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

        # Level 2: Structural Elements Checks strictly on localized candidate
        expected_symbols = gt_item.get("expected_symbols", [])
        if expected_symbols:
            symbols_found = sum(
                1 for sym in expected_symbols
                if sym in norm_text or sym in raw_text or sym.replace("\\", "") in norm_text or sym.replace("{", "").replace("}", "") in norm_text
            )
            if symbols_found == len(expected_symbols):
                metrics["symbol_accuracy"] = "HIGH"
            elif symbols_found >= max(1, len(expected_symbols) // 2):
                metrics["symbol_accuracy"] = "MEDIUM"
            elif symbols_found > 0:
                metrics["symbol_accuracy"] = "LOW"

        # Subscript & Superscript
        if gt_item.get("has_superscript") or gt_item.get("has_subscript"):
            if "^" in norm_text or "_" in norm_text or any(c in norm_text for c in ['²', '³', '⁴', '₁', '₂', '₃']):
                metrics["subscript_superscript"] = "MEDIUM"
            else:
                metrics["subscript_superscript"] = "FAIL"

        # Fraction
        if gt_item.get("has_fraction"):
            if "\\frac" in norm_text or "/" in norm_text:
                metrics["fraction_accuracy"] = "MEDIUM"
            else:
                metrics["fraction_accuracy"] = "FAIL"

        # Radical
        if "\\sqrt" in gt_latex:
            if "\\sqrt" in norm_text or "√" in norm_text:
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
            metrics["structural_accuracy"] = metrics["symbol_accuracy"]

        # Aggregate Semantic Accuracy
        if metrics["symbol_accuracy"] in ["HIGH", "MEDIUM"] and metrics["structural_accuracy"] != "FAIL":
            metrics["semantic_accuracy"] = "REVIEW"

        return metrics

    def evaluate_page(self, page_num: int, extracted: Any, document: Optional[str] = None) -> Dict[str, Any]:
        """
        Evaluate a single page's extraction against its Ground Truth.
        Uses unique key (document, page) for disambiguation across textbooks.

        Treats bounding-box localization as primary localization mechanism.
        For baseline text-only extraction without spatial coordinates, explicitly labels
        candidates as UNLOCALIZED and evaluates cohesive statement lines to eliminate
        page-level token leakage across disjoint sections.
        """
        if document:
            norm_doc = document.replace("\\", "/").strip()
            gt_page = next((item for item in self.gt_data if item["page"] == page_num and item.get("document", "").replace("\\", "/").strip() == norm_doc), None)
        else:
            gt_page = next((item for item in self.gt_data if item["page"] == page_num), None)

        if not gt_page:
            return {"error": f"No ground truth for page {page_num}" + (f" in {document}" if document else "")}

        results = {}
        items = [it for it in gt_page.get("items", []) if it.get("type") == "formula"]

        # Parse extraction input
        recovered_formulas = []
        full_text = ""
        is_localized = False

        if isinstance(extracted, dict):
            recovered_formulas = extracted.get("recovered_formulas", [])
            full_text = extracted.get("text", "") or extracted.get("baseline_text", "")
            is_localized = bool(recovered_formulas)
        elif isinstance(extracted, str):
            full_text = extracted
            is_localized = False

        for item in items:
            best_ev = None
            best_score = -1.0

            # 1. Primary localization mechanism: evaluate against individual bounding-box crops
            # Tokens from one crop do not leak into another crop.
            if is_localized and recovered_formulas:
                for rf in recovered_formulas:
                    ev = self.evaluate_formula(
                        extracted=rf,
                        gt_item=item,
                        localization_status="LOCALIZED",
                        bbox=rf.get("bbox")
                    )
                    score = 0.0
                    if ev["exact_match"] == "PASS":
                        score = 100.0
                    elif ev["semantic_accuracy"] == "HIGH":
                        score = 50.0
                    elif ev["structural_accuracy"] in ("HIGH", "MEDIUM"):
                        score = 25.0
                    elif ev["symbol_accuracy"] in ("HIGH", "MEDIUM"):
                        score = 10.0

                    if score > best_score or best_ev is None:
                        best_score = score
                        best_ev = ev

                # If localized bounding box crop captured the formula satisfactorily, use it
                if best_ev and best_score >= 25.0:
                    results[item["id"]] = best_ev
                    continue

            # 2. Baseline text-only extraction without spatial coordinates:
            # Explicitly labeled as UNLOCALIZED (no localized accuracy claimed).
            # To eliminate page-level token leakage, evaluate individual statement lines
            # rather than aggregating tokens across unrelated sections of the page.
            lines = [line.strip() for line in full_text.splitlines() if len(line.strip()) > 1]
            if not lines:
                results[item["id"]] = best_ev if best_ev else self.evaluate_formula("", item, localization_status="UNLOCALIZED")
                continue

            for line in lines:
                ev = self.evaluate_formula(
                    extracted=line,
                    gt_item=item,
                    localization_status="UNLOCALIZED",
                    bbox=None
                )
                score = 0.0
                if ev["exact_match"] == "PASS":
                    score = 100.0
                elif ev["semantic_accuracy"] == "HIGH":
                    score = 50.0
                elif ev["structural_accuracy"] in ("HIGH", "MEDIUM"):
                    score = 25.0
                elif ev["symbol_accuracy"] in ("HIGH", "MEDIUM"):
                    score = 10.0

                if score > best_score or best_ev is None:
                    best_score = score
                    best_ev = ev

            results[item["id"]] = best_ev

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
            localized_count = sum(1 for it in items if it.get("localization_status") == "LOCALIZED")

            report[track_name] = {
                "count": total,
                "exact_match": f"{exact_count}/{total} ({100.0 * exact_count / total:.2f}%)",
                "semantic_high": f"{semantic_high}/{total} ({100.0 * semantic_high / total:.2f}%)",
                "semantic_valid": f"{semantic_valid}/{total} ({100.0 * semantic_valid / total:.2f}%)",
                "structural_accuracy": f"{struct_valid}/{total} ({100.0 * struct_valid / total:.2f}%)",
                "symbol_accuracy": f"{symbol_valid}/{total} ({100.0 * symbol_valid / total:.2f}%)",
                "localized_candidates": f"{localized_count}/{total} ({100.0 * localized_count / total:.2f}%)"
            }

        return report
