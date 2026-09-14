"""
Milestone 4.4: Mathematical Region Detector
Identifies and localizes mathematical equation regions on physical PDF pages
using PDF layout and token analysis prior to rendering/cropping.
"""

from typing import List, Dict, Any, Tuple, Optional
from pathlib import Path
import re
import pymupdf
import numpy as np


class MathRegion:
    def __init__(
        self,
        region_id: str,
        page_number: int,
        bbox: Tuple[float, float, float, float],
        confidence: float,
        raw_text: str,
        is_display_math: bool = False,
        signals: Optional[List[str]] = None,
        has_stacked_geometry: bool = False
    ):
        self.region_id = region_id
        self.page_number = page_number
        self.bbox = bbox  # (x0, y0, x1, y1) in points
        self.confidence = confidence
        self.raw_text = raw_text
        self.is_display_math = is_display_math
        self.signals = signals or []
        self.has_stacked_geometry = has_stacked_geometry

    def to_dict(self) -> Dict[str, Any]:
        return {
            "region_id": self.region_id,
            "page_number": self.page_number,
            "bbox": [round(c, 2) for c in self.bbox],
            "confidence": round(self.confidence, 3),
            "raw_text": self.raw_text,
            "is_display_math": self.is_display_math,
            "signals": self.signals,
            "has_stacked_geometry": self.has_stacked_geometry
        }


