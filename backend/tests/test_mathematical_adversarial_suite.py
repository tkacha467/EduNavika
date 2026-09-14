"""
Milestone 4.5 Stratified 100-Case Adversarial Suite.
Verifies that the mathematical equivalence engine achieves ZERO false equivalences (0/100, 0% FPR)
across 10 distinct mathematical error categories (10 cases each).
"""
import pytest
from backend.app.ingestion.math.symbolic import (
    MathematicalEquivalenceEngine,
    EquivalenceStatus,
)


# 100 Stratified Adversarial Test Pairs (Target, Corrupted Prediction, Error Type)
ADVERSARIAL_CASES = [
    # Category 1: Sign Inversions (10 cases)
    ("x - y", "y - x", "SIGN_INVERSION"),
    ("a - b = c", "b - a = c", "SIGN_INVERSION"),
    ("x^2 - y^2", "y^2 - x^2", "SIGN_INVERSION"),
    ("-b + 2a", "b - 2a", "SIGN_INVERSION"),
    ("x - 1 = 0", "x + 1 = 0", "SIGN_INVERSION"),
    ("a - b - c", "a - b + c", "SIGN_INVERSION"),
    ("2x - 3y = 5", "2x + 3y = 5", "SIGN_INVERSION"),
    ("-x^2 + 4", "x^2 + 4", "SIGN_INVERSION"),
    (r"\frac{a - b}{c}", r"\frac{b - a}{c}", "SIGN_INVERSION"),
    ("1 - \\sin^2\\theta", "1 + \\sin^2\\theta", "SIGN_INVERSION"),

    # Category 2: Coefficient Mutations (10 cases)
    ("2x + 3y", "2x + 5y", "COEFFICIENT_MUTATION"),
    ("4x = 12", "5x = 12", "COEFFICIENT_MUTATION"),
    ("x^2 + 2xy + y^2", "x^2 + 3xy + y^2", "COEFFICIENT_MUTATION"),
    (r"\frac{1}{2}at^2", r"\frac{1}{3}at^2", "COEFFICIENT_MUTATION"),
    ("3a + 4b = 7", "3a + 5b = 7", "COEFFICIENT_MUTATION"),
    ("2\\pi r", "3\\pi r", "COEFFICIENT_MUTATION"),
    (r"\frac{n}{2}[2a + (n - 1)d]", r"\frac{n}{3}[2a + (n - 1)d]", "COEFFICIENT_MUTATION"),
    ("4x^3 - 2x", "4x^3 - 3x", "COEFFICIENT_MUTATION"),
    ("5x - 10 = 0", "5x - 15 = 0", "COEFFICIENT_MUTATION"),
    ("2x^2 + 4x + 1", "2x^2 + 5x + 1", "COEFFICIENT_MUTATION"),

    # Category 3: Degree and Exponent Errors (10 cases)
    ("x^2 + y^2", "x^3 + y^2", "DEGREE_EXPONENT_ERROR"),
    ("a^m \\cdot a^n = a^{m+n}", "a^m \\cdot a^n = a^{mn}", "DEGREE_EXPONENT_ERROR"),
    ("x^4 - 1", "x^2 - 1", "DEGREE_EXPONENT_ERROR"),
    ("r^3", "r^2", "DEGREE_EXPONENT_ERROR"),
    ("(x + 1)^2", "(x + 1)^3", "DEGREE_EXPONENT_ERROR"),
    ("x^{-1}", "x^{-2}", "DEGREE_EXPONENT_ERROR"),
    ("a^2 + b^2 = c^2", "a^3 + b^3 = c^3", "DEGREE_EXPONENT_ERROR"),
    ("t^2", "t", "DEGREE_EXPONENT_ERROR"),
    ("(a - b)^2", "(a - b)^4", "DEGREE_EXPONENT_ERROR"),
    ("x^5 + x^3", "x^5 + x^2", "DEGREE_EXPONENT_ERROR"),

    # Category 4: Denominator Omissions (10 cases)
    (r"\frac{a + b}{c}", "a + \\frac{b}{c}", "DENOMINATOR_OMISSION"),
    (r"\frac{x + y}{2}", "x + y", "DENOMINATOR_OMISSION"),
    (r"\frac{-b}{2a}", "-b", "DENOMINATOR_OMISSION"),
    (r"\frac{1}{x + y}", "1 + \\frac{1}{x + y}", "DENOMINATOR_OMISSION"),
    (r"\frac{m_1 + m_2}{2}", "m_1 + m_2", "DENOMINATOR_OMISSION"),
    (r"\frac{v^2}{r}", "v^2", "DENOMINATOR_OMISSION"),
    (r"\frac{a_1}{a_2}", "a_1", "DENOMINATOR_OMISSION"),
    (r"\frac{x_1 + x_2}{2}", "x_1 + x_2", "DENOMINATOR_OMISSION"),
    (r"\frac{k q_1 q_2}{r^2}", "k q_1 q_2", "DENOMINATOR_OMISSION"),
    (r"\frac{1}{R_1} + \frac{1}{R_2}", "R_1 + R_2", "DENOMINATOR_OMISSION"),

    # Category 5: Radicand Truncations (10 cases)
    (r"\sqrt{x + 1}", r"\sqrt{x} + 1", "RADICAND_TRUNCATION"),
    (r"\sqrt{b^2 - 4ac}", r"b - \sqrt{4ac}", "RADICAND_TRUNCATION"),
    (r"\sqrt{x^2 + y^2}", r"x + y", "RADICAND_TRUNCATION"),
    (r"\sqrt{a + b}", r"\sqrt{a} + \sqrt{b}", "RADICAND_TRUNCATION"),
    (r"\sqrt{(x_2 - x_1)^2 + (y_2 - y_1)^2}", r"(x_2 - x_1) + (y_2 - y_1)", "RADICAND_TRUNCATION"),
    (r"\sqrt{2x + 3}", r"\sqrt{2x} + 3", "RADICAND_TRUNCATION"),
    (r"\sqrt{r^2 - x^2}", r"r - x", "RADICAND_TRUNCATION"),
    (r"\sqrt{4x^2 + 1}", r"2x + 1", "RADICAND_TRUNCATION"),
    (r"\sqrt{a^2 + 1}", r"a + 1", "RADICAND_TRUNCATION"),
    (r"\sqrt{1 - \sin^2\theta}", r"1 - \sin\theta", "RADICAND_TRUNCATION"),

    # Category 6: Inverse and Reciprocal Errors (10 cases)
    (r"\frac{a}{b}", r"\frac{b}{a}", "INVERSE_RECIPROCAL_ERROR"),
    (r"\frac{x_1}{x_2} = \frac{y_1}{y_2}", r"\frac{x_2}{x_1} = \frac{y_1}{y_2}", "INVERSE_RECIPROCAL_ERROR"),
    (r"\sin\theta", r"\csc\theta", "INVERSE_RECIPROCAL_ERROR"),
    (r"\tan\theta", r"\cot\theta", "INVERSE_RECIPROCAL_ERROR"),
    (r"\frac{1}{f} = \frac{1}{u} + \frac{1}{v}", r"f = u + v", "INVERSE_RECIPROCAL_ERROR"),
    (r"\frac{m}{V}", r"\frac{V}{m}", "INVERSE_RECIPROCAL_ERROR"),
    (r"R = \frac{V}{I}", r"R = \frac{I}{V}", "INVERSE_RECIPROCAL_ERROR"),
    (r"\frac{a_1}{b_1} = c", r"\frac{b_1}{a_1} = c", "INVERSE_RECIPROCAL_ERROR"),
    (r"\cos\theta", r"\sec\theta", "INVERSE_RECIPROCAL_ERROR"),
    (r"\frac{1}{x} = y", r"x = \frac{1}{y^2}", "INVERSE_RECIPROCAL_ERROR"),

    # Category 7: Cross-Term Dropouts (10 cases)
    ("(x + y)^2", "x^2 + y^2", "CROSS_TERM_DROPOUT"),
    ("(a - b)^2", "a^2 - b^2", "CROSS_TERM_DROPOUT"),
    ("(2x + 1)^2", "4x^2 + 1", "CROSS_TERM_DROPOUT"),
    ("(x + 3)^2", "x^2 + 9", "CROSS_TERM_DROPOUT"),
    ("(a + b + c)^2", "a^2 + b^2 + c^2", "CROSS_TERM_DROPOUT"),
    ("(x - 2)^2", "x^2 + 4", "CROSS_TERM_DROPOUT"),
    ("(3x - y)^2", "9x^2 + y^2", "CROSS_TERM_DROPOUT"),
    ("(p + q)^3", "p^3 + q^3", "CROSS_TERM_DROPOUT"),
    ("(x - 1)^3", "x^3 - 1", "CROSS_TERM_DROPOUT"),
    ("(2a - 3b)^2", "4a^2 + 9b^2", "CROSS_TERM_DROPOUT"),

    # Category 8: Constant and Variable Drift (10 cases)
    (r"\pi r^2", "3.14 r^2", "CONSTANT_VARIABLE_DRIFT"),
    ("E = mc^2", "E = mv^2", "CONSTANT_VARIABLE_DRIFT"),
    ("F = ma", "F = mv", "CONSTANT_VARIABLE_DRIFT"),
    ("y = mx + c", "y = ax + b", "CONSTANT_VARIABLE_DRIFT"),
    ("2\\pi r h", "2\\pi r l", "CONSTANT_VARIABLE_DRIFT"),
    (r"\frac{4}{3}\pi r^3", r"\frac{4}{3}\pi r^2", "CONSTANT_VARIABLE_DRIFT"),
    ("v = u + at", "v = u + gt", "CONSTANT_VARIABLE_DRIFT"),
    ("W = F \\cdot s", "W = F \\cdot t", "CONSTANT_VARIABLE_DRIFT"),
    (r"\frac{1}{2}mv^2", r"\frac{1}{2}m u^2", "CONSTANT_VARIABLE_DRIFT"),
    ("Q = I t", "Q = V t", "CONSTANT_VARIABLE_DRIFT"),

    # Category 9: Domain Singularity Traps (10 cases)
    (r"\frac{x^2}{x} = 0", "x = 0", "DOMAIN_SINGULARITY_TRAP"),
    (r"\frac{x - 1}{x - 1} = 1", "0 = 0", "DOMAIN_SINGULARITY_TRAP"),  # x != 1 required
    (r"\frac{x(x - 2)}{x} = 3", "x - 2 = 3", "DOMAIN_SINGULARITY_TRAP"),  # x != 0
    (r"\frac{1}{x} = \frac{1}{x}", "0 = 1", "DOMAIN_SINGULARITY_TRAP"),
    (r"\frac{x^2 - 4}{x - 2} = 4", "x + 2 = 4", "DOMAIN_SINGULARITY_TRAP"),
    (r"\frac{\sin\theta}{\cos\theta} = 1", r"\tan\theta = 0", "DOMAIN_SINGULARITY_TRAP"),
    (r"\frac{1}{x^2} = -1", "1 = -x^2", "DOMAIN_SINGULARITY_TRAP"),
    (r"\frac{x}{x + 1} = 1", "x = x + 1", "DOMAIN_SINGULARITY_TRAP"),
    (r"\frac{y}{y} = y", "1 = y", "DOMAIN_SINGULARITY_TRAP"),  # y != 0
    (r"\frac{a}{a - a} = 1", "1 = 1", "DOMAIN_SINGULARITY_TRAP"),  # Undefined 1/0

    # Category 10: Operator Confusions (10 cases)
    ("x + y", "x * y", "OPERATOR_CONFUSION"),
    ("a - b = 0", "a + b = 0", "OPERATOR_CONFUSION"),
    ("x / y", "x - y", "OPERATOR_CONFUSION"),
    ("2x + 1 = 3", "2x - 1 = 3", "OPERATOR_CONFUSION"),
    ("a \\cdot b = c", "a + b = c", "OPERATOR_CONFUSION"),
    ("x^2 + 1", "2x + 1", "OPERATOR_CONFUSION"),
    ("x = y", "x \\neq y", "OPERATOR_CONFUSION"),
    ("a \\times b", "a / b", "OPERATOR_CONFUSION"),
    ("x + y = 10", "x - y = 10", "OPERATOR_CONFUSION"),
    ("x^2 - 4 = 0", "x^2 + 4 = 0", "OPERATOR_CONFUSION"),
]


