import re
import enum
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field

class MathPageClassification(str, enum.Enum):
    NORMAL = "NORMAL"
    MATH_PRESENT = "MATH_PRESENT"
    MATH_HEAVY = "MATH_HEAVY"

@dataclass
class MathDetectionResult:
    is_math: bool
    classification: MathPageClassification
    score: float
    signals: List[str] = field(default_factory=list)
    feature_counts: Dict[str, int] = field(default_factory=dict)
    confidence: float = 1.0

class MathPageDetector:
    """
    Lightweight, deterministic, explainable mathematical content detector.
    Analyzes raw text to classify pages into NORMAL, MATH_PRESENT, or MATH_HEAVY
    without requiring heavy neural models or LLMs.
    """

    # 1. Dedicated mathematical and Greek operators
    MATH_OPERATORS = [
        r'[\u2200-\u22FF]',                  # Mathematical operators: ∀, ∂, ∃, ∅, ∇, ∈, ∏, ∑, √, ∝, ∞, ∠, ∧, ∨, ∩, ∪, ∫, ∴, ∵, ≈, ≠, ≡, ≤, ≥
        r'[\u0391-\u03A9\u03B1-\u03C9]',      # Greek letters: α, β, γ, δ, θ, λ, μ, π, σ, φ, ω, etc.
        r'\\(?:frac|sqrt|alpha|beta|gamma|theta|pi|sigma|sum|int|pm|times|div|leq|geq|neq|approx|angle|partial)', # LaTeX
    ]

    # 2. Exponents, indices, and coordinate variables
    EXPONENTS_INDICES = [
        r'[\u00B2\u00B3\u00B9\u2070-\u2079]', # Unicode superscripts: ⁰, ¹, ², ³, ⁴...
        r'[\u2080-\u2089]',                   # Unicode subscripts: ₀, ₁, ₂, ₃...
        r'[a-zA-Z0-9]\^[0-9a-zA-Z\+\-]',     # Caret exponent: x^2, e^-x
        r'[a-zA-Z0-9]_[0-9a-zA-Z\+\-]',     # Subscript: x_1, S_n
        r'\b[xyzabmn][1234]\b',              # De-elevated subscript tokens: x1, y1, x2, y2
    ]

    # 3. Equation and algebraic relations
    EQUATIONS = [
        r'[a-zA-Z0-9]\s*[\+\-\*\/]\s*[a-zA-Z0-9]\s*=\s*[a-zA-Z0-9]', # e.g. y = mx + c, a + b = c
        r'\b\d+\s*[\+\-\*\/]\s*\d+\s*=\s*\d+\b',                     # 4 + 5 = 9
        r'\b[a-zA-Z]\s*=\s*[\+\-\d\w\(\)\/\\]+',                     # V = IR, P = 1/f
        r'\b[a-zA-Z]\s*[\+\-\=]\s*\d+\b',                           # x = 5, y + 2
    ]

    # 4. Trigonometry, logarithms, and geometric terms
    FUNCTIONS_AND_TERMS = [
        r'\b(?:sin|cos|tan|cot|sec|cosec|arcsin|arccos|arctan)\b',
        r'\b(?:log|ln)\b\s*[\(\d\w]',
        r'\b(?:quadratic|polynomial|hypotenuse|pythagoras|theorem|trigonometr|circumference|radicand|algebraic)\w*\b',
    ]

    # 5. Chemical formulas and reaction arrows
    CHEMICAL = [
        r'\\rightarrow|\u2192|->',                                    # Reaction arrows
        r'\b(?:H\+|OH\-|CO2|H2O|NaCl|CaCO3|MgO|H2SO4|C2H6)\b',        # Common chemical species without sub/sup
        r'(?:H\s*\+\s*\(aq\)|OH\s*\-\s*\(aq\))',                      # Ionic aqueous species
        r'[A-Z][a-z]?[0-9]*\s*\+\s*[A-Z][a-z]?[0-9]*\s*(?:->|\u2192|\\rightarrow)', # Reactions: Mg + O2 ->
    ]

    def __init__(
        self,
        math_present_threshold: float = 0.15,
        math_heavy_threshold: float = 0.45
    ):
        self.math_present_threshold = math_present_threshold
        self.math_heavy_threshold = math_heavy_threshold

        self._re_operators = [re.compile(p, re.IGNORECASE) for p in self.MATH_OPERATORS]
        self._re_exponents = [re.compile(p) for p in self.EXPONENTS_INDICES]
        self._re_equations = [re.compile(p, re.IGNORECASE) for p in self.EQUATIONS]
        self._re_functions = [re.compile(p, re.IGNORECASE) for p in self.FUNCTIONS_AND_TERMS]
        self._re_chemical = [re.compile(p, re.IGNORECASE) for p in self.CHEMICAL]

    def detect(self, text: str) -> MathDetectionResult:
        """
        Analyzes page text and produces an explainable MathDetectionResult.
        """
        if not text or len(text.strip()) == 0:
            return MathDetectionResult(
                is_math=False,
                classification=MathPageClassification.NORMAL,
                score=0.0,
                signals=[],
                feature_counts={"total_features": 0, "word_count": 0},
                confidence=1.0
            )

        words = text.split()
        word_count = max(len(words), 1)

        # Count individual feature groups
        op_count = sum(len(p.findall(text)) for p in self._re_operators)
        exp_count = sum(len(p.findall(text)) for p in self._re_exponents)
        eq_count = sum(len(p.findall(text)) for p in self._re_equations)
        fn_count = sum(len(p.findall(text)) for p in self._re_functions)
        chem_count = sum(len(p.findall(text)) for p in self._re_chemical)

        total_features = op_count + exp_count + eq_count + fn_count + chem_count
        signals = []

        if op_count > 0:
            signals.append(f"math_operators({op_count})")
        if exp_count > 0:
            signals.append(f"exponents_indices({exp_count})")
        if eq_count > 0:
            signals.append(f"equation_patterns({eq_count})")
        if fn_count > 0:
            signals.append(f"math_terms_functions({fn_count})")
        if chem_count > 0:
            signals.append(f"chemical_patterns({chem_count})")

        # Density score normalized against text length
        density = (total_features / word_count) * 10.0
        
        # Base score accounts for absolute feature presence + density
        presence_score = min(1.0, total_features / 10.0)
        composite_score = round(min(1.0, (presence_score * 0.6) + (min(1.0, density) * 0.4)), 3)

        feature_counts = {
            "operators": op_count,
            "exponents": exp_count,
            "equations": eq_count,
            "functions": fn_count,
            "chemical": chem_count,
            "total_features": total_features,
            "word_count": word_count,
            "density_per_100_words": round((total_features / word_count) * 100, 2)
        }

        # Classification decision
        if composite_score >= self.math_heavy_threshold or (total_features >= 6 and (exp_count >= 2 or eq_count >= 2)):
            classification = MathPageClassification.MATH_HEAVY
            is_math = True
        elif composite_score >= self.math_present_threshold or total_features >= 2:
            classification = MathPageClassification.MATH_PRESENT
            is_math = True
        else:
            classification = MathPageClassification.NORMAL
            is_math = False

        return MathDetectionResult(
            is_math=is_math,
            classification=classification,
            score=composite_score,
            signals=signals,
            feature_counts=feature_counts,
            confidence=round(min(1.0, 0.7 + (abs(composite_score - self.math_present_threshold) * 0.5)), 2)
        )
