import json
import time
import os
import sys
from pathlib import Path
from typing import Dict, Any, List

# Ensure project root in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.app.ingestion.math.evaluator import MathEvaluator
from backend.app.ingestion.math.extractors import (
    PyPDFium2Extractor,
    PyPDFExtractor,
    RapidOCRExtractor,
    HeuristicMathExtractor,
)

CANDIDATES_NOT_EVALUATED = [
    {
        "name": "Nougat (facebook/nougat-small)",
        "category": "Vision-Encoder-Decoder (Swin-Transformer + mBART)",
        "status": "NOT EVALUATED",
        "reason": "Requires 1.5GB+ PyTorch weights, dedicated CUDA GPU recommended; CPU inference latency >20s/page exceeds local resource constraints."
    },
    {
        "name": "Marker (VikParuchuri/marker)",
        "category": "Deep Layout + OCR + Texify Pipeline",
        "status": "NOT EVALUATED",
        "reason": "Requires multi-model ensemble (Surya layout detection + Texify OCR, ~3.5GB weights) and heavy GPU dependencies."
    },
    {
        "name": "Tesseract OCR (pytesseract)",
        "category": "Traditional OCR Engine",
        "status": "NOT EVALUATED",
        "reason": "External C++ binary 'tesseract.exe' is not installed in the Windows system PATH."
    }
]

def classify_failure(gt_item: Dict[str, Any], extracted_text: str, eval_metrics: Dict[str, str]) -> List[str]:
    """Classifies mathematical extraction failure into granular error categories."""
    failures = []
    if eval_metrics.get("exact_match") == "PASS":
        return failures

    # 1. Missing radical
    if "\\sqrt" in gt_item.get("expected_symbols", []):
        if "\\sqrt" not in extracted_text and "√" not in extracted_text:
            failures.append("missing_radical")

    # 2. Exponent flattening (e.g. x^2 became x2 or x 2)
    if gt_item.get("has_superscript"):
        if "^" not in extracted_text and not any(c in extracted_text for c in "²³¹⁰⁴⁵⁶⁷⁸⁹"):
            failures.append("exponent_flattening")

    # 3. Subscript flattening (e.g. x_1 became x1 or x 1)
    if gt_item.get("has_subscript"):
        if "_" not in extracted_text and not any(c in extracted_text for c in "₀₁₂₃₄₅₆₇₈₉"):
            failures.append("subscript_flattening")

    # 4. Fraction splitting (e.g. \frac{a}{b} became a b without division)
    if gt_item.get("has_fraction"):
        if "\\frac" not in extracted_text and "/" not in extracted_text:
            failures.append("fraction_splitting")

    # 5. Chemical bond / reaction corruption
    if any(sym in ["\\rightarrow", "->"] for sym in gt_item.get("expected_symbols", [])):
        if "\\rightarrow" not in extracted_text and "->" not in extracted_text and "→" not in extracted_text:
            failures.append("reaction_arrow_omission")

    # Fallback category if failed without specific tag
    if not failures and eval_metrics.get("semantic_accuracy") == "FAIL":
        failures.append("symbol_omission_or_substitution")

    return failures