class TestAdversarialEquivalenceSuite:
    """
    Test suite validating that the equivalence engine accepts ZERO false equivalences
    across all 100 adversarial cases.
    """

    @pytest.fixture(scope="class")
    def engine(self):
        return MathematicalEquivalenceEngine()

    def test_total_adversarial_count(self):
        assert len(ADVERSARIAL_CASES) == 100, f"Expected 100 adversarial cases, found {len(ADVERSARIAL_CASES)}"

    @pytest.mark.parametrize("target,corrupted,category", ADVERSARIAL_CASES)
    def test_adversarial_case_must_not_be_equivalent(self, engine, target, corrupted, category):
        res = engine.evaluate(corrupted, target)

        # STRICT ASSERTION: Must NOT be SYMBOLIC_EQUIVALENT or NUMERICALLY_EQUIVALENT
        is_falsely_equivalent = res.status in (
            EquivalenceStatus.SYMBOLIC_EQUIVALENT,
            EquivalenceStatus.NUMERICALLY_EQUIVALENT,
        )

        assert not is_falsely_equivalent, (
            f"FAILED ADVERSARIAL TEST: [{category}] '{corrupted}' was falsely accepted as equivalent to '{target}'. "
            f"Status: {res.status}, Method: {res.verification_method}"
        )
