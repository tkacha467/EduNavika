"""
Vector Diagram Extractor for Competitive Examination Ingestion (Milestone 5.7).

Extracts, isolates, rasterizes, and verifies vector diagrams and graphical answer
options from authoritative examination PDFs (such as NEET UG 2021 Booklet M4)
using vector path geometry (PyMuPDF / fitz).

Features:
- Source validation with SHA-256 integrity verification.
- Two-column layout detection and column divider filtering.
- Text-anchor-based question boundary identification.
- Midpoint-based non-overlapping option bounding box calculation.
- Lossless PNG rasterization with configurable scale matrix and padding.
- Collision-resistant, deterministic asset naming convention.
- Machine-readable JSON manifest generation with asset SHA-256 and PENDING_HUMAN_REVIEW status.
- Zero database mutations (completely decoupled from persistent database).
"""

from __future__ import annotations

import os
import re
import hashlib
import json
from dataclasses import dataclass, asdict, field
from typing import List, Dict, Optional, Tuple, Any
import pymupdf


# ==============================================================================
# Custom Exceptions
# ==============================================================================

class VectorExtractionError(Exception):
    """Base exception for vector extraction operations."""
    pass


class PDFSourceError(VectorExtractionError):
    """Raised when PDF file is missing, unreadable, or fails checksum validation."""
    pass


class BoundingBoxError(VectorExtractionError):
    """Raised when diagram bounding box cannot be reliably identified or is degenerate."""
    pass


class AssetIntegrityError(VectorExtractionError):
    """Raised when output asset generation, writing, or verification fails."""
    pass


class ManifestError(VectorExtractionError):
    """Raised when manifest generation or serialization fails."""
    pass


# ==============================================================================
# Configuration and Record Models
# ==============================================================================

@dataclass
class QuestionTargetConfig:
    """Configuration targeting a specific question for visual asset extraction."""
    question_number: int
    page_index: int  # 0-based index
    page_number: int  # 1-based human-readable page number
    column: int  # 0 for left column, 1 for right column
    mode: str  # 'stem', 'options', or 'stem_and_options'
    description: Optional[str] = None


