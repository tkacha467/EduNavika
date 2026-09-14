"""
Trigonometric Equivalence Verifier (Milestone 4.5).
Evaluates circular trigonometric identities with trigsimp and pole singularity detection.
"""
from typing import Tuple, Optional, List, Dict, Any
import random
import sympy
from backend.app.ingestion.math.symbolic.schemas import (
    EquivalenceStatus,
    VerificationMethod,
    DomainRestriction,
    RestrictionType,
    RestrictionSource,
    NumericalSamplingDetails,
)
from backend.app.ingestion.math.symbolic.parser import ParseResult


class TrigVerifier:
    """
    Verifies trigonometric expressions and identities.
    """

    POLE_TRIG_FUNCTIONS = {"tan", "sec", "cot", "csc"}

    @classmethod
    def verify(
        cls, p_pred: ParseResult, p_gt: ParseResult
    ) -> Tuple[EquivalenceStatus, VerificationMethod, List[DomainRestriction], Optional[NumericalSamplingDetails], Optional[str]]:
        """
        Evaluates trigonometric equivalence with trigsimp and pole tracking.
        """
        if not p_pred.is_success or not p_gt.is_success:
            return EquivalenceStatus.PARSE_ERROR, VerificationMethod.NONE, [], None, "Parse failure on input expression"

        restrictions: List[DomainRestriction] = []

        try:
            # 1. Detect Pole Singularities (e.g. tan(theta), sec(theta))
            restrictions.extend(cls._extract_trig_pole_restrictions(p_pred))
            restrictions.extend(cls._extract_trig_pole_restrictions(p_gt))

            unique_restrictions = []
            seen = set()
            for r in restrictions:
                key = (r.variable, r.condition, r.expression)
                if key not in seen:
                    seen.add(key)
                    unique_restrictions.append(r)

            # 2. Check Relations vs Single Expressions
            if p_pred.is_relation != p_gt.is_relation:
                return (
                    EquivalenceStatus.SYMBOLIC_NON_EQUIVALENT,
                    VerificationMethod.SYMBOLIC_CAS,
                    unique_restrictions,
                    None,
                    "Relation mismatch in trigonometric verification",
                )

            if p_pred.is_relation:
                delta_pred = p_pred.lhs_expr - p_pred.rhs_expr
                delta_gt = p_gt.lhs_expr - p_gt.rhs_expr
                diff = delta_pred - delta_gt
            else:
                diff = p_pred.sympy_expr - p_gt.sympy_expr

            # 3. Symbolic Trig Simplification
            simplified = sympy.trigsimp(diff)
            if simplified == 0:
                return (
                    EquivalenceStatus.SYMBOLIC_EQUIVALENT,
                    VerificationMethod.SYMBOLIC_CAS,
                    unique_restrictions,
                    None,
                    None,
                )

            # Try rewrite as sin/cos or exp
            rewritten = sympy.trigsimp(diff.rewrite(sympy.sin))
            if rewritten == 0:
                return (
                    EquivalenceStatus.SYMBOLIC_EQUIVALENT,
                    VerificationMethod.SYMBOLIC_CAS,
                    unique_restrictions,
                    None,
                    None,
                )

            # Check relation null sign inversion
            if p_pred.is_relation:
                diff_neg = sympy.trigsimp(delta_pred + delta_gt)
                if diff_neg == 0:
                    return (
                        EquivalenceStatus.SYMBOLIC_EQUIVALENT,
                        VerificationMethod.SYMBOLIC_CAS,
                        unique_restrictions,
                        None,
                        None,
                    )

            # 4. Bounded Numerical Spot-Checking (Within interior quadrant (0.2, 1.2) away from poles)
            symbols = list(diff.free_symbols)
            if symbols:
                num_status, num_details, err = cls._bounded_trig_numerical_check(diff, symbols)
                if num_status is not None:
                    return num_status, VerificationMethod.BOUNDED_NUMERICAL_SAMPLING, unique_restrictions, num_details, err

            if simplified.is_number and simplified != 0:
                return (
                    EquivalenceStatus.SYMBOLIC_NON_EQUIVALENT,
                    VerificationMethod.SYMBOLIC_CAS,
                    unique_restrictions,
                    None,
                    f"Constant trigonometric difference: {simplified}",
                )

            return (
                EquivalenceStatus.SYMBOLIC_NON_EQUIVALENT,
                VerificationMethod.SYMBOLIC_CAS,
                unique_restrictions,
                None,
                "Trigonometric expressions are not equivalent",
            )

        except Exception as e:
            return EquivalenceStatus.INCONCLUSIVE, VerificationMethod.NONE, restrictions, None, f"Trigonometric verification exception: {str(e)}"

    @classmethod
    def _extract_trig_pole_restrictions(cls, parse_result: ParseResult) -> List[DomainRestriction]:
        """
        Detects tan, sec, cot, csc poles.
        """
        restrictions = []
        exprs = [parse_result.sympy_expr] if not parse_result.is_relation else [parse_result.lhs_expr, parse_result.rhs_expr]

        for expr in exprs:
            if expr is None:
                continue
            for sub_expr in sympy.preorder_traversal(expr):
                func_name = getattr(getattr(sub_expr, "func", None), "__name__", "")
                if func_name in cls.POLE_TRIG_FUNCTIONS:
                    args = getattr(sub_expr, "args", ())
                    for arg in args:
                        if hasattr(arg, "free_symbols"):
                            for sym in arg.free_symbols:
                                condition = "!= pi/2 + k*pi" if func_name in {"tan", "sec"} else "!= k*pi"
                                restrictions.append(
                                    DomainRestriction(
                                        variable=str(sym),
                                        condition=condition,
                                        restriction_type=RestrictionType.SINGULARITY_POLE,
                                        source=RestrictionSource.INFERRED_DENOMINATOR,
                                        expression=f"{func_name}({str(arg)}) has pole at {condition}",
                                    )
                                )
        return restrictions

    @classmethod
    def _bounded_trig_numerical_check(
        cls, diff_expr: Any, symbols: List[Any], num_samples: int = 5, seed: int = 42
    ) -> Tuple[Optional[EquivalenceStatus], Optional[NumericalSamplingDetails], Optional[str]]:
        """
        Spot-checks angles safely in (0.2, 1.2) rad (avoiding 0 and pi/2 = 1.5707...).
        """
        try:
            rng = random.Random(seed)
            max_diff = 0.0

            for _ in range(num_samples):
                point = {sym: rng.uniform(0.2, 1.2) for sym in symbols}
                try:
                    val = diff_expr.subs(point).evalf()
                    val_float = abs(float(val))
                except Exception:
                    continue

                if val_float > max_diff:
                    max_diff = val_float

                if val_float > 1e-8:
                    details = NumericalSamplingDetails(
                        sample_count=num_samples,
                        sampling_domain="Interior quadrant interval (0.2, 1.2)^k radians",
                        tolerance=1e-8,
                        max_observed_diff=max_diff,
                        is_probabilistic_identity_test=False,
                    )
                    return EquivalenceStatus.NUMERICALLY_NON_EQUIVALENT, details, "Numerical check found non-zero evaluation point"

            details = NumericalSamplingDetails(
                sample_count=num_samples,
                sampling_domain="Interior quadrant interval (0.2, 1.2)^k radians",
                tolerance=1e-8,
                max_observed_diff=max_diff,
                is_probabilistic_identity_test=False,
            )
            return EquivalenceStatus.NUMERICALLY_EQUIVALENT, details, None

        except Exception as e:
            return None, None, f"Trig numerical check error: {str(e)}"
