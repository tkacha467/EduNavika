import pytest
from pathlib import Path
from backend.app.ingestion.quality import PageQualityAnalyzer
from backend.app.ingestion.cleaner import DeterministicCleaner
from backend.app.ingestion.schemas import ExtractedPage, PageQualityStatus


def test_quality_analyzer_classification():
    analyzer = PageQualityAnalyzer()

    # Empty page
    res_empty = analyzer.analyze("")
    assert res_empty["quality_status"] == PageQualityStatus.EMPTY
    assert res_empty["character_count"] == 0

    # Extremely low char count (needs OCR / scan watermark)
    res_ocr = analyzer.analyze("Page 1")
    assert res_ocr["quality_status"] == PageQualityStatus.NEEDS_OCR

    # Normal extracted text
    sample_text = (
        "Chemical reactions involve the breaking and making of bonds between atoms "
        "to produce new substances. As you have observed, chemical reactions take place "
        "with changes in state, color, or evolution of gas and change in temperature."
    )
    res_extracted = analyzer.analyze(sample_text)
    assert res_extracted["quality_status"] == PageQualityStatus.EXTRACTED
    assert res_extracted["alphabetic_ratio"] > 0.6
    assert res_extracted["word_count"] > 20


def test_deterministic_cleaner_transformations():
    cleaner = DeterministicCleaner()

    # 1. Hyphenated word repair: "reac-\ntion" -> "reaction"
    dirty_text = "A chemical reac-\ntion occurs when bonds break."
    cleaned, header, footer = cleaner.clean_text(dirty_text)
    assert "reaction" in cleaned
    assert "reac-\ntion" not in cleaned

    # 2. Font glyph decoding: /G83/G111 -> So
    glyph_text = "/G83/G111/G108/G117/G116/G105/G111/G110 : This is step 1."
    cleaned_glyph, _, _ = cleaner.clean_text(glyph_text)
    assert "Solution" in cleaned_glyph

    # 3. Header and footer suppression
    header_footer_text = "SCIENCE\n\nChapter content here.\n\n42"
    cleaned_hf, h, f = cleaner.clean_text(header_footer_text)
    assert h == "SCIENCE"
    assert f == "42"
    assert "Chapter content here." in cleaned_hf