class MathRegionDetector:
    """
    Detects bounding boxes of mathematical expressions on PDF pages.
    """

    MATH_CHARS = set("=+-*/^<≤>≥≠±×÷√∑∏∫∂∇∼⊥∠°²³⁴₁₂₃")
    GREEK_CHARS = set("αβγδεζηθικλμνξπρστυφχψωΔΣΩ")

    def __init__(self, min_confidence: float = 0.35, padding: float = 6.0):
        self.min_confidence = min_confidence
        self.padding = padding

    def detect_regions(self, pdf_path: str, page_number: int, max_regions: int = 4) -> List[MathRegion]:
        """
        Scan a 1-indexed page in pdf_path and return detected mathematical regions.
        """
        doc = pymupdf.open(pdf_path)
        if page_number < 1 or page_number > len(doc):
            return []

        page = doc[page_number - 1]
        page_rect = page.rect
        page_width = page_rect.width
        page_height = page_rect.height

        blocks = page.get_text("blocks")
        candidate_boxes = []

        for b in blocks:
            x0, y0, x1, y1, text, block_no, block_type = b
            if block_type != 0:  # 0 is text block, 1 is image block
                continue

            text_clean = text.strip()
            if not text_clean or len(text_clean) < 3:
                continue

            # Must contain at least one alphanumeric character
            if not re.search(r'[a-zA-Z0-9]', text_clean):
                continue

            score = 0.0
            signals = []

            # 1. Check mathematical symbol presence
            math_symbols = sum(1 for c in text_clean if c in self.MATH_CHARS or c in self.GREEK_CHARS)
            has_equality = ("=" in text_clean or "→" in text_clean or "\\rightarrow" in text_clean)
            has_trig = bool(re.search(r'\b(sin|cos|tan|cot|sec|csc|log|lim)\b', text_clean, re.I))
            has_rad_pow = any(c in text_clean for c in ['√', '²', '³', '^', '_'])

            if math_symbols > 0:
                score += min(0.15 * math_symbols, 0.45)
                signals.append(f"math_symbols_{math_symbols}")

            if has_equality:
                score += 0.30
                signals.append("equality_relation")

            if has_trig:
                score += 0.30
                signals.append("trig_or_function")

            if has_rad_pow:
                score += 0.30
                signals.append("radical_or_power")

            # Centered display equations
            block_height = y1 - y0
            is_centered = (x0 > page_width * 0.15) and (x1 < page_width * 0.88)
            is_single_or_double_line = block_height < 70.0
            is_display_math = is_centered and is_single_or_double_line and (has_equality or has_rad_pow or has_trig)

            if is_display_math:
                score += 0.20
                signals.append("display_math_layout")

            # Filter out pure prose with high word count and no equation structures
            words = text_clean.split()
            if len(words) > 25 and not has_equality and not has_trig and not has_rad_pow:
                score = 0.0

            if score >= self.min_confidence:
                candidate_boxes.append({
                    "bbox": [x0, y0, x1, y1],
                    "score": min(score, 1.0),
                    "text": text_clean,
                    "is_display": is_display_math,
                    "signals": signals,
                    "has_stacked_geometry": False
                })

        if not candidate_boxes:
            return []

        # Merge vertically adjacent bounding boxes (e.g. numerator and denominator fractions)
        candidate_boxes.sort(key=lambda b: b["bbox"][1])  # sort by y0
        merged_boxes = []
        for box in candidate_boxes:
            if not merged_boxes:
                merged_boxes.append(box)
                continue
            prev = merged_boxes[-1]
            # If vertical gap < 15 points and horizontal overlap
            y_gap = box["bbox"][1] - prev["bbox"][3]
            x_overlap = min(prev["bbox"][2], box["bbox"][2]) - max(prev["bbox"][0], box["bbox"][0])
            if 0 <= y_gap <= 15.0 and x_overlap > 30.0:
                # Merge into previous box
                prev["bbox"][0] = min(prev["bbox"][0], box["bbox"][0])
                prev["bbox"][1] = min(prev["bbox"][1], box["bbox"][1])
                prev["bbox"][2] = max(prev["bbox"][2], box["bbox"][2])
                prev["bbox"][3] = max(prev["bbox"][3], box["bbox"][3])
                prev["text"] += " " + box["text"]
                prev["score"] = max(prev["score"], box["score"])
                prev["signals"].extend(box["signals"])
                prev["signals"].append("stacked_fraction_geometry")
                prev["has_stacked_geometry"] = True
            else:
                merged_boxes.append(box)

        # Sort by score descending and cap at max_regions
        merged_boxes.sort(key=lambda b: b["score"], reverse=True)
        merged_boxes = merged_boxes[:max_regions]

        detected: List[MathRegion] = []
        for idx, b in enumerate(merged_boxes, 1):
            x0, y0, x1, y1 = b["bbox"]
            padded_x0 = max(0.0, x0 - self.padding)
            padded_y0 = max(0.0, y0 - self.padding)
            padded_x1 = min(page_width, x1 + self.padding)
            padded_y1 = min(page_height, y1 + self.padding)

            region = MathRegion(
                region_id=f"p{page_number}_r{idx}",
                page_number=page_number,
                bbox=(padded_x0, padded_y0, padded_x1, padded_y1),
                confidence=b["score"],
                raw_text=b["text"],
                is_display_math=b["is_display"],
                signals=b["signals"],
                has_stacked_geometry=b.get("has_stacked_geometry", False)
            )
            detected.append(region)

        return detected

    @staticmethod
    def crop_region_from_image(
        full_page_img: np.ndarray,
        bbox: Tuple[float, float, float, float],
        page_size_pts: Tuple[float, float]
    ) -> np.ndarray:
        """
        Crop the region bounding box from a rendered page numpy image.
        Converts PDF points coordinates to image pixel coordinates.
        """
        img_h, img_w = full_page_img.shape[:2]
        pdf_w, pdf_h = page_size_pts

        scale_x = img_w / pdf_w
        scale_y = img_h / pdf_h

        px0 = max(0, int(bbox[0] * scale_x))
        py0 = max(0, int(bbox[1] * scale_y))
        px1 = min(img_w, int(bbox[2] * scale_x))
        py1 = min(img_h, int(bbox[3] * scale_y))

        # Ensure non-empty slice
        if px1 <= px0:
            px1 = min(img_w, px0 + 10)
        if py1 <= py0:
            py1 = min(img_h, py0 + 10)

        return full_page_img[py0:py1, px0:px1]
