import argparse
import time
import json
import os
import sys
from pathlib import Path
from typing import Dict, Any

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.app.ingestion.math.base import MathExtractor
from backend.app.ingestion.math.evaluator import MathEvaluator

class DummyExtractor(MathExtractor):
    """Synthetic extractor for testing benchmark evaluator behavior."""
    @property
    def name(self) -> str:
        return "DummyExtractor"
        
    def load_model(self) -> None:
        time.sleep(0.01) # Simulate load
        
    def extract_page(self, pdf_path: str, page_num: int) -> Dict[str, Any]:
        # Return controlled predictions to test the evaluator
        if page_num == 127:
            # PASS prediction (Exact LaTeX match for formula 1, but Formula 2 is degraded)
            text = "The distance between P(x1, y1) and Q(x2, y2) is \\sqrt{(x_2-x_1)^2+(y_2-y_1)^2} \n and distance from origin is (x2 + y2)"
        elif page_num == 35:
            # REVIEW prediction
            text = "x^2 - 3 = (x - 3)(x + 3)" # Missing \sqrt
        else:
            text = "Standard paragraph text without mathematical formulas."
            
        return {
            "text": text,
            "execution_time_seconds": 0.005,
            "success": True
        }

class PyPDFium2Extractor(MathExtractor):
    """
    Production baseline extractor using pypdfium2 (the current EduNavika engine).
    Demonstrates actual textbook text extraction behavior on mathematical pages.
    """
    @property
    def name(self) -> str:
        return "PyPDFium2Extractor"
        
    def load_model(self) -> None:
        import pypdfium2
        self._engine = pypdfium2
        
    def extract_page(self, pdf_path: str, page_num: int) -> Dict[str, Any]:
        start = time.time()
        try:
            if not os.path.exists(pdf_path):
                return {
                    "text": "",
                    "execution_time_seconds": time.time() - start,
                    "success": False,
                    "error": f"PDF not found: {pdf_path}"
                }
            pdf = self._engine.PdfDocument(pdf_path)
            if page_num < 1 or page_num > len(pdf):
                return {
                    "text": "",
                    "execution_time_seconds": time.time() - start,
                    "success": False,
                    "error": f"Page {page_num} out of range (1..{len(pdf)})"
                }
            page = pdf[page_num - 1]
            textpage = page.get_textpage()
            text = textpage.get_text_bounded()
            return {
                "text": text,
                "execution_time_seconds": time.time() - start,
                "success": True,
                "error": None
            }
        except Exception as e:
            return {
                "text": "",
                "execution_time_seconds": time.time() - start,
                "success": False,
                "error": str(e)
            }

def run_benchmark(extractor: MathExtractor, gt_path: str, output_path: str):
    if not os.path.exists(gt_path):
        print(f"Error: Ground truth file not found at {gt_path}")
        sys.exit(1)
        
    evaluator = MathEvaluator(gt_path)
    
    print(f"\n============================================================")
    print(f"RUNNING MATH EXTRACTION BENCHMARK: {extractor.name}")
    print(f"============================================================")
    print(f"Loading model for {extractor.name}...")
    load_start = time.time()
    extractor.load_model()
    load_time = time.time() - load_start
    print(f"Model loaded in {load_time:.3f}s")
    
    results = {
        "extractor": extractor.name,
        "load_time_seconds": load_time,
        "pages": []
    }
    
    for gt_page in evaluator.gt_data:
        pdf_path = os.path.join(PROJECT_ROOT, "GSEB-Dataset", gt_page["document"])
        page_num = gt_page["page"]
        
        start = time.time()
        ext_result = extractor.extract_page(pdf_path, page_num)
        ext_time = time.time() - start
        
        # Evaluate
        eval_result = evaluator.evaluate_page(page_num, ext_result.get("text", ""), document=gt_page["document"])
        
        results["pages"].append({
            "document": gt_page["document"],
            "page": page_num,
            "execution_time_seconds": round(ext_time, 4),
            "success": ext_result.get("success", False),
            "evaluation": eval_result
        })
        
    summary = MathEvaluator.compute_summary(results)
    results["summary"] = summary
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
        
    print(f"\n--- BENCHMARK RESULTS ---")
    print(f"Evaluator Engine:            {summary['extractor']}")
    print(f"Total Pages Evaluated:       {summary['total_pages_evaluated']}")
    print(f"Total Formulas Evaluated:    {summary['total_formulas_evaluated']}")
    print(f"Exact Matches:               {summary['exact_matches']} ({summary['exact_match_rate']*100:.1f}%)")
    print(f"High Symbol Retention:       {summary['high_symbols']} ({summary['high_symbol_rate']*100:.1f}%)")
    print(f"Semantic HIGH:               {summary['semantic_high']} ({summary['semantic_high_rate']*100:.1f}%)")
    print(f"Semantic REVIEW:             {summary['semantic_review']}")
    print(f"Semantic FAIL:               {summary['semantic_fail']}")
    print(f"Avg Time Per Page:           {summary['average_time_per_page_seconds']}s")
    print(f"Report saved to:             {output_path}\n")
    return results

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run mathematical document extraction benchmark.")
    parser.add_argument("--extractor", choices=["pypdfium2", "dummy", "nougat", "marker"], default="pypdfium2")
    parser.add_argument("--gt", default=str(PROJECT_ROOT / "data" / "processed" / "reports" / "math_ground_truth.json"))
    parser.add_argument("--out", default=str(PROJECT_ROOT / "data" / "processed" / "reports" / "math_ocr_benchmark_report.json"))
    args = parser.parse_args()
    
    if args.extractor == "dummy":
        extractor = DummyExtractor()
    elif args.extractor == "pypdfium2":
        extractor = PyPDFium2Extractor()
    else:
        raise NotImplementedError(f"{args.extractor} requires specialized ML runtime dependencies not currently bundled.")
        
    run_benchmark(extractor, args.gt, args.out)
