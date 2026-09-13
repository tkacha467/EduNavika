import argparse
import time
import json
import os
from typing import Dict, Any

from backend.app.ingestion.math.base import MathExtractor
from backend.app.ingestion.math.evaluator import MathEvaluator

class DummyExtractor(MathExtractor):
    @property
    def name(self) -> str:
        return "DummyExtractor"
        
    def load_model(self) -> None:
        time.sleep(0.1) # Simulate load
        
    def extract_page(self, pdf_path: str, page_num: int) -> Dict[str, Any]:
        # Return controlled predictions to test the evaluator
        if page_num == 127:
            # PASS prediction (Exact LaTeX match for formula 1)
            text = "The distance between P(x1, y1) and Q(x2, y2) is \\sqrt{(x_2-x_1)^2+(y_2-y_1)^2} \n and distance from origin is (x2 + y2)"
            # Formula 1 -> PASS, Formula 2 -> FAIL (semantic loss)
        elif page_num == 35:
            # REVIEW prediction
            text = "x^2 - 3 = (x - 3)(x + 3)" # Missing \sqrt
        else:
            text = "Garbage text"
            
        return {
            "text": text,
            "execution_time_seconds": 0.05,
            "success": True
        }

def run_benchmark(extractor: MathExtractor, gt_path: str, output_path: str):
    evaluator = MathEvaluator(gt_path)
    
    print(f"Loading model for {extractor.name}...")
    load_start = time.time()
    extractor.load_model()
    load_time = time.time() - load_start
    print(f"Model loaded in {load_time:.2f}s")
    
    results = {
        "extractor": extractor.name,
        "load_time_seconds": load_time,
        "pages": []
    }
    
    for gt_page in evaluator.gt_data:
        pdf_path = os.path.join("GSEB-Dataset", gt_page["document"])
        page_num = gt_page["page"]
        
        print(f"Extracting {gt_page['document']} - Page {page_num}...")
        start = time.time()
        ext_result = extractor.extract_page(pdf_path, page_num)
        ext_time = time.time() - start
        
        # Evaluate
        eval_result = evaluator.evaluate_page(page_num, ext_result.get("text", ""))
        
        results["pages"].append({
            "document": gt_page["document"],
            "page": page_num,
            "execution_time_seconds": ext_time,
            "evaluation": eval_result
        })
        
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
        
    print(f"Benchmark completed. Report saved to {output_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--extractor", choices=["nougat", "marker", "dummy"], default="dummy")
    parser.add_argument("--gt", default="data/processed/reports/math_ground_truth.json")
    parser.add_argument("--out", default="data/processed/reports/dummy_math_benchmark.json")
    args = parser.parse_args()
    
    if args.extractor == "dummy":
        extractor = DummyExtractor()
    else:
        raise NotImplementedError(f"{args.extractor} not yet implemented")
        
    run_benchmark(extractor, args.gt, args.out)
