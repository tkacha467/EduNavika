import os
import time
import re
from typing import Dict, Any, Optional
from pathlib import Path

import pypdf
import pypdfium2

from backend.app.ingestion.math.base import MathExtractor


class PyPDFium2Extractor(MathExtractor):
    """
    Current EduNavika production baseline extractor using pypdfium2.
    Fast, deterministic, layout-bounded text extraction.
    """
    @property
    def name(self) -> str:
        return "PyPDFium2Extractor"

    def load_model(self) -> None:
        self._engine = pypdfium2

    def extract_page(self, pdf_path: str, page_num: int) -> Dict[str, Any]:
        start = time.time()
        try:
            if not os.path.exists(pdf_path):
                return {
                    "text": "",
                    "execution_time_seconds": time.time() - start,
                    "success": False,
                    "error": f"PDF not found: {pdf_path}"
                }
            pdf = self._engine.PdfDocument(pdf_path)
            if page_num < 1 or page_num > len(pdf):
                return {
                    "text": "",
                    "execution_time_seconds": time.time() - start,
                    "success": False,
                    "error": f"Page {page_num} out of bounds"
                }
            page = pdf[page_num - 1]
            text = page.get_textpage().get_text_bounded()
            return {
                "text": text,
                "execution_time_seconds": round(time.time() - start, 4),
                "success": True,
                "error": None
            }
        except Exception as e:
            return {
                "text": "",
                "execution_time_seconds": round(time.time() - start, 4),
                "success": False,
                "error": str(e)
            }


class PyPDFExtractor(MathExtractor):
    """
    Standard pure-Python PDF reader baseline using pypdf.
    Evaluates whether pypdf character grouping differs from PDFium.
    """
    @property
    def name(self) -> str:
        return "PyPDFExtractor"

    def load_model(self) -> None:
        pass

    def extract_page(self, pdf_path: str, page_num: int) -> Dict[str, Any]:
        start = time.time()
        try:
            if not os.path.exists(pdf_path):
                return {
                    "text": "",
                    "execution_time_seconds": time.time() - start,
                    "success": False,
                    "error": f"PDF not found: {pdf_path}"
                }
            reader = pypdf.PdfReader(pdf_path)
            if page_num < 1 or page_num > len(reader.pages):
                return {
                    "text": "",
                    "execution_time_seconds": time.time() - start,
                    "success": False,
                    "error": f"Page {page_num} out of bounds"
                }
            page = reader.pages[page_num - 1]
            text = page.extract_text() or ""
            return {
                "text": text,
                "execution_time_seconds": round(time.time() - start, 4),
                "success": True,
                "error": None
            }
        except Exception as e:
            return {
                "text": "",
                "execution_time_seconds": round(time.time() - start, 4),
                "success": False,
                "error": str(e)
            }


class RapidOCRExtractor(MathExtractor):
    """
    Visual OCR extractor using RapidOCR (ONNX Runtime engine)
    over pages rendered at 150 DPI via pypdfium2.
    Evaluates whether general-purpose computer vision OCR captures
    mathematical glyphs and layout.
    """
    def __init__(self, render_scale: float = 1.5):
        self.render_scale = render_scale
        self._ocr = None

    @property
    def name(self) -> str:
        return "RapidOCRExtractor"

    def load_model(self) -> None:
        if self._ocr is None:
            from rapidocr_onnxruntime import RapidOCR
            self._ocr = RapidOCR()

    def extract_page(self, pdf_path: str, page_num: int) -> Dict[str, Any]:
        start = time.time()
        try:
            if self._ocr is None:
                self.load_model()

            if not os.path.exists(pdf_path):
                return {
                    "text": "",
                    "execution_time_seconds": time.time() - start,
                    "success": False,
                    "error": f"PDF not found: {pdf_path}"
                }

            pdf = pypdfium2.PdfDocument(pdf_path)
            if page_num < 1 or page_num > len(pdf):
                return {
                    "text": "",
                    "execution_time_seconds": time.time() - start,
                    "success": False,
                    "error": f"Page {page_num} out of bounds"
                }

            page = pdf[page_num - 1]
            pil_image = page.render(scale=self.render_scale).to_pil()
            ocr_res, _ = self._ocr(pil_image)

            extracted_lines = []
            if ocr_res:
                for item in ocr_res:
                    # item format: [bounding_box, text, confidence]
                    extracted_lines.append(item[1])

            text = "\n".join(extracted_lines)
            return {
                "text": text,
                "execution_time_seconds": round(time.time() - start, 4),
                "success": True,
                "error": None
            }
        except Exception as e:
            return {
                "text": "",
                "execution_time_seconds": round(time.time() - start, 4),
                "success": False,
                "error": str(e)
            }


