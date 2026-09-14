"""
Schemas and data structures for Milestone 4.5 Mathematical Equivalence Framework.
"""
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional, Any, Dict


class EquivalenceStatus(str, Enum):
    SYMBOLIC_EQUIVALENT = "SYMBOLIC_EQUIVALENT"
    SYMBOLIC_NON_EQUIVALENT = "SYMBOLIC_NON_EQUIVALENT"
    NUMERICALLY_EQUIVALENT = "NUMERICALLY_EQUIVALENT"
    NUMERICALLY_NON_EQUIVALENT = "NUMERICALLY_NON_EQUIVALENT"
    INCONCLUSIVE = "INCONCLUSIVE"
    PARSE_ERROR = "PARSE_ERROR"
    UNSUPPORTED = "UNSUPPORTED"


class MathCategory(str, Enum):
    ARITHMETIC = "ARITHMETIC"
    ALGEBRA = "ALGEBRA"
    RATIONAL = "RATIONAL"
    RADICAL = "RADICAL"
    TRIGONOMETRY = "TRIGONOMETRY"
    PHYSICS = "PHYSICS"
    COORDINATE_GEOMETRY = "COORDINATE_GEOMETRY"
    UNSUPPORTED_CHEMISTRY = "UNSUPPORTED_CHEMISTRY"
    UNSUPPORTED_GEOMETRY_PROOF = "UNSUPPORTED_GEOMETRY_PROOF"
    UNSUPPORTED_ELLIPSIS = "UNSUPPORTED_ELLIPSIS"
    UNKNOWN = "UNKNOWN"


class RestrictionType(str, Enum):
    SINGULARITY_POLE = "SINGULARITY_POLE"                  # e.g., denominator != 0 (pole)
    NATURAL_DOMAIN_BOUNDARY = "NATURAL_DOMAIN_BOUNDARY"    # e.g., radicand >= 0, log argument > 0
    EXPLICIT_PHYSICAL_ASSUMPTION = "EXPLICIT_PHYSICAL_ASSUMPTION"  # e.g., mass > 0, radius > 0
    BRANCH_CUT_CONDITION = "BRANCH_CUT_CONDITION"          # e.g., theta in (-pi, pi]


class RestrictionSource(str, Enum):
    INFERRED_DENOMINATOR = "INFERRED_DENOMINATOR"
    INFERRED_RADICAL = "INFERRED_RADICAL"
    INFERRED_LOGARITHM = "INFERRED_LOGARITHM"
    PHYSICAL_MODEL = "PHYSICAL_MODEL"
    USER_DECLARED = "USER_DECLARED"


@dataclass
class DomainRestriction:
    variable: str
    condition: str  # e.g., "!= 0", ">= 0", "> 0"
    restriction_type: RestrictionType
    source: RestrictionSource
    expression: str  # The term giving rise to restriction, e.g., "x - 1" in denominator

    def to_dict(self) -> Dict[str, Any]:
        return {
            "variable": self.variable,
            "condition": self.condition,
            "restriction_type": self.restriction_type.value,
            "source": self.source.value,
            "expression": self.expression,
        }


class VerificationMethod(str, Enum):
    SYMBOLIC_CAS = "SYMBOLIC_CAS"
    POLYNOMIAL_SCHWARTZ_ZIPPEL = "POLYNOMIAL_SCHWARTZ_ZIPPEL_PROBABILISTIC"
    BOUNDED_NUMERICAL_SAMPLING = "BOUNDED_NUMERICAL_SAMPLING"
    DIRECT_RATIONAL_REDUCTION = "DIRECT_RATIONAL_REDUCTION"
    NONE = "NONE"


@dataclass
class NumericalSamplingDetails:
    sample_count: int = 0
    sampling_domain: str = ""
    tolerance: float = 1e-12
    max_observed_diff: float = 0.0
    is_probabilistic_identity_test: bool = False
    theoretical_error_bound: Optional[float] = None  # e.g., Schwartz-Zippel d / |S|

    def to_dict(self) -> Dict[str, Any]:
        return {
            "sample_count": self.sample_count,
            "sampling_domain": self.sampling_domain,
            "tolerance": self.tolerance,
            "max_observed_diff": self.max_observed_diff,
            "is_probabilistic_identity_test": self.is_probabilistic_identity_test,
            "theoretical_error_bound": self.theoretical_error_bound,
        }


@dataclass
class EquivalenceResult:
    status: EquivalenceStatus
    target_raw: str
    extracted_raw: str
    target_category: MathCategory
    extracted_category: MathCategory
    category_agreement: bool
    verification_method: VerificationMethod
    domain_restrictions: List[DomainRestriction] = field(default_factory=list)
    numerical_details: Optional[NumericalSamplingDetails] = None
    eval_time_ms: float = 0.0
    error_reason: Optional[str] = None
    details: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "status": self.status.value,
            "target_raw": self.target_raw,
            "extracted_raw": self.extracted_raw,
            "target_category": self.target_category.value,
            "extracted_category": self.extracted_category.value,
            "category_agreement": self.category_agreement,
            "verification_method": self.verification_method.value,
            "domain_restrictions": [r.to_dict() for r in self.domain_restrictions],
            "numerical_details": self.numerical_details.to_dict() if self.numerical_details else None,
            "eval_time_ms": round(self.eval_time_ms, 3),
            "error_reason": self.error_reason,
            "details": self.details,
        }
