import time
from pathlib import Path
from typing import List, Optional, Tuple, Dict, Any
from pydantic import BaseModel, Field

try:
    import pypdfium2 as pdfium
    from rapidocr_onnxruntime import RapidOCR
    HAS_OCR_DEPS = True
except ImportError:
    HAS_OCR_DEPS = False
    pdfium = None
    RapidOCR = None


class OCRLine(BaseModel):
    text: str
    confidence: float
    box: List[List[float]] = Field(default_factory=list)


class OCRPageResult(BaseModel):
    page_number: int
    text: str
    confidence: float
    line_count: int
    word_count: int
    char_count: int
    elapsed_seconds: float
    lines: List[OCRLine] = Field(default_factory=list)


class OCREngine:
    """
    Offline, deterministic OCR engine powered by RapidOCR (ONNX Runtime)
    and pypdfium2 for high-fidelity vector/raster PDF rendering.
    Runs entirely local, CPU-compatible, zero external cloud or daemon dependencies.
    """

    def __init__(self, render_scale: float = 2.0):
        if not HAS_OCR_DEPS:
            raise RuntimeError(
                "OCR dependencies are missing. Install pypdfium2 and rapidocr-onnxruntime."
            )
        self.render_scale = render_scale
        self._ocr = RapidOCR()

    def render_page_to_numpy(self, pdf_path: Path, page_index: int):
        doc = pdfium.PdfDocument(str(pdf_path))
        if page_index < 0 or page_index >= len(doc):
            raise IndexError(f"Page index {page_index} out of range for {pdf_path} (len={len(doc)})")
        page = doc[page_index]
        bitmap = page.render(scale=self.render_scale)
        return bitmap.to_numpy()

    def ocr_page(self, pdf_path: Path, page_number: int) -> OCRPageResult:
        """
        Runs OCR on a 1-indexed page of a PDF file.
        """
        start_time = time.time()
        page_index = page_number - 1
        img_np = self.render_page_to_numpy(pdf_path, page_index)

        ocr_res, _ = self._ocr(img_np)
        elapsed = time.time() - start_time

        if not ocr_res:
            return OCRPageResult(
                page_number=page_number,
                text="",
                confidence=0.0,
                line_count=0,
                word_count=0,
                char_count=0,
                elapsed_seconds=round(elapsed, 3),
                lines=[],
            )

        extracted_lines: List[OCRLine] = []
        conf_sum = 0.0
        text_parts: List[str] = []

        for item in ocr_res:
            # RapidOCR output item: [box, text, confidence]
            box, text, score = item
            box_coords = [[float(coord) for coord in pt] for pt in box]
            score_f = float(score)
            text_str = str(text).strip()
            if text_str:
                extracted_lines.append(OCRLine(text=text_str, confidence=score_f, box=box_coords))
                conf_sum += score_f
                text_parts.append(text_str)

        full_text = "\n".join(text_parts)
        avg_conf = (conf_sum / len(extracted_lines)) if extracted_lines else 0.0
        words = full_text.split()

        return OCRPageResult(
            page_number=page_number,
            text=full_text,
            confidence=round(avg_conf, 4),
            line_count=len(extracted_lines),
            word_count=len(words),
            char_count=len(full_text),
            elapsed_seconds=round(elapsed, 3),
            lines=extracted_lines,
        )

    def ocr_document_sample(
        self, pdf_path: Path, sample_pages: List[int]
    ) -> List[OCRPageResult]:
        """
        Runs OCR on a subset of pages.
        """
        results: List[OCRPageResult] = []
        for p in sample_pages:
            results.append(self.ocr_page(pdf_path, p))
        return results
