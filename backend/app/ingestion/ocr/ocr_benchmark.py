import json
import time
from pathlib import Path
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

from backend.app.ingestion.ocr.ocr_engine import OCREngine, OCRPageResult


class GroundTruthSnippet(BaseModel):
    document: str
    page_number: int
    ground_truth: str


class BookBenchmarkResult(BaseModel):
    filename: str
    relative_path: str
    standard: int
    subject: str
    pages_tested: List[int]
    total_lines: int
    total_words: int
    total_chars: int
    avg_confidence: float
    total_elapsed_sec: float
    sec_per_page: float
    pages_per_minute: float
    sample_text: str
    cer: Optional[float] = None
    wer: Optional[float] = None
    quality_gate_passed: bool


class OCRBenchmarkReport(BaseModel):
    engine_name: str = "RapidOCR (ONNXRuntime-CPU) + pypdfium2"
    timestamp: str
    total_books_tested: int
    total_pages_tested: int
    overall_sec_per_page: float
    overall_avg_confidence: float
    overall_cer: Optional[float] = None
    overall_wer: Optional[float] = None
    quality_gate_status: str  # PASS, CONDITIONAL_PASS, FAIL
    results: List[BookBenchmarkResult]


def compute_levenshtein(s1: str, s2: str) -> int:
    """Standard Levenshtein distance."""
    if len(s1) < len(s2):
        return compute_levenshtein(s2, s1)
    if len(s2) == 0:
        return len(s1)

    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row

    return previous_row[-1]


def calculate_cer(reference: str, hypothesis: str) -> float:
    """Character Error Rate: Levenshtein(ref, hyp) / len(ref)"""
    ref = reference.strip()
    hyp = hypothesis.strip()
    if not ref:
        return 0.0 if not hyp else 1.0
    dist = compute_levenshtein(ref, hyp)
    return min(1.0, dist / len(ref))


def calculate_wer(reference: str, hypothesis: str) -> float:
    """Word Error Rate: Levenshtein on word tokens."""
    ref_words = reference.strip().split()
    hyp_words = hypothesis.strip().split()
    if not ref_words:
        return 0.0 if not hyp_words else 1.0
    
    # Map words to unique characters for token-level levenshtein
    word2char: Dict[str, str] = {}
    char_code = 1000

    def encode(words: List[str]) -> str:
        nonlocal char_code
        chars = []
        for w in words:
            w_lower = w.lower()
            if w_lower not in word2char:
                word2char[w_lower] = chr(char_code)
                char_code += 1
            chars.append(word2char[w_lower])
        return "".join(chars)

    s1 = encode(ref_words)
    s2 = encode(hyp_words)
    dist = compute_levenshtein(s1, s2)
    return min(1.0, dist / len(ref_words))


