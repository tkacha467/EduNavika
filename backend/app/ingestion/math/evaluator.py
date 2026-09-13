import json
import re
from typing import Dict, Any, List, Optional

class MathEvaluator:
    """
    Evaluator for mathematical formula extraction quality against ground truth.
    Measures exact matches, symbol retention, structural preservation, and semantic accuracy.
    """
    def __init__(self, ground_truth_path: str):
        with open(ground_truth_path, 'r', encoding='utf-8') as f:
            self.gt_data = json.load(f)
            
    def _clean_syntax(self, text: str) -> str:
        """
        Strip LaTeX spacing, map Unicode mathematical symbols, and lowercase,
        preserving whitespace for boundary-sensitive comparisons.
        """
        if not text:
            return ""
        # Remove common LaTeX spacing commands: \,, \;, \:, \quad, \qquad, \!
        cleaned = re.sub(r'\\[,;:!]|\\quad|\\qquad', '', text)
        # Strip LaTeX \text{...} wrappers for plain comparison
        cleaned = re.sub(r'\\text\{([^}]+)\}', r'\1', cleaned)
        # Normalize Unicode dashes, minuses, and hyphen-minus
        cleaned = re.sub(r'[\u2212\u2013\u2014]', '-', cleaned)
        # Normalize Unicode superscripts
        sup_map = {'⁰':'^0', '¹':'^1', '²':'^2', '³':'^3', '⁴':'^4', '⁵':'^5', '⁶':'^6', '⁷':'^7', '⁸':'^8', '⁹':'^9'}
        for k, v in sup_map.items():
            cleaned = cleaned.replace(k, v)
        # Normalize Unicode subscripts
        sub_map = {'₀':'_0', '₁':'_1', '₂':'_2', '₃':'_3', '₄':'_4', '₅':'_5', '₆':'_6', '₇':'_7', '₈':'_8', '₉':'_9'}
        for k, v in sub_map.items():
            cleaned = cleaned.replace(k, v)
        # Normalize mathematical symbols to LaTeX equivalents
        sym_map = {
            '√': '\\sqrt', '±': '\\pm', '×': '\\times', '÷': '\\div',
            'π': '\\pi', 'θ': '\\theta', 'α': '\\alpha', 'β': '\\beta',
            '→': '\\rightarrow', '≤': '\\le', '≥': '\\ge', '°': '^\\circ'
        }
        for k, v in sym_map.items():
            cleaned = cleaned.replace(k, v)
        # Strip single-character group braces: e.g. \sqrt{3} -> \sqrt3, x_{1} -> x_1
        cleaned = re.sub(r'\{([a-zA-Z0-9])\}', r'\1', cleaned)
        return cleaned.lower()

    def _normalize(self, text: str) -> str:
        """Strip all whitespace and lowercase for structural comparison."""
        cleaned = self._clean_syntax(text)
        return re.sub(r'\s+', '', cleaned)

    def evaluate_formula(self, extracted: str, gt_item: Dict[str, Any]) -> Dict[str, str]:
        """
        Grades formula extraction on multiple specific accuracy metrics.
        Returns HIGH, MEDIUM, LOW, or FAIL for each dimension.
        Note: exact_match measures normalized formula substring presence in extracted text.
        """
        gt_latex = gt_item.get("latex", "")
        clean_ext = self._clean_syntax(extracted)
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
        
        # 1. Exact match (normalized substring presence)
        is_exact = False
        if norm_gt and norm_ext:
            if len(norm_gt) <= 4:
                # Boundary-sensitive match in whitespace-preserved text to prevent accidental substring hits (e.g. 'oh' inside 'alcohol')
                pattern = r'(?<![a-zA-Z0-9])' + re.escape(norm_gt) + r'(?![a-zA-Z0-9])'
                if re.search(pattern, clean_ext):
                    is_exact = True
            else:
                if norm_gt in norm_ext or norm_ext == norm_gt:
                    is_exact = True

        if is_exact:
            metrics["exact_match"] = "PASS"
            metrics["semantic_accuracy"] = "HIGH"
            metrics["structure_accuracy"] = "HIGH"
            metrics["symbol_accuracy"] = "HIGH"
            if gt_item.get("has_subscript") or gt_item.get("has_superscript"):
                metrics["subscript_superscript"] = "HIGH"
            if gt_item.get("has_fraction"):
                metrics["fraction_accuracy"] = "HIGH"
            return metrics
            
        if not extracted or len(extracted) < 2:
            return metrics
            
        # 2. Symbol accuracy
        expected_symbols = gt_item.get("expected_symbols", [])
        if expected_symbols:
            symbols_found = 0
            for sym in expected_symbols:
                norm_sym = self._normalize(sym)
                # Check verbatim LaTeX symbol or normalized form
                if sym in extracted or (norm_sym and norm_sym in norm_ext):
                    symbols_found += 1
                # Check stripped representation only if meaningful (>2 chars)
                elif len(sym) > 2 and sym.replace("\\", "") in extracted:
                    symbols_found += 1
                    
            if symbols_found == len(expected_symbols):
                metrics["symbol_accuracy"] = "HIGH"
            elif symbols_found > 0:
                metrics["symbol_accuracy"] = "MEDIUM"
                
        # 3. Super/Subscript logic
        if gt_item.get("has_superscript") or gt_item.get("has_subscript"):
            has_markers = "^" in norm_ext or "_" in norm_ext
            if has_markers:
                metrics["subscript_superscript"] = "MEDIUM"
            else:
                metrics["subscript_superscript"] = "FAIL"
                
        # 4. Fraction logic
        if gt_item.get("has_fraction"):
            if "\\frac" in extracted or "/" in extracted:
                metrics["fraction_accuracy"] = "MEDIUM"
            else:
                metrics["fraction_accuracy"] = "FAIL"
                
        # 5. Semantic Accuracy heuristic
        if metrics["symbol_accuracy"] in ["HIGH", "MEDIUM"] and metrics.get("subscript_superscript") != "FAIL":
            metrics["semantic_accuracy"] = "REVIEW"
            metrics["structure_accuracy"] = "REVIEW"
            
        return metrics

    def evaluate_page(self, page_num: int, extracted_text: str, document: Optional[str] = None) -> Dict[str, Any]:
        """
        Evaluate a single page's extraction against its GT.
        If document is provided, disambiguates between textbooks sharing the same page number.
        """
        if document:
            doc_target = document.replace("\\", "/").split("/")[-1]
            gt_page = next(
                (item for item in self.gt_data if item["page"] == page_num and item.get("document", "").replace("\\", "/").endswith(doc_target)),
                None
            )
            if not gt_page:
                gt_page = next((item for item in self.gt_data if item["page"] == page_num), None)
        else:
            gt_page = next((item for item in self.gt_data if item["page"] == page_num), None)

        if not gt_page:
            return {"error": f"No ground truth for page {page_num}"}
            
        results = {}
        for item in gt_page.get("items", []):
            if item["type"] == "formula":
                results[item["id"]] = self.evaluate_formula(extracted_text, item)
                
        return results

    @staticmethod
    def compute_summary(benchmark_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Computes aggregate statistics across all benchmarked pages.
        """
        total_pages = len(benchmark_results.get("pages", []))
        total_formulas = 0
        exact_matches = 0
        high_symbols = 0
        high_semantics = 0
        review_semantics = 0
        fail_semantics = 0
        total_ext_time = 0.0

        for p in benchmark_results.get("pages", []):
            total_ext_time += p.get("execution_time_seconds", 0.0)
            evals = p.get("evaluation", {})
            for f_id, f_eval in evals.items():
                if not isinstance(f_eval, dict):
                    continue
                total_formulas += 1
                if f_eval.get("exact_match") == "PASS":
                    exact_matches += 1
                if f_eval.get("symbol_accuracy") == "HIGH":
                    high_symbols += 1
                sem = f_eval.get("semantic_accuracy")
                if sem == "HIGH":
                    high_semantics += 1
                elif sem == "REVIEW":
                    review_semantics += 1
                else:
                    fail_semantics += 1

        exact_match_rate = round(exact_matches / total_formulas, 4) if total_formulas > 0 else 0.0
        high_symbol_rate = round(high_symbols / total_formulas, 4) if total_formulas > 0 else 0.0
        high_semantic_rate = round(high_semantics / total_formulas, 4) if total_formulas > 0 else 0.0

        return {
            "extractor": benchmark_results.get("extractor", "unknown"),
            "total_pages_evaluated": total_pages,
            "total_formulas_evaluated": total_formulas,
            "exact_matches": exact_matches,
            "exact_match_rate": exact_match_rate,
            "high_symbols": high_symbols,
            "high_symbol_rate": high_symbol_rate,
            "semantic_high": high_semantics,
            "semantic_high_rate": high_semantic_rate,
            "semantic_review": review_semantics,
            "semantic_fail": fail_semantics,
            "total_execution_time_seconds": round(total_ext_time, 3),
            "average_time_per_page_seconds": round(total_ext_time / total_pages, 3) if total_pages > 0 else 0.0
        }
