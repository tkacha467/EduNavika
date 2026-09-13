import time
from typing import Dict, Any, Optional, Tuple
from dataclasses import dataclass

from backend.app.ingestion.math.base import MathExtractor
from backend.app.ingestion.math.detector import (
    MathPageDetector,
    MathPageClassification,
    MathDetectionResult,
)
from backend.app.ingestion.math.quality_gate import (
    MathQualityGate,
    MathValidationResult,
)

@dataclass
class RoutedPageExtraction:
    text: str
    extraction_method: str
    detection_result: MathDetectionResult
    validation_result: MathValidationResult
    fallback_triggered: bool = False
    execution_time_seconds: float = 0.0
    error: Optional[str] = None

class MathExtractionRouter:
    """
    Intelligent routing coordinator for document extraction.
    Determines whether a page requires standard text extraction or specialized
    mathematical extraction, then validates output through MathQualityGate
    before downstream ingestion.
    """

    def __init__(
        self,
        standard_extractor: MathExtractor,
        specialized_extractor: Optional[MathExtractor] = None,
        detector: Optional[MathPageDetector] = None,
        quality_gate: Optional[MathQualityGate] = None,
    ):
        self.standard_extractor = standard_extractor
        self.specialized_extractor = specialized_extractor
        self.detector = detector or MathPageDetector()
        self.quality_gate = quality_gate or MathQualityGate()

    def route_and_extract(
        self,
        pdf_path: str,
        page_num: int,
        initial_text: Optional[str] = None
    ) -> RoutedPageExtraction:
        """
        Executes policy-driven extraction and validation for a single PDF page.
        
        Args:
            pdf_path: Path to the target PDF.
            page_num: 1-indexed page number.
            initial_text: Optional pre-extracted text (e.g. from standard pypdf pass)
                          to avoid redundant extraction when detecting math.
        """
        start_time = time.time()
        fallback_triggered = False

        # 1. Obtain initial text if not already supplied
        if initial_text is None:
            std_res = self.standard_extractor.extract_page(pdf_path, page_num)
            raw_text = std_res.get("text", "")
            method = self.standard_extractor.name
        else:
            raw_text = initial_text
            method = self.standard_extractor.name

        # 2. Detect mathematical content and density
        detection = self.detector.detect(raw_text)

        # 3. Apply Routing Policy
        final_text = raw_text
        chosen_method = method

        if detection.classification == MathPageClassification.MATH_HEAVY:
            # Policy: Math-heavy pages route to specialized extractor if available
            if self.specialized_extractor is not None:
                spec_res = self.specialized_extractor.extract_page(pdf_path, page_num)
                if spec_res.get("success"):
                    final_text = spec_res.get("text", "")
                    chosen_method = self.specialized_extractor.name
            # If no specialized extractor is configured, standard extraction is retained
            # and will be strictly scrutinized by the quality gate

        # 4. Scrutinize via MathQualityGate
        validation = self.quality_gate.validate_chunk(final_text)

        # 5. Check if fallback to specialized extractor is warranted
        # If standard extraction produced CORRUPTED output on a math-present page
        if (
            validation.status == "CORRUPTED"
            and chosen_method == self.standard_extractor.name
            and self.specialized_extractor is not None
        ):
            fallback_res = self.specialized_extractor.extract_page(pdf_path, page_num)
            if fallback_res.get("success"):
                final_text = fallback_res.get("text", "")
                chosen_method = self.specialized_extractor.name
                fallback_triggered = True
                # Re-validate with quality gate
                validation = self.quality_gate.validate_chunk(final_text)

        duration = round(time.time() - start_time, 4)

        return RoutedPageExtraction(
            text=final_text,
            extraction_method=chosen_method,
            detection_result=detection,
            validation_result=validation,
            fallback_triggered=fallback_triggered,
            execution_time_seconds=duration,
        )