class HeuristicMathExtractor(MathExtractor):
    """
    Deterministic domain post-processor adapter over PyPDFium2 extraction.
    Applies mathematical elevation heuristics:
    1. Reconstructs caret exponents from de-elevated variable-digit pairs (e.g. x2 -> x^2, r2 -> r^2).
    2. Reconstructs subscript indices for coordinate pairs (e.g. x1, y1 -> x_1, y_1).
    3. Normalizes common division slash expressions.
    4. Cleans Unicode symbols to standard LaTeX representation where deterministic.
    """
    def __init__(self, base_extractor: Optional[MathExtractor] = None):
        self.base_extractor = base_extractor or PyPDFium2Extractor()

    @property
    def name(self) -> str:
        return "HeuristicMathExtractor"

    def load_model(self) -> None:
        self.base_extractor.load_model()

    def extract_page(self, pdf_path: str, page_num: int) -> Dict[str, Any]:
        start = time.time()
        base_res = self.base_extractor.extract_page(pdf_path, page_num)
        if not base_res.get("success"):
            return base_res

        raw_text = base_res.get("text", "")
        processed = self._apply_math_heuristics(raw_text)
        return {
            "text": processed,
            "raw_text": raw_text,
            "execution_time_seconds": round(time.time() - start, 4),
            "success": True,
            "error": None
        }

    def clean_math_text(self, text: str) -> str:
        """Public interface for heuristic math cleaning."""
        return self._apply_math_heuristics(text)

    def _apply_math_heuristics(self, text: str) -> str:
        if not text:
            return ""

        # 1. Coordinate index reconstruction: P(x1, y1) -> P(x_1, y_1)
        res = re.sub(r'\b([xyabmn])([1234])\b', r'\1_\2', text)

        # 2. Exponent elevation for known variable powers (e.g. x2 -> x^2, r2 -> r^2)
        # Protect natural prose (e.g. 'in a 2 hour period'): restrict 'a' elevation to algebraic operator contexts
        res = re.sub(r'(?:^|(?<=[\(\+\-\*\/\=\s]))([xyr])\s*([23])\b', r'\1^\2', res)
        res = re.sub(r'(?<=[\(\+\-\*\/\=])([abc])\s*([23])\b', r'\1^\2', res)
        res = re.sub(r'\b([xyr])([23])\b', r'\1^\2', res)

        # 3. Unicode superscript normalization: x² -> x^2, r² -> r^2
        res = res.replace("²", "^2").replace("³", "^3").replace("¹", "^1")

        # 4. Unicode subscript normalization: x₁ -> x_1, y₂ -> y_2
        subscript_map = {
            "₀": "_0", "₁": "_1", "₂": "_2", "₃": "_3", "₄": "_4",
            "₅": "_5", "₆": "_6", "₇": "_7", "₈": "_8", "₉": "_9"
        }
        for sub_char, sub_rep in subscript_map.items():
            res = res.replace(sub_char, sub_rep)

        # 5. Radical normalization: if square root symbol is present without LaTeX tag
        res = res.replace("√", "\\sqrt")

        # 6. Multiplication and plus-minus signs
        res = res.replace("±", "\\pm").replace("×", "\\times").replace("÷", "\\div")

        # 7. Degree symbol
        res = res.replace("°", "^\\circ")

        # 8. Greek letters to LaTeX
        greek_map = {
            "π": "\\pi", "θ": "\\theta", "α": "\\alpha", "β": "\\beta", "γ": "\\gamma"
        }
        for g_char, g_latex in greek_map.items():
            res = res.replace(g_char, g_latex)

        return res
