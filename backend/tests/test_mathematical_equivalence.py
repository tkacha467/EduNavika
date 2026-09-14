"""
Unit tests for Milestone 4.5 Mathematical Equivalence Framework.
Tests valid positive equivalences, independent categorical dispatch, and domain restriction logging.
"""
import pytest
from backend.app.ingestion.math.symbolic import (
    MathematicalEquivalenceEngine,
    EquivalenceStatus,
    MathCategory,
    VerificationMethod,
    RestrictionType,
)


class TestMathematicalEquivalenceEngine:
    @pytest.fixture(scope="class")
    @classmethod
    def engine(cls):
        return MathematicalEquivalenceEngine()

    def test_arithmetic_equivalence(self, engine):
        r = engine.evaluate(r"\frac{3}{4} + \frac{1}{2}", "0.75 + 0.5")
        assert r.status == EquivalenceStatus.SYMBOLIC_EQUIVALENT
        assert r.target_category == MathCategory.ARITHMETIC
        assert r.extracted_category == MathCategory.ARITHMETIC

    def test_polynomial_commutativity(self, engine):
        r = engine.evaluate("y + x = z", "x + y = z")
        assert r.status == EquivalenceStatus.SYMBOLIC_EQUIVALENT
        assert r.verification_method == VerificationMethod.SYMBOLIC_CAS
        assert r.target_category == MathCategory.ALGEBRA

    def test_polynomial_expansion(self, engine):
        r = engine.evaluate("x^2 + 2xy + y^2", "(x + y)^2")
        assert r.status == EquivalenceStatus.SYMBOLIC_EQUIVALENT

    def test_fraction_coefficient_representation(self, engine):
        r = engine.evaluate(r"\frac{x}{2}", r"\frac{1}{2}x")
        assert r.status == EquivalenceStatus.SYMBOLIC_EQUIVALENT

    def test_quadratic_formula_reordering(self, engine):
        r = engine.evaluate(
            r"x = \frac{\pm \sqrt{b^2 - 4ac} - b}{2a}",
            r"x = \frac{-b \pm \sqrt{b^2 - 4ac}}{2a}",
        )
        assert r.status in (EquivalenceStatus.SYMBOLIC_EQUIVALENT, EquivalenceStatus.NUMERICALLY_EQUIVALENT)

    def test_trigonometric_pythagorean_identity(self, engine):
        r = engine.evaluate(r"\cos^2\theta + \sin^2\theta = 1", r"\sin^2\theta + \cos^2\theta = 1")
        assert r.status == EquivalenceStatus.SYMBOLIC_EQUIVALENT
        assert r.target_category == MathCategory.TRIGONOMETRY

    def test_physics_formula_atomic_subscripts(self, engine):
        r = engine.evaluate(r"F = G \frac{m_1 m_2}{r^2}", r"F = \frac{G m_1 m_2}{r^2}")
        assert r.status == EquivalenceStatus.SYMBOLIC_EQUIVALENT
        assert r.target_category == MathCategory.PHYSICS
        phys_restrictions = [res for res in r.domain_restrictions if res.restriction_type == RestrictionType.EXPLICIT_PHYSICAL_ASSUMPTION]
        assert len(phys_restrictions) > 0

    def test_rational_domain_pole_logging(self, engine):
        r = engine.evaluate(r"\frac{a}{b} = c", r"\frac{a}{b} = c")
        assert r.status == EquivalenceStatus.SYMBOLIC_EQUIVALENT
        poles = [res for res in r.domain_restrictions if res.restriction_type == RestrictionType.SINGULARITY_POLE]
        assert len(poles) == 1
        assert poles[0].variable == "b"
        assert poles[0].condition == "!= 0"

    def test_independent_category_disagreement_logging(self, engine):
        r = engine.evaluate("42", "E = mc^2")
        assert r.status in (EquivalenceStatus.SYMBOLIC_NON_EQUIVALENT, EquivalenceStatus.PARSE_ERROR)
        assert r.target_category == MathCategory.PHYSICS
        assert r.extracted_category == MathCategory.ARITHMETIC
        assert r.category_agreement is False

    def test_unsupported_chemistry_handling(self, engine):
        r = engine.evaluate(
            r"3\text{Fe} + 4\text{H}_2\text{O} \rightarrow \text{Fe}_3\text{O}_4 + 4\text{H}_2",
            r"3\text{Fe} + 4\text{H}_2\text{O} \rightarrow \text{Fe}_3\text{O}_4 + 4\text{H}_2",
        )
        assert r.status == EquivalenceStatus.UNSUPPORTED
        assert r.target_category == MathCategory.UNSUPPORTED_CHEMISTRY

    def test_latency_tracking(self, engine):
        stats = engine.get_latency_stats()
        assert "mean_ms" in stats
        assert "median_ms" in stats
        assert "p95_ms" in stats
        assert "max_ms" in stats
        assert stats["count"] >= 10
