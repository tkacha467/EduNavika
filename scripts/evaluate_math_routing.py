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

import pypdfium2
from backend.app.ingestion.math.detector import MathPageDetector, MathPageClassification
from backend.app.ingestion.math.quality_gate import MathQualityGate
from backend.app.ingestion.math.router import MathExtractionRouter
from backend.app.ingestion.math.base import MathExtractor

class PyPDFium2Extractor(MathExtractor):
    @property
    def name(self) -> str:
        return "PyPDFium2Extractor"

    def load_model(self) -> None:
        pass

    def extract_page(self, pdf_path: str, page_num: int) -> Dict[str, Any]:
        start = time.time()
        try:
            pdf = pypdfium2.PdfDocument(pdf_path)
            page = pdf[page_num - 1]
            text = page.get_textpage().get_text_bounded()
            return {"text": text, "execution_time_seconds": time.time() - start, "success": True}
        except Exception as e:
            return {"text": "", "execution_time_seconds": time.time() - start, "success": False, "error": str(e)}

class MockSpecializedMathExtractor(MathExtractor):
    @property
    def name(self) -> str:
        return "SpecializedMathExtractor(Mock)"

    def load_model(self) -> None:
        pass

    def extract_page(self, pdf_path: str, page_num: int) -> Dict[str, Any]:
        start = time.time()
        # Simulates a specialized OCR/vision model extracting structured LaTeX
        return {
            "text": "\\text{High-fidelity specialized extraction of page } " + str(page_num),
            "execution_time_seconds": 0.045,
            "success": True
        }

