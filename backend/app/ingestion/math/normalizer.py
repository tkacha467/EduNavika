"""
Milestone 4.4: Canonical LaTeX Normalizer
Transforms raw mathematical OCR / text strings into valid, canonical LaTeX representation
using mathematically justified deterministic conversions.
"""

import re
from typing import Optional


class CanonicalLaTeXNormalizer:
    """
    Normalizes mathematical OCR output into standard, canonical LaTeX markup.
    Guaranteed not to modify plain prose strings that lack mathematical indicators.
    """

    SUPERSCRIPT_MAP = {
        '²': '^2', '³': '^3', '⁴': '^4', '⁵': '^5', '⁶': '^6', '⁷': '^7', '⁸': '^8', '⁹': '^9', '⁰': '^0',
        'ⁿ': '^n', 'ⁱ': '^i', '⁺': '^+', '⁻': '^-'
    }

    SUBSCRIPT_MAP = {
        '₁': '_1', '₂': '_2', '₃': '_3', '₄': '_4', '₅': '_5', '₆': '_6', '₇': '_7', '₈': '_8', '₉': '_9', '₀': '_0',
        'ᵢ': '_i', 'ⱼ': '_j', 'ₖ': '_k', 'ₙ': '_n', 'ₘ': '_m'
    }

    GREEK_MAP = {
        'α': r'\alpha', 'β': r'\beta', 'γ': r'\gamma', 'δ': r'\delta', 'θ': r'\theta',
        'λ': r'\lambda', 'μ': r'\mu', 'π': r'\pi', 'ρ': r'\rho', 'σ': r'\sigma',
        'φ': r'\phi', 'ω': r'\omega', 'Δ': r'\Delta', 'Σ': r'\sum', 'Ω': r'\Omega'
    }

    OPERATOR_MAP = {
        '±': r'\pm', '∓': r'\mp', '×': r'\times', '·': r'\cdot', '÷': r'\div',
        '≤': r'\le', '≥': r'\ge', '≠': r'\ne', '≈': r'\approx', '∼': r'\sim',
        '⊥': r'\perp', '∠': r'\angle', '°': r'^\circ', '→': r'\rightarrow',
        '−': '-', '–': '-'
    }

    @classmethod
    def is_likely_mathematical(cls, text: str) -> bool:
        """Determines if the string contains actual mathematical tokens or structure."""
        if not text:
            return False
        # Check for special mathematical characters
        special_chars = (
            set(cls.SUPERSCRIPT_MAP.keys()) |
            set(cls.SUBSCRIPT_MAP.keys()) |
            set(cls.GREEK_MAP.keys()) |
            set(cls.OPERATOR_MAP.keys()) |
            {'√', '^', '_', '\\'}
        )
        if any(c in special_chars for c in text):
            return True
        # Check for equation-like assignment / equality
        if re.search(r'[a-zA-Z0-9]\s*=\s*[a-zA-Z0-9]', text):
            return True
        return False

    @classmethod
    def normalize(cls, raw_text: str) -> str:
        """
        Convert mathematical OCR output into canonical LaTeX.
        If the text is plain prose, returns it unmodified.
        """
        if not raw_text or not cls.is_likely_mathematical(raw_text):
            return raw_text

        text = raw_text.strip()

        # 1. Normalize Unicode minus and dashes to standard hyphen/minus
        text = text.replace('−', '-').replace('–', '-')

        # 2. Convert Unicode superscripts
        for sup, lat in cls.SUPERSCRIPT_MAP.items():
            text = text.replace(sup, lat)

        # 3. Convert Unicode subscripts
        for sub, lat in cls.SUBSCRIPT_MAP.items():
            text = text.replace(sub, lat)

        # 4. Convert Greek letters
        for grk, lat in cls.GREEK_MAP.items():
            text = text.replace(grk, ' ' + lat + ' ')

        # 5. Convert Mathematical Operators
        for op, lat in cls.OPERATOR_MAP.items():
            if op not in ('-',):
                text = text.replace(op, ' ' + lat + ' ')

        # 6. Normalize radicals (square roots)
        # e.g. √(x2 - x1) or √{...} or √x
        # Match √(expr) -> \sqrt{expr}
        text = re.sub(r'√\s*\(([^)]+)\)', r'\\sqrt{\1}', text)
        text = re.sub(r'√\s*\{([^}]+)\}', r'\\sqrt{\1}', text)
        text = re.sub(r'√\s*([a-zA-Z0-9]+)', r'\\sqrt{\1}', text)

        # 7. Normalize simple horizontal fractions in formula context
        # e.g. (a)/(b) -> \frac{a}{b} or \frac a b
        text = re.sub(r'\\frac\s+([a-zA-Z0-9_]+)\s+([a-zA-Z0-9_]+)', r'\\frac{\1}{\2}', text)

        # 8. Variable subscript heuristic for common textbook OCR dropouts
        # e.g. x2 -> x_2, y1 -> y_1 when preceded by variable and in formula context
        text = re.sub(r'\b([a-zA-Z])([0-9])\b', r'\1_\2', text)

        # 9. Clean excessive spaces
        text = re.sub(r'\s+', ' ', text).strip()

        # Fix spacing around LaTeX commands
        text = re.sub(r'\s*([_^])\s*', r'\1', text)
        text = re.sub(r'\\([a-zA-Z]+)\s+([0-9a-zA-Z])', r'\\\1 \2', text)

        return text
