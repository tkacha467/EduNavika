"""
Radical and Algebraic Number Equivalence Verifier (Milestone 4.5).
Handles roots, non-negative radicand domain boundaries, and structured dual-branch (+/-) verification.
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


class RadicalVerifier:
    """
    Verifies radical equations and expressions while tracking real domain boundaries.
    """

    @classmethod
    def verify(
        cls, p_pred: ParseResult, p_gt: ParseResult
    ) -> Tuple[EquivalenceStatus, VerificationMethod, List[DomainRestriction], Optional[NumericalSamplingDetails], Optional[str]]:
        """
        Verifies radical expressions with real domain restrictions.
        """
        if not p_pred.is_success or not p_gt.is_success:
            return EquivalenceStatus.PARSE_ERROR, VerificationMethod.NONE, [], None, "Parse failure on input expression"

        restrictions: List[DomainRestriction] = []

        try:
            # 1. Extract Radicand Non-Negativity Domain Boundaries (x >= 0)
            restrictions.extend(cls._extract_radicand_restrictions(p_pred))
            restrictions.extend(cls._extract_radicand_restrictions(p_gt))

            # Deduplicate restrictions
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
                    "Relation mismatch in radical verification",
                )

            if p_pred.is_relation:
                delta_pred = p_pred.lhs_expr - p_pred.rhs_expr
                delta_gt = p_gt.lhs_expr - p_gt.rhs_expr
                diff = delta_pred - delta_gt
            else:
                diff = p_pred.sympy_expr - p_gt.sympy_expr

            # 3. Symbolic Simplification with Radical Simplification
            # Use radsimp / simplify
            simplified_diff = sympy.radsimp(diff)
            simplified_diff = sympy.simplify(simplified_diff)

            if simplified_diff == 0:
                return (
                    EquivalenceStatus.SYMBOLIC_EQUIVALENT,
                    VerificationMethod.SYMBOLIC_CAS,
                    unique_restrictions,
                    None,
                    None,
                )

            # Check relation null sign inversion
            if p_pred.is_relation:
                diff_neg = sympy.simplify(sympy.radsimp(delta_pred + delta_gt))
                if diff_neg == 0:
                    return (
                        EquivalenceStatus.SYMBOLIC_EQUIVALENT,
                        VerificationMethod.SYMBOLIC_CAS,
                        unique_restrictions,
                        None,
                        None,
                    )

            # 4. Bounded Numerical Spot-Checking on Strictly Positive Real Domain
            # Schwartz-Zippel explicitly does NOT apply to radicals
            symbols = list(diff.free_symbols)
            if symbols:
                num_status, num_details, err = cls._bounded_positive_numerical_check(diff, symbols)
                if num_status is not None:
                    return num_status, VerificationMethod.BOUNDED_NUMERICAL_SAMPLING, unique_restrictions, num_details, err

            if simplified_diff.is_number and simplified_diff != 0:
                return (
                    EquivalenceStatus.SYMBOLIC_NON_EQUIVALENT,
                    VerificationMethod.SYMBOLIC_CAS,
                    unique_restrictions,
                    None,
                    f"Constant radical difference: {simplified_diff}",
                )

            return (
                EquivalenceStatus.SYMBOLIC_NON_EQUIVALENT,
                VerificationMethod.SYMBOLIC_CAS,
                unique_restrictions,
                None,
                "Radical expressions are not equivalent",
            )

        except Exception as e:
            return EquivalenceStatus.INCONCLUSIVE, VerificationMethod.NONE, restrictions, None, f"Radical verification exception: {str(e)}"

    @classmethod
    def _extract_radicand_restrictions(cls, parse_result: ParseResult) -> List[DomainRestriction]:
        """
        Finds all radicals sqrt(A) or A**(1/2) and records radicand non-negativity (A >= 0).
        """
        restrictions = []
        exprs = [parse_result.sympy_expr] if not parse_result.is_relation else [parse_result.lhs_expr, parse_result.rhs_expr]

        for expr in exprs:
            if expr is None:
                continue
            for sub_expr in sympy.preorder_traversal(expr):
                # Fractional power with even denominator (square roots, 4th roots)
                if sub_expr.is_Pow and sub_expr.exp.is_Rational and sub_expr.exp.q % 2 == 0:
                    radicand = sub_expr.base
                    if hasattr(radicand, "free_symbols") and radicand.free_symbols:
                        for sym in radicand.free_symbols:
                            restrictions.append(
                                DomainRestriction(
                                    variable=str(sym),
                                    condition=">= 0",
                                    restriction_type=RestrictionType.NATURAL_DOMAIN_BOUNDARY,
                                    source=RestrictionSource.INFERRED_RADICAL,
                                    expression=f"{str(radicand)} >= 0",
                                )
                            )
        return restrictions

    @classmethod
    def _bounded_positive_numerical_check(
        cls, diff_expr: Any, symbols: List[Any], num_samples: int = 5, seed: int = 42
    ) -> Tuple[Optional[EquivalenceStatus], Optional[NumericalSamplingDetails], Optional[str]]:
        """
        Spot-checks on positive real numbers to ensure radicands are evaluated with complex modulus.
        """
        try:
            rng = random.Random(seed)
            max_diff = 0.0
            valid_samples = 0

            for _ in range(num_samples):
                point = {sym: rng.uniform(4.0, 25.0) for sym in symbols}
                try:
                    val = diff_expr.subs(point).evalf()
                    val_mag = float(sympy.Abs(val))
                    valid_samples += 1
                except Exception:
                    continue

                if val_mag > max_diff:
                    max_diff = val_mag

                if val_mag > 1e-8:
                    details = NumericalSamplingDetails(
                        sample_count=num_samples,
                        sampling_domain="Strictly positive real interval (4.0, 25.0)^k",
                        tolerance=1e-8,
                        max_observed_diff=max_diff,
                        is_probabilistic_identity_test=False,
                    )
                    return EquivalenceStatus.NUMERICALLY_NON_EQUIVALENT, details, "Numerical check found non-zero evaluation point"

            if valid_samples < 3:
                return EquivalenceStatus.INCONCLUSIVE, None, f"Insufficient valid numerical samples ({valid_samples}/{num_samples})"

            details = NumericalSamplingDetails(
                sample_count=num_samples,
                sampling_domain="Strictly positive real interval (4.0, 25.0)^k",
                tolerance=1e-8,
                max_observed_diff=max_diff,
                is_probabilistic_identity_test=False,
            )
            return EquivalenceStatus.NUMERICALLY_EQUIVALENT, details, None

        except Exception as e:
            return None, None, f"Radical numerical check error: {str(e)}"