class OCRBenchmark:
    """
    Executes Phase 3: Offline OCR Benchmark across representative scanned GSEB textbooks.
    Evaluates throughput, confidence, CER, and WER against ground-truth snippets.
    """

    BENCHMARK_SUITE = [
        {
            "relative_path": "STD-10th/Std-10_Social_Science_EnglishMedium.pdf",
            "standard": 10,
            "subject": "Social Science",
            "pages": [15],
            "gt_snippet": "Saurashtra regions of Gujarat. The traditional art of embroidery, sakhtorans, chakda"
        },
        {
            "relative_path": "STD-10th/Std-10_ComputerStudies_EnglishMedium.pdf",
            "standard": 10,
            "subject": "Computer Studies",
            "pages": [15],
            "gt_snippet": "Elements Description The content is displayed one font size smaller"
        },
        {
            "relative_path": "STD-9th/Std-9 Sanskrit E.M.pdf",
            "standard": 9,
            "subject": "Sanskrit",
            "pages": [10],
            "gt_snippet": "Samgachhadhvam samvadadhvam"
        },
        {
            "relative_path": "STD-11th/Std-11_Hornbill_EnglishMedium.pdf",
            "standard": 11,
            "subject": "Hornbill English",
            "pages": [12],
            "gt_snippet": "The Portrait of a Lady by Khushwant Singh"
        }
    ]

    def __init__(
        self,
        dataset_dir: Path = Path("GSEB-Dataset"),
        output_dir: Path = Path("data/processed/reports"),
        render_scale: float = 1.5
    ):
        self.dataset_dir = Path(dataset_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.engine = OCREngine(render_scale=render_scale)

    def run_benchmark(self) -> OCRBenchmarkReport:
        results: List[BookBenchmarkResult] = []
        total_pages = 0
        total_time = 0.0
        conf_sum = 0.0
        cer_sum = 0.0
        wer_sum = 0.0
        measured_items = 0

        for item in self.BENCHMARK_SUITE:
            pdf_path = self.dataset_dir / item["relative_path"]
            if not pdf_path.exists():
                continue

            tested_pages = item["pages"]
            page_results = self.engine.ocr_document_sample(pdf_path, tested_pages)

            book_words = sum(p.word_count for p in page_results)
            book_chars = sum(p.char_count for p in page_results)
            book_lines = sum(p.line_count for p in page_results)
            book_time = sum(p.elapsed_seconds for p in page_results)
            book_conf = (
                sum(p.confidence for p in page_results) / len(page_results)
                if page_results
                else 0.0
            )

            p_count = len(page_results)
            sec_per_page = (book_time / p_count) if p_count > 0 else 0.0
            ppm = (60.0 / sec_per_page) if sec_per_page > 0 else 0.0

            combined_text = "\n\n".join(p.text for p in page_results)
            sample_preview = combined_text[:300].replace("\n", " ")

            # Error rate computation against gt_snippet if present
            gt = item.get("gt_snippet", "")
            cer, wer = None, None
            if gt:
                # Find best matching window in combined text
                # We normalize and evaluate error rate on ground truth
                # Look for matching line or sub-phrase
                words_gt = gt.split()
                # Simple extraction of best slice
                slice_len = len(gt) + 20
                best_sub = ""
                min_dist = 99999
                # Scan slices
                step = 10
                for start in range(0, max(1, len(combined_text) - len(gt)), step):
                    candidate = combined_text[start : start + slice_len]
                    d = compute_levenshtein(gt, candidate[:len(gt)])
                    if d < min_dist:
                        min_dist = d
                        best_sub = candidate[:len(gt)]

                if best_sub:
                    cer = calculate_cer(gt, best_sub)
                    wer = calculate_wer(gt, best_sub)
                    cer_sum += cer
                    wer_sum += wer
                    measured_items += 1

            passed = (book_conf >= 0.70) and (sec_per_page <= 30.0) and (book_lines > 10)

            results.append(
                BookBenchmarkResult(
                    filename=pdf_path.name,
                    relative_path=item["relative_path"],
                    standard=item["standard"],
                    subject=item["subject"],
                    pages_tested=tested_pages,
                    total_lines=book_lines,
                    total_words=book_words,
                    total_chars=book_chars,
                    avg_confidence=round(book_conf, 4),
                    total_elapsed_sec=round(book_time, 2),
                    sec_per_page=round(sec_per_page, 2),
                    pages_per_minute=round(ppm, 1),
                    sample_text=sample_preview,
                    cer=round(cer, 4) if cer is not None else None,
                    wer=round(wer, 4) if wer is not None else None,
                    quality_gate_passed=passed,
                )
            )

            total_pages += p_count
            total_time += book_time
            conf_sum += book_conf

        overall_sec_per_page = (total_time / total_pages) if total_pages > 0 else 0.0
        overall_conf = (conf_sum / len(results)) if results else 0.0
        overall_cer = (cer_sum / measured_items) if measured_items > 0 else None
        overall_wer = (wer_sum / measured_items) if measured_items > 0 else None

        # Quality Gate decision: PASS / CONDITIONAL_PASS / FAIL
        all_passed = all(r.quality_gate_passed for r in results)
        if all_passed and overall_conf >= 0.80:
            status = "PASS"
        elif overall_conf >= 0.70:
            status = "CONDITIONAL_PASS"
        else:
            status = "FAIL"

        report = OCRBenchmarkReport(
            timestamp=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            total_books_tested=len(results),
            total_pages_tested=total_pages,
            overall_sec_per_page=round(overall_sec_per_page, 2),
            overall_avg_confidence=round(overall_conf, 4),
            overall_cer=round(overall_cer, 4) if overall_cer is not None else None,
            overall_wer=round(overall_wer, 4) if overall_wer is not None else None,
            quality_gate_status=status,
            results=results,
        )

        self._export_reports(report)
        return report

    def _export_reports(self, report: OCRBenchmarkReport):
        json_path = self.output_dir / "ocr_benchmark_report.json"
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(report.model_dump(), f, indent=2)

        md_path = self.output_dir / "ocr_benchmark_report.md"
        with open(md_path, "w", encoding="utf-8") as f:
            f.write("# GSEB Textbook OCR Benchmark Report\n\n")
            f.write(f"- **Engine**: `{report.engine_name}`\n")
            f.write(f"- **Timestamp**: `{report.timestamp}`\n")
            f.write(f"- **Quality Gate Verdict**: **`{report.quality_gate_status}`**\n")
            f.write(f"- **Books Tested**: {report.total_books_tested}\n")
            f.write(f"- **Total Pages Tested**: {report.total_pages_tested}\n")
            f.write(f"- **Overall Speed**: {report.overall_sec_per_page} sec/page\n")
            f.write(f"- **Overall Average Confidence**: {report.overall_avg_confidence * 100:.1f}%\n")
            if report.overall_cer is not None:
                f.write(f"- **Overall CER**: {report.overall_cer * 100:.2f}%\n")
            if report.overall_wer is not None:
                f.write(f"- **Overall WER**: {report.overall_wer * 100:.2f}%\n")
            f.write("\n---\n\n")

            f.write("## Benchmark Results by Textbook\n\n")
            f.write("| Standard | Subject | File | Pages Tested | Lines | Words | Avg Conf | Sec/Page | Gate |\n")
            f.write("|----------|---------|------|--------------|-------|-------|----------|----------|------|\n")
            for r in report.results:
                gate_str = "✅ PASS" if r.quality_gate_passed else "❌ FAIL"
                f.write(
                    f"| Std {r.standard} | {r.subject} | `{r.filename}` | {r.pages_tested} | "
                    f"{r.total_lines} | {r.total_words} | {r.avg_confidence * 100:.1f}% | {r.sec_per_page}s | {gate_str} |\n"
                )
            f.write("\n---\n\n")
            f.write("## Sample Extracted Previews\n\n")
            for r in report.results:
                f.write(f"### {r.subject} (Std {r.standard})\n")
                f.write(f"> *Preview:* {r.sample_text[:200]}...\n\n")
