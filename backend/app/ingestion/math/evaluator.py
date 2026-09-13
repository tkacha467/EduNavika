import json
import re
from typing import Dict, Any, List

class MathEvaluator:
    def __init__(self, ground_truth_path: str):
        with open(ground_truth_path, 'r', encoding='utf-8') as f:
            self.gt_data = json.load(f)
            
    def _normalize(self, text: str) -> str:
        if not text:
            return ""
        return re.sub(r'\s+', '', text).lower()

    def evaluate_formula(self, extracted: str, gt_item: Dict[str, Any]) -> Dict[str, str]:
        """
        Grades formula extraction on multiple specific accuracy metrics.
        Returns HIGH, MEDIUM, LOW, or FAIL.
        """
        gt_latex = gt_item["latex"]
        norm_ext = self._normalize(extracted)
        norm_gt = self._normalize(gt_latex)
        
        metrics = {
            "semantic_accuracy": "FAIL",
            "exact_match": "FAIL",
            "symbol_accuracy": "FAIL",
            "structure_accuracy": "FAIL",
            "subscript_superscript": "N/A",
            "fraction_accuracy": "N/A"
        }
        
        # Exact match
        if norm_ext == norm_gt:
            metrics["exact_match"] = "PASS"
            metrics["semantic_accuracy"] = "HIGH"
            metrics["structure_accuracy"] = "HIGH"
            metrics["symbol_accuracy"] = "HIGH"
            if gt_item.get("has_subscript") or gt_item.get("has_superscript"):
                metrics["subscript_superscript"] = "HIGH"
            if gt_item.get("has_fraction"):
                metrics["fraction_accuracy"] = "HIGH"
            return metrics
            
        if not extracted or len(extracted) < 3:
            return metrics
            
        # Symbol accuracy
        expected_symbols = gt_item.get("expected_symbols", [])
        if expected_symbols:
            # Very naive check for presence in the raw extracted string
            symbols_found = sum(1 for sym in expected_symbols if sym in extracted or sym.replace("\\", "") in extracted)
            if symbols_found == len(expected_symbols):
                metrics["symbol_accuracy"] = "HIGH"
            elif symbols_found > 0:
                metrics["symbol_accuracy"] = "MEDIUM"
                
        # Super/Subscript logic
        if gt_item.get("has_superscript") or gt_item.get("has_subscript"):
            # If the extracted text has generic digits but no formatting marks (^, _, or valid latex)
            if "^" in extracted or "_" in extracted or "²" in extracted or "₁" in extracted:
                metrics["subscript_superscript"] = "MEDIUM" # At least formatting was attempted
            else:
                metrics["subscript_superscript"] = "FAIL"
                
        # Fraction logic
        if gt_item.get("has_fraction"):
            if "\\frac" in extracted or "/" in extracted:
                metrics["fraction_accuracy"] = "MEDIUM"
            else:
                metrics["fraction_accuracy"] = "FAIL"
                
        # Semantic Accuracy heuristic
        # If it failed exact match, but has symbols and structural hints, it's REVIEW
        if metrics["symbol_accuracy"] in ["HIGH", "MEDIUM"] and metrics.get("subscript_superscript") != "FAIL":
            metrics["semantic_accuracy"] = "REVIEW"
            metrics["structure_accuracy"] = "REVIEW"
            
        return metrics

    def evaluate_page(self, page_num: int, extracted_text: str) -> Dict[str, Any]:
        """
        Evaluate a single page's extraction against its GT.
        """
        gt_page = next((item for item in self.gt_data if item["page"] == page_num), None)
        if not gt_page:
            return {"error": "No ground truth for page"}
            
        results = {}
        for item in gt_page.get("items", []):
            if item["type"] == "formula":
                # For this simple automated evaluation, we just pass the entire extracted text
                # to see if the formula is preserved *anywhere* in the page.
                # A true evaluation would extract the specific bounding box.
                results[item["id"]] = self.evaluate_formula(extracted_text, item)
                
        return results
