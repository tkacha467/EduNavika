"""
Isolated LaTeX parser for Mathematical Equivalence Framework (Milestone 4.5).
Translates raw LaTeX strings into SymPy AST representations or structured relations.
"""
import re
from typing import Optional, Tuple, Any, Dict, List
import sympy
from sympy.parsing.latex import parse_latex


class ParseResult:
    def __init__(
        self,
        raw_latex: str,
        cleaned_latex: str,
        is_relation: bool,
        relation_op: Optional[str] = None,
        sympy_expr: Optional[Any] = None,
        lhs_expr: Optional[Any] = None,
        rhs_expr: Optional[Any] = None,
        error: Optional[str] = None,
        free_symbols: Optional[List[str]] = None,
    ):
        self.raw_latex = raw_latex
        self.cleaned_latex = cleaned_latex
        self.is_relation = is_relation
        self.relation_op = relation_op
        self.sympy_expr = sympy_expr
        self.lhs_expr = lhs_expr
        self.rhs_expr = rhs_expr
        self.error = error
        self.free_symbols = free_symbols or []

    @property
    def is_success(self) -> bool:
        return self.error is None and (self.sympy_expr is not None or (self.lhs_expr is not None and self.rhs_expr is not None))


class LaTeXParser:
    """
    Hermetic LaTeX parser that converts textbook LaTeX formulas to SymPy AST objects.
    """

    @staticmethod
    def clean_presentation_noise(latex: str) -> str:
        """
        Strips visual typography macros that carry no mathematical semantics.
        """
        if not latex:
            return ""

        s = latex.strip()

        # Strip presentation whitespace
        s = re.sub(r"\\(?:quad|qquad|enspace|thinspace|negthinspace|medspace|thickspace)", " ", s)
        s = re.sub(r"\\[,;!:]", " ", s)
        s = re.sub(r"\\hspace\{[^}]*\}", " ", s)
        s = re.sub(r"\\vspace\{[^}]*\}", " ", s)

        # Standardize brackets and sizing
        s = re.sub(r"\\(?:left|right|big|Big|bigg|Bigg)", "", s)

        # Normalize text and font wrappers: \text{...}, \mathbf{...}, \mathit{...}, \mathrm{...}
        s = re.sub(r"\\(?:text|mathrm|mathbf|mathit|mathsf|mathtt)\{([^{}]+)\}", r"\1", s)

        # Standardize multiplication symbols
        s = re.sub(r"\\times\b", "*", s)
        s = re.sub(r"\\cdot\b", "*", s)

        # Standardize division
        s = re.sub(r"\\div\b", "/", s)

        # Standardize binary \pm (when preceded by an operand, it behaves additively: -b \pm \sqrt -> -b + \pm \sqrt)
        s = re.sub(r"([a-zA-Z0-9_\}\)])\s*\\pm\s*", r"\1 + \\pm ", s)

        # Normalize display math fences
        s = re.sub(r"^\$\$|\$\$$", "", s)
        s = re.sub(r"^\$|\$$", "", s)
        s = re.sub(r"^\\\[|\\\]$", "", s)
        s = re.sub(r"^\\\(|\\\)$", "", s)

        # Normalize curly braces on simple subscripts/superscripts: x_1 -> x_{1}
        s = re.sub(r"_([a-zA-Z0-9])\b", r"_{\1}", s)
        s = re.sub(r"\^([a-zA-Z0-9])\b", r"^{\1}", s)

        # Normalize \bar{x} -> x_bar
        s = re.sub(r"\\bar\{([^{}]+)\}", r"\1_bar", s)
        s = re.sub(r"\\bar\s+([a-zA-Z0-9])", r"\1_bar", s)

        # Normalize \sum -> S_
        s = re.sub(r"\\sum\s*", "S_", s)

        # Compress spaces
        s = re.sub(r"\s+", " ", s).strip()
        return s

    @classmethod
    def _parse_single_expr(cls, expr_str: str) -> Tuple[Optional[Any], Optional[str]]:
        """
        Parses a non-relational sub-expression with SymPy parse_latex or as coordinate tuple.
        """
        s = expr_str.strip()
        if not s:
            return None, "Empty expression string"

        # Check for coordinate tuple (expr1, expr2)
        if s.startswith("(") and s.endswith(")") and "," in s:
            inner = s[1:-1].strip()
            # Split on comma not nested within brackets or braces
            parts = cls._split_top_level_comma(inner)
            if len(parts) >= 2:
                parsed_coords = []
                for p in parts:
                    sub_e, sub_err = cls._parse_single_expr(p)
                    if sub_err or sub_e is None:
                        return None, f"Tuple coordinate parse error: {sub_err}"
                    parsed_coords.append(sub_e)
                return sympy.Tuple(*parsed_coords), None

        try:
            # Handle standard parse_latex
            expr = parse_latex(s)
            return expr, None
        except Exception as e1:
            # Fallback 1: replace compound subscripts with valid SymPy symbol names
            # e.g., x_{1} -> x_1, S_{n} -> S_n
            try:
                s_sub = re.sub(r"([a-zA-Z])_\{([a-zA-Z0-9]+)\}", r"\1_\2", s)
                if s_sub != s:
                    expr = parse_latex(s_sub)
                    return expr, None
            except Exception:
                pass

            # Fallback 2: convert inline fractions 'a / b' to '\frac{a}{b}' if parse_latex rejected plain slash
            try:
                s_frac = re.sub(r"([a-zA-Z0-9_+^]+)\s*/\s*([a-zA-Z0-9_+^]+)", r"\\frac{\1}{\2}", s)
                if s_frac != s:
                    expr = parse_latex(s_frac)
                    return expr, None
            except Exception:
                pass

            return None, f"LaTeX parse error: {str(e1)}"

    @classmethod
    def _split_top_level_comma(cls, s: str) -> List[str]:
        """
        Splits a comma-separated string only on commas at the top bracket/brace depth.
        """
        parts = []
        current = []
        depth = 0
        for char in s:
            if char in "({[":
                depth += 1
                current.append(char)
            elif char in ")}]":
                depth -= 1
                current.append(char)
            elif char == "," and depth == 0:
                parts.append("".join(current).strip())
                current = []
            else:
                current.append(char)
        if current:
            parts.append("".join(current).strip())
        return parts

    @classmethod
    def parse(cls, raw_latex: str) -> ParseResult:
        """
        Parse raw LaTeX into a ParseResult containing SymPy ASTs.
        """
        if not raw_latex or not raw_latex.strip():
            return ParseResult(
                raw_latex=raw_latex or "",
                cleaned_latex="",
                is_relation=False,
                error="Empty or null LaTeX input",
            )

        cleaned = cls.clean_presentation_noise(raw_latex)

        # Detect relational operators (=, <=, >=, <, >)
        # Prioritize '='
        rel_match = None
        for op in ["<=", ">=", "\\le", "\\ge", "\\leq", "\\geq", "=", "<", ">"]:
            if op in cleaned:
                rel_match = op
                break

        if rel_match:
            # Split into LHS and RHS
            parts = cleaned.split(rel_match, 1)
            lhs_str = parts[0].strip()
            rhs_str = parts[1].strip()

            if not lhs_str or not rhs_str:
                return ParseResult(
                    raw_latex=raw_latex,
                    cleaned_latex=cleaned,
                    is_relation=True,
                    relation_op=rel_match,
                    error=f"Malformed relation with missing LHS or RHS: '{cleaned}'",
                )

            lhs_expr, lhs_err = cls._parse_single_expr(lhs_str)
            rhs_expr, rhs_err = cls._parse_single_expr(rhs_str)

            if lhs_err or rhs_err:
                err = f"Relation parse error: LHS=[{lhs_err or 'OK'}], RHS=[{rhs_err or 'OK'}]"
                return ParseResult(
                    raw_latex=raw_latex,
                    cleaned_latex=cleaned,
                    is_relation=True,
                    relation_op=rel_match,
                    error=err,
                )

            symbols = set()
            if lhs_expr is not None and hasattr(lhs_expr, "free_symbols"):
                symbols.update(str(sym) for sym in lhs_expr.free_symbols)
            if rhs_expr is not None and hasattr(rhs_expr, "free_symbols"):
                symbols.update(str(sym) for sym in rhs_expr.free_symbols)

            return ParseResult(
                raw_latex=raw_latex,
                cleaned_latex=cleaned,
                is_relation=True,
                relation_op=rel_match,
                lhs_expr=lhs_expr,
                rhs_expr=rhs_expr,
                free_symbols=sorted(list(symbols)),
            )

        # Single expression
        expr, err = cls._parse_single_expr(cleaned)
        if err:
            return ParseResult(
                raw_latex=raw_latex,
                cleaned_latex=cleaned,
                is_relation=False,
                error=err,
            )

        symbols = []
        if expr is not None and hasattr(expr, "free_symbols"):
            symbols = sorted([str(sym) for sym in expr.free_symbols])

        return ParseResult(
            raw_latex=raw_latex,
            cleaned_latex=cleaned,
            is_relation=False,
            sympy_expr=expr,
            free_symbols=symbols,
        )
