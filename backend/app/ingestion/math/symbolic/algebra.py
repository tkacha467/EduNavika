"""
Algebraic and Polynomial Equivalence Verifier (Milestone 4.5).
Evaluates polynomial identities and algebraic relations with symbolic proof and
strictly bounded Schwartz-Zippel probabilistic testing.
"""
from typing import Tuple, Optional, List, Dict, Any
import random
import sympy
from backend.app.ingestion.math.symbolic.schemas import (
    EquivalenceStatus,
    VerificationMethod,
    NumericalSamplingDetails,
)
from backend.app.ingestion.math.symbolic.parser import ParseResult


class AlgebraVerifier:
    """
    Verifies polynomial and general algebraic expressions/equations.
    """

    @classmethod
    def verify(
        cls, p_pred: ParseResult, p_gt: ParseResult, allow_schwartz_zippel: bool = True
    ) -> Tuple[EquivalenceStatus, VerificationMethod, Optional[NumericalSamplingDetails], Optional[str]]:
        """
        Executes algebraic verification through symbolic CAS and optional restricted Schwartz-Zippel testing.
        """
        if not p_pred.is_success or not p_gt.is_success:
            return EquivalenceStatus.PARSE_ERROR, VerificationMethod.NONE, None, "Parse failure on input expression"

        try:
            # 1. Structural Relation Alignment
            if p_pred.is_relation != p_gt.is_relation:
                return EquivalenceStatus.SYMBOLIC_NON_EQUIVALENT, VerificationMethod.SYMBOLIC_CAS, None, "Relation mismatch: one is an equation, one is an expression"

            if p_pred.is_relation:
                return cls._verify_relation(p_pred, p_gt, allow_schwartz_zippel)
            else:
                return cls._verify_expression(p_pred.sympy_expr, p_gt.sympy_expr, allow_schwartz_zippel)

        except Exception as e:
            return EquivalenceStatus.INCONCLUSIVE, VerificationMethod.NONE, None, f"Algebraic CAS error: {str(e)}"

    @classmethod
    def _verify_relation(
        cls, p_pred: ParseResult, p_gt: ParseResult, allow_schwartz_zippel: bool
    ) -> Tuple[EquivalenceStatus, VerificationMethod, Optional[NumericalSamplingDetails], Optional[str]]:
        """
        Verifies relational equations: L1 = R1 vs L2 = R2.
        """
        # Step A: Direct side-by-side equivalence: (L1 == L2) and (R1 == R2)
        diff_lhs = sympy.simplify(p_pred.lhs_expr - p_gt.lhs_expr)
        diff_rhs = sympy.simplify(p_pred.rhs_expr - p_gt.rhs_expr)
        if diff_lhs == 0 and diff_rhs == 0:
            return EquivalenceStatus.SYMBOLIC_EQUIVALENT, VerificationMethod.SYMBOLIC_CAS, None, None

        # Step B: Symmetric inversion: (L1 == R2) and (R1 == L2)
        inv_lhs = sympy.simplify(p_pred.lhs_expr - p_gt.rhs_expr)
        inv_rhs = sympy.simplify(p_pred.rhs_expr - p_gt.lhs_expr)
        if inv_lhs == 0 and inv_rhs == 0:
            return EquivalenceStatus.SYMBOLIC_EQUIVALENT, VerificationMethod.SYMBOLIC_CAS, None, None

        # Step C: Null form subtraction: Delta_pred = L1 - R1, Delta_gt = L2 - R2
        delta_pred = sympy.simplify(p_pred.lhs_expr - p_pred.rhs_expr)
        delta_gt = sympy.simplify(p_gt.lhs_expr - p_gt.rhs_expr)

        diff_null = sympy.simplify(delta_pred - delta_gt)
        if diff_null == 0:
            return EquivalenceStatus.SYMBOLIC_EQUIVALENT, VerificationMethod.SYMBOLIC_CAS, None, None

        # Step D: Sign inversion null form: Delta_pred == -Delta_gt
        diff_neg_null = sympy.simplify(delta_pred + delta_gt)
        if diff_neg_null == 0:
            return EquivalenceStatus.SYMBOLIC_EQUIVALENT, VerificationMethod.SYMBOLIC_CAS, None, None

        # Step E: Constant non-zero multiple: Delta_pred / Delta_gt == c
        try:
            ratio = sympy.simplify(delta_pred / delta_gt)
            if ratio.is_number and ratio != 0:
                return EquivalenceStatus.SYMBOLIC_EQUIVALENT, VerificationMethod.SYMBOLIC_CAS, None, None
        except Exception:
            pass

        # Step F: Check if both polynomials, attempt Schwartz-Zippel probabilistic check if simplify was inconclusive
        if allow_schwartz_zippel and cls._is_polynomial(delta_pred - delta_gt):
            sz_status, details, err = cls._schwartz_zippel_test(delta_pred - delta_gt)
            if sz_status is not None:
                return sz_status, VerificationMethod.POLYNOMIAL_SCHWARTZ_ZIPPEL, details, err

        # If constant non-zero difference, definitively non-equivalent
        if diff_null.is_number and diff_null != 0:
            return EquivalenceStatus.SYMBOLIC_NON_EQUIVALENT, VerificationMethod.SYMBOLIC_CAS, None, f"Constant difference: {diff_null}"

        return EquivalenceStatus.SYMBOLIC_NON_EQUIVALENT, VerificationMethod.SYMBOLIC_CAS, None, "Relational expressions are not algebraically equivalent"

    @classmethod
    def _verify_expression(
        cls, expr_pred: Any, expr_gt: Any, allow_schwartz_zippel: bool
    ) -> Tuple[EquivalenceStatus, VerificationMethod, Optional[NumericalSamplingDetails], Optional[str]]:
        """
        Verifies single expressions: expr_pred vs expr_gt.
        """
        diff = sympy.simplify(expr_pred - expr_gt)
        if diff == 0:
            return EquivalenceStatus.SYMBOLIC_EQUIVALENT, VerificationMethod.SYMBOLIC_CAS, None, None

        # Try expand
        diff_expanded = sympy.expand(expr_pred - expr_gt)
        if diff_expanded == 0:
            return EquivalenceStatus.SYMBOLIC_EQUIVALENT, VerificationMethod.SYMBOLIC_CAS, None, None

        # If constant non-zero difference, definitively non-equivalent
        if diff.is_number and diff != 0:
            return EquivalenceStatus.SYMBOLIC_NON_EQUIVALENT, VerificationMethod.SYMBOLIC_CAS, None, f"Constant difference: {diff}"

        # If polynomial, perform Schwartz-Zippel test
        if allow_schwartz_zippel and cls._is_polynomial(diff):
            sz_status, details, err = cls._schwartz_zippel_test(diff)
            if sz_status is not None:
                return sz_status, VerificationMethod.POLYNOMIAL_SCHWARTZ_ZIPPEL, details, err

        return EquivalenceStatus.SYMBOLIC_NON_EQUIVALENT, VerificationMethod.SYMBOLIC_CAS, None, "Expressions are not algebraically equivalent"

    @classmethod
    def _is_polynomial(cls, expr: Any) -> bool:
        """
        Checks whether expr is a genuine polynomial over free symbols.
        """
        try:
            poly = sympy.Poly(expr)
            return True
        except Exception:
            return False

    @classmethod
    def _schwartz_zippel_test(
        cls, diff_poly: Any, num_samples: int = 5, seed: int = 42
    ) -> Tuple[Optional[EquivalenceStatus], Optional[NumericalSamplingDetails], Optional[str]]:
        """
        Executes Schwartz-Zippel probabilistic polynomial identity testing.
        Applies strictly to polynomial elements.
        """
        try:
            symbols = sorted(list(diff_poly.free_symbols), key=lambda s: str(s))
            if not symbols:
                return None, None, None

            # Determine degree
            try:
                poly = sympy.Poly(diff_poly, *symbols)
                degree = poly.total_degree()
            except Exception:
                degree = 5  # Safe upper bound

            degree = max(1, degree)
            grid_size = max(1000, 100 * degree)

            rng = random.Random(seed)
            max_diff = 0.0

            for _ in range(num_samples):
                point = {sym: rng.randint(-grid_size, grid_size) for sym in symbols}
                val = diff_poly.subs(point)
                val_float = abs(float(val))
                if val_float > max_diff:
                    max_diff = val_float

                if val_float > 1e-9:
                    details = NumericalSamplingDetails(
                        sample_count=num_samples,
                        sampling_domain=f"Discrete grid [-{grid_size}, {grid_size}]^k",
                        tolerance=1e-9,
                        max_observed_diff=max_diff,
                        is_probabilistic_identity_test=True,
                        theoretical_error_bound=round(degree / grid_size, 6),
                    )
                    return EquivalenceStatus.NUMERICALLY_NON_EQUIVALENT, details, "Schwartz-Zippel test found non-zero evaluation point"

            # All points evaluated to 0
            details = NumericalSamplingDetails(
                sample_count=num_samples,
                sampling_domain=f"Discrete grid [-{grid_size}, {grid_size}]^k",
                tolerance=1e-9,
                max_observed_diff=0.0,
                is_probabilistic_identity_test=True,
                theoretical_error_bound=round(degree / grid_size, 6),
            )
            return EquivalenceStatus.NUMERICALLY_EQUIVALENT, details, None

        except Exception as e:
            return None, None, f"Schwartz-Zippel test exception: {str(e)}"