def run_candidate_benchmark(
    extractor,
    gt_data: List[Dict[str, Any]],
    evaluator: MathEvaluator
) -> Dict[str, Any]:
    print(f"\nEvaluating: {extractor.name}...")
    load_start = time.time()
    extractor.load_model()
    load_time = round(time.time() - load_start, 3)

    pages_results = []
    failure_taxonomy_counts: Dict[str, int] = {}
    total_ext_time = 0.0

    for gt_page in gt_data:
        pdf_path = os.path.join(PROJECT_ROOT, "GSEB-Dataset", gt_page["document"])
        page_num = gt_page["page"]

        ext_res = extractor.extract_page(pdf_path, page_num)
        text = ext_res.get("text", "")
        duration = ext_res.get("execution_time_seconds", 0.0)
        total_ext_time += duration

        eval_res = evaluator.evaluate_page(page_num, text, document=gt_page["document"])

        # Classify failures for each formula
        formula_failures = {}
        for item in gt_page.get("items", []):
            f_id = item["id"]
            metrics = eval_res.get(f_id, {})
            fails = classify_failure(item, text, metrics)
            formula_failures[f_id] = fails
            for f in fails:
                failure_taxonomy_counts[f] = failure_taxonomy_counts.get(f, 0) + 1

        pages_results.append({
            "document": gt_page["document"],
            "page": page_num,
            "execution_time_seconds": duration,
            "success": ext_res.get("success", False),
            "evaluation": eval_res,
            "failure_categories": formula_failures
        })

    candidate_results = {
        "extractor": extractor.name,
        "load_time_seconds": load_time,
        "pages": pages_results
    }
    summary = MathEvaluator.compute_summary(candidate_results)
    summary["model_load_time_seconds"] = load_time
    summary["failure_taxonomy"] = failure_taxonomy_counts

    return {
        "summary": summary,
        "pages": pages_results
    }


def run_full_comparison(
    gt_path: str = "backend/app/ingestion/math/ground_truth.json",
    output_json: str = "data/processed/reports/math_extraction_comparison.json"
):
    print("============================================================")
    print("MILESTONE 4.3: SPECIALIZED MATHEMATICAL EXTRACTION BENCHMARK")
    print("============================================================")

    with open(gt_path, "r", encoding="utf-8") as f:
        gt_data = json.load(f)

    evaluator = MathEvaluator(gt_path)

    candidates = [
        PyPDFium2Extractor(),       # Baseline
        PyPDFExtractor(),           # Standard Alternative
        RapidOCRExtractor(),        # Visual OCR
        HeuristicMathExtractor(),   # Domain Post-Processor
    ]

    all_results = {}
    comparison_table = []

    for extractor in candidates:
        res = run_candidate_benchmark(extractor, gt_data, evaluator)
        all_results[extractor.name] = res
        s = res["summary"]
        comparison_table.append({
            "extractor": s["extractor"],
            "exact_matches": f"{s['exact_matches']} ({s['exact_match_rate']*100:.1f}%)",
            "high_symbols": f"{s['high_symbols']} ({s['high_symbol_rate']*100:.1f}%)",
            "semantic_high": f"{s['semantic_high']} ({s['semantic_high_rate']*100:.1f}%)",
            "semantic_review": s["semantic_review"],
            "semantic_fail": s["semantic_fail"],
            "avg_time_per_page": f"{s['average_time_per_page_seconds']:.4f}s",
            "total_time": f"{s['total_execution_time_seconds']:.2f}s"
        })

    full_output = {
        "benchmark_metadata": {
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "total_pages": len(gt_data),
            "total_formulas": sum(len(item.get("items", [])) for item in gt_data),
            "ground_truth_file": gt_path,
        },
        "comparison_table": comparison_table,
        "candidates_evaluated": all_results,
        "candidates_not_evaluated": CANDIDATES_NOT_EVALUATED
    }

    os.makedirs(os.path.dirname(output_json), exist_ok=True)
    with open(output_json, "w", encoding="utf-8") as f:
        json.dump(full_output, f, indent=2)

    # Print Summary Table
    print("\n=========================================================================================")
    print("BENCHMARK COMPARISON RESULTS")
    print("=========================================================================================")
    print(f"{'Extractor':<25} | {'Exact Match':<12} | {'High Symbols':<13} | {'Semantic (H/R/F)':<18} | {'Avg Time/Page':<13}")
    print("-" * 89)
    for row in comparison_table:
        ext = row["extractor"]
        exact = row["exact_matches"]
        sym = row["high_symbols"]
        sem = f"{row['semantic_high'].split()[0]} / {row['semantic_review']} / {row['semantic_fail']}"
        t = row["avg_time_per_page"]
        print(f"{ext:<25} | {exact:<12} | {sym:<13} | {sem:<18} | {t:<13}")
    print("=========================================================================================\n")
    print(f"Detailed benchmark artifacts saved to: {output_json}\n")

    return full_output

if __name__ == "__main__":
    run_full_comparison()
