"""
Rational Function and Singularity Verifier (Milestone 4.5).
Analyzes rational equations and expressions with explicit pole detection and domain tracking.
"""
from typing import Tuple, Optional, List, Dict, Any, Set
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


class RationalVerifier:
    """
    Verifies rational expressions and detects denominator poles/singularities.
    """

    @classmethod
    def verify(
        cls, p_pred: ParseResult, p_gt: ParseResult
    ) -> Tuple[EquivalenceStatus, VerificationMethod, List[DomainRestriction], Optional[NumericalSamplingDetails], Optional[str]]:
        """
        Evaluates rational equivalence while extracting denominator singularities.
        """
        if not p_pred.is_success or not p_gt.is_success:
            return EquivalenceStatus.PARSE_ERROR, VerificationMethod.NONE, [], None, "Parse failure on input expression"

        restrictions: List[DomainRestriction] = []

        try:
            # 1. Extract Denominator Singularities
            restrictions.extend(cls._extract_denominator_restrictions(p_pred))
            restrictions.extend(cls._extract_denominator_restrictions(p_gt))

            # Deduplicate restrictions
            unique_restrictions = []
            seen = set()
            for r in restrictions:
                key = (r.variable, r.condition, r.expression)
                if key not in seen:
                    seen.add(key)
                    unique_restrictions.append(r)

            # 2. Check Domain Pole Consistency (Domain Singularity Trap Prevention)
            restr_pred = cls._extract_denominator_restrictions(p_pred)
            restr_gt = cls._extract_denominator_restrictions(p_gt)
            poles_pred = {r.variable for r in restr_pred}
            poles_gt = {r.variable for r in restr_gt}

            # If one expression has variable denominator poles that the other lacks, domains differ
            if poles_pred != poles_gt:
                return (
                    EquivalenceStatus.SYMBOLIC_NON_EQUIVALENT,
                    VerificationMethod.SYMBOLIC_CAS,
                    unique_restrictions,
                    None,
                    f"Domain mismatch: expressions have different denominator poles ({poles_pred} vs {poles_gt})",
                )

            # 3. Check Relations vs Single Expressions
            if p_pred.is_relation != p_gt.is_relation:
                return (
                    EquivalenceStatus.SYMBOLIC_NON_EQUIVALENT,
                    VerificationMethod.SYMBOLIC_CAS,
                    unique_restrictions,
                    None,
                    "Relation mismatch in rational verification",
                )

            if p_pred.is_relation:
                delta_pred = p_pred.lhs_expr - p_pred.rhs_expr
                delta_gt = p_gt.lhs_expr - p_gt.rhs_expr
                diff = sympy.together(delta_pred - delta_gt)

                # Check numerator cross-multiplied equivalence: N_pred == c * N_gt
                n_pred, d_pred = sympy.fraction(sympy.together(delta_pred))
                n_gt, d_gt = sympy.fraction(sympy.together(delta_gt))

                diff_num = sympy.simplify(n_pred - n_gt)
                if diff_num == 0:
                    return (
                        EquivalenceStatus.SYMBOLIC_EQUIVALENT,
                        VerificationMethod.SYMBOLIC_CAS,
                        unique_restrictions,
                        None,
                        None,
                    )
                # Check sign inversion of numerators
                if sympy.simplify(n_pred + n_gt) == 0:
                    return (
                        EquivalenceStatus.SYMBOLIC_EQUIVALENT,
                        VerificationMethod.SYMBOLIC_CAS,
                        unique_restrictions,
                        None,
                        None,
                    )
                # Check constant multiple of numerators
                try:
                    num_ratio = sympy.simplify(n_pred / n_gt)
                    if getattr(num_ratio, "is_number", False) and getattr(num_ratio, "is_finite", False) and num_ratio != 0:
                        return (
                            EquivalenceStatus.SYMBOLIC_EQUIVALENT,
                            VerificationMethod.SYMBOLIC_CAS,
                            unique_restrictions,
                            None,
                            None,
                        )
                except Exception:
                    pass
            else:
                diff = sympy.together(p_pred.sympy_expr - p_gt.sympy_expr)

            # 4. Symbolic Zero-Test on Numerator
            numer, denom = sympy.fraction(diff)
            simplified_numer = sympy.simplify(numer)

            if simplified_numer == 0:
                return (
                    EquivalenceStatus.SYMBOLIC_EQUIVALENT,
                    VerificationMethod.SYMBOLIC_CAS,
                    unique_restrictions,
                    None,
                    None,
                )

            # Check if negative difference in relation (L - R == -(L - R))
            if p_pred.is_relation:
                diff_neg = sympy.together(delta_pred + delta_gt)
                n_neg, _ = sympy.fraction(diff_neg)
                if sympy.simplify(n_neg) == 0:
                    return (
                        EquivalenceStatus.SYMBOLIC_EQUIVALENT,
                        VerificationMethod.SYMBOLIC_CAS,
                        unique_restrictions,
                        None,
                        None,
                    )

            # If constant non-zero difference
            if simplified_numer.is_number and simplified_numer != 0:
                return (
                    EquivalenceStatus.SYMBOLIC_NON_EQUIVALENT,
                    VerificationMethod.SYMBOLIC_CAS,
                    unique_restrictions,
                    None,
                    f"Constant rational numerator difference: {simplified_numer}",
                )

            # 4. Bounded Numerical Spot-Checking (Avoiding Singularities)
            symbols = list(diff.free_symbols)
            if symbols:
                num_status, num_details, err = cls._bounded_numerical_check(diff, symbols, unique_restrictions)
                if num_status is not None:
                    return num_status, VerificationMethod.BOUNDED_NUMERICAL_SAMPLING, unique_restrictions, num_details, err

            return (
                EquivalenceStatus.SYMBOLIC_NON_EQUIVALENT,
                VerificationMethod.SYMBOLIC_CAS,
                unique_restrictions,
                None,
                "Rational expressions are not equivalent",
            )

        except Exception as e:
            return EquivalenceStatus.INCONCLUSIVE, VerificationMethod.NONE, restrictions, None, f"Rational verification exception: {str(e)}"

    @classmethod
    def _extract_denominator_restrictions(cls, parse_result: ParseResult) -> List[DomainRestriction]:
        """
        Finds all denominator expressions and records singularity poles.
        """
        restrictions = []
        exprs = [parse_result.sympy_expr] if not parse_result.is_relation else [parse_result.lhs_expr, parse_result.rhs_expr]

        for expr in exprs:
            if expr is None:
                continue
            # Traverse AST for rational fractions
            for sub_expr in sympy.preorder_traversal(expr):
                if sub_expr.is_Pow and sub_expr.exp.is_negative:
                    # e.g., x**(-1) or (x - 1)**(-1)
                    base = sub_expr.base
                    for sym in base.free_symbols:
                        restrictions.append(
                            DomainRestriction(
                                variable=str(sym),
                                condition="!= 0",
                                restriction_type=RestrictionType.SINGULARITY_POLE,
                                source=RestrictionSource.INFERRED_DENOMINATOR,
                                expression=f"{str(base)} != 0",
                            )
                        )
                elif hasattr(sub_expr, "as_numer_denom"):
                    _, denom = sub_expr.as_numer_denom()
                    if denom != 1 and hasattr(denom, "free_symbols") and denom.free_symbols:
                        for sym in denom.free_symbols:
                            restrictions.append(
                                DomainRestriction(
                                    variable=str(sym),
                                    condition="!= 0",
                                    restriction_type=RestrictionType.SINGULARITY_POLE,
                                    source=RestrictionSource.INFERRED_DENOMINATOR,
                                    expression=f"{str(denom)} != 0",
                                )
                            )
        return restrictions

    @classmethod
    def _bounded_numerical_check(
        cls, diff_expr: Any, symbols: List[Any], restrictions: List[DomainRestriction], num_samples: int = 5, seed: int = 42
    ) -> Tuple[Optional[EquivalenceStatus], Optional[NumericalSamplingDetails], Optional[str]]:
        """
        Performs bounded numerical sampling outside singularity locus.
        """
        try:
            rng = random.Random(seed)
            max_diff = 0.0

            for _ in range(num_samples):
                # Pick values safely away from 0 and small integers to avoid poles
                point = {sym: rng.uniform(2.5, 10.5) for sym in symbols}
                try:
                    val = diff_expr.subs(point)
                    val_float = abs(float(val))
                except (ZeroDivisionError, ValueError):
                    continue

                if val_float > max_diff:
                    max_diff = val_float

                if val_float > 1e-8:
                    details = NumericalSamplingDetails(
                        sample_count=num_samples,
                        sampling_domain="Open real interval (2.5, 10.5)^k excluding poles",
                        tolerance=1e-8,
                        max_observed_diff=max_diff,
                        is_probabilistic_identity_test=False,
                    )
                    return EquivalenceStatus.NUMERICALLY_NON_EQUIVALENT, details, "Numerical check found non-zero evaluation point"

            details = NumericalSamplingDetails(
                sample_count=num_samples,
                sampling_domain="Open real interval (2.5, 10.5)^k excluding poles",
                tolerance=1e-8,
                max_observed_diff=max_diff,
                is_probabilistic_identity_test=False,
            )
            return EquivalenceStatus.NUMERICALLY_EQUIVALENT, details, None

        except Exception as e:
            return None, None, f"Numerical check error: {str(e)}"
