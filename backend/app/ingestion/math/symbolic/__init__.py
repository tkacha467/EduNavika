"""
Milestone 4.5 Mathematical Equivalence Framework.
"""
from backend.app.ingestion.math.symbolic.schemas import (
    EquivalenceStatus,
    MathCategory,
    VerificationMethod,
    EquivalenceResult,
    DomainRestriction,
    RestrictionType,
    RestrictionSource,
    NumericalSamplingDetails,
)
from backend.app.ingestion.math.symbolic.parser import LaTeXParser, ParseResult
from backend.app.ingestion.math.symbolic.dispatcher import CategoryDispatcher
from backend.app.ingestion.math.symbolic.evaluator import MathematicalEquivalenceEngine

__all__ = [
    "EquivalenceStatus",
    "MathCategory",
    "VerificationMethod",
    "EquivalenceResult",
    "DomainRestriction",
    "RestrictionType",
    "RestrictionSource",
    "NumericalSamplingDetails",
    "LaTeXParser",
    "ParseResult",
    "CategoryDispatcher",
    "MathematicalEquivalenceEngine",
]
