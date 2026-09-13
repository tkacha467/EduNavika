import pytest
from pathlib import Path
from backend.app.ingestion.ocr.ocr_benchmark import (
    compute_levenshtein,
    calculate_cer,
    calculate_wer,
    OCRBenchmark,
)
from backend.app.ingestion.ocr.ocr_engine import OCREngine, HAS_OCR_DEPS


def test_levenshtein_distance():
    assert compute_levenshtein("kitten", "sitting") == 3
    assert compute_levenshtein("", "abc") == 3
    assert compute_levenshtein("same", "same") == 0


def test_cer_and_wer_metrics():
    ref = "The quick brown fox jumps over the lazy dog"
    hyp = "The quick brown fox jumps over the lazy dog"
    assert calculate_cer(ref, hyp) == 0.0
    assert calculate_wer(ref, hyp) == 0.0

    # 1 char substitution
    hyp_sub = "The quick brown fox jumps over the lazy fog"
    cer = calculate_cer(ref, hyp_sub)
    assert 0.0 < cer < 0.1
    wer = calculate_wer(ref, hyp_sub)
    assert 0.0 < wer < 0.2


def test_ocr_engine_initialization():
    assert HAS_OCR_DEPS is True
    engine = OCREngine()
    assert engine._ocr is not None


def test_ocr_benchmark_runner_structure():
    benchmark = OCRBenchmark()
    assert len(benchmark.BENCHMARK_SUITE) >= 3