@dataclass
class DiagramAssetRecord:
    """Metadata record for an extracted visual diagram asset."""
    asset_id: str
    exam_code: str
    exam_year: int
    paper_code: str
    question_number: int
    asset_role: str  # 'stem' or 'option'
    option_label: Optional[str] = None  # e.g., '(1)', '(2)', '(3)', '(4)'
    option_key: Optional[str] = None  # e.g., 'A', 'B', 'C', 'D'
    source_pdf_identifier: str = ""
    source_pdf_sha256: str = ""
    source_page_index: int = 0
    source_page_number: int = 1
    original_bbox: List[float] = field(default_factory=list)  # [x0, y0, x1, y1] in PDF pt
    padded_bbox: List[float] = field(default_factory=list)  # [x0, y0, x1, y1] in PDF pt
    padding_pts: float = 4.0
    render_scale: float = 2.0
    effective_dpi: int = 144
    output_relative_path: str = ""
    output_dimensions: List[int] = field(default_factory=list)  # [width_px, height_px]
    file_size_bytes: int = 0
    output_sha256: str = ""
    extraction_method: str = "pymupdf_vector_geometry_v1"
    extraction_status: str = "EXTRACTED"  # 'EXTRACTED' or 'FAILED'
    human_review_status: str = "PENDING_HUMAN_REVIEW"
    review_notes: str = ""
    failure_reason: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert record to JSON-serializable dictionary."""
        return asdict(self)


# ==============================================================================
# Default Target Configurations for NEET 2021 Booklet M4
# ==============================================================================

NEET_2021_M4_CONFIGS: List[QuestionTargetConfig] = [
    # Category A: 4 Stem diagrams
    QuestionTargetConfig(4,  1, 2,  0, "stem", "Capacitor network bridge"),
    QuestionTargetConfig(20, 3, 4,  1, "stem", "LCR series AC circuit with meters"),
    QuestionTargetConfig(40, 6, 7,  1, "stem", "Suspended meter rule on fulcrum wedge"),
    QuestionTargetConfig(49, 8, 9,  0, "stem", "Resistor network bridge with current split"),
    # Category B: 8 Graphical option questions (32 options)
    QuestionTargetConfig(26, 4, 5,  0, "options", "Magnetic field B(r) vs radial distance r plots"),
    QuestionTargetConfig(60, 9, 10, 0, "options", "Enthalpy reaction coordinate potential curves"),
    QuestionTargetConfig(62, 9, 10, 1, "options", "Acid-catalyzed alcohol dehydration alkene structures"),
    QuestionTargetConfig(63, 10, 11, 0, "options", "Boyle's law isotherms P vs 1/V"),
    QuestionTargetConfig(79, 11, 12, 1, "options", "Aromatic electrophilic substitution isomer structures"),
    QuestionTargetConfig(82, 12, 13, 0, "options", "2,6-Dimethyl-dec-4-ene skeletal hydrocarbon isomers"),
    QuestionTargetConfig(88, 13, 14, 0, "options", "Aromatic diazonium / phenol coupling products"),
    QuestionTargetConfig(99, 14, 15, 1, "options", "Organometallic Grignard reaction intermediates"),
    # Category C: 1 Hybrid question (Logic gate stem + 4 waveform options)
    QuestionTargetConfig(38, 6, 7,  0, "stem_and_options", "Combinational logic gates (AND/NAND/OR) and output waveforms"),
]


# ==============================================================================
# Core Extractor
# ==============================================================================

class VectorDiagramExtractor:
    """
    Production-grade extractor for vector diagrams and graphical options from PDF documents.
    """

    def __init__(
        self,
        output_base_dir: str = "backend/static/assets/diagrams/neet_2021",
        render_scale: float = 2.0,
        padding_pts: float = 4.0,
    ) -> None:
        self.output_base_dir = output_base_dir
        self.render_scale = float(render_scale)
        self.padding_pts = float(padding_pts)
        self.effective_dpi = int(round(72.0 * self.render_scale))

    # --------------------------------------------------------------------------
    # Source Validation
    # --------------------------------------------------------------------------

    @staticmethod
    def compute_sha256(file_path: str) -> str:
        """Compute SHA-256 checksum of a file."""
        if not os.path.isfile(file_path):
            raise PDFSourceError(f"File not found: {file_path}")
        hasher = hashlib.sha256()
        with open(file_path, "rb") as f:
            while chunk := f.read(65536):
                hasher.update(chunk)
        return hasher.hexdigest()

    def validate_source_pdf(
        self,
        pdf_path: str,
        expected_sha256: Optional[str] = None
    ) -> Tuple[pymupdf.Document, str]:
        """
        Validate source PDF exists, compute its SHA-256, and open via PyMuPDF.
        """
        if not os.path.exists(pdf_path):
            raise PDFSourceError(f"PDF source file does not exist: {pdf_path}")

        actual_sha256 = self.compute_sha256(pdf_path)
        if expected_sha256 and actual_sha256.lower() != expected_sha256.lower():
            raise PDFSourceError(
                f"PDF checksum mismatch for {pdf_path}: expected {expected_sha256}, got {actual_sha256}"
            )

        try:
            doc = pymupdf.open(pdf_path)
        except Exception as e:
            raise PDFSourceError(f"Failed to open PDF document: {e}") from e

        return doc, actual_sha256

    # --------------------------------------------------------------------------
    # Column and Question Boundary Detection
    # --------------------------------------------------------------------------

    @staticmethod
    def get_column_boundaries(column: int) -> Tuple[float, float]:
        """
        Return (x0, x1) horizontal bounds for a column.
        For NEET 2-column layout:
        Column 0: [35.0, 296.0]
        Column 1: [302.0, 560.0]
        Page vertical divider line sits at x ~= 298.08.
        """
        if column == 0:
            return 35.0, 296.0
        elif column == 1:
            return 302.0, 560.0
        else:
            raise ValueError(f"Invalid column index: {column}. Must be 0 or 1.")

    def detect_question_column_bounds(
        self,
        page: pymupdf.Page,
        question_number: int,
        column: int
    ) -> Tuple[float, float, List[Tuple]]:
        """
        Detect vertical (y_start, y_end) range for a question within a column.
        """
        col_x0, col_x1 = self.get_column_boundaries(column)
        words = page.get_text("words")
        # Filter words within column margins (with 5 pt tolerance) and main body vertical span
        col_words = [
            w for w in words
            if (col_x0 - 5.0) <= w[0] <= (col_x1 + 5.0) and 80.0 <= w[1] <= 810.0
        ]

        # Locate question anchor
        q_target = f"{question_number}."
        q_words = [w for w in col_words if w[4] == q_target and w[0] < col_x0 + 35.0]
        if not q_words:
            # Fallback regex match at margin
            for w in col_words:
                if re.match(rf"^{question_number}\.", w[4]) and w[0] < col_x0 + 35.0:
                    q_words = [w]
                    break

        if not q_words:
            raise BoundingBoxError(
                f"Question {question_number} start marker not found on page in column {column}"
            )

        q_y0 = q_words[0][1]

        # Locate next question start marker within column
        next_q_y = 800.0
        for w in col_words:
            token = w[4]
            if token.endswith(".") and token[:-1].isdigit():
                val = int(token[:-1])
                if val > question_number and w[0] < col_x0 + 35.0:
                    next_q_y = min(next_q_y, w[1])

        return q_y0, next_q_y, col_words

    # --------------------------------------------------------------------------
    # Drawing Inspection & Filtering
    # --------------------------------------------------------------------------

    @staticmethod
    def filter_column_drawings(
        drawings: List[Dict],
        col_x0: float,
        col_x1: float,
        y_min: float,
        y_max: float
    ) -> List[Dict]:
        """
        Filter vector drawings that fall within column horizontal bounds and specified vertical interval.
        Explicitly excludes page borders and the vertical column divider rule.
        """
        filtered = []
        for d in drawings:
            r = d["rect"]
            # Exclude full-page vertical rules or decorations (height > 200 pt)
            if (r.y1 - r.y0) > 200.0:
                continue
            # Exclude the central column divider rule (around x = 298.08)
            if abs(r.x0 - 298.08) < 1.0 and abs(r.x1 - 298.08) < 1.0:
                continue

            # Expand zero-dimension rects (horizontal or vertical stroke lines)
            x0, y0, x1, y1 = r.x0, r.y0, r.x1, r.y1
            if x0 == x1:
                x0 -= 0.5
                x1 += 0.5
            if y0 == y1:
                y0 -= 0.5
                y1 += 0.5

            mid_x = (x0 + x1) / 2.0
            mid_y = (y0 + y1) / 2.0

            if col_x0 <= mid_x <= col_x1 and y_min <= mid_y < y_max:
                filtered.append(d)

        return filtered

    @staticmethod
    def compute_bounding_rect(drawings: List[Dict]) -> pymupdf.Rect:
        """
        Compute the tight union bounding box for a list of drawings.
        Handles zero-thickness strokes properly without losing geometry.
        """
        if not drawings:
            raise BoundingBoxError("Cannot compute bounding box for empty drawings list")

        min_x0 = min(d["rect"].x0 for d in drawings)
        min_y0 = min(d["rect"].y0 for d in drawings)
        max_x1 = max(d["rect"].x1 for d in drawings)
        max_y1 = max(d["rect"].y1 for d in drawings)

        # Ensure non-zero width and height
        if min_x0 == max_x1:
            max_x1 += 1.0
        if min_y0 == max_y1:
            max_y1 += 1.0

        return pymupdf.Rect(min_x0, min_y0, max_x1, max_y1)

    # --------------------------------------------------------------------------
    # Stem Diagram Extraction
    # --------------------------------------------------------------------------

    def extract_stem_bbox(
        self,
        page: pymupdf.Page,
        question_number: int,
        column: int,
        q_y0: float,
        next_q_y: float,
        col_words: List[Tuple]
    ) -> pymupdf.Rect:
        """
        Extract the tight bounding box of a question's stem diagram.
        """
        col_x0, col_x1 = self.get_column_boundaries(column)

        # Find option labels if present
        opt_words = [
            w for w in col_words
            if q_y0 <= w[1] < next_q_y and w[4] in ("(1)", "(2)", "(3)", "(4)")
        ]
        first_opt_y = min((w[1] for w in opt_words), default=next_q_y)

        # Question-specific vertical cutoffs to avoid capturing text or option marks
        if question_number == 4:
            y_start = 625.0
            y_end = first_opt_y - 5.0
        elif question_number == 20:
            y_start = 192.0
            y_end = 280.0
        elif question_number == 38:
            y_start = 130.0
            y_end = 415.0  # Logic gate circuit ends at ~406; waveforms start at ~435
        elif question_number == 40:
            y_start = 175.0
            y_end = 247.0  # Suspending wedge/mass ends at 245.2; option fractions at 253.6
        elif question_number == 49:
            y_start = 152.0
            y_end = 265.0
        else:
            y_start = q_y0 + 20.0
            y_end = first_opt_y - 4.0

        drawings = page.get_drawings()
        stem_drawings = self.filter_column_drawings(drawings, col_x0, col_x1, y_start, y_end)

        if not stem_drawings:
            raise BoundingBoxError(
                f"No vector drawing elements found for Q{question_number} stem diagram "
                f"between y={y_start:.1f} and y={y_end:.1f}"
            )

        bbox = self.compute_bounding_rect(stem_drawings)
        return bbox

    # --------------------------------------------------------------------------
    # Option Diagram Extraction
    # --------------------------------------------------------------------------

    def extract_option_bboxes(
        self,
        page: pymupdf.Page,
        question_number: int,
        column: int,
        q_y0: float,
        next_q_y: float,
        col_words: List[Tuple]
    ) -> List[Tuple[str, str, pymupdf.Rect, int]]:
        """
        Extract the 4 option diagram bounding boxes for graphical option questions.
        Returns list of tuples: (option_key, option_label, bbox, drawing_count).
        """
        col_x0, col_x1 = self.get_column_boundaries(column)

        # Locate (1), (2), (3), (4) labels
        opt_words = [
            w for w in col_words
            if q_y0 <= w[1] < next_q_y and w[4] in ("(1)", "(2)", "(3)", "(4)")
        ]
        opt_words.sort(key=lambda w: w[1])

        if len(opt_words) != 4:
            raise BoundingBoxError(
                f"Expected 4 option labels for Q{question_number}, found {len(opt_words)}"
            )

        lbl_ys = [w[1] for w in opt_words]
        mids = [(lbl_ys[i] + lbl_ys[i + 1]) / 2.0 for i in range(3)]

        top_0 = max(q_y0 + 15.0, lbl_ys[0] - (mids[0] - lbl_ys[0]))
        if question_number == 38:
            top_0 = 430.0  # Waveform time axis starts around y=435

        bands = [
            (top_0, mids[0]),
            (mids[0], mids[1]),
            (mids[1], mids[2]),
            (mids[2], next_q_y),
        ]

        drawings = page.get_drawings()
        option_keys = ["A", "B", "C", "D"]
        option_labels = ["(1)", "(2)", "(3)", "(4)"]
        results = []

        for i in range(4):
            y_min, y_max = bands[i]
            opt_drawings = self.filter_column_drawings(drawings, col_x0, col_x1, y_min, y_max)

            if not opt_drawings:
                raise BoundingBoxError(
                    f"No vector drawings found for Q{question_number} Option {option_labels[i]} "
                    f"in band [{y_min:.1f}, {y_max:.1f}]"
                )

            bbox = self.compute_bounding_rect(opt_drawings)
            results.append((option_keys[i], option_labels[i], bbox, len(opt_drawings)))

        return results

    # --------------------------------------------------------------------------
    # Rasterization & Asset Verification
    # --------------------------------------------------------------------------

    def rasterize_bbox(
        self,
        page: pymupdf.Page,
        bbox: pymupdf.Rect,
        output_path: str,
        column: int,
        overwrite: bool = False
    ) -> Tuple[List[int], int, str]:
        """
        Rasterize a page bounding box to a lossless PNG file.
        Clamps padded bbox within column bounds and page rect.
        Writes atomically via temporary file.
        Returns: (dimensions [w, h], file_size_bytes, sha256).
        """
        col_x0, col_x1 = self.get_column_boundaries(column)

        # Apply padding and clamp
        padded = pymupdf.Rect(
            max(col_x0, bbox.x0 - self.padding_pts),
            max(0.0, bbox.y0 - self.padding_pts),
            min(col_x1, bbox.x1 + self.padding_pts),
            min(page.rect.height, bbox.y1 + self.padding_pts),
        )

        if padded.width <= 0 or padded.height <= 0:
            raise AssetIntegrityError(f"Degenerate padded crop rectangle: {padded}")

        matrix = pymupdf.Matrix(self.render_scale, self.render_scale)
        pixmap = page.get_pixmap(matrix=matrix, clip=padded)

        if pixmap.width <= 0 or pixmap.height <= 0:
            raise AssetIntegrityError(f"Rendered pixmap has zero dimensions: {pixmap.width}x{pixmap.height}")

        png_bytes = pixmap.tobytes("png")
        if len(png_bytes) < 8 or png_bytes[:8] != b"\x89PNG\r\n\x1a\n":
            raise AssetIntegrityError("Rendered bytes do not contain a valid PNG header")

        output_sha256 = hashlib.sha256(png_bytes).hexdigest()
        file_size = len(png_bytes)

        # Check existing asset conflict
        if os.path.exists(output_path) and not overwrite:
            existing_hash = self.compute_sha256(output_path)
            if existing_hash == output_sha256:
                # Idempotent match
                return [pixmap.width, pixmap.height], file_size, output_sha256
            else:
                raise AssetIntegrityError(
                    f"Asset conflict: {output_path} exists with different checksum ({existing_hash} vs {output_sha256}). "
                    f"Set overwrite=True to replace."
                )

        # Atomic file write
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        tmp_path = f"{output_path}.tmp"
        try:
            with open(tmp_path, "wb") as f:
                f.write(png_bytes)
            os.replace(tmp_path, output_path)
        except Exception as e:
            if os.path.exists(tmp_path):
                try:
                    os.remove(tmp_path)
                except OSError:
                    pass
            raise AssetIntegrityError(f"Failed atomic write to {output_path}: {e}") from e

        return [pixmap.width, pixmap.height], file_size, output_sha256

    # --------------------------------------------------------------------------
    # Main Orchestrator
    # --------------------------------------------------------------------------

    def extract_all(
        self,
        pdf_path: str,
        target_configs: Optional[List[QuestionTargetConfig]] = None,
        expected_pdf_sha256: Optional[str] = None,
        overwrite: bool = False
    ) -> List[DiagramAssetRecord]:
        """
        Extract visual diagram assets for all configured targets.
        """
        configs = target_configs or NEET_2021_M4_CONFIGS
        doc, pdf_sha256 = self.validate_source_pdf(pdf_path, expected_pdf_sha256)
        pdf_filename = os.path.basename(pdf_path)

        records: List[DiagramAssetRecord] = []

        for cfg in configs:
            q = cfg.question_number
            p_idx = cfg.page_index
            col = cfg.column
            mode = cfg.mode

            if p_idx < 0 or p_idx >= len(doc):
                rec = DiagramAssetRecord(
                    asset_id=f"neet_2021_q{q:03d}_unknown",
                    exam_code="NEET_UG",
                    exam_year=2021,
                    paper_code="M4",
                    question_number=q,
                    asset_role="unknown",
                    source_pdf_identifier=pdf_filename,
                    source_pdf_sha256=pdf_sha256,
                    source_page_index=p_idx,
                    source_page_number=cfg.page_number,
                    extraction_status="FAILED",
                    failure_reason=f"Page index {p_idx} out of range (PDF has {len(doc)} pages)",
                )
                records.append(rec)
                continue

            page = doc[p_idx]

            try:
                q_y0, next_q_y, col_words = self.detect_question_column_bounds(page, q, col)
            except Exception as e:
                rec = DiagramAssetRecord(
                    asset_id=f"neet_2021_q{q:03d}_boundary_failed",
                    exam_code="NEET_UG",
                    exam_year=2021,
                    paper_code="M4",
                    question_number=q,
                    asset_role="unknown",
                    source_pdf_identifier=pdf_filename,
                    source_pdf_sha256=pdf_sha256,
                    source_page_index=p_idx,
                    source_page_number=cfg.page_number,
                    extraction_status="FAILED",
                    failure_reason=str(e),
                )
                records.append(rec)
                continue

            # Stem diagram extraction
            if mode in ("stem", "stem_and_options"):
                asset_id = f"neet_2021_q{q:03d}_stem"
                filename = f"{asset_id}.png"
                rel_path = os.path.join(self.output_base_dir, filename).replace("\\", "/")
                try:
                    bbox = self.extract_stem_bbox(page, q, col, q_y0, next_q_y, col_words)
                    dims, size_b, img_hash = self.rasterize_bbox(page, bbox, rel_path, col, overwrite)

                    padded = pymupdf.Rect(
                        max(self.get_column_boundaries(col)[0], bbox.x0 - self.padding_pts),
                        max(0.0, bbox.y0 - self.padding_pts),
                        min(self.get_column_boundaries(col)[1], bbox.x1 + self.padding_pts),
                        min(page.rect.height, bbox.y1 + self.padding_pts),
                    )

                    rec = DiagramAssetRecord(
                        asset_id=asset_id,
                        exam_code="NEET_UG",
                        exam_year=2021,
                        paper_code="M4",
                        question_number=q,
                        asset_role="stem",
                        source_pdf_identifier=pdf_filename,
                        source_pdf_sha256=pdf_sha256,
                        source_page_index=p_idx,
                        source_page_number=cfg.page_number,
                        original_bbox=[round(v, 2) for v in (bbox.x0, bbox.y0, bbox.x1, bbox.y1)],
                        padded_bbox=[round(v, 2) for v in (padded.x0, padded.y0, padded.x1, padded.y1)],
                        padding_pts=self.padding_pts,
                        render_scale=self.render_scale,
                        effective_dpi=self.effective_dpi,
                        output_relative_path=rel_path,
                        output_dimensions=dims,
                        file_size_bytes=size_b,
                        output_sha256=img_hash,
                        extraction_status="EXTRACTED",
                        human_review_status="PENDING_HUMAN_REVIEW",
                        review_notes=f"Candidate stem crop for Q{q} ({cfg.description or ''})",
                    )
                except Exception as e:
                    rec = DiagramAssetRecord(
                        asset_id=asset_id,
                        exam_code="NEET_UG",
                        exam_year=2021,
                        paper_code="M4",
                        question_number=q,
                        asset_role="stem",
                        source_pdf_identifier=pdf_filename,
                        source_pdf_sha256=pdf_sha256,
                        source_page_index=p_idx,
                        source_page_number=cfg.page_number,
                        output_relative_path=rel_path,
                        extraction_status="FAILED",
                        failure_reason=str(e),
                    )
                records.append(rec)

            # Option diagrams extraction
            if mode in ("options", "stem_and_options"):
                try:
                    opt_bboxes = self.extract_option_bboxes(page, q, col, q_y0, next_q_y, col_words)
                    for opt_key, opt_lbl, bbox, d_count in opt_bboxes:
                        asset_id = f"neet_2021_q{q:03d}_option_{opt_key.lower()}"
                        filename = f"{asset_id}.png"
                        rel_path = os.path.join(self.output_base_dir, filename).replace("\\", "/")

                        dims, size_b, img_hash = self.rasterize_bbox(page, bbox, rel_path, col, overwrite)
                        padded = pymupdf.Rect(
                            max(self.get_column_boundaries(col)[0], bbox.x0 - self.padding_pts),
                            max(0.0, bbox.y0 - self.padding_pts),
                            min(self.get_column_boundaries(col)[1], bbox.x1 + self.padding_pts),
                            min(page.rect.height, bbox.y1 + self.padding_pts),
                        )

                        rec = DiagramAssetRecord(
                            asset_id=asset_id,
                            exam_code="NEET_UG",
                            exam_year=2021,
                            paper_code="M4",
                            question_number=q,
                            asset_role="option",
                            option_label=opt_lbl,
                            option_key=opt_key,
                            source_pdf_identifier=pdf_filename,
                            source_pdf_sha256=pdf_sha256,
                            source_page_index=p_idx,
                            source_page_number=cfg.page_number,
                            original_bbox=[round(v, 2) for v in (bbox.x0, bbox.y0, bbox.x1, bbox.y1)],
                            padded_bbox=[round(v, 2) for v in (padded.x0, padded.y0, padded.x1, padded.y1)],
                            padding_pts=self.padding_pts,
                            render_scale=self.render_scale,
                            effective_dpi=self.effective_dpi,
                            output_relative_path=rel_path,
                            output_dimensions=dims,
                            file_size_bytes=size_b,
                            output_sha256=img_hash,
                            extraction_status="EXTRACTED",
                            human_review_status="PENDING_HUMAN_REVIEW",
                            review_notes=f"Candidate option {opt_key} {opt_lbl} crop for Q{q} ({cfg.description or ''})",
                        )
                        records.append(rec)
                except Exception as e:
                    # Record failure for options
                    for opt_key in ["a", "b", "c", "d"]:
                        asset_id = f"neet_2021_q{q:03d}_option_{opt_key}"
                        rec = DiagramAssetRecord(
                            asset_id=asset_id,
                            exam_code="NEET_UG",
                            exam_year=2021,
                            paper_code="M4",
                            question_number=q,
                            asset_role="option",
                            option_key=opt_key.upper(),
                            source_pdf_identifier=pdf_filename,
                            source_pdf_sha256=pdf_sha256,
                            source_page_index=p_idx,
                            source_page_number=cfg.page_number,
                            extraction_status="FAILED",
                            failure_reason=str(e),
                        )
                        records.append(rec)

        return records

    # --------------------------------------------------------------------------
    # Manifest Generation
    # --------------------------------------------------------------------------

    @staticmethod
    def generate_manifest(records: List[DiagramAssetRecord], output_json_path: str) -> Dict[str, Any]:
        """
        Generate machine-readable JSON manifest containing summary statistics
        and individual asset records.
        """
        total = len(records)
        extracted = sum(1 for r in records if r.extraction_status == "EXTRACTED")
        failed = sum(1 for r in records if r.extraction_status == "FAILED")
        pending_review = sum(1 for r in records if r.human_review_status == "PENDING_HUMAN_REVIEW")

        manifest = {
            "manifest_version": "1.0",
            "extraction_specification": "Milestone 5.7 Vector Diagram Extraction",
            "summary": {
                "total_candidate_assets": total,
                "successfully_extracted": extracted,
                "extraction_failures": failed,
                "pending_human_review": pending_review,
                "human_verified": 0,
            },
            "assets": [r.to_dict() for r in records],
        }

        os.makedirs(os.path.dirname(output_json_path), exist_ok=True)
        try:
            with open(output_json_path, "w", encoding="utf-8") as f:
                json.dump(manifest, f, indent=2)
        except Exception as e:
            raise ManifestError(f"Failed to write manifest to {output_json_path}: {e}") from e

        return manifest

    # --------------------------------------------------------------------------
    # Review Contact Sheet Generation
    # --------------------------------------------------------------------------

    @staticmethod
    def generate_contact_sheet(
        records: List[DiagramAssetRecord],
        output_html_path: str,
        title: str = "NEET UG 2021 Vector Diagram Extraction Contact Sheet"
    ) -> str:
        """
        Generate a visual HTML review document (contact sheet) displaying all crops,
        their question identity, bounding box, dimensions, and review checkboxes.
        """
        os.makedirs(os.path.dirname(output_html_path), exist_ok=True)

        rows = []
        for r in records:
            status_badge = (
                '<span style="background:#22c55e;color:#fff;padding:2px 8px;border-radius:4px;font-size:12px;">EXTRACTED</span>'
                if r.extraction_status == "EXTRACTED"
                else '<span style="background:#ef4444;color:#fff;padding:2px 8px;border-radius:4px;font-size:12px;">FAILED</span>'
            )
            review_badge = (
                '<span style="background:#f59e0b;color:#fff;padding:2px 8px;border-radius:4px;font-size:12px;">PENDING REVIEW</span>'
            )

            # Resolve relative asset path for HTML preview
            # If asset path is relative to repo root, calculate relative path from html location
            html_dir = os.path.dirname(os.path.abspath(output_html_path))
            asset_abs = os.path.abspath(r.output_relative_path)
            rel_to_html = os.path.relpath(asset_abs, html_dir).replace("\\", "/")

            img_tag = (
                f'<img src="{rel_to_html}" alt="{r.asset_id}" style="max-height:160px;border:1px solid #e2e8f0;background:#fff;border-radius:4px;padding:4px;"/>'
                if r.extraction_status == "EXTRACTED" and os.path.exists(r.output_relative_path)
                else f'<div style="color:#ef4444;font-style:italic;">Failed: {r.failure_reason or "Asset missing"}</div>'
            )

            dims_str = f"{r.output_dimensions[0]}x{r.output_dimensions[1]} px" if r.output_dimensions else "N/A"
            size_kb = f"{r.file_size_bytes / 1024.0:.1f} KB" if r.file_size_bytes else "N/A"
            hash_short = r.output_sha256[:12] if r.output_sha256 else "N/A"
            bbox_str = f"[{', '.join(str(v) for v in r.original_bbox)}]" if r.original_bbox else "N/A"

            rows.append(f"""
            <tr style="border-bottom:1px solid #e2e8f0;">
                <td style="padding:10px;font-weight:600;font-family:monospace;">{r.asset_id}</td>
                <td style="padding:10px;text-align:center;">Q{r.question_number}</td>
                <td style="padding:10px;text-align:center;">{r.asset_role.upper()} {r.option_label or ''}</td>
                <td style="padding:10px;text-align:center;">P{r.source_page_number}</td>
                <td style="padding:10px;text-align:center;">{img_tag}</td>
                <td style="padding:10px;font-size:12px;color:#475569;">
                    <b>Dims:</b> {dims_str}<br/>
                    <b>Size:</b> {size_kb}<br/>
                    <b>BBox:</b> {bbox_str}<br/>
                    <b>SHA-256:</b> <code title="{r.output_sha256}">{hash_short}...</code>
                </td>
                <td style="padding:10px;text-align:center;">{status_badge}<br/><br/>{review_badge}</td>
                <td style="padding:10px;font-size:12px;color:#334155;">{r.review_notes}</td>
            </tr>
            """)

        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>{title}</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; background: #f8fafc; color: #1e293b; margin: 0; padding: 24px; }}
        h1 {{ margin-top: 0; color: #0f172a; font-size: 24px; }}
        .meta {{ background: #fff; border: 1px solid #e2e8f0; border-radius: 8px; padding: 16px; margin-bottom: 24px; box-shadow: 0 1px 3px rgba(0,0,0,0.05); }}
        table {{ width: 100%; border-collapse: collapse; background: #fff; border-radius: 8px; overflow: hidden; box-shadow: 0 1px 3px rgba(0,0,0,0.05); }}
        th {{ background: #f1f5f9; padding: 12px 10px; text-align: left; font-size: 13px; text-transform: uppercase; letter-spacing: 0.05em; color: #475569; border-bottom: 2px solid #cbd5e1; }}
        td {{ vertical-align: middle; }}
    </style>
</head>
<body>
    <h1>{title}</h1>
    <div class="meta">
        <p><b>Target Exam:</b> NEET UG 2021 Booklet M4 | <b>Extractor:</b> <code>pymupdf_vector_geometry_v1</code></p>
        <p><b>Total Candidate Assets:</b> {len(records)} | <b>Successfully Extracted:</b> {sum(1 for r in records if r.extraction_status == "EXTRACTED")} | <b>Human Review:</b> <span style="color:#f59e0b;font-weight:600;">PENDING HUMAN REVIEW (All Assets)</span></p>
        <p style="margin-bottom:0;color:#64748b;font-size:13px;"><i>Policy Reminder: No asset is considered verified or approved for scoring/publication until a human subject-matter reviewer inspects this contact sheet.</i></p>
    </div>
    <table>
        <thead>
            <tr>
                <th>Asset ID</th>
                <th>Question</th>
                <th>Role</th>
                <th>Page</th>
                <th>Rendered Visual Crop</th>
                <th>Geometry & Checksum</th>
                <th>Status</th>
                <th>Notes</th>
            </tr>
        </thead>
        <tbody>
            {"".join(rows)}
        </tbody>
    </table>
</body>
</html>
"""
        with open(output_html_path, "w", encoding="utf-8") as f:
            f.write(html_content)

        return output_html_path