def run_evaluation(
    gt_path: str = "backend/app/ingestion/math/ground_truth.json",
    prose_pdf: str = "GSEB-Dataset/STD-10th/Std-10_English_First Flight.pdf",
    output_path: str = "data/processed/reports/math_routing_evaluation.json"
):
    print("\n============================================================")
    print("RUNNING MILESTONE 4.2 MATHEMATICAL ROUTING RESEARCH EVALUATION")
    print("============================================================\n")

    detector = MathPageDetector()
    quality_gate = MathQualityGate()
    std_extractor = PyPDFium2Extractor()
    spec_extractor = MockSpecializedMathExtractor()

    router = MathExtractionRouter(
        standard_extractor=std_extractor,
        specialized_extractor=spec_extractor,
        detector=detector,
        quality_gate=quality_gate
    )

    # 1. Load Ground-Truth Math Pages (30 pages)
    with open(gt_path, "r", encoding="utf-8") as f:
        gt_data = json.load(f)

    math_eval_results = []
    tp = 0
    fn = 0
    math_detection_times = []
    routing_counts = {"STANDARD": 0, "SPECIALIZED": 0}
    gate_counts = {"SAFE": 0, "NEEDS_REVIEW": 0, "CORRUPTED": 0}

    print(f"Evaluating {len(gt_data)} authentic GSEB mathematical/science pages...")
    for item in gt_data:
        pdf_path = os.path.join(PROJECT_ROOT, "GSEB-Dataset", item["document"])
        page_num = item["page"]

        start = time.time()
        ext_res = std_extractor.extract_page(pdf_path, page_num)
        text = ext_res.get("text", "")

        t0 = time.time()
        det = detector.detect(text)
        math_detection_times.append(time.time() - t0)

        route_res = router.route_and_extract(pdf_path, page_num, initial_text=text)

        is_math = det.is_math
        if is_math:
            tp += 1
        else:
            fn += 1

        if route_res.extraction_method == spec_extractor.name:
            routing_counts["SPECIALIZED"] += 1
        else:
            routing_counts["STANDARD"] += 1

        gate_counts[route_res.validation_result.status] += 1

        math_eval_results.append({
            "document": item["document"],
            "page": page_num,
            "expected_math": True,
            "detected_as_math": is_math,
            "classification": det.classification.value,
            "score": det.score,
            "signals": det.signals,
            "validation_status": route_res.validation_result.status,
            "extraction_method": route_res.extraction_method,
        })

    # 2. Evaluate 30 Prose Pages from English First Flight (Pages 10 to 39)
    fp = 0
    tn = 0
    prose_eval_results = []
    prose_pdf_path = os.path.join(PROJECT_ROOT, prose_pdf)

    print("Evaluating 30 GSEB English literature prose pages (negative controls)...")
    for page_num in range(10, 40):
        ext_res = std_extractor.extract_page(prose_pdf_path, page_num)
        text = ext_res.get("text", "")

        t0 = time.time()
        det = detector.detect(text)
        math_detection_times.append(time.time() - t0)

        route_res = router.route_and_extract(prose_pdf_path, page_num, initial_text=text)

        is_math = det.is_math
        if is_math:
            fp += 1
        else:
            tn += 1

        if route_res.extraction_method == spec_extractor.name:
            routing_counts["SPECIALIZED"] += 1
        else:
            routing_counts["STANDARD"] += 1

        gate_counts[route_res.validation_result.status] += 1

        prose_eval_results.append({
            "document": prose_pdf,
            "page": page_num,
            "expected_math": False,
            "detected_as_math": is_math,
            "classification": det.classification.value,
            "score": det.score,
            "signals": det.signals,
            "validation_status": route_res.validation_result.status,
            "extraction_method": route_res.extraction_method,
        })

    # Metrics calculation
    total_eval = tp + fn + fp + tn
    precision = round(tp / (tp + fp), 4) if (tp + fp) > 0 else 0.0
    recall = round(tp / (tp + fn), 4) if (tp + fn) > 0 else 0.0
    f1 = round(2 * (precision * recall) / (precision + recall), 4) if (precision + recall) > 0 else 0.0
    fpr = round(fp / (fp + tn), 4) if (fp + tn) > 0 else 0.0
    fnr = round(fn / (fn + tp), 4) if (fn + tp) > 0 else 0.0
    avg_det_time_ms = round((sum(math_detection_times) / len(math_detection_times)) * 1000, 3)

    summary = {
        "total_pages_evaluated": total_eval,
        "math_pages_evaluated": tp + fn,
        "prose_pages_evaluated": fp + tn,
        "confusion_matrix": {
            "true_positives": tp,
            "false_positives": fp,
            "true_negatives": tn,
            "false_negatives": fn
        },
        "metrics": {
            "precision": precision,
            "recall": recall,
            "f1_score": f1,
            "false_positive_rate": fpr,
            "false_negative_rate": fnr
        },
        "routing_distribution": routing_counts,
        "quality_gate_decisions": gate_counts,
        "average_detection_overhead_ms": avg_det_time_ms
    }

    full_report = {
        "summary": summary,
        "math_evaluations": math_eval_results,
        "prose_evaluations": prose_eval_results
    }

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(full_report, f, indent=2)

    print("\n--- RESEARCH EVALUATION METRICS ---")
    print(f"Total Pages Evaluated:            {total_eval} (30 Math, 30 Prose)")
    print(f"True Positives (TP):              {tp}")
    print(f"False Positives (FP):             {fp}")
    print(f"True Negatives (TN):              {tn}")
    print(f"False Negatives (FN):             {fn}")
    print(f"Precision:                        {precision * 100:.1f}%")
    print(f"Recall:                           {recall * 100:.1f}%")
    print(f"F1 Score:                         {f1 * 100:.1f}%")
    print(f"False Positive Rate:              {fpr * 100:.1f}%")
    print(f"False Negative Rate:              {fnr * 100:.1f}%")
    print(f"Routing -> Standard Extractor:    {routing_counts['STANDARD']}")
    print(f"Routing -> Specialized Extractor: {routing_counts['SPECIALIZED']}")
    print(f"Quality Gate -> SAFE:             {gate_counts['SAFE']}")
    print(f"Quality Gate -> NEEDS_REVIEW:     {gate_counts['NEEDS_REVIEW']}")
    print(f"Quality Gate -> CORRUPTED:        {gate_counts['CORRUPTED']}")
    print(f"Avg Detection Latency:            {avg_det_time_ms} ms / page")
    print(f"Evaluation report saved to:       {output_path}\n")

    return full_report

if __name__ == "__main__":
    run_evaluation()
