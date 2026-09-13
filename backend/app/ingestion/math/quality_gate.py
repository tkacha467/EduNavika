"""
Milestone 4.4: Mathematical Quality Gate
Fast, deterministic gate that inspects extracted text to classify whether a page
or chunk contains clean prose or math-heavy / corrupted mathematical notation
requiring targeted mathematical recovery.
"""

import re
from typing import Dict, Any, List


class MathQualityGate:
    """
    Evaluates text for mathematical notation presence and corruption indicators.
    """

    MATH_OPERATORS = set("=+-*/^<≤>≥≠±×÷√∑∏∫∂∇∼⊥∠°")
    GREEK_SYMBOLS = set("αβγδεζηθικλμνξπρστυφχψωΔΣΩ")
    MATH_KEYWORDS = {
        "formula", "equation", "theorem", "lemma", "polynomial", "quadratic",
        "discriminant", "sin", "cos", "tan", "cot", "sec", "csc",
        "log", "lim", "matrix", "vector", "hypotenuse", "pythagoras"
    }

    # Patterns indicating corrupted PDF text extraction
    CORRUPTION_PATTERNS = [
        re.compile(r'[a-zA-Z]\s*\d+\s*[a-zA-Z]\s*\d+'),      # e.g., 'x2 y2' or 'x1 y1' missing subscripts
        re.compile(r'\(\s*[a-zA-Z]\s*\d+\s*,\s*[a-zA-Z]'),    # e.g., 'P(x1, y1)'
        re.compile(r'\d+\s*[a-zA-Z]+\s*[-+−]\s*\d+'),         # e.g., scrambled linear term
        re.compile(r'\b[a-zA-Z]\s*2\s*[-+]\s*[a-zA-Z]\s*2\b'), # e.g., 'x 2 + y 2' instead of 'x² + y²'
        re.compile(r'[\u2212\u221a\u2248\u2260\u2264\u2265]'), # Math Unicode symbols often isolated
        re.compile(r'\b[a-zA-Z]_\d+\b'),                      # Extracted raw LaTeX subscript
        re.compile(r'\b[a-zA-Z]\^\d+\b'),                      # Extracted raw LaTeX power
    ]

    def analyze(self, text: str) -> Dict[str, Any]:
        """
        Analyze text string and decide if it contains mathematical regions
        requiring targeted extraction.
        """
        if not text or len(text.strip()) < 5:
            return {
                "is_math_heavy": False,
                "needs_recovery": False,
                "math_score": 0.0,
                "reasons": ["empty_or_too_short"],
                "confidence": 1.0
            }

        reasons = []
        math_score = 0.0

        # 1. Math symbol density
        sym_count = sum(1 for ch in text if ch in self.MATH_OPERATORS or ch in self.GREEK_SYMBOLS)
        if sym_count >= 2:
            math_score += min(sym_count * 0.15, 0.45)
            reasons.append(f"math_symbols_detected_{sym_count}")

        # 2. Math keywords
        words = set(re.findall(r'\b[a-zA-Z]{2,}\b', text.lower()))
        matched_kw = words.intersection(self.MATH_KEYWORDS)
        if matched_kw:
            math_score += min(len(matched_kw) * 0.15, 0.35)
            reasons.append(f"math_keywords_{','.join(list(matched_kw)[:3])}")

        # 3. Known equation structures
        if "=" in text:
            # Check if '=' is surrounded by algebraic variables or numbers
            if re.search(r'[a-zA-Z0-9]\s*=\s*[a-zA-Z0-9]', text):
                math_score += 0.3
                reasons.append("algebraic_equality")

        # 4. Corruption signals
        corruption_hits = 0
        for pattern in self.CORRUPTION_PATTERNS:
            if pattern.search(text):
                corruption_hits += 1

        if corruption_hits > 0:
            math_score += min(corruption_hits * 0.2, 0.4)
            reasons.append(f"corruption_patterns_hit_{corruption_hits}")

        is_math_heavy = math_score >= 0.35
        needs_recovery = math_score >= 0.45 or (is_math_heavy and corruption_hits > 0)

        return {
            "is_math_heavy": is_math_heavy,
            "needs_recovery": needs_recovery,
            "math_score": round(min(math_score, 1.0), 3),
            "reasons": reasons,
            "confidence": round(min(0.5 + (math_score * 0.5), 0.99), 2)
        }
