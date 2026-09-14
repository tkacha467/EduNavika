"""
Milestone 4.4: Targeted Mathematical Extractor
Implements hybrid quality-gated targeted mathematical extraction.
Only crops and runs specialized OCR on detected mathematical regions while
preserving fast baseline extraction on clean prose paragraphs.
"""

import time
import os
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
import numpy as np
import pypdfium2 as pdfium
import pymupdf

from backend.app.ingestion.math.base import MathExtractor
from backend.app.ingestion.math.quality_gate import MathQualityGate
from backend.app.ingestion.math.region_detector import MathRegionDetector, MathRegion
from backend.app.ingestion.math.normalizer import CanonicalLaTeXNormalizer
from backend.app.ingestion.ocr.ocr_engine import OCREngine, HAS_OCR_DEPS


class TargetedMathExtractor(MathExtractor):
    """
    Quality-gated targeted mathematical document extractor.
    """

    def __init__(
        self,
        render_scale: float = 2.0,
        min_region_confidence: float = 0.35,
        enable_ocr: bool = True
    ):
        self.render_scale = render_scale
        self.min_region_confidence = min_region_confidence
        self.enable_ocr = enable_ocr and HAS_OCR_DEPS
        self.quality_gate = MathQualityGate()
        self.region_detector = MathRegionDetector(min_confidence=min_region_confidence)
        self.normalizer = CanonicalLaTeXNormalizer()
        self._ocr_engine: Optional[OCREngine] = None

    @property
    def name(self) -> str:
        return "TargetedMathExtractor"

    def load_model(self) -> None:
        """Initialize OCR engine if enabled."""
        if self.enable_ocr and self._ocr_engine is None:
            self._ocr_engine = OCREngine(render_scale=self.render_scale)

    def extract_page_baseline_pypdfium2(self, pdf_path: str, page_num: int) -> str:
        """Extracts standard text using pypdfium2."""
        try:
            doc = pdfium.PdfDocument(pdf_path)
            if page_num < 1 or page_num > len(doc):
                return ""
            page = doc[page_num - 1]
            textpage = page.get_textpage()
            return textpage.get_text_bounded()
        except Exception as e:
            return f"Error: {e}"

    def extract_page(self, pdf_path: str, page_num: int) -> Dict[str, Any]:
        """
        Extract page with quality-gated targeted math recovery.
        
        Args:
            pdf_path: Path to the physical PDF document.
            page_num: 1-indexed page number.
            
        Returns:
            Dict containing:
            - 'text': Final enriched text (with canonical LaTeX in math regions)
            - 'baseline_text': Raw PyPDFium2 text
            - 'is_math_heavy': Boolean from MathQualityGate
            - 'needs_recovery': Boolean from MathQualityGate
            - 'recovered_formulas': List of metadata for each recovered region
            - 'regions_detected': Count of detected math regions
            - 'execution_time_seconds': Latency
            - 'success': Boolean
        """
        start_time = time.time()
        
        # Step 1: Fast PyPDFium2 baseline text extraction
        baseline_text = self.extract_page_baseline_pypdfium2(pdf_path, page_num)
        if not baseline_text:
            return {
                "text": "",
                "baseline_text": "",
                "is_math_heavy": False,
                "needs_recovery": False,
                "recovered_formulas": [],
                "regions_detected": 0,
                "execution_time_seconds": round(time.time() - start_time, 3),
                "success": False,
                "error": f"Failed to extract page {page_num}"
            }

        # Step 2: MathQualityGate evaluation
        gate_res = self.quality_gate.analyze(baseline_text)

        # If clean prose without math corruption, return fast baseline directly
        if not gate_res["needs_recovery"]:
            return {
                "text": baseline_text,
                "baseline_text": baseline_text,
                "is_math_heavy": gate_res["is_math_heavy"],
                "needs_recovery": False,
                "recovered_formulas": [],
                "regions_detected": 0,
                "execution_time_seconds": round(time.time() - start_time, 3),
                "success": True,
                "error": None
            }

        # Step 3: MathRegionDetector localizes math bounding boxes
        regions = self.region_detector.detect_regions(pdf_path, page_num)
        if not regions or not self.enable_ocr:
            # Fallback to normalized baseline text if no regions or OCR unavailable
            normalized_baseline = self.normalizer.normalize(baseline_text)
            return {
                "text": normalized_baseline,
                "baseline_text": baseline_text,
                "is_math_heavy": gate_res["is_math_heavy"],
                "needs_recovery": gate_res["needs_recovery"],
                "recovered_formulas": [],
                "regions_detected": len(regions),
                "execution_time_seconds": round(time.time() - start_time, 3),
                "success": True,
                "error": None
            }

        # Step 4: Crop ONLY the detected math regions and run targeted OCR
        self.load_model()
        doc = pymupdf.open(pdf_path)
        page = doc[page_num - 1]
        page_size_pts = (page.rect.width, page.rect.height)

        # Render full page image once to crop regions in-memory
        full_img = self._ocr_engine.render_page_to_numpy(Path(pdf_path), page_num - 1)

        recovered_formulas = []
        enriched_text = baseline_text

        for r in regions:
            crop_img = self.region_detector.crop_region_from_image(
                full_page_img=full_img,
                bbox=r.bbox,
                page_size_pts=page_size_pts
            )

            # Skip empty crops
            if crop_img.size == 0:
                continue

            # Run OCR specifically on this crop
            ocr_res, _ = self._ocr_engine._ocr(crop_img)
            if not ocr_res:
                continue

            raw_crop_lines = [str(item[1]).strip() for item in ocr_res if str(item[1]).strip()]
            raw_crop_text = " ".join(raw_crop_lines)

            # Convert to canonical LaTeX with math region context and spatial evidence
            has_stacked = getattr(r, "has_stacked_geometry", False)
            canonical_latex = self.normalizer.normalize(
                raw_crop_text,
                has_stacked_geometry=has_stacked,
                in_math_region=True
            )

            recovered_item = {
                "region_id": r.region_id,
                "bbox": [round(c, 2) for c in r.bbox],
                "confidence": r.confidence,
                "raw_ocr": raw_crop_text,
                "canonical_latex": canonical_latex,
                "is_display_math": r.is_display_math,
                "has_stacked_geometry": has_stacked,
                "localization_status": "LOCALIZED",
                "extraction_method": "targeted_crop_rapidocr"
            }
            recovered_formulas.append(recovered_item)

            # Integrate into text: append or merge canonical LaTeX into text context
            if canonical_latex and canonical_latex not in enriched_text:
                enriched_text += f"\n[FORMULA_RECOVERED: {canonical_latex}]\n"

        total_elapsed = round(time.time() - start_time, 3)

        return {
            "text": enriched_text,
            "baseline_text": baseline_text,
            "is_math_heavy": True,
            "needs_recovery": True,
            "recovered_formulas": recovered_formulas,
            "regions_detected": len(regions),
            "execution_time_seconds": total_elapsed,
            "success": True,
            "error": None
        }
