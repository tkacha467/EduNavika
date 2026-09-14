"""
Milestone 4.5: Mathematical Equivalence Benchmark Runner
Evaluates 3 approaches against Ground Truth splits (DEV / TEST) with formal symbolic CAS
and restricted numerical verification:
  1. PyPDFium2 Baseline (Unlocalized text layer)
  2. PyPDFium2 + Heuristic Normalizer (Unlocalized text layer)
  3. Targeted Mathematical Extraction (M4.4 Hybrid Gate + Crop OCR, Frozen & Unchanged)

Preserves strict decoupling between:
  - Exact Match (Level 1)
  - Structural Accuracy (Level 2)
  - Mathematical Equivalence (Level 3)
  - Unsupported / Parse Error Categories
"""

import sys
import os
import time
import json
import argparse
from pathlib import Path
from typing import Dict, Any, List
import numpy as np

# Ensure local import path
sys.path.insert(0, os.path.abspath("."))
sys.stdout.reconfigure(encoding='utf-8')

import pypdfium2 as pdfium
from backend.app.ingestion.math.evaluator import MathEvaluator
from backend.app.ingestion.math.normalizer import CanonicalLaTeXNormalizer
from backend.app.ingestion.math.targeted_extractor import TargetedMathExtractor
from backend.app.ingestion.math.symbolic import (
    MathematicalEquivalenceEngine,
    EquivalenceStatus,
    MathCategory,
    VerificationMethod,
)


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
    print(f"RUNNING MILESTONE 4.5 BENCHMARK: SPLIT = {split.upper()}")
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
    equiv_engine = MathematicalEquivalenceEngine()

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
            "regions_cropped": 0
        }
    }

    for idx, r in enumerate(records, 1):
        rel_path = r["document"]
        full_pdf_path = os.path.join("GSEB-Dataset", rel_path)
        page_num = r["page"]
        items = r.get("items", [])

        print(f"[{idx}/{total_pages}] Processing {rel_path} Page {page_num} ({len(items)} formulas)...", end="", flush=True)

        # 1. Approach: PyPDFium2 Baseline (unlocalized baseline extraction)
        t0 = time.time()
        base_text = get_pypdfium2_text(full_pdf_path, page_num)
        t_base = time.time() - t0
        approaches["pypdfium2_baseline"]["total_time_seconds"] += t_base
        approaches["pypdfium2_baseline"]["page_times"].append(t_base)

        base_evals = evaluator.evaluate_page(page_num, {"text": base_text, "localization_status": "UNLOCALIZED"}, document=rel_path)
        for it in items:
            ev = base_evals.get(it["id"], evaluator.evaluate_formula("", it, localization_status="UNLOCALIZED"))
            ev["formula_id"] = it["id"]
            ev["document"] = rel_path
            ev["page"] = page_num

            # Milestone 4.5: Mathematical Equivalence Engine Evaluation
            eq_res = equiv_engine.evaluate(ev["normalized_extracted"], it.get("latex", ""))
            ev["m45_equivalence"] = eq_res.to_dict()
            approaches["pypdfium2_baseline"]["evaluations"].append(ev)

        # 2. Approach: Heuristic Normalizer on baseline (unlocalized)
        t0 = time.time()
        norm_text = normalizer.normalize(base_text)
        t_norm = t_base + (time.time() - t0)
        approaches["baseline_heuristic_norm"]["total_time_seconds"] += t_norm
        approaches["baseline_heuristic_norm"]["page_times"].append(t_norm)

        norm_evals = evaluator.evaluate_page(page_num, {"text": norm_text, "localization_status": "UNLOCALIZED"}, document=rel_path)
        for it in items:
            ev = norm_evals.get(it["id"], evaluator.evaluate_formula("", it, localization_status="UNLOCALIZED"))
            ev["formula_id"] = it["id"]
            ev["document"] = rel_path
            ev["page"] = page_num

            # Milestone 4.5: Mathematical Equivalence Engine Evaluation
            eq_res = equiv_engine.evaluate(ev["normalized_extracted"], it.get("latex", ""))
            ev["m45_equivalence"] = eq_res.to_dict()
            approaches["baseline_heuristic_norm"]["evaluations"].append(ev)

        # 3. Approach: Targeted Math Extractor (bounding-box localized)
        t0 = time.time()
        target_res = targeted_extractor.extract_page(full_pdf_path, page_num)
        t_target = time.time() - t0
        approaches["targeted_math_extraction"]["total_time_seconds"] += t_target
        approaches["targeted_math_extraction"]["page_times"].append(t_target)
        approaches["targeted_math_extraction"]["regions_cropped"] += len(target_res.get("recovered_formulas", []))

        target_evals = evaluator.evaluate_page(page_num, target_res, document=rel_path)
        for it in items:
            ev = target_evals.get(it["id"], evaluator.evaluate_formula("", it, localization_status="UNLOCALIZED"))
            ev["formula_id"] = it["id"]
            ev["document"] = rel_path
            ev["page"] = page_num

            # Milestone 4.5: Mathematical Equivalence Engine Evaluation
            eq_res = equiv_engine.evaluate(ev["normalized_extracted"], it.get("latex", ""))
            ev["m45_equivalence"] = eq_res.to_dict()
            approaches["targeted_math_extraction"]["evaluations"].append(ev)

        print(f" Done in {t_target:.2f}s (targeted)")

    # Aggregate and Compile Reports
    summary_report = {
        "split": split,
        "total_pages": total_pages,
        "total_formulas": total_formulas,
        "results": {}
    }

    def compute_approach_summary(app_data: Dict[str, Any]) -> Dict[str, Any]:
        evals = app_data["evaluations"]
        total_time = app_data["total_time_seconds"]
        n_pages = max(1, total_pages)
        n_formulas = max(1, total_formulas)

        # Track subsets: CORE vs DIAGNOSTIC vs OVERALL
        subsets = {
            "CORE": [e for e in evals if e.get("track") == "CORE"],
            "DIAGNOSTIC": [e for e in evals if e.get("track") == "DIAGNOSTIC"],
            "OVERALL": evals
        }

        metrics_summary = {}
        for s_name, s_evals in subsets.items():
            count = len(s_evals)
            if count == 0:
                continue
            exact_count = sum(1 for e in s_evals if e.get("exact_match") == "PASS")
            struct_count = sum(1 for e in s_evals if e.get("structural_accuracy") in ["HIGH", "MEDIUM"])
            symbol_count = sum(1 for e in s_evals if e.get("symbol_accuracy") in ["HIGH", "MEDIUM"])
            loc_count = sum(1 for e in s_evals if e.get("localization_status") == "LOCALIZED")

            # Milestone 4.5 Equivalence metrics
            sym_equiv = sum(1 for e in s_evals if e.get("m45_equivalence", {}).get("status") == EquivalenceStatus.SYMBOLIC_EQUIVALENT.value)
            num_equiv = sum(1 for e in s_evals if e.get("m45_equivalence", {}).get("status") == EquivalenceStatus.NUMERICALLY_EQUIVALENT.value)
            total_equiv = sym_equiv + num_equiv
            non_equiv = sum(1 for e in s_evals if e.get("m45_equivalence", {}).get("status") in [
                EquivalenceStatus.SYMBOLIC_NON_EQUIVALENT.value,
                EquivalenceStatus.NUMERICALLY_NON_EQUIVALENT.value,
            ])
            inconclusive = sum(1 for e in s_evals if e.get("m45_equivalence", {}).get("status") == EquivalenceStatus.INCONCLUSIVE.value)
            parse_errors = sum(1 for e in s_evals if e.get("m45_equivalence", {}).get("status") == EquivalenceStatus.PARSE_ERROR.value)
            unsupported = sum(1 for e in s_evals if e.get("m45_equivalence", {}).get("status") == EquivalenceStatus.UNSUPPORTED.value)

            metrics_summary[s_name] = {
                "count": count,
                "exact_match": f"{exact_count}/{count} ({100.0 * exact_count / count:.2f}%)",
                "structural_accuracy": f"{struct_count}/{count} ({100.0 * struct_count / count:.2f}%)",
                "symbol_accuracy": f"{symbol_count}/{count} ({100.0 * symbol_count / count:.2f}%)",
                "localized_candidates": f"{loc_count}/{count} ({100.0 * loc_count / count:.2f}%)",
                "mathematical_equivalence": {
                    "total_certified_equivalent": f"{total_equiv}/{count} ({100.0 * total_equiv / count:.2f}%)",
                    "symbolic_equivalent": f"{sym_equiv}/{count} ({100.0 * sym_equiv / count:.2f}%)",
                    "numerically_equivalent_probabilistic": f"{num_equiv}/{count} ({100.0 * num_equiv / count:.2f}%)",
                    "non_equivalent": f"{non_equiv}/{count} ({100.0 * non_equiv / count:.2f}%)",
                    "inconclusive": f"{inconclusive}/{count} ({100.0 * inconclusive / count:.2f}%)",
                    "parse_errors": f"{parse_errors}/{count} ({100.0 * parse_errors / count:.2f}%)",
                    "unsupported_out_of_scope": f"{unsupported}/{count} ({100.0 * unsupported / count:.2f}%)",
                }
            }

        # Category-level breakdown (for OVERALL)
        category_breakdown = {}
        all_categories = sorted(list(set(e.get("category", "UNKNOWN") for e in evals)))
        for cat in all_categories:
            cat_evals = [e for e in evals if e.get("category") == cat]
            cat_count = len(cat_evals)
            c_sym = sum(1 for e in cat_evals if e.get("m45_equivalence", {}).get("status") == EquivalenceStatus.SYMBOLIC_EQUIVALENT.value)
            c_num = sum(1 for e in cat_evals if e.get("m45_equivalence", {}).get("status") == EquivalenceStatus.NUMERICALLY_EQUIVALENT.value)
            c_tot = c_sym + c_num
            c_pe = sum(1 for e in cat_evals if e.get("m45_equivalence", {}).get("status") == EquivalenceStatus.PARSE_ERROR.value)
            c_un = sum(1 for e in cat_evals if e.get("m45_equivalence", {}).get("status") == EquivalenceStatus.UNSUPPORTED.value)

            category_breakdown[cat] = {
                "count": cat_count,
                "equivalent": f"{c_tot}/{cat_count} ({100.0 * c_tot / cat_count:.2f}%)",
                "parse_errors": f"{c_pe}/{cat_count} ({100.0 * c_pe / cat_count:.2f}%)",
                "unsupported": f"{c_un}/{cat_count} ({100.0 * c_un / cat_count:.2f}%)"
            }

        # Structural elements breakdown
        frac_items = [e for e in evals if e.get("fraction_accuracy") != "N/A"]
        sub_items = [e for e in evals if e.get("subscript_superscript") != "N/A"]
        rad_items = [e for e in evals if e.get("radical_accuracy") != "N/A"]

        frac_high = sum(1 for e in frac_items if e.get("fraction_accuracy") in ["HIGH", "MEDIUM"])
        sub_high = sum(1 for e in sub_items if e.get("subscript_superscript") in ["HIGH", "MEDIUM"])
        rad_high = sum(1 for e in rad_items if e.get("radical_accuracy") in ["HIGH", "MEDIUM"])

        return {
            "name": app_data["name"],
            "total_time_seconds": round(total_time, 2),
            "avg_latency_per_page_ms": round(total_time * 1000.0 / n_pages, 1),
            "avg_latency_per_formula_ms": round(total_time * 1000.0 / n_formulas, 1),
            "regions_cropped": app_data.get("regions_cropped", 0),
            "metrics": metrics_summary,
            "category_breakdown": category_breakdown,
            "structural_breakdown": {
                "fraction_preservation": f"{frac_high}/{len(frac_items)} ({100.0 * frac_high / len(frac_items):.2f}%)" if frac_items else "N/A",
                "sub_super_preservation": f"{sub_high}/{len(sub_items)} ({100.0 * sub_high / len(sub_items):.2f}%)" if sub_items else "N/A",
                "radical_preservation": f"{rad_high}/{len(rad_items)} ({100.0 * rad_high / len(rad_items):.2f}%)" if rad_items else "N/A"
            }
        }

    for app_key, app_val in approaches.items():
        summary_report["results"][app_key] = compute_approach_summary(app_val)

    # Attach Symbolic Equivalence Engine Latency Profile
    summary_report["equivalence_engine_latency_stats"] = equiv_engine.get_latency_stats()

    # Print Formatted Comparison Table
    print(f"\n==================== BENCHMARK RESULTS ({split.upper()}) ====================")
    for app_key, res in summary_report["results"].items():
        print(f"\n>>> Approach: {res['name']}")
        print(f"  Latency: {res['total_time_seconds']}s total ({res['avg_latency_per_page_ms']} ms/page)")
        for track in ["CORE", "DIAGNOSTIC", "OVERALL"]:
            m = res["metrics"].get(track, {})
            if m.get("count", 0) > 0:
                print(f"  [{track}] (N={m['count']}):")
                print(f"    Exact Match (Level 1):       {m['exact_match']}")
                print(f"    Structural Valid (Level 2):  {m['structural_accuracy']}")
                print(f"    Symbol Valid:                {m['symbol_accuracy']}")
                eq = m["mathematical_equivalence"]
                print(f"    Mathematical Equiv (Level 3):{eq['total_certified_equivalent']}")
                print(f"      - Symbolic Proven:         {eq['symbolic_equivalent']}")
                print(f"      - Numerical Certified:     {eq['numerically_equivalent_probabilistic']}")
                print(f"      - Certified Non-Equiv:     {eq['non_equivalent']}")
                print(f"      - Inconclusive:            {eq['inconclusive']}")
                print(f"      - Parse Errors:            {eq['parse_errors']}")
                print(f"      - Unsupported Out-of-Scope:{eq['unsupported_out_of_scope']}")

        print(f"  Category Breakdown:")
        for cat, c_data in res["category_breakdown"].items():
            print(f"    {cat:<22} N={c_data['count']:<2}: Equiv={c_data['equivalent']:<16} ParseErr={c_data['parse_errors']:<14} Unsupported={c_data['unsupported']}")

        sb = res["structural_breakdown"]
        print(f"  Structural Elements:")
        print(f"    Fractions:   {sb['fraction_preservation']}")
        print(f"    Sub/Super:   {sb['sub_super_preservation']}")
        print(f"    Radicals:    {sb['radical_preservation']}")

    lat = summary_report["equivalence_engine_latency_stats"]
    print(f"\n>>> Mathematical Equivalence Engine Latency Profile:")
    print(f"  Mean: {lat['mean_ms']} ms | Median: {lat['median_ms']} ms | p95: {lat['p95_ms']} ms | Max: {lat['max_ms']} ms (N={lat['count']} calls)")

    out_file = os.path.join(gt_dir, f"milestone_4_5_benchmark_{split}.json")
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(summary_report, f, indent=2, ensure_ascii=False)
    print(f"\nReport written to: {out_file}")

    return summary_report


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--split", choices=["dev", "test"], default="dev", help="Dataset split to evaluate")
    args = parser.parse_args()
    run_benchmark(args.split)
