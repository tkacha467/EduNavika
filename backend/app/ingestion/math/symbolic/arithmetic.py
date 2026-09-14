"""
Exact Arithmetic Equivalence Verifier (Milestone 4.5).
Evaluates purely numeric expressions with arbitrary-precision rational arithmetic.
"""
from typing import Tuple, Optional
import sympy
from backend.app.ingestion.math.symbolic.schemas import (
    EquivalenceStatus,
    VerificationMethod,
)
from backend.app.ingestion.math.symbolic.parser import ParseResult


class ArithmeticVerifier:
    """
    Verifies purely numerical arithmetic expressions using exact rational arithmetic.
    """

    @classmethod
    def verify(
        cls, p_pred: ParseResult, p_gt: ParseResult
    ) -> Tuple[EquivalenceStatus, VerificationMethod, Optional[str]]:
        """
        Evaluates equivalence between two arithmetic parse results.
        """
        # Both must have parsed successfully
        if not p_pred.is_success or not p_gt.is_success:
            return EquivalenceStatus.PARSE_ERROR, VerificationMethod.NONE, "One or both arithmetic expressions failed parsing"

        try:
            # Case 1: Both are relations (equations)
            if p_pred.is_relation and p_gt.is_relation:
                diff_lhs = sympy.simplify(p_pred.lhs_expr - p_gt.lhs_expr)
                diff_rhs = sympy.simplify(p_pred.rhs_expr - p_gt.rhs_expr)

                if diff_lhs == 0 and diff_rhs == 0:
                    return EquivalenceStatus.SYMBOLIC_EQUIVALENT, VerificationMethod.DIRECT_RATIONAL_REDUCTION, None

                # Check symmetric inversion A = B vs B = A
                inv_lhs = sympy.simplify(p_pred.lhs_expr - p_gt.rhs_expr)
                inv_rhs = sympy.simplify(p_pred.rhs_expr - p_gt.lhs_expr)
                if inv_lhs == 0 and inv_rhs == 0:
                    return EquivalenceStatus.SYMBOLIC_EQUIVALENT, VerificationMethod.DIRECT_RATIONAL_REDUCTION, None

                # Check zero-subtraction identity (L1 - R1) == (L2 - R2)
                null_pred = sympy.simplify(p_pred.lhs_expr - p_pred.rhs_expr)
                null_gt = sympy.simplify(p_gt.lhs_expr - p_gt.rhs_expr)
                if null_pred == 0 and null_gt == 0:
                    return EquivalenceStatus.SYMBOLIC_EQUIVALENT, VerificationMethod.DIRECT_RATIONAL_REDUCTION, None

                return EquivalenceStatus.SYMBOLIC_NON_EQUIVALENT, VerificationMethod.DIRECT_RATIONAL_REDUCTION, "Arithmetic relation sides do not match"

            # Case 2: One is a relation and one is single expression
            if p_pred.is_relation != p_gt.is_relation:
                return EquivalenceStatus.SYMBOLIC_NON_EQUIVALENT, VerificationMethod.DIRECT_RATIONAL_REDUCTION, "Structural mismatch: one is relation, one is single expression"

            # Case 3: Both are single arithmetic expressions
            diff = sympy.simplify(p_pred.sympy_expr - p_gt.sympy_expr)
            if diff == 0:
                return EquivalenceStatus.SYMBOLIC_EQUIVALENT, VerificationMethod.DIRECT_RATIONAL_REDUCTION, None
            else:
                return EquivalenceStatus.SYMBOLIC_NON_EQUIVALENT, VerificationMethod.DIRECT_RATIONAL_REDUCTION, f"Arithmetic value difference: {diff} != 0"

        except Exception as e:
            return EquivalenceStatus.INCONCLUSIVE, VerificationMethod.NONE, f"Arithmetic evaluation exception: {str(e)}"
