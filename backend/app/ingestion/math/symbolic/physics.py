"""
Physics and Coordinate Geometry Equivalence Verifier (Milestone 4.5).
Handles atomic compound symbols, physical equations, and explicit physical domain assumptions.
"""
from typing import Tuple, Optional, List, Dict, Any
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


class PhysicsVerifier:
    """
    Verifies physics and coordinate geometry formulas with physical domain constraints.
    """

    POSITIVE_PHYSICAL_VARIABLES = {
        "m", "m_1", "m_2", "r", "R", "c", "h", "G", "T", "t", "rho", "lambda", "d",
    }

    @classmethod
    def verify(
        cls, p_pred: ParseResult, p_gt: ParseResult
    ) -> Tuple[EquivalenceStatus, VerificationMethod, List[DomainRestriction], Optional[NumericalSamplingDetails], Optional[str]]:
        """
        Verifies physics relations and coordinate expressions.
        """
        if not p_pred.is_success or not p_gt.is_success:
            return EquivalenceStatus.PARSE_ERROR, VerificationMethod.NONE, [], None, "Parse failure on input expression"

        restrictions: List[DomainRestriction] = []

        try:
            # 1. Attach Explicit Physical Assumptions (e.g. m > 0, r > 0, c > 0)
            all_symbols = set(p_pred.free_symbols).union(set(p_gt.free_symbols))
            for sym in all_symbols:
                clean_sym = sym.replace("{", "").replace("}", "")
                if clean_sym in cls.POSITIVE_PHYSICAL_VARIABLES:
                    restrictions.append(
                        DomainRestriction(
                            variable=sym,
                            condition="> 0",
                            restriction_type=RestrictionType.EXPLICIT_PHYSICAL_ASSUMPTION,
                            source=RestrictionSource.PHYSICAL_MODEL,
                            expression=f"{sym} > 0 (Physical parameter positivity)",
                        )
                    )

            # 2. Check Relations vs Single Expressions
            if p_pred.is_relation != p_gt.is_relation:
                return (
                    EquivalenceStatus.SYMBOLIC_NON_EQUIVALENT,
                    VerificationMethod.SYMBOLIC_CAS,
                    restrictions,
                    None,
                    "Relation mismatch in physics verification",
                )

            if p_pred.is_relation:
                delta_pred = p_pred.lhs_expr - p_pred.rhs_expr
                delta_gt = p_gt.lhs_expr - p_gt.rhs_expr
                diff = delta_pred - delta_gt
            else:
                diff = p_pred.sympy_expr - p_gt.sympy_expr

            # 3. Direct Simplification
            simplified = sympy.simplify(diff)
            if simplified == 0:
                return (
                    EquivalenceStatus.SYMBOLIC_EQUIVALENT,
                    VerificationMethod.SYMBOLIC_CAS,
                    restrictions,
                    None,
                    None,
                )

            # Symmetric relation or ratio test
            if p_pred.is_relation:
                diff_neg = sympy.simplify(delta_pred + delta_gt)
                if diff_neg == 0:
                    return (
                        EquivalenceStatus.SYMBOLIC_EQUIVALENT,
                        VerificationMethod.SYMBOLIC_CAS,
                        restrictions,
                        None,
                        None,
                    )

                # Check if LHS_pred == RHS_gt and RHS_pred == LHS_gt
                inv_lhs = sympy.simplify(p_pred.lhs_expr - p_gt.rhs_expr)
                inv_rhs = sympy.simplify(p_pred.rhs_expr - p_gt.lhs_expr)
                if inv_lhs == 0 and inv_rhs == 0:
                    return (
                        EquivalenceStatus.SYMBOLIC_EQUIVALENT,
                        VerificationMethod.SYMBOLIC_CAS,
                        restrictions,
                        None,
                        None,
                    )

            # 4. Rational Together Check (Common in Ohm's law, gravitation, kinetic energy)
            together_diff = sympy.together(diff)
            n, _ = sympy.fraction(together_diff)
            if sympy.simplify(n) == 0:
                return (
                    EquivalenceStatus.SYMBOLIC_EQUIVALENT,
                    VerificationMethod.SYMBOLIC_CAS,
                    restrictions,
                    None,
                    None,
                )

            if simplified.is_number and simplified != 0:
                return (
                    EquivalenceStatus.SYMBOLIC_NON_EQUIVALENT,
                    VerificationMethod.SYMBOLIC_CAS,
                    restrictions,
                    None,
                    f"Constant physics difference: {simplified}",
                )

            return (
                EquivalenceStatus.SYMBOLIC_NON_EQUIVALENT,
                VerificationMethod.SYMBOLIC_CAS,
                restrictions,
                None,
                "Physics expressions are not algebraically equivalent",
            )

        except Exception as e:
            return EquivalenceStatus.INCONCLUSIVE, VerificationMethod.NONE, restrictions, None, f"Physics verification exception: {str(e)}"
