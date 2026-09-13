"""
Milestone 4.4: Mathematical Extraction Benchmark Runner
Evaluates 3 approaches against Ground Truth splits (DEV / TEST):
  1. PyPDFium2 Baseline
  2. Baseline + Heuristic Normalization
  3. Quality-Gated Targeted Mathematical Extraction (MathQualityGate + MathRegionDetector + Crop OCR + Normalizer)
"""

import sys
import os
import time
import json
import argparse
from pathlib import Path
from typing import Dict, Any, List

# Ensure local import path
sys.path.insert(0, os.path.abspath("."))
sys.stdout.reconfigure(encoding='utf-8')

import pypdfium2 as pdfium
from backend.app.ingestion.math.evaluator import MathEvaluator
from backend.app.ingestion.math.normalizer import CanonicalLaTeXNormalizer
from backend.app.ingestion.math.targeted_extractor import TargetedMathExtractor


def get_pypdfium2_text(pdf_path: str, page_num: int) -> str:
    try:
        doc = pdfium.PdfDocument(pdf_path)
        if page_num < 1 or page_num > len(doc):
            return ""
        page = doc[page_num - 1]
        tp = page.get_textpage()
        return tp.get_text_bounded()
    except Exception as e:
        return f"Error: {e}"


def run_benchmark(split: str = "dev") -> Dict[str, Any]:
    gt_dir = "data/processed/reports"
    gt_path = os.path.join(gt_dir, f"math_ground_truth_{split}.json")
    manifest_path = os.path.join(gt_dir, "test_manifest.json")

    print(f"\n=======================================================")
    print(f"RUNNING MILESTONE 4.4 BENCHMARK: SPLIT = {split.upper()}")
    print(f"=======================================================")

    # Invariant check for TEST split: verify cryptographic SHA-256 seal
    if split == "test":
        print("Verifying cryptographic test manifest SHA-256 seal...")
        is_sealed = MathEvaluator.verify_test_manifest(manifest_path, gt_path)
        if not is_sealed:
            raise RuntimeError("CRITICAL INTEGRITY FAILURE: Test manifest SHA-256 mismatch! Halting.")
        print("Test manifest SHA-256 verified successfully.")

    evaluator = MathEvaluator(gt_path)
    normalizer = CanonicalLaTeXNormalizer()
    targeted_extractor = TargetedMathExtractor(enable_ocr=True)
    targeted_extractor.load_model()

    records = evaluator.gt_data
    total_pages = len(records)
    total_formulas = sum(len(r.get("items", [])) for r in records)

    print(f"Loaded {total_pages} pages containing {total_formulas} formulas from {gt_path}")

    approaches = {
        "pypdfium2_baseline": {
            "name": "PyPDFium2 Baseline",
            "evaluations": [],
            "total_time_seconds": 0.0,
            "page_times": []
        },
        "baseline_heuristic_norm": {
            "name": "PyPDFium2 + Heuristic Normalizer",
            "evaluations": [],
            "total_time_seconds": 0.0,
            "page_times": []
        },
        "targeted_math_extraction": {
            "name": "Targeted Mathematical Extraction (Hybrid Gate + Crop OCR)",
            "evaluations": [],
            "total_time_seconds": 0.0,
            "page_times": [],
            "targeted_regions_cropped": 0
        }
    }

    # Iterate through all pages in split
    for idx, r in enumerate(records, 1):
        rel_path = r["document"]
        full_pdf_path = os.path.join("GSEB-Dataset", rel_path)
        page_num = r["page"]
        items = r.get("items", [])

        print(f"[{idx}/{total_pages}] Processing {rel_path} Page {page_num} ({len(items)} formulas)...", end="", flush=True)

        # 1. Approach: PyPDFium2 Baseline
        t0 = time.time()
        base_text = get_pypdfium2_text(full_pdf_path, page_num)
        t_base = time.time() - t0
        approaches["pypdfium2_baseline"]["total_time_seconds"] += t_base
        approaches["pypdfium2_baseline"]["page_times"].append(t_base)

        for it in items:
            ev = evaluator.evaluate_formula(base_text, it)
            ev["formula_id"] = it["id"]
            ev["document"] = rel_path
            ev["page"] = page_num
            approaches["pypdfium2_baseline"]["evaluations"].append(ev)

        # 2. Approach: Heuristic Normalizer on baseline
        t0 = time.time()
        norm_text = normalizer.normalize(base_text)
        t_norm = t_base + (time.time() - t0)
        approaches["baseline_heuristic_norm"]["total_time_seconds"] += t_norm
        approaches["baseline_heuristic_norm"]["page_times"].append(t_norm)

        for it in items:
            ev = evaluator.evaluate_formula(norm_text, it)
            ev["formula_id"] = it["id"]
            ev["document"] = rel_path
            ev["page"] = page_num
            approaches["baseline_heuristic_norm"]["evaluations"].append(ev)

        # 3. Approach: Targeted Math Extractor
        t0 = time.time()
        target_res = targeted_extractor.extract_page(full_pdf_path, page_num)
        t_target = time.time() - t0
        approaches["targeted_math_extraction"]["total_time_seconds"] += t_target
        approaches["targeted_math_extraction"]["page_times"].append(t_target)
        approaches["targeted_math_extraction"]["targeted_regions_cropped"] += len(target_res.get("recovered_formulas", []))

        target_text = target_res.get("text", "")
        for it in items:
            ev = evaluator.evaluate_formula(target_text, it)
            ev["formula_id"] = it["id"]
            ev["document"] = rel_path
            ev["page"] = page_num
            approaches["targeted_math_extraction"]["evaluations"].append(ev)

        print(f" Done in {t_target:.2f}s (targeted)")

    # Aggregate Results
    summary_report = {
        "split": split,
        "total_pages": total_pages,
        "total_formulas": total_formulas,
        "results": {}
    }

    for app_key, app_data in approaches.items():
        evals = app_data["evaluations"]
        agg = MathEvaluator.aggregate_metrics(evals)
        total_time = app_data["total_time_seconds"]
        avg_page_latency = total_time / total_pages if total_pages else 0.0
        avg_formula_latency = total_time / total_formulas if total_formulas else 0.0

        # Detailed structural breakdown
        frac_items = [e for e in evals if e.get("fraction_accuracy") != "N/A"]
        frac_high = sum(1 for e in frac_items if e.get("fraction_accuracy") in ("HIGH", "MEDIUM"))

        sub_items = [e for e in evals if e.get("subscript_superscript") != "N/A"]
        sub_high = sum(1 for e in sub_items if e.get("subscript_superscript") in ("HIGH", "MEDIUM"))

        rad_items = [e for e in evals if e.get("radical_accuracy") != "N/A"]
        rad_high = sum(1 for e in rad_items if e.get("radical_accuracy") in ("HIGH", "MEDIUM"))

        summary_report["results"][app_key] = {
            "name": app_data["name"],
            "total_time_seconds": round(total_time, 2),
            "avg_latency_per_page_ms": round(avg_page_latency * 1000, 1),
            "avg_latency_per_formula_ms": round(avg_formula_latency * 1000, 1),
            "regions_cropped": app_data.get("targeted_regions_cropped", 0),
            "metrics": agg,
            "structural_breakdown": {
                "fraction_preservation": f"{frac_high}/{len(frac_items)} ({100.0 * frac_high / len(frac_items):.2f}%)" if frac_items else "N/A",
                "sub_super_preservation": f"{sub_high}/{len(sub_items)} ({100.0 * sub_high / len(sub_items):.2f}%)" if sub_items else "N/A",
                "radical_preservation": f"{rad_high}/{len(rad_items)} ({100.0 * rad_high / len(rad_items):.2f}%)" if rad_items else "N/A"
            }
        }

    # Print Comparison Table
    print(f"\n==================== BENCHMARK RESULTS ({split.upper()}) ====================")
    for app_key, res in summary_report["results"].items():
        print(f"\n>>> Approach: {res['name']}")
        print(f"  Latency: {res['total_time_seconds']}s total ({res['avg_latency_per_page_ms']} ms/page)")
        for track in ["CORE", "DIAGNOSTIC", "OVERALL"]:
            m = res["metrics"].get(track, {})
            if m.get("count", 0) > 0:
                print(f"  [{track}] (N={m['count']}):")
                print(f"    Exact Match:        {m['exact_match']}")
                print(f"    Semantic High:      {m['semantic_high']}")
                print(f"    Semantic Valid:     {m['semantic_valid']}")
                print(f"    Structural Valid:   {m['structural_accuracy']}")
                print(f"    Symbol Valid:       {m['symbol_accuracy']}")
        sb = res["structural_breakdown"]
        print(f"  Structural Elements:")
        print(f"    Fractions:   {sb['fraction_preservation']}")
        print(f"    Sub/Super:   {sb['sub_super_preservation']}")
        print(f"    Radicals:    {sb['radical_preservation']}")

    out_file = os.path.join(gt_dir, f"milestone_4_4_benchmark_{split}.json")
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(summary_report, f, indent=2, ensure_ascii=False)
    print(f"\nReport written to: {out_file}")

    return summary_report


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--split", choices=["dev", "test"], default="dev", help="Dataset split to evaluate")
    args = parser.parse_args()
    run_benchmark(args.split)
