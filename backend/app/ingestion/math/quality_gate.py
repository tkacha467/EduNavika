import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field

@dataclass
class MathValidationResult:
    is_safe: bool
    status: str  # "SAFE", "NEEDS_REVIEW", "CORRUPTED"
    has_math: bool
    detected_formulas_count: int
    detected_issues: List[str] = field(default_factory=list)
    confidence_score: float = 1.0

class MathQualityGate:
    """
    Quality gate for validating mathematical and scientific content
    before downstream ingestion, vector indexing, and RAG generation.
    
    Prevents corrupted equations (e.g., lost radicals, stripped exponents,
    broken chemical reactions) from entering the RAG context.
    """
    
    # Indicators that a text block contains mathematical or scientific expressions
    MATH_INDICATORS = [
        r'\b\d+\s*[\+\-\*\/=]\s*\d+\b',       # Simple arithmetic expressions
        r'[a-zA-Z]\s*[\+\-\*=]\s*[a-zA-Z0-9]', # Algebraic expressions
        r'\b(?:sin|cos|tan|cot|sec|cosec)\b',   # Trigonometry
        r'[\u00B2\u00B3\u00B9\u2070-\u2079]',  # Unicode superscripts
        r'[\u2080-\u2089]',                     # Unicode subscripts
        r'[\u2200-\u22FF]',                     # Mathematical operators (∀, ∂, ∃, ∅, ∇, ∈, ∏, ∑, √, ∝, ∞, ∠, ∧, ∨, ∩, ∪, ∫, ∴, ∵, ≈, ≠, ≡, ≤, ≥)
        r'\b(?:equation|formula|theorem|polynomial|quadratic)\b',
        r'\\(?:frac|sqrt|alpha|beta|theta|pi|sigma|sum|int|pm|times|div)', # LaTeX commands
    ]
    
    # Patterns indicating corrupted mathematical/chemical text from standard PDF extractors
    CORRUPTION_PATTERNS = [
        # Detached sequences of numbers following chemical/formula terms (e.g. "H O3 3 2 3 2 3 2")
        (r'\b[A-Z][a-z]?\s+(?:[0-9]\s+){3,}', "Detached subscript digit sequence from broken chemical formula"),
        # Broken bond chains (e.g. "- + - - - - - +")
        (r'(?:[\-\+\−]\s+){4,}', "Disordered bond/operator chain"),
        # Floating fractions where divisor line was stripped: e.g. standalone "1" and "2" without context
        (r'\b(?:fraction|ratio)\b[^\n]*?\n\s*\d+\s*\n\s*\d+\b', "Vertical fraction broken into disconnected numeric lines"),
        # Unbalanced brackets/parentheses inside formula-dense blocks
        (r'\([^\)\n]{20,}$', "Unclosed formula parenthesis at line boundary"),
        # Disconnected radical radicand: e.g. "√ " followed by blank or stripped expression
        (r'√\s*[\n\r]', "Orphaned radical symbol with lost radicand"),
    ]

    def __init__(self, reject_threshold: float = 0.5):
        self.reject_threshold = reject_threshold
        self._compiled_indicators = [re.compile(p, re.IGNORECASE) for p in self.MATH_INDICATORS]
        self._compiled_corruptions = [(re.compile(p, re.MULTILINE), desc) for p, desc in self.CORRUPTION_PATTERNS]

    def has_mathematical_content(self, text: str) -> bool:
        """Determines if the text contains mathematical or chemical notation."""
        if not text:
            return False
        return any(pattern.search(text) for pattern in self._compiled_indicators)

    def validate_chunk(self, content_text: str, chunk_id: Optional[str] = None) -> MathValidationResult:
        """
        Evaluates the mathematical integrity of a content chunk.
        Returns a structured MathValidationResult with safety status.
        """
        if not content_text or len(content_text.strip()) == 0:
            return MathValidationResult(
                is_safe=True,
                status="SAFE",
                has_math=False,
                detected_formulas_count=0,
                confidence_score=1.0
            )

        has_math = self.has_mathematical_content(content_text)
        if not has_math:
            return MathValidationResult(
                is_safe=True,
                status="SAFE",
                has_math=False,
                detected_formulas_count=0,
                confidence_score=1.0
            )

        issues = []
        # Check known corruption patterns
        for pattern, desc in self._compiled_corruptions:
            matches = pattern.findall(content_text)
            if matches:
                issues.append(f"{desc} (matches: {len(matches)})")

        # Check bracket parity on mathematical lines
        open_parens = content_text.count("(")
        close_parens = content_text.count(")")
        if abs(open_parens - close_parens) > 2:
            issues.append(f"Severe parenthesis imbalance (open={open_parens}, close={close_parens})")

        open_brackets = content_text.count("[")
        close_brackets = content_text.count("]")
        if abs(open_brackets - close_brackets) > 2:
            issues.append(f"Severe bracket imbalance (open={open_brackets}, close={close_brackets})")

        # Classification
        if len(issues) == 0:
            return MathValidationResult(
                is_safe=True,
                status="SAFE",
                has_math=True,
                detected_formulas_count=1,
                confidence_score=1.0
            )
        elif len(issues) == 1 and "imbalance" in issues[0]:
            return MathValidationResult(
                is_safe=True,
                status="NEEDS_REVIEW",
                has_math=True,
                detected_formulas_count=1,
                detected_issues=issues,
                confidence_score=0.7
            )
        else:
            return MathValidationResult(
                is_safe=False,
                status="CORRUPTED",
                has_math=True,
                detected_formulas_count=1,
                detected_issues=issues,
                confidence_score=round(max(0.1, 1.0 - (len(issues) * 0.3)), 2)
            )
