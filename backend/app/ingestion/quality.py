import re
from typing import Dict, Any
from backend.app.ingestion.schemas import PageQualityStatus


class PageQualityAnalyzer:
    """
    Evaluates raw extracted text quality conservatively.
    Calculates character count, word count, alphabetic ratio, whitespace ratio,
    and flags low-quality or image-only scanned pages (NEEDS_OCR) without invoking heavy OCR.
    """

    def __init__(
        self,
        min_char_count: int = 40,
        min_word_count: int = 8,
        min_alphabetic_ratio: float = 0.45,
        max_whitespace_ratio: float = 0.85,
    ):
        self.min_char_count = min_char_count
        self.min_word_count = min_word_count
        self.min_alphabetic_ratio = min_alphabetic_ratio
        self.max_whitespace_ratio = max_whitespace_ratio

    def analyze(self, raw_text: str) -> Dict[str, Any]:
        if not raw_text or not raw_text.strip():
            return {
                "character_count": 0,
                "word_count": 0,
                "alphabetic_ratio": 0.0,
                "whitespace_ratio": 0.0,
                "quality_status": PageQualityStatus.EMPTY,
            }

        total_chars = len(raw_text)
        alpha_chars = sum(1 for c in raw_text if c.isalpha())
        whitespace_chars = sum(1 for c in raw_text if c.isspace())

        # Extract distinct words
        words = re.findall(r"\b\w+\b", raw_text)
        word_count = len(words)

        alphabetic_ratio = round(alpha_chars / total_chars, 4) if total_chars > 0 else 0.0
        whitespace_ratio = round(whitespace_chars / total_chars, 4) if total_chars > 0 else 0.0

        # Classification logic
        if total_chars < self.min_char_count or word_count < self.min_word_count:
            # If text is extremely tiny (e.g. only page number, artifact, or image watermark)
            # classify as NEEDS_OCR if < 15 chars, or LOW_QUALITY
            if total_chars < 20:
                quality_status = PageQualityStatus.NEEDS_OCR
            else:
                quality_status = PageQualityStatus.LOW_QUALITY
        elif alphabetic_ratio < self.min_alphabetic_ratio:
            # Low alphabetic ratio could indicate scanned gibberish, dense formula-only page, or broken font encoding
            quality_status = PageQualityStatus.LOW_QUALITY
        elif whitespace_ratio > self.max_whitespace_ratio:
            quality_status = PageQualityStatus.LOW_QUALITY
        else:
            quality_status = PageQualityStatus.EXTRACTED

        return {
            "character_count": total_chars,
            "word_count": word_count,
            "alphabetic_ratio": alphabetic_ratio,
            "whitespace_ratio": whitespace_ratio,
            "quality_status": quality_status,
        }
