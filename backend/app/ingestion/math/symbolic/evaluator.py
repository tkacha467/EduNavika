"""
Mathematical Equivalence Engine Orchestrator (Milestone 4.5).
Coordinates the 6-stage decision hierarchy and measures latency profiles.
"""
import time
from typing import Optional, Dict, Any, List
import numpy as np

from backend.app.ingestion.math.symbolic.schemas import (
    EquivalenceStatus,
    MathCategory,
    VerificationMethod,
    EquivalenceResult,
    DomainRestriction,
    NumericalSamplingDetails,
)
from backend.app.ingestion.math.symbolic.parser import LaTeXParser, ParseResult
from backend.app.ingestion.math.symbolic.dispatcher import CategoryDispatcher
from backend.app.ingestion.math.symbolic.arithmetic import ArithmeticVerifier
from backend.app.ingestion.math.symbolic.algebra import AlgebraVerifier
from backend.app.ingestion.math.symbolic.rational import RationalVerifier
from backend.app.ingestion.math.symbolic.radical import RadicalVerifier
from backend.app.ingestion.math.symbolic.trig import TrigVerifier
from backend.app.ingestion.math.symbolic.physics import PhysicsVerifier


class MathematicalEquivalenceEngine:
    """
    Main entry point for verifying mathematical equivalence between predicted and ground-truth expressions.
    """

    def __init__(self):
        self._latencies_ms: List[float] = []

    def evaluate(self, extracted_latex: str, target_latex: str) -> EquivalenceResult:
        """
        Executes the 6-stage equivalence verification hierarchy.
        """
        t0 = time.perf_counter()

        # Stage 1: Independent Parsing
        p_pred = LaTeXParser.parse(extracted_latex)
        p_gt = LaTeXParser.parse(target_latex)

        # Stage 2: Independent Classification
        cat_pred = CategoryDispatcher.classify(p_pred)
        cat_gt = CategoryDispatcher.classify(p_gt)
        category_agreement = (cat_pred == cat_gt)

        # Check for Parse Errors
        if not p_pred.is_success or not p_gt.is_success:
            t_elapsed = (time.perf_counter() - t0) * 1000.0
            self._latencies_ms.append(t_elapsed)
            err_msg = []
            if not p_pred.is_success:
                err_msg.append(f"Extraction parse error: {p_pred.error}")
            if not p_gt.is_success:
                err_msg.append(f"Ground truth parse error: {p_gt.error}")

            return EquivalenceResult(
                status=EquivalenceStatus.PARSE_ERROR,
                target_raw=target_latex,
                extracted_raw=extracted_latex,
                target_category=cat_gt,
                extracted_category=cat_pred,
                category_agreement=category_agreement,
                verification_method=VerificationMethod.NONE,
                eval_time_ms=t_elapsed,
                error_reason="; ".join(err_msg),
            )

        # Check for Unsupported Classes (Chemistry, Geometry Proofs, Ellipses)
        unsupported_cats = {
            MathCategory.UNSUPPORTED_CHEMISTRY,
            MathCategory.UNSUPPORTED_GEOMETRY_PROOF,
            MathCategory.UNSUPPORTED_ELLIPSIS,
        }
        if cat_pred in unsupported_cats or cat_gt in unsupported_cats:
            t_elapsed = (time.perf_counter() - t0) * 1000.0
            self._latencies_ms.append(t_elapsed)
            reason = f"Expression belongs to unsupported category (pred={cat_pred.value}, gt={cat_gt.value})"
            return EquivalenceResult(
                status=EquivalenceStatus.UNSUPPORTED,
                target_raw=target_latex,
                extracted_raw=extracted_latex,
                target_category=cat_gt,
                extracted_category=cat_pred,
                category_agreement=category_agreement,
                verification_method=VerificationMethod.NONE,
                eval_time_ms=t_elapsed,
                error_reason=reason,
            )

        # Stage 3-5: Categorical Verification Dispatch
        status = EquivalenceStatus.INCONCLUSIVE
        method = VerificationMethod.NONE
        restrictions: List[DomainRestriction] = []
        numerical_details: Optional[NumericalSamplingDetails] = None
        error_reason: Optional[str] = None

        # Priority dispatch based on category content
        active_cat = cat_gt if cat_gt != MathCategory.ALGEBRA else cat_pred

        if cat_gt == MathCategory.ARITHMETIC and cat_pred == MathCategory.ARITHMETIC:
            status, method, error_reason = ArithmeticVerifier.verify(p_pred, p_gt)

        elif active_cat == MathCategory.TRIGONOMETRY:
            status, method, restrictions, numerical_details, error_reason = TrigVerifier.verify(p_pred, p_gt)

        elif active_cat in (MathCategory.RADICAL, MathCategory.COORDINATE_GEOMETRY):
            status, method, restrictions, numerical_details, error_reason = RadicalVerifier.verify(p_pred, p_gt)

        elif active_cat == MathCategory.RATIONAL:
            status, method, restrictions, numerical_details, error_reason = RationalVerifier.verify(p_pred, p_gt)

        elif active_cat == MathCategory.PHYSICS:
            status, method, restrictions, numerical_details, error_reason = PhysicsVerifier.verify(p_pred, p_gt)

        else:
            # General Algebra
            status, method, numerical_details, error_reason = AlgebraVerifier.verify(p_pred, p_gt)

        t_elapsed = (time.perf_counter() - t0) * 1000.0
        self._latencies_ms.append(t_elapsed)

        return EquivalenceResult(
            status=status,
            target_raw=target_latex,
            extracted_raw=extracted_latex,
            target_category=cat_gt,
            extracted_category=cat_pred,
            category_agreement=category_agreement,
            verification_method=method,
            domain_restrictions=restrictions,
            numerical_details=numerical_details,
            eval_time_ms=t_elapsed,
            error_reason=error_reason,
            details={
                "target_symbols": p_gt.free_symbols,
                "extracted_symbols": p_pred.free_symbols,
                "is_relation": p_gt.is_relation,
            },
        )

    def get_latency_stats(self) -> Dict[str, float]:
        """
        Computes summary latency metrics across all evaluations.
        """
        if not self._latencies_ms:
            return {"mean_ms": 0.0, "median_ms": 0.0, "p95_ms": 0.0, "max_ms": 0.0, "count": 0}

        arr = np.array(self._latencies_ms)
        return {
            "mean_ms": round(float(np.mean(arr)), 3),
            "median_ms": round(float(np.median(arr)), 3),
            "p95_ms": round(float(np.percentile(arr, 95)), 3),
            "max_ms": round(float(np.max(arr)), 3),
            "count": len(self._latencies_ms),
        }
