"""
Categorical Classifier and Dispatcher for Mathematical Equivalence (Milestone 4.5).
Independently classifies prediction and ground-truth ASTs without cross-contamination.
"""
import re
from typing import Any, Set
from backend.app.ingestion.math.symbolic.schemas import MathCategory
from backend.app.ingestion.math.symbolic.parser import ParseResult


class CategoryDispatcher:
    """
    Classifies a mathematical expression into one of the formal MathCategory types.
    Executed independently on prediction and ground truth.
    """

    CHEMISTRY_INDICATORS = [
        r"\\rightarrow", r"->", r"\\rightleftharpoons",
        r"\b(?:Fe|H2O|CuSO4|Zn|HCl|NaCl|NaOH|H2SO4|CaCO3|CaO|CO2|O2|H2|Pb|AgCl|BaSO4)\b",
        r"\(s\)", r"\(l\)", r"\(g\)", r"\(aq\)",
    ]

    GEOMETRY_PROOF_INDICATORS = [
        r"\\cong", r"\\parallel", r"\\perp", r"\\angle", r"\\Delta\s*[A-Z]{3}",
    ]

    TRIG_FUNCTIONS = {
        "sin", "cos", "tan", "cot", "sec", "csc",
        "arcsin", "arccos", "arctan", "theta", "\\theta", "\\phi", "\\alpha", "\\beta",
    }

    PHYSICS_VARIABLES = {
        "v_0", "m_1", "m_2", "v_1", "v_2", "r^2", "mc^2",
        "\\Omega", "ohm", "ampere", "volt", "joule", "watt",
        "R_1", "R_2", "R_3", "R_s", "R_p", "I_1", "I_2",
    }

    @classmethod
    def classify(cls, parse_result: ParseResult) -> MathCategory:
        """
        Classifies a ParseResult based strictly on its own content.
        """
        raw = parse_result.raw_latex
        cleaned = parse_result.cleaned_latex

        # 1. Check for Unsupported Chemistry
        for pattern in cls.CHEMISTRY_INDICATORS:
            if re.search(pattern, raw, re.IGNORECASE):
                return MathCategory.UNSUPPORTED_CHEMISTRY

        # 2. Check for Unsupported Geometry Proofs
        for pattern in cls.GEOMETRY_PROOF_INDICATORS:
            if re.search(pattern, raw):
                return MathCategory.UNSUPPORTED_GEOMETRY_PROOF

        # 3. Check for Unsupported Ellipsis / Open Series
        if r"\dots" in raw or r"\cdots" in raw or "..." in raw:
            return MathCategory.UNSUPPORTED_ELLIPSIS

        # 4. Check for Arithmetic (no free variables)
        if parse_result.is_success and len(parse_result.free_symbols) == 0:
            return MathCategory.ARITHMETIC

        # Also inspect raw text for arithmetic if parse failed
        if not re.search(r"[a-zA-Z]", cleaned) or re.match(r"^[\d\s\+\-\*\/\=\.\,\(\)\^\{\}\\]+$", cleaned):
            return MathCategory.ARITHMETIC

        # 5. Check Trigonometry
        for trig_token in cls.TRIG_FUNCTIONS:
            if trig_token in cleaned or trig_token in raw:
                return MathCategory.TRIGONOMETRY

        # 6. Check Physics equations
        for phys in cls.PHYSICS_VARIABLES:
            if phys in raw or phys in cleaned:
                return MathCategory.PHYSICS
        # Standard physics formulas check
        if re.search(r"\b[QVIREFPW]\s*=\s*", cleaned) and any(sym in cleaned for sym in ["I", "V", "R", "t", "m", "c", "F", "a"]):
            return MathCategory.PHYSICS

        # 7. Check Coordinate Geometry
        if re.search(r"x_[12]|y_[12]|x_1|x_2|y_1|y_2", cleaned):
            if "sqrt" in cleaned or "\\sqrt" in raw or "r^2" in cleaned:
                return MathCategory.COORDINATE_GEOMETRY

        # 8. Check Radicals
        if "\\sqrt" in raw or "sqrt(" in cleaned:
            return MathCategory.RADICAL

        # 9. Check Rational Functions (variables in denominator)
        if cls._has_rational_denominator(parse_result):
            return MathCategory.RATIONAL

        # 10. Default to general Algebra
        if parse_result.is_success or re.search(r"[a-zA-Z]", cleaned):
            return MathCategory.ALGEBRA

        return MathCategory.UNKNOWN

    @classmethod
    def _has_rational_denominator(cls, parse_result: ParseResult) -> bool:
        """
        Detects if an expression has free variables appearing in a denominator.
        """
        # Check raw text pattern: \frac{...}{...variable...} or / (variable)
        if re.search(r"\\frac\{[^}]*\}\{[^}]*[a-zA-Z][^}]*\}", parse_result.raw_latex):
            return True
        if re.search(r"\/\s*\([^\)]*[a-zA-Z][^\)]*\)", parse_result.cleaned_latex):
            return True

        # Check SymPy AST if available
        if parse_result.is_success:
            exprs = [parse_result.sympy_expr] if not parse_result.is_relation else [parse_result.lhs_expr, parse_result.rhs_expr]
            for expr in exprs:
                if expr is not None and hasattr(expr, "as_numer_denom"):
                    try:
                        _, denom = expr.as_numer_denom()
                        if hasattr(denom, "free_symbols") and len(denom.free_symbols) > 0:
                            return True
                    except Exception:
                        pass
        return False
