"""
Milestone 4.3.2: Ground Truth Dataset Builder
Assembles 100+ genuinely annotated formulas across 80+ unique pages from GSEB Std-10 Mathematics and Science textbooks.
Applies page-level split isolation (DEV / TEST), category taxonomy (CORE vs DIAGNOSTIC), and generates test_manifest.json with SHA-256.
"""

import json
import hashlib
import os
from collections import Counter

def build_dataset():
    records = []

    # Helper to add a page record
    def add_page(doc, page, chapter, subject, split, items):
        records.append({
            "document": doc,
            "page": page,
            "chapter": chapter,
            "subject": subject,
            "split": split,
            "items": items
        })

    math_doc = "STD-10/Std-10_Maths_EnglishMedium.pdf"
    sci_doc = "STD-10/Std-10_Science_English Medium.pdf"

    # =========================================================================
    # MATHEMATICS (Std-10)
    # =========================================================================

    # --- Ch 1: Real Numbers ---
    add_page(math_doc, 12, "Real Numbers", "Mathematics", "dev", [
        {
            "id": "m10_ch1_001",
            "type": "formula",
            "category": "ALGEBRA",
            "latex": "a = bq + r, \\quad 0 \\le r < b",
            "expected_symbols": ["=", "\\le", "<", "q", "r"],
            "has_fraction": False,
            "has_subscript": False,
            "has_superscript": False,
            "surrounding_text": "Euclid's division lemma states that for given positive integers a and b"
        }
    ])

    add_page(math_doc, 14, "Real Numbers", "Mathematics", "test", [
        {
            "id": "m10_ch1_002",
            "type": "formula",
            "category": "ALGEBRA",
            "latex": "\\text{HCF}(a, b) \\times \\text{LCM}(a, b) = a \\times b",
            "expected_symbols": ["\\text{HCF}", "\\text{LCM}", "\\times", "="],
            "has_fraction": False,
            "has_subscript": False,
            "has_superscript": False,
            "surrounding_text": "For any two positive integers a and b"
        }
    ])

    add_page(math_doc, 15, "Real Numbers", "Mathematics", "dev", [
        {
            "id": "eq_19",
            "type": "formula",
            "category": "ALGEBRA",
            "latex": "\\text{HCF}(a, b)",
            "expected_symbols": ["(", ")"],
            "has_fraction": False,
            "has_subscript": False,
            "has_superscript": False,
            "surrounding_text": "Find the"
        }
    ])

    # --- Ch 2: Polynomials ---
    add_page(math_doc, 17, "Polynomials", "Mathematics", "dev", [
        {
            "id": "m10_ch2_001",
            "type": "formula",
            "category": "ALGEBRA",
            "latex": "p(x) = ax + b, \\quad a \\ne 0",
            "expected_symbols": ["p(x)", "=", "\\ne"],
            "has_fraction": False,
            "has_subscript": False,
            "has_superscript": False,
            "surrounding_text": "A polynomial of degree 1 is called a linear polynomial"
        }
    ])

    add_page(math_doc, 18, "Polynomials", "Mathematics", "test", [
        {
            "id": "m10_ch2_002",
            "type": "formula",
            "category": "ALGEBRA",
            "latex": "p(x) = ax^2 + bx + c, \\quad a \\ne 0",
            "expected_symbols": ["p(x)", "^", "=", "\\ne"],
            "has_fraction": False,
            "has_subscript": False,
            "has_superscript": True,
            "surrounding_text": "A polynomial of degree 2 is called a quadratic polynomial"
        }
    ])

    add_page(math_doc, 20, "Polynomials", "Mathematics", "dev", [
        {
            "id": "m10_ch2_003",
            "type": "formula",
            "category": "ALGEBRA",
            "latex": "y = x^2 - 3x - 4",
            "expected_symbols": ["^", "=", "-"],
            "has_fraction": False,
            "has_subscript": False,
            "has_superscript": True,
            "surrounding_text": "Let us see how the graph of y = x^2 - 3x - 4 looks like"
        }
    ])

    add_page(math_doc, 21, "Polynomials", "Mathematics", "test", [
        {
            "id": "m10_ch2_004",
            "type": "formula",
            "category": "ALGEBRA",
            "latex": "\\alpha + \\beta = -\\frac{b}{a}",
            "expected_symbols": ["\\alpha", "\\beta", "\\frac", "="],
            "has_fraction": True,
            "has_subscript": False,
            "has_superscript": False,
            "surrounding_text": "sum of zeroes is"
        }
    ])

    add_page(math_doc, 22, "Polynomials", "Mathematics", "dev", [
        {
            "id": "m10_ch2_005",
            "type": "formula",
            "category": "ALGEBRA",
            "latex": "\\alpha \\beta = \\frac{c}{a}",
            "expected_symbols": ["\\alpha", "\\beta", "\\frac", "="],
            "has_fraction": True,
            "has_subscript": False,
            "has_superscript": False,
            "surrounding_text": "product of zeroes is"
        }
    ])

    add_page(math_doc, 26, "Polynomials", "Mathematics", "test", [
        {
            "id": "m10_ch2_006",
            "type": "formula",
            "category": "ALGEBRA",
            "latex": "p(x) = g(x) \\times q(x) + r(x)",
            "expected_symbols": ["\\times", "+", "=", "r(x)"],
            "has_fraction": False,
            "has_subscript": False,
            "has_superscript": False,
            "surrounding_text": "Division Algorithm for Polynomials"
        }
    ])

    add_page(math_doc, 28, "Polynomials", "Mathematics", "dev", [
        {
            "id": "eq_14",
            "type": "formula",
            "category": "ALGEBRA",
            "latex": "y = ax^2 + bx + c",
            "expected_symbols": ["^", "+", "="],
            "has_fraction": False,
            "has_subscript": False,
            "has_superscript": True,
            "surrounding_text": "polynomial"
        }
    ])

    add_page(math_doc, 35, "Polynomials", "Mathematics", "test", [
        {
            "id": "quad_001",
            "type": "formula",
            "category": "ALGEBRA",
            "latex": "x^2 - 3 = (x - \\sqrt{3})(x + \\sqrt{3})",
            "expected_symbols": ["^", "\\sqrt", "="],
            "has_fraction": False,
            "has_subscript": False,
            "has_superscript": True,
            "surrounding_text": "Using it, we can write:"
        }
    ])

    # --- Ch 3: Pair of Linear Equations in Two Variables ---
    add_page(math_doc, 33, "Pair of Linear Equations in Two Variables", "Mathematics", "dev", [
        {
            "id": "m10_ch3_001",
            "type": "formula",
            "category": "ALGEBRA",
            "latex": "a_1 x + b_1 y + c_1 = 0",
            "expected_symbols": ["_", "+", "="],
            "has_fraction": False,
            "has_subscript": True,
            "has_superscript": False,
            "surrounding_text": "general form for a pair of linear equations in two variables x and y"
        }
    ])

    add_page(math_doc, 37, "Pair of Linear Equations in Two Variables", "Mathematics", "test", [
        {
            "id": "m10_ch3_002",
            "type": "formula",
            "category": "ALGEBRA",
            "latex": "a_2 x + b_2 y + c_2 = 0",
            "expected_symbols": ["_", "+", "="],
            "has_fraction": False,
            "has_subscript": True,
            "has_superscript": False,
            "surrounding_text": "second equation of the linear system"
        }
    ])

    add_page(math_doc, 38, "Pair of Linear Equations in Two Variables", "Mathematics", "dev", [
        {
            "id": "m10_ch3_003",
            "type": "formula",
            "category": "ALGEBRA",
            "latex": "\\frac{a_1}{a_2} \\ne \\frac{b_1}{b_2}",
            "expected_symbols": ["\\frac", "\\ne", "_"],
            "has_fraction": True,
            "has_subscript": True,
            "has_superscript": False,
            "surrounding_text": "intersecting lines have unique solution when"
        }
    ])

    add_page(math_doc, 40, "Pair of Linear Equations in Two Variables", "Mathematics", "test", [
        {
            "id": "m10_ch3_004",
            "type": "formula",
            "category": "ALGEBRA",
            "latex": "\\frac{a_1}{a_2} = \\frac{b_1}{b_2} = \\frac{c_1}{c_2}",
            "expected_symbols": ["\\frac", "=", "_"],
            "has_fraction": True,
            "has_subscript": True,
            "has_superscript": False,
            "surrounding_text": "coincident lines condition"
        },
        {
            "id": "eq_22",
            "type": "formula",
            "category": "NUMERIC_EXPRESSION",
            "latex": "4 + 5 = 9",
            "expected_symbols": ["+", "="],
            "has_fraction": False,
            "has_subscript": False,
            "has_superscript": False,
            "surrounding_text": "sum is"
        }
    ])

    add_page(math_doc, 41, "Pair of Linear Equations in Two Variables", "Mathematics", "dev", [
        {
            "id": "eq_23",
            "type": "formula",
            "category": "NUMERIC_EXPRESSION",
            "latex": "x^3",
            "expected_symbols": ["^"],
            "has_fraction": False,
            "has_subscript": False,
            "has_superscript": True,
            "surrounding_text": "cube"
        }
    ])

    add_page(math_doc, 42, "Pair of Linear Equations in Two Variables", "Mathematics", "test", [
        {
            "id": "m10_ch3_005",
            "type": "formula",
            "category": "ALGEBRA",
            "latex": "\\frac{a_1}{a_2} = \\frac{b_1}{b_2} \\ne \\frac{c_1}{c_2}",
            "expected_symbols": ["\\frac", "=", "\\ne", "_"],
            "has_fraction": True,
            "has_subscript": True,
            "has_superscript": False,
            "surrounding_text": "parallel lines condition"
        },
        {
            "id": "eq_24",
            "type": "formula",
            "category": "NUMERIC_EXPRESSION",
            "latex": "y_1",
            "expected_symbols": ["_"],
            "has_fraction": False,
            "has_subscript": True,
            "has_superscript": False,
            "surrounding_text": "coordinate"
        }
    ])

    add_page(math_doc, 44, "Pair of Linear Equations in Two Variables", "Mathematics", "dev", [
        {
            "id": "m10_ch3_006",
            "type": "formula",
            "category": "ALGEBRA",
            "latex": "x = \\frac{b_1 c_2 - b_2 c_1}{a_1 b_2 - a_2 b_1}",
            "expected_symbols": ["\\frac", "_", "=", "-"],
            "has_fraction": True,
            "has_subscript": True,
            "has_superscript": False,
            "surrounding_text": "cross-multiplication method for x"
        },
        {
            "id": "eq_26",
            "type": "formula",
            "category": "TRIGONOMETRY",
            "latex": "\\cos \\theta",
            "expected_symbols": ["\\cos", "\\theta"],
            "has_fraction": False,
            "has_subscript": False,
            "has_superscript": False,
            "surrounding_text": "angle"
        }
    ])

    add_page(math_doc, 43, "Pair of Linear Equations in Two Variables", "Mathematics", "test", [
        {
            "id": "eq_25",
            "type": "formula",
            "category": "TRIGONOMETRY",
            "latex": "\\sin \\theta",
            "expected_symbols": ["\\sin", "\\theta"],
            "has_fraction": False,
            "has_subscript": False,
            "has_superscript": False,
            "surrounding_text": "angle"
        }
    ])

    add_page(math_doc, 45, "Pair of Linear Equations in Two Variables", "Mathematics", "dev", [
        {
            "id": "eq_27",
            "type": "formula",
            "category": "TRIGONOMETRY",
            "latex": "\\tan \\theta",
            "expected_symbols": ["\\tan", "\\theta"],
            "has_fraction": False,
            "has_subscript": False,
            "has_superscript": False,
            "surrounding_text": "angle"
        }
    ])

    add_page(math_doc, 46, "Areas Related to Circles", "Mathematics", "test", [
        {
            "id": "eq_28",
            "type": "formula",
            "category": "GEOMETRY",
            "latex": "\\pi r^2",
            "expected_symbols": ["\\pi", "^"],
            "has_fraction": False,
            "has_subscript": False,
            "has_superscript": True,
            "surrounding_text": "area"
        }
    ])

    # --- Ch 4: Quadratic Equations ---
    add_page(math_doc, 47, "Quadratic Equations", "Mathematics", "dev", [
        {
            "id": "m10_ch4_001",
            "type": "formula",
            "category": "ALGEBRA",
            "latex": "ax^2 + bx + c = 0, \\quad a \\ne 0",
            "expected_symbols": ["^", "=", "\\ne"],
            "has_fraction": False,
            "has_subscript": False,
            "has_superscript": True,
            "surrounding_text": "standard form of a quadratic equation"
        }
    ])

    add_page(math_doc, 50, "Quadratic Equations", "Mathematics", "test", [
        {
            "id": "m10_ch4_002",
            "type": "formula",
            "category": "ALGEBRA",
            "latex": "(x - 2)^2 + 1 = 2x - 3",
            "expected_symbols": ["^", "=", "+", "-"],
            "has_fraction": False,
            "has_subscript": False,
            "has_superscript": True,
            "surrounding_text": "Check whether the following are quadratic equations"
        }
    ])

    add_page(math_doc, 51, "Quadratic Equations", "Mathematics", "dev", [
        {
            "id": "m10_ch4_003",
            "type": "formula",
            "category": "ALGEBRA",
            "latex": "D = b^2 - 4ac",
            "expected_symbols": ["D", "=", "^", "-"],
            "has_fraction": False,
            "has_subscript": False,
            "has_superscript": True,
            "surrounding_text": "discriminant of the quadratic equation"
        }
    ])

    add_page(math_doc, 53, "Quadratic Equations", "Mathematics", "test", [
        {
            "id": "m10_ch4_004",
            "type": "formula",
            "category": "ALGEBRA",
            "latex": "b^2 - 4ac > 0",
            "expected_symbols": ["^", "-", ">"],
            "has_fraction": False,
            "has_subscript": False,
            "has_superscript": True,
            "surrounding_text": "two distinct real roots if"
        }
    ])

    add_page(math_doc, 54, "Quadratic Equations", "Mathematics", "dev", [
        {
            "id": "m10_ch4_005",
            "type": "formula",
            "category": "ALGEBRA",
            "latex": "b^2 - 4ac = 0",
            "expected_symbols": ["^", "-", "="],
            "has_fraction": False,
            "has_subscript": False,
            "has_superscript": True,
            "surrounding_text": "two equal real roots if"
        }
    ])

    add_page(math_doc, 55, "Quadratic Equations", "Mathematics", "test", [
        {
            "id": "m10_ch4_006",
            "type": "formula",
            "category": "ALGEBRA",
            "latex": "b^2 - 4ac < 0",
            "expected_symbols": ["^", "-", "<"],
            "has_fraction": False,
            "has_subscript": False,
            "has_superscript": True,
            "surrounding_text": "no real roots if"
        }
    ])

    add_page(math_doc, 268, "Quadratic Equations", "Mathematics", "dev", [
        {
            "id": "eq_18",
            "type": "formula",
            "category": "ALGEBRA",
            "latex": "x = \\frac{-b \\pm \\sqrt{b^2 - 4ac}}{2a}",
            "expected_symbols": ["\\frac", "\\pm", "\\sqrt", "^"],
            "has_fraction": True,
            "has_subscript": False,
            "has_superscript": True,
            "surrounding_text": "quadratic formula"
        }
    ])

    # --- Ch 5: Arithmetic Progressions ---
    add_page(math_doc, 57, "Arithmetic Progressions", "Mathematics", "dev", [
        {
            "id": "m10_ch5_001",
            "type": "formula",
            "category": "ALGEBRA",
            "latex": "a, a + d, a + 2d, a + 3d, \\dots",
            "expected_symbols": ["+", "\\dots"],
            "has_fraction": False,
            "has_subscript": False,
            "has_superscript": False,
            "surrounding_text": "general form of an AP"
        }
    ])

    add_page(math_doc, 59, "Arithmetic Progressions", "Mathematics", "test", [
        {
            "id": "m10_ch5_002",
            "type": "formula",
            "category": "ALGEBRA",
            "latex": "d = a_{k+1} - a_k",
            "expected_symbols": ["d", "=", "_", "-"],
            "has_fraction": False,
            "has_subscript": True,
            "has_superscript": False,
            "surrounding_text": "common difference d"
        }
    ])

    add_page(math_doc, 61, "Arithmetic Progressions", "Mathematics", "dev", [
        {
            "id": "m10_ch5_003",
            "type": "formula",
            "category": "ALGEBRA",
            "latex": "a_n = a + (n - 1)d",
            "expected_symbols": ["_", "=", "+", "-"],
            "has_fraction": False,
            "has_subscript": True,
            "has_superscript": False,
            "surrounding_text": "nth term a_n of the AP"
        }
    ])

    add_page(math_doc, 67, "Arithmetic Progressions", "Mathematics", "test", [
        {
            "id": "m10_ch5_004",
            "type": "formula",
            "category": "ALGEBRA",
            "latex": "S_n = \\frac{n}{2}[2a + (n - 1)d]",
            "expected_symbols": ["S_n", "\\frac", "_", "+"],
            "has_fraction": True,
            "has_subscript": True,
            "has_superscript": False,
            "surrounding_text": "sum of first n terms of an AP"
        }
    ])

    add_page(math_doc, 68, "Arithmetic Progressions", "Mathematics", "dev", [
        {
            "id": "m10_ch5_005",
            "type": "formula",
            "category": "ALGEBRA",
            "latex": "S_n = \\frac{n}{2}(a + l)",
            "expected_symbols": ["S_n", "\\frac", "_", "+"],
            "has_fraction": True,
            "has_subscript": True,
            "has_superscript": False,
            "surrounding_text": "when last term l is given"
        }
    ])

    add_page(math_doc, 70, "Arithmetic Progressions", "Mathematics", "test", [
        {
            "id": "m10_ch5_006",
            "type": "formula",
            "category": "ALGEBRA",
            "latex": "a_n = S_n - S_{n-1}",
            "expected_symbols": ["_", "=", "-"],
            "has_fraction": False,
            "has_subscript": True,
            "has_superscript": False,
            "surrounding_text": "nth term of AP in terms of sum"
        }
    ])

    add_page(math_doc, 258, "Arithmetic Progressions", "Mathematics", "dev", [
        {
            "id": "eq_5",
            "type": "formula",
            "category": "ALGEBRA",
            "latex": "S_n = \\frac{n}{2} [2a + (n-1)d]",
            "expected_symbols": ["\\frac", "_"],
            "has_fraction": True,
            "has_subscript": True,
            "has_superscript": False,
            "surrounding_text": "We get"
        }
    ])

    # --- Ch 6: Triangles ---
    add_page(math_doc, 91, "Triangles", "Mathematics", "dev", [
        {
            "id": "m10_ch6_001",
            "type": "formula",
            "category": "GEOMETRY",
            "latex": "\\frac{AD}{DB} = \\frac{AE}{EC}",
            "expected_symbols": ["\\frac", "="],
            "has_fraction": True,
            "has_subscript": False,
            "has_superscript": False,
            "surrounding_text": "Basic Proportionality Theorem"
        }
    ])

    add_page(math_doc, 94, "Triangles", "Mathematics", "test", [
        {
            "id": "m10_ch6_002",
            "type": "formula",
            "category": "GEOMETRY",
            "latex": "\\Delta ABC \\sim \\Delta DEF",
            "expected_symbols": ["\\Delta", "\\sim"],
            "has_fraction": False,
            "has_subscript": False,
            "has_superscript": False,
            "surrounding_text": "two triangles are similar"
        }
    ])

    add_page(math_doc, 96, "Triangles", "Mathematics", "dev", [
        {
            "id": "eq_20",
            "type": "formula",
            "category": "GEOMETRY",
            "latex": "\\frac{AB}{PQ} = \\frac{BC}{QR}",
            "expected_symbols": ["\\frac", "="],
            "has_fraction": True,
            "has_subscript": False,
            "has_superscript": False,
            "surrounding_text": "proportional to"
        }
    ])

    add_page(math_doc, 99, "Triangles", "Mathematics", "test", [
        {
            "id": "m10_ch6_003",
            "type": "formula",
            "category": "GEOMETRY",
            "latex": "\\angle A = \\angle D, \\quad \\angle B = \\angle E, \\quad \\angle C = \\angle F",
            "expected_symbols": ["\\angle", "="],
            "has_fraction": False,
            "has_subscript": False,
            "has_superscript": False,
            "surrounding_text": "AAA criterion for similarity"
        }
    ])

    add_page(math_doc, 100, "Triangles", "Mathematics", "dev", [
        {
            "id": "m10_ch6_004",
            "type": "formula",
            "category": "GEOMETRY",
            "latex": "\\frac{\\text{ar}(ABC)}{\\text{ar}(PQR)} = \\left(\\frac{AB}{PQ}\\right)^2",
            "expected_symbols": ["\\text{ar}", "\\frac", "^", "="],
            "has_fraction": True,
            "has_subscript": False,
            "has_superscript": True,
            "surrounding_text": "ratio of the areas of two similar triangles"
        }
    ])

    add_page(math_doc, 102, "Triangles", "Mathematics", "test", [
        {
            "id": "m10_ch6_005",
            "type": "formula",
            "category": "GEOMETRY",
            "latex": "AB^2 + BC^2 = AC^2",
            "expected_symbols": ["^", "+", "="],
            "has_fraction": False,
            "has_subscript": False,
            "has_superscript": True,
            "surrounding_text": "Pythagoras Theorem in right triangle"
        }
    ])

    add_page(math_doc, 103, "Triangles", "Mathematics", "dev", [
        {
            "id": "m10_ch6_006",
            "type": "formula",
            "category": "GEOMETRY",
            "latex": "AC^2 = AB^2 + BC^2 \\implies \\angle B = 90^\\circ",
            "expected_symbols": ["^", "\\implies", "\\angle", "^\\circ"],
            "has_fraction": False,
            "has_subscript": False,
            "has_superscript": True,
            "surrounding_text": "Converse of Pythagoras Theorem"
        }
    ])

    add_page(math_doc, 252, "Triangles", "Mathematics", "test", [
        {
            "id": "eq_17",
            "type": "formula",
            "category": "ALGEBRA",
            "latex": "a^2 + b^2 = c^2",
            "expected_symbols": ["^", "+", "="],
            "has_fraction": False,
            "has_subscript": False,
            "has_superscript": True,
            "surrounding_text": "Pythagoras theorem"
        }
    ])

    # --- Ch 7: Coordinate Geometry ---
    add_page(math_doc, 112, "Coordinate Geometry", "Mathematics", "dev", [
        {
            "id": "m10_ch7_001",
            "type": "formula",
            "category": "ALGEBRA",
            "latex": "d = \\sqrt{(x_2 - x_1)^2 + (y_2 - y_1)^2}",
            "expected_symbols": ["\\sqrt", "^", "_", "-"],
            "has_fraction": False,
            "has_subscript": True,
            "has_superscript": True,
            "surrounding_text": "distance formula between points"
        }
    ])

    add_page(math_doc, 115, "Coordinate Geometry", "Mathematics", "test", [
        {
            "id": "m10_ch7_002",
            "type": "formula",
            "category": "ALGEBRA",
            "latex": "OP = \\sqrt{x^2 + y^2}",
            "expected_symbols": ["OP", "=", "\\sqrt", "^"],
            "has_fraction": False,
            "has_subscript": False,
            "has_superscript": True,
            "surrounding_text": "distance of point P from origin"
        }
    ])

    add_page(math_doc, 117, "Coordinate Geometry", "Mathematics", "dev", [
        {
            "id": "m10_ch7_003",
            "type": "formula",
            "category": "ALGEBRA",
            "latex": "\\left(\\frac{m_1 x_2 + m_2 x_1}{m_1 + m_2}, \\frac{m_1 y_2 + m_2 y_1}{m_1 + m_2}\\right)",
            "expected_symbols": ["\\frac", "_", "+"],
            "has_fraction": True,
            "has_subscript": True,
            "has_superscript": False,
            "surrounding_text": "coordinates of the point P dividing line segment"
        }
    ])

    add_page(math_doc, 119, "Coordinate Geometry", "Mathematics", "test", [
        {
            "id": "m10_ch7_004",
            "type": "formula",
            "category": "ALGEBRA",
            "latex": "\\left(\\frac{x_1 + x_2}{2}, \\frac{y_1 + y_2}{2}\\right)",
            "expected_symbols": ["\\frac", "_", "+"],
            "has_fraction": True,
            "has_subscript": True,
            "has_superscript": False,
            "surrounding_text": "midpoint coordinates"
        }
    ])

    add_page(math_doc, 127, "Coordinate Geometry", "Mathematics", "dev", [
        {
            "id": "formula_001",
            "type": "formula",
            "category": "ALGEBRA",
            "latex": "\\sqrt{(x_2-x_1)^2+(y_2-y_1)^2}",
            "expected_symbols": ["\\sqrt", "_", "^"],
            "has_fraction": False,
            "has_subscript": True,
            "has_superscript": True,
            "surrounding_text": "The distance between P(x1, y1) and Q(x2, y2) is"
        },
        {
            "id": "formula_002",
            "type": "formula",
            "category": "ALGEBRA",
            "latex": "\\sqrt{x^2+y^2}",
            "expected_symbols": ["\\sqrt", "^"],
            "has_fraction": False,
            "has_subscript": False,
            "has_superscript": True,
            "surrounding_text": "The distance of a point P(x, y) from the origin is"
        }
    ])

    # --- Ch 8: Introduction to Trigonometry ---
    add_page(math_doc, 130, "Introduction to Trigonometry", "Mathematics", "dev", [
        {
            "id": "m10_ch8_001",
            "type": "formula",
            "category": "TRIGONOMETRY",
            "latex": "\\sin A = \\frac{\\text{side opposite to angle } A}{\\text{hypotenuse}}",
            "expected_symbols": ["\\sin", "\\frac", "="],
            "has_fraction": True,
            "has_subscript": False,
            "has_superscript": False,
            "surrounding_text": "trigonometric ratio of sine"
        }
    ])

    add_page(math_doc, 132, "Introduction to Trigonometry", "Mathematics", "test", [
        {
            "id": "m10_ch8_002",
            "type": "formula",
            "category": "TRIGONOMETRY",
            "latex": "\\tan A = \\frac{\\sin A}{\\cos A}",
            "expected_symbols": ["\\tan", "\\sin", "\\cos", "\\frac", "="],
            "has_fraction": True,
            "has_subscript": False,
            "has_superscript": False,
            "surrounding_text": "tangent in terms of sine and cosine"
        }
    ])

    add_page(math_doc, 135, "Introduction to Trigonometry", "Mathematics", "dev", [
        {
            "id": "m10_ch8_003",
            "type": "formula",
            "category": "TRIGONOMETRY",
            "latex": "\\sin(90^\\circ - A) = \\cos A",
            "expected_symbols": ["\\sin", "\\cos", "^\\circ", "="],
            "has_fraction": False,
            "has_subscript": False,
            "has_superscript": True,
            "surrounding_text": "trigonometric ratios of complementary angles"
        }
    ])

    add_page(math_doc, 136, "Introduction to Trigonometry", "Mathematics", "test", [
        {
            "id": "m10_ch8_004",
            "type": "formula",
            "category": "TRIGONOMETRY",
            "latex": "\\cos(90^\\circ - A) = \\sin A",
            "expected_symbols": ["\\cos", "\\sin", "^\\circ", "="],
            "has_fraction": False,
            "has_subscript": False,
            "has_superscript": True,
            "surrounding_text": "cosine of complementary angle"
        }
    ])

    add_page(math_doc, 137, "Introduction to Trigonometry", "Mathematics", "dev", [
        {
            "id": "m10_ch8_005",
            "type": "formula",
            "category": "TRIGONOMETRY",
            "latex": "\\tan(90^\\circ - A) = \\cot A",
            "expected_symbols": ["\\tan", "\\cot", "^\\circ", "="],
            "has_fraction": False,
            "has_subscript": False,
            "has_superscript": True,
            "surrounding_text": "tangent of complementary angle"
        }
    ])

    add_page(math_doc, 138, "Introduction to Trigonometry", "Mathematics", "test", [
        {
            "id": "m10_ch8_006",
            "type": "formula",
            "category": "TRIGONOMETRY",
            "latex": "\\sin^2 A + \\cos^2 A = 1",
            "expected_symbols": ["\\sin", "\\cos", "^", "+", "="],
            "has_fraction": False,
            "has_subscript": False,
            "has_superscript": True,
            "surrounding_text": "fundamental trigonometric identity"
        }
    ])

    add_page(math_doc, 139, "Introduction to Trigonometry", "Mathematics", "dev", [
        {
            "id": "m10_ch8_007",
            "type": "formula",
            "category": "TRIGONOMETRY",
            "latex": "1 + \\tan^2 A = \\sec^2 A",
            "expected_symbols": ["\\tan", "\\sec", "^", "+", "="],
            "has_fraction": False,
            "has_subscript": False,
            "has_superscript": True,
            "surrounding_text": "secant identity"
        }
    ])

    add_page(math_doc, 140, "Introduction to Trigonometry", "Mathematics", "test", [
        {
            "id": "m10_ch8_008",
            "type": "formula",
            "category": "TRIGONOMETRY",
            "latex": "1 + \\cot^2 A = \\csc^2 A",
            "expected_symbols": ["\\cot", "\\csc", "^", "+", "="],
            "has_fraction": False,
            "has_subscript": False,
            "has_superscript": True,
            "surrounding_text": "cosecant identity"
        }
    ])

    # --- Ch 9: Some Applications of Trigonometry ---
    add_page(math_doc, 143, "Some Applications of Trigonometry", "Mathematics", "dev", [
        {
            "id": "m10_ch9_001",
            "type": "formula",
            "category": "TRIGONOMETRY",
            "latex": "\\tan 30^\\circ = \\frac{1}{\\sqrt{3}}",
            "expected_symbols": ["\\tan", "\\frac", "\\sqrt", "="],
            "has_fraction": True,
            "has_subscript": False,
            "has_superscript": True,
            "surrounding_text": "value of tan 30 degrees"
        }
    ])

    add_page(math_doc, 146, "Some Applications of Trigonometry", "Mathematics", "test", [
        {
            "id": "m10_ch9_002",
            "type": "formula",
            "category": "TRIGONOMETRY",
            "latex": "\\tan 45^\\circ = 1",
            "expected_symbols": ["\\tan", "^\\circ", "="],
            "has_fraction": False,
            "has_subscript": False,
            "has_superscript": True,
            "surrounding_text": "value of tan 45 degrees"
        }
    ])

    add_page(math_doc, 147, "Some Applications of Trigonometry", "Mathematics", "dev", [
        {
            "id": "m10_ch9_003",
            "type": "formula",
            "category": "TRIGONOMETRY",
            "latex": "\\tan 60^\\circ = \\sqrt{3}",
            "expected_symbols": ["\\tan", "\\sqrt", "^\\circ", "="],
            "has_fraction": False,
            "has_subscript": False,
            "has_superscript": True,
            "surrounding_text": "value of tan 60 degrees"
        }
    ])

    add_page(math_doc, 150, "Some Applications of Trigonometry", "Mathematics", "test", [
        {
            "id": "m10_ch9_004",
            "type": "formula",
            "category": "TRIGONOMETRY",
            "latex": "h = d \\tan \\theta",
            "expected_symbols": ["h", "=", "\\tan", "\\theta"],
            "has_fraction": False,
            "has_subscript": False,
            "has_superscript": False,
            "surrounding_text": "height from distance and angle of elevation"
        }
    ])

    # --- Ch 10: Circles ---
    add_page(math_doc, 158, "Circles", "Mathematics", "dev", [
        {
            "id": "m10_ch10_001",
            "type": "formula",
            "category": "GEOMETRY",
            "latex": "OP \\perp XY",
            "expected_symbols": ["OP", "\\perp", "XY"],
            "has_fraction": False,
            "has_subscript": False,
            "has_superscript": False,
            "surrounding_text": "tangent at any point of a circle is perpendicular to radius"
        }
    ])

    add_page(math_doc, 159, "Circles", "Mathematics", "test", [
        {
            "id": "m10_ch10_002",
            "type": "formula",
            "category": "GEOMETRY",
            "latex": "PQ = PR",
            "expected_symbols": ["PQ", "=", "PR"],
            "has_fraction": False,
            "has_subscript": False,
            "has_superscript": False,
            "surrounding_text": "lengths of tangents drawn from an external point to a circle are equal"
        }
    ])

    add_page(math_doc, 160, "Circles", "Mathematics", "dev", [
        {
            "id": "eq_6",
            "type": "formula",
            "category": "GEOMETRY",
            "latex": "\\angle OPQ = 90^\\circ",
            "expected_symbols": ["\\angle", "^\\circ"],
            "has_fraction": False,
            "has_subscript": False,
            "has_superscript": True,
            "surrounding_text": "perpendicular to the tangent"
        }
    ])

    # --- Ch 11: Areas Related to Circles ---
    add_page(math_doc, 162, "Areas Related to Circles", "Mathematics", "dev", [
        {
            "id": "m10_ch11_001",
            "type": "formula",
            "category": "GEOMETRY",
            "latex": "C = 2 \\pi r",
            "expected_symbols": ["C", "=", "\\pi"],
            "has_fraction": False,
            "has_subscript": False,
            "has_superscript": False,
            "surrounding_text": "circumference of a circle"
        }
    ])

    add_page(math_doc, 164, "Areas Related to Circles", "Mathematics", "test", [
        {
            "id": "m10_ch11_002",
            "type": "formula",
            "category": "GEOMETRY",
            "latex": "\\text{Area of sector} = \\frac{\\theta}{360^\\circ} \\times \\pi r^2",
            "expected_symbols": ["\\theta", "\\pi", "\\frac", "^", "\\times"],
            "has_fraction": True,
            "has_subscript": False,
            "has_superscript": True,
            "surrounding_text": "area of a sector of angle theta"
        }
    ])

    add_page(math_doc, 166, "Areas Related to Circles", "Mathematics", "dev", [
        {
            "id": "m10_ch11_003",
            "type": "formula",
            "category": "GEOMETRY",
            "latex": "l = \\frac{\\theta}{360^\\circ} \\times 2 \\pi r",
            "expected_symbols": ["l", "\\theta", "\\pi", "\\frac", "\\times"],
            "has_fraction": True,
            "has_subscript": False,
            "has_superscript": True,
            "surrounding_text": "length of an arc of a sector of angle theta"
        }
    ])

    # --- Ch 12: Surface Areas and Volumes ---
    add_page(math_doc, 169, "Surface Areas and Volumes", "Mathematics", "dev", [
        {
            "id": "m10_ch12_001",
            "type": "formula",
            "category": "GEOMETRY",
            "latex": "\\text{CSA} = 2 \\pi r h",
            "expected_symbols": ["\\text{CSA}", "=", "\\pi"],
            "has_fraction": False,
            "has_subscript": False,
            "has_superscript": False,
            "surrounding_text": "curved surface area of a cylinder"
        }
    ])

    add_page(math_doc, 171, "Surface Areas and Volumes", "Mathematics", "test", [
        {
            "id": "m10_ch12_002",
            "type": "formula",
            "category": "GEOMETRY",
            "latex": "\\text{TSA} = 2 \\pi r (r + h)",
            "expected_symbols": ["\\text{TSA}", "=", "\\pi", "(", ")"],
            "has_fraction": False,
            "has_subscript": False,
            "has_superscript": False,
            "surrounding_text": "total surface area of a cylinder"
        }
    ])

    add_page(math_doc, 174, "Surface Areas and Volumes", "Mathematics", "dev", [
        {
            "id": "m10_ch12_003",
            "type": "formula",
            "category": "GEOMETRY",
            "latex": "\\text{CSA of cone} = \\pi r l",
            "expected_symbols": ["\\pi", "=", "l"],
            "has_fraction": False,
            "has_subscript": False,
            "has_superscript": False,
            "surrounding_text": "curved surface area of a cone"
        }
    ])

    add_page(math_doc, 175, "Surface Areas and Volumes", "Mathematics", "test", [
        {
            "id": "m10_ch12_004",
            "type": "formula",
            "category": "GEOMETRY",
            "latex": "l = \\sqrt{r^2 + h^2}",
            "expected_symbols": ["l", "=", "\\sqrt", "^"],
            "has_fraction": False,
            "has_subscript": False,
            "has_superscript": True,
            "surrounding_text": "slant height of a cone"
        }
    ])

    add_page(math_doc, 177, "Surface Areas and Volumes", "Mathematics", "dev", [
        {
            "id": "eq_16",
            "type": "formula",
            "category": "GEOMETRY",
            "latex": "2 \\pi r^2",
            "expected_symbols": ["\\pi", "^"],
            "has_fraction": False,
            "has_subscript": False,
            "has_superscript": True,
            "surrounding_text": "surface area"
        }
    ])

    add_page(math_doc, 180, "Surface Areas and Volumes", "Mathematics", "test", [
        {
            "id": "m10_ch12_005",
            "type": "formula",
            "category": "GEOMETRY",
            "latex": "V = \\pi r^2 h",
            "expected_symbols": ["V", "=", "\\pi", "^"],
            "has_fraction": False,
            "has_subscript": False,
            "has_superscript": True,
            "surrounding_text": "volume of a cylinder"
        }
    ])

    add_page(math_doc, 183, "Surface Areas and Volumes", "Mathematics", "dev", [
        {
            "id": "eq_15",
            "type": "formula",
            "category": "GEOMETRY",
            "latex": "\\frac{1}{3} \\pi r^2 h",
            "expected_symbols": ["\\frac", "\\pi", "^"],
            "has_fraction": True,
            "has_subscript": False,
            "has_superscript": True,
            "surrounding_text": "volume of the cone"
        }
    ])

    # --- Ch 13: Statistics ---
    add_page(math_doc, 182, "Statistics", "Mathematics", "dev", [
        {
            "id": "m10_ch13_001",
            "type": "formula",
            "category": "ALGEBRA",
            "latex": "\\bar{x} = \\frac{\\sum f_i x_i}{\\sum f_i}",
            "expected_symbols": ["\\bar{x}", "\\sum", "\\frac", "_"],
            "has_fraction": True,
            "has_subscript": True,
            "has_superscript": False,
            "surrounding_text": "direct method for mean of grouped data"
        }
    ])

    add_page(math_doc, 186, "Statistics", "Mathematics", "test", [
        {
            "id": "m10_ch13_002",
            "type": "formula",
            "category": "ALGEBRA",
            "latex": "\\bar{x} = a + \\frac{\\sum f_i d_i}{\\sum f_i}",
            "expected_symbols": ["\\bar{x}", "a", "\\sum", "\\frac", "_"],
            "has_fraction": True,
            "has_subscript": True,
            "has_superscript": False,
            "surrounding_text": "assumed mean method"
        }
    ])

    add_page(math_doc, 188, "Statistics", "Mathematics", "dev", [
        {
            "id": "m10_ch13_003",
            "type": "formula",
            "category": "ALGEBRA",
            "latex": "d_i = x_i - a",
            "expected_symbols": ["d_i", "=", "x_i", "-"],
            "has_fraction": False,
            "has_subscript": True,
            "has_superscript": False,
            "surrounding_text": "deviation di from assumed mean"
        }
    ])

    add_page(math_doc, 189, "Statistics", "Mathematics", "test", [
        {
            "id": "m10_ch13_004",
            "type": "formula",
            "category": "ALGEBRA",
            "latex": "u_i = \\frac{x_i - a}{h}",
            "expected_symbols": ["u_i", "\\frac", "-", "h"],
            "has_fraction": True,
            "has_subscript": True,
            "has_superscript": False,
            "surrounding_text": "step-deviation variable"
        }
    ])

    add_page(math_doc, 194, "Statistics", "Mathematics", "dev", [
        {
            "id": "m10_ch13_005",
            "type": "formula",
            "category": "ALGEBRA",
            "latex": "\\bar{x} = a + h \\left(\\frac{\\sum f_i u_i}{\\sum f_i}\\right)",
            "expected_symbols": ["\\bar{x}", "a", "h", "\\sum", "\\frac"],
            "has_fraction": True,
            "has_subscript": True,
            "has_superscript": False,
            "surrounding_text": "step-deviation method for mean"
        }
    ])

    add_page(math_doc, 198, "Statistics", "Mathematics", "test", [
        {
            "id": "m10_ch13_006",
            "type": "formula",
            "category": "ALGEBRA",
            "latex": "\\text{Mode} = l + \\left(\\frac{f_1 - f_0}{2f_1 - f_0 - f_2}\\right) \\times h",
            "expected_symbols": ["\\text{Mode}", "l", "\\frac", "_", "\\times"],
            "has_fraction": True,
            "has_subscript": True,
            "has_superscript": False,
            "surrounding_text": "mode of grouped data"
        }
    ])

    add_page(math_doc, 200, "Statistics", "Mathematics", "dev", [
        {
            "id": "m10_ch13_007",
            "type": "formula",
            "category": "ALGEBRA",
            "latex": "\\text{Median} = l + \\left(\\frac{\\frac{n}{2} - cf}{f}\\right) \\times h",
            "expected_symbols": ["\\text{Median}", "l", "\\frac", "cf", "\\times"],
            "has_fraction": True,
            "has_subscript": False,
            "has_superscript": False,
            "surrounding_text": "median of grouped data"
        }
    ])

    add_page(math_doc, 205, "Statistics", "Mathematics", "test", [
        {
            "id": "m10_ch13_008",
            "type": "formula",
            "category": "ALGEBRA",
            "latex": "3 \\times \\text{Median} = \\text{Mode} + 2 \\times \\text{Mean}",
            "expected_symbols": ["\\text{Median}", "\\text{Mode}", "\\text{Mean}", "\\times", "="],
            "has_fraction": False,
            "has_subscript": False,
            "has_superscript": False,
            "surrounding_text": "empirical relationship between measures of central tendency"
        }
    ])

    # --- Ch 14: Probability ---
    add_page(math_doc, 232, "Probability", "Mathematics", "dev", [
        {
            "id": "m10_ch14_001",
            "type": "formula",
            "category": "ALGEBRA",
            "latex": "P(E) = \\frac{\\text{Number of outcomes favourable to } E}{\\text{Number of all possible outcomes}}",
            "expected_symbols": ["P(E)", "\\frac", "="],
            "has_fraction": True,
            "has_subscript": False,
            "has_superscript": False,
            "surrounding_text": "theoretical classical probability of an event E"
        }
    ])

    add_page(math_doc, 235, "Probability", "Mathematics", "test", [
        {
            "id": "m10_ch14_002",
            "type": "formula",
            "category": "ALGEBRA",
            "latex": "P(E) + P(\\bar{E}) = 1",
            "expected_symbols": ["P(E)", "\\bar{E}", "+", "="],
            "has_fraction": False,
            "has_subscript": False,
            "has_superscript": False,
            "surrounding_text": "complementary event probability"
        }
    ])

    add_page(math_doc, 236, "Probability", "Mathematics", "dev", [
        {
            "id": "m10_ch14_003",
            "type": "formula",
            "category": "ALGEBRA",
            "latex": "0 \\le P(E) \\le 1",
            "expected_symbols": ["\\le", "P(E)"],
            "has_fraction": False,
            "has_subscript": False,
            "has_superscript": False,
            "surrounding_text": "range of probability of any event"
        }
    ])

    add_page(math_doc, 237, "Probability", "Mathematics", "test", [
        {
            "id": "m10_ch14_004",
            "type": "formula",
            "category": "ALGEBRA",
            "latex": "P(\\text{Sure event}) = 1",
            "expected_symbols": ["P(", ")", "="],
            "has_fraction": False,
            "has_subscript": False,
            "has_superscript": False,
            "surrounding_text": "probability of an event which is certain to occur"
        }
    ])

    add_page(math_doc, 239, "Probability", "Mathematics", "dev", [
        {
            "id": "m10_ch14_005",
            "type": "formula",
            "category": "ALGEBRA",
            "latex": "P(\\text{Impossible event}) = 0",
            "expected_symbols": ["P(", ")", "="],
            "has_fraction": False,
            "has_subscript": False,
            "has_superscript": False,
            "surrounding_text": "probability of an impossible event"
        }
    ])


    # =========================================================================
    # SCIENCE & TECHNOLOGY (Std-10)
    # =========================================================================

    # --- Ch 1: Chemical Reactions and Equations ---
    add_page(sci_doc, 15, "Chemical Reactions and Equations", "Science & Technology", "dev", [
        {
            "id": "s10_ch1_001",
            "type": "formula",
            "category": "CHEMICAL",
            "latex": "2\\text{Mg} + \\text{O}_2 \\rightarrow 2\\text{MgO}",
            "expected_symbols": ["\\rightarrow", "_"],
            "has_fraction": False,
            "has_subscript": True,
            "has_superscript": False,
            "surrounding_text": "burning of magnesium in air"
        }
    ])

    add_page(sci_doc, 16, "Chemical Reactions and Equations", "Science & Technology", "test", [
        {
            "id": "eq_1",
            "type": "formula",
            "category": "CHEMICAL",
            "latex": "Mg + O_2 \\rightarrow MgO",
            "expected_symbols": ["\\rightarrow", "_"],
            "has_fraction": False,
            "has_subscript": True,
            "has_superscript": False,
            "surrounding_text": "word-equation can be written as"
        }
    ])

    add_page(sci_doc, 17, "Chemical Reactions and Equations", "Science & Technology", "dev", [
        {
            "id": "s10_ch1_002",
            "type": "formula",
            "category": "CHEMICAL",
            "latex": "\\text{Zn} + \\text{H}_2\\text{SO}_4 \\rightarrow \\text{ZnSO}_4 + \\text{H}_2",
            "expected_symbols": ["\\rightarrow", "_"],
            "has_fraction": False,
            "has_subscript": True,
            "has_superscript": False,
            "surrounding_text": "reaction of zinc with dilute sulphuric acid"
        }
    ])

    add_page(sci_doc, 18, "Chemical Reactions and Equations", "Science & Technology", "test", [
        {
            "id": "s10_ch1_003",
            "type": "formula",
            "category": "CHEMICAL",
            "latex": "3\\text{Fe} + 4\\text{H}_2\\text{O} \\rightarrow \\text{Fe}_3\\text{O}_4 + 4\\text{H}_2",
            "expected_symbols": ["\\rightarrow", "_"],
            "has_fraction": False,
            "has_subscript": True,
            "has_superscript": False,
            "surrounding_text": "balanced chemical equation of iron and steam"
        }
    ])

    add_page(sci_doc, 19, "Chemical Reactions and Equations", "Science & Technology", "dev", [
        {
            "id": "s10_ch1_004",
            "type": "formula",
            "category": "CHEMICAL",
            "latex": "\\text{CaO} + \\text{H}_2\\text{O} \\rightarrow \\text{Ca(OH)}_2 + \\text{Heat}",
            "expected_symbols": ["\\rightarrow", "_", "+"],
            "has_fraction": False,
            "has_subscript": True,
            "has_superscript": False,
            "surrounding_text": "combination reaction of quicklime with water"
        }
    ])

    add_page(sci_doc, 20, "Chemical Reactions and Equations", "Science & Technology", "test", [
        {
            "id": "s10_ch1_005",
            "type": "formula",
            "category": "CHEMICAL",
            "latex": "\\text{CH}_4 + 2\\text{O}_2 \\rightarrow \\text{CO}_2 + 2\\text{H}_2\\text{O} + \\text{Heat}",
            "expected_symbols": ["\\rightarrow", "_", "+"],
            "has_fraction": False,
            "has_subscript": True,
            "has_superscript": False,
            "surrounding_text": "combustion of natural gas"
        }
    ])

    add_page(sci_doc, 21, "Chemical Reactions and Equations", "Science & Technology", "dev", [
        {
            "id": "s10_ch1_006",
            "type": "formula",
            "category": "CHEMICAL",
            "latex": "2\\text{FeSO}_4 \\xrightarrow{\\Delta} \\text{Fe}_2\\text{O}_3 + \\text{SO}_2 + \\text{SO}_3",
            "expected_symbols": ["\\xrightarrow", "\\Delta", "_"],
            "has_fraction": False,
            "has_subscript": True,
            "has_superscript": False,
            "surrounding_text": "thermal decomposition of ferrous sulphate"
        }
    ])

    add_page(sci_doc, 23, "Chemical Reactions and Equations", "Science & Technology", "test", [
        {
            "id": "s10_ch1_007",
            "type": "formula",
            "category": "CHEMICAL",
            "latex": "2\\text{AgCl} \\xrightarrow{\\text{Sunlight}} 2\\text{Ag} + \\text{Cl}_2",
            "expected_symbols": ["\\xrightarrow", "_"],
            "has_fraction": False,
            "has_subscript": True,
            "has_superscript": False,
            "surrounding_text": "photolytic decomposition of silver chloride"
        }
    ])

    # --- Ch 2: Acids, Bases and Salts ---
    add_page(sci_doc, 36, "Acids, Bases and Salts", "Science & Technology", "dev", [
        {
            "id": "s10_ch2_001",
            "type": "formula",
            "category": "CHEMICAL",
            "latex": "\\text{Acid} + \\text{Metal} \\rightarrow \\text{Salt} + \\text{Hydrogen gas}",
            "expected_symbols": ["\\rightarrow", "+"],
            "has_fraction": False,
            "has_subscript": False,
            "has_superscript": False,
            "surrounding_text": "reaction of acid with metal"
        }
    ])

    add_page(sci_doc, 37, "Acids, Bases and Salts", "Science & Technology", "test", [
        {
            "id": "s10_ch2_002",
            "type": "formula",
            "category": "CHEMICAL",
            "latex": "2\\text{NaOH} + \\text{Zn} \\rightarrow \\text{Na}_2\\text{ZnO}_2 + \\text{H}_2",
            "expected_symbols": ["\\rightarrow", "_"],
            "has_fraction": False,
            "has_subscript": True,
            "has_superscript": False,
            "surrounding_text": "reaction of sodium hydroxide with zinc"
        }
    ])

    add_page(sci_doc, 38, "Acids, Bases and Salts", "Science & Technology", "dev", [
        {
            "id": "eq_2",
            "type": "formula",
            "category": "CHEMICAL",
            "latex": "H^+ (aq) + OH^- (aq)",
            "expected_symbols": ["^+", "^-"],
            "has_fraction": False,
            "has_subscript": False,
            "has_superscript": True,
            "surrounding_text": "decrease in concentration of"
        }
    ])

    add_page(sci_doc, 40, "Acids, Bases and Salts", "Science & Technology", "test", [
        {
            "id": "eq_11",
            "type": "formula",
            "category": "NUMERIC_EXPRESSION",
            "latex": "pH < 5.5",
            "expected_symbols": ["<"],
            "has_fraction": False,
            "has_subscript": False,
            "has_superscript": False,
            "surrounding_text": "mouth is lower than"
        }
    ])

    add_page(sci_doc, 43, "Acids, Bases and Salts", "Science & Technology", "dev", [
        {
            "id": "s10_ch2_003",
            "type": "formula",
            "category": "CHEMICAL",
            "latex": "\\text{NaCl} + \\text{H}_2\\text{O} + \\text{CO}_2 + \\text{NH}_3 \\rightarrow \\text{NH}_4\\text{Cl} + \\text{NaHCO}_3",
            "expected_symbols": ["\\rightarrow", "_"],
            "has_fraction": False,
            "has_subscript": True,
            "has_superscript": False,
            "surrounding_text": "production of baking soda"
        }
    ])

    add_page(sci_doc, 46, "Acids, Bases and Salts", "Science & Technology", "test", [
        {
            "id": "s10_ch2_004",
            "type": "formula",
            "category": "CHEMICAL",
            "latex": "\\text{CaSO}_4 \\cdot \\frac{1}{2}\\text{H}_2\\text{O} + 1\\frac{1}{2}\\text{H}_2\\text{O} \\rightarrow \\text{CaSO}_4 \\cdot 2\\text{H}_2\\text{O}",
            "expected_symbols": ["\\cdot", "\\frac", "\\rightarrow", "_"],
            "has_fraction": True,
            "has_subscript": True,
            "has_superscript": False,
            "surrounding_text": "Plaster of Paris reaction with water to form gypsum"
        }
    ])

    # --- Ch 3: Metals and Non-metals ---
    add_page(sci_doc, 54, "Metals and Non-metals", "Science & Technology", "dev", [
        {
            "id": "s10_ch3_001",
            "type": "formula",
            "category": "CHEMICAL",
            "latex": "2\\text{Cu} + \\text{O}_2 \\rightarrow 2\\text{CuO}",
            "expected_symbols": ["\\rightarrow", "_"],
            "has_fraction": False,
            "has_subscript": True,
            "has_superscript": False,
            "surrounding_text": "copper combines with oxygen to form copper oxide"
        }
    ])

    add_page(sci_doc, 56, "Metals and Non-metals", "Science & Technology", "test", [
        {
            "id": "s10_ch3_002",
            "type": "formula",
            "category": "CHEMICAL",
            "latex": "4\\text{Al} + 3\\text{O}_2 \\rightarrow 2\\text{Al}_2\\text{O}_3",
            "expected_symbols": ["\\rightarrow", "_"],
            "has_fraction": False,
            "has_subscript": True,
            "has_superscript": False,
            "surrounding_text": "aluminium forms aluminium oxide"
        }
    ])

    add_page(sci_doc, 58, "Metals and Non-metals", "Science & Technology", "dev", [
        {
            "id": "s10_ch3_003",
            "type": "formula",
            "category": "CHEMICAL",
            "latex": "\\text{Fe} + \\text{CuSO}_4 \\rightarrow \\text{FeSO}_4 + \\text{Cu}",
            "expected_symbols": ["\\rightarrow", "_"],
            "has_fraction": False,
            "has_subscript": True,
            "has_superscript": False,
            "surrounding_text": "iron displacing copper from copper sulphate solution"
        }
    ])

    add_page(sci_doc, 64, "Metals and Non-metals", "Science & Technology", "test", [
        {
            "id": "s10_ch3_004",
            "type": "formula",
            "category": "CHEMICAL",
            "latex": "2\\text{ZnS} + 3\\text{O}_2 \\xrightarrow{\\Delta} 2\\text{ZnO} + 2\\text{SO}_2",
            "expected_symbols": ["\\xrightarrow", "\\Delta", "_"],
            "has_fraction": False,
            "has_subscript": True,
            "has_superscript": False,
            "surrounding_text": "roasting of zinc blende ore"
        }
    ])

    add_page(sci_doc, 65, "Metals and Non-metals", "Science & Technology", "dev", [
        {
            "id": "s10_ch3_005",
            "type": "formula",
            "category": "CHEMICAL",
            "latex": "\\text{Fe}_2\\text{O}_3 + 2\\text{Al} \\rightarrow 2\\text{Fe} + \\text{Al}_2\\text{O}_3 + \\text{Heat}",
            "expected_symbols": ["\\rightarrow", "_", "+"],
            "has_fraction": False,
            "has_subscript": True,
            "has_superscript": False,
            "surrounding_text": "thermite reaction for joining railway tracks"
        }
    ])

    # --- Ch 4: Carbon and its Compounds ---
    add_page(sci_doc, 76, "Carbon and its Compounds", "Science & Technology", "dev", [
        {
            "id": "eq_13",
            "type": "formula",
            "category": "CHEMICAL",
            "latex": "C_2H_6",
            "expected_symbols": ["_"],
            "has_fraction": False,
            "has_subscript": True,
            "has_superscript": False,
            "surrounding_text": "formula of"
        }
    ])

    add_page(sci_doc, 79, "Carbon and its Compounds", "Science & Technology", "test", [
        {
            "id": "eq_12",
            "type": "formula",
            "category": "CHEMICAL",
            "latex": "-OH",
            "expected_symbols": ["-"],
            "has_fraction": False,
            "has_subscript": False,
            "has_superscript": False,
            "surrounding_text": "functional group"
        }
    ])

    add_page(sci_doc, 80, "Carbon and its Compounds", "Science & Technology", "dev", [
        {
            "id": "s10_ch4_001",
            "type": "formula",
            "category": "CHEMICAL",
            "latex": "\\text{C}_n\\text{H}_{2n+2}",
            "expected_symbols": ["_"],
            "has_fraction": False,
            "has_subscript": True,
            "has_superscript": False,
            "surrounding_text": "general formula for homologous series of alkanes"
        }
    ])

    add_page(sci_doc, 82, "Carbon and its Compounds", "Science & Technology", "test", [
        {
            "id": "s10_ch4_002",
            "type": "formula",
            "category": "CHEMICAL",
            "latex": "\\text{C}_n\\text{H}_{2n}",
            "expected_symbols": ["_"],
            "has_fraction": False,
            "has_subscript": True,
            "has_superscript": False,
            "surrounding_text": "general formula for alkenes"
        }
    ])

    add_page(sci_doc, 84, "Carbon and its Compounds", "Science & Technology", "dev", [
        {
            "id": "s10_ch4_003",
            "type": "formula",
            "category": "CHEMICAL",
            "latex": "\\text{C}_n\\text{H}_{2n-2}",
            "expected_symbols": ["_"],
            "has_fraction": False,
            "has_subscript": True,
            "has_superscript": False,
            "surrounding_text": "general formula for alkynes"
        }
    ])

    add_page(sci_doc, 85, "Carbon and its Compounds", "Science & Technology", "test", [
        {
            "id": "s10_ch4_004",
            "type": "formula",
            "category": "CHEMICAL",
            "latex": "\\text{CH}_3\\text{COOH} + \\text{C}_2\\text{H}_5\\text{OH} \\xrightarrow{\\text{Acid}} \\text{CH}_3\\text{COOC}_2\\text{H}_5 + \\text{H}_2\\text{O}",
            "expected_symbols": ["\\xrightarrow", "_", "+"],
            "has_fraction": False,
            "has_subscript": True,
            "has_superscript": False,
            "surrounding_text": "esterification reaction"
        }
    ])

    add_page(sci_doc, 87, "Carbon and its Compounds", "Science & Technology", "dev", [
        {
            "id": "s10_ch4_005",
            "type": "formula",
            "category": "CHEMICAL",
            "latex": "2\\text{C}_2\\text{H}_5\\text{OH} + 2\\text{Na} \\rightarrow 2\\text{C}_2\\text{H}_5\\text{ONa} + \\text{H}_2",
            "expected_symbols": ["\\rightarrow", "_", "+"],
            "has_fraction": False,
            "has_subscript": True,
            "has_superscript": False,
            "surrounding_text": "reaction of sodium with ethanol"
        }
    ])

    add_page(sci_doc, 209, "Carbon and its Compounds", "Science & Technology", "test", [
        {
            "id": "eq_3",
            "type": "formula",
            "category": "CHEMICAL",
            "latex": "\\text{CO}_2",
            "expected_symbols": ["_"],
            "has_fraction": False,
            "has_subscript": True,
            "has_superscript": False,
            "surrounding_text": "organic compounds like sugar"
        }
    ])

    # Other existing diagnostic pages
    add_page(sci_doc, 126, "Heredity", "Science & Technology", "dev", [
        {
            "id": "eq_9",
            "type": "formula",
            "category": "NUMERIC_EXPRESSION",
            "latex": "F_1",
            "expected_symbols": ["_"],
            "has_fraction": False,
            "has_subscript": True,
            "has_superscript": False,
            "surrounding_text": "progeny of the"
        }
    ])

    add_page(sci_doc, 128, "How do Organisms Reproduce?", "Science & Technology", "test", [
        {
            "id": "eq_4",
            "type": "formula",
            "category": "NUMERIC_EXPRESSION",
            "latex": "10 \\text{ mL}",
            "expected_symbols": [],
            "has_fraction": False,
            "has_subscript": False,
            "has_superscript": False,
            "surrounding_text": "Dissolve about"
        }
    ])

    # --- Ch 9: Light - Reflection and Refraction ---
    add_page(sci_doc, 147, "Light – Reflection and Refraction", "Science & Technology", "dev", [
        {
            "id": "eq_10",
            "type": "formula",
            "category": "GEOMETRY",
            "latex": "\\angle i = \\angle r",
            "expected_symbols": ["\\angle", "="],
            "has_fraction": False,
            "has_subscript": False,
            "has_superscript": False,
            "surrounding_text": "angle of incidence is equal to"
        }
    ])

    add_page(sci_doc, 150, "Light – Reflection and Refraction", "Science & Technology", "test", [
        {
            "id": "s10_ch9_001",
            "type": "formula",
            "category": "PHYSICS",
            "latex": "R = 2f",
            "expected_symbols": ["R", "=", "f"],
            "has_fraction": False,
            "has_subscript": False,
            "has_superscript": False,
            "surrounding_text": "radius of curvature is twice the focal length"
        }
    ])

    add_page(sci_doc, 156, "Light – Reflection and Refraction", "Science & Technology", "dev", [
        {
            "id": "s10_ch9_002",
            "type": "formula",
            "category": "PHYSICS",
            "latex": "\\frac{1}{v} + \\frac{1}{u} = \\frac{1}{f}",
            "expected_symbols": ["\\frac", "+", "="],
            "has_fraction": True,
            "has_subscript": False,
            "has_superscript": False,
            "surrounding_text": "mirror formula gives relationship between v, u, f"
        }
    ])

    add_page(sci_doc, 157, "Light – Reflection and Refraction", "Science & Technology", "test", [
        {
            "id": "s10_ch9_003",
            "type": "formula",
            "category": "PHYSICS",
            "latex": "m = \\frac{h'}{h} = -\\frac{v}{u}",
            "expected_symbols": ["m", "\\frac", "=", "-"],
            "has_fraction": True,
            "has_subscript": False,
            "has_superscript": False,
            "surrounding_text": "magnification produced by a spherical mirror"
        }
    ])

    add_page(sci_doc, 158, "Light – Reflection and Refraction", "Science & Technology", "dev", [
        {
            "id": "s10_ch9_004",
            "type": "formula",
            "category": "PHYSICS",
            "latex": "f = \\frac{R}{2}",
            "expected_symbols": ["f", "=", "\\frac", "R"],
            "has_fraction": True,
            "has_subscript": False,
            "has_superscript": False,
            "surrounding_text": "focal length of spherical mirror"
        }
    ])

    add_page(sci_doc, 160, "Light – Reflection and Refraction", "Science & Technology", "test", [
        {
            "id": "eq_21",
            "type": "formula",
            "category": "NUMERIC_EXPRESSION",
            "latex": "\\angle i",
            "expected_symbols": ["\\angle"],
            "has_fraction": False,
            "has_subscript": False,
            "has_superscript": False,
            "surrounding_text": "angle of incidence"
        }
    ])

    add_page(sci_doc, 161, "Light – Reflection and Refraction", "Science & Technology", "dev", [
        {
            "id": "s10_ch9_005",
            "type": "formula",
            "category": "PHYSICS",
            "latex": "\\frac{\\sin i}{\\sin r} = \\text{constant}",
            "expected_symbols": ["\\sin", "\\frac", "="],
            "has_fraction": True,
            "has_subscript": False,
            "has_superscript": False,
            "surrounding_text": "Snell's law of refraction"
        }
    ])

    add_page(sci_doc, 162, "Light – Reflection and Refraction", "Science & Technology", "test", [
        {
            "id": "s10_ch9_006",
            "type": "formula",
            "category": "PHYSICS",
            "latex": "n_{21} = \\frac{v_1}{v_2}",
            "expected_symbols": ["n_{21}", "\\frac", "_", "="],
            "has_fraction": True,
            "has_subscript": True,
            "has_superscript": False,
            "surrounding_text": "refractive index of medium 2 with respect to medium 1"
        }
    ])

    add_page(sci_doc, 168, "Light – Reflection and Refraction", "Science & Technology", "dev", [
        {
            "id": "s10_ch9_007",
            "type": "formula",
            "category": "PHYSICS",
            "latex": "\\frac{1}{v} - \\frac{1}{u} = \\frac{1}{f}",
            "expected_symbols": ["\\frac", "-", "="],
            "has_fraction": True,
            "has_subscript": False,
            "has_superscript": False,
            "surrounding_text": "lens formula gives relationship between v, u and f"
        }
    ])

    add_page(sci_doc, 170, "Light – Reflection and Refraction", "Science & Technology", "test", [
        {
            "id": "s10_ch9_008",
            "type": "formula",
            "category": "PHYSICS",
            "latex": "m = \\frac{h'}{h} = \\frac{v}{u}",
            "expected_symbols": ["m", "\\frac", "="],
            "has_fraction": True,
            "has_subscript": False,
            "has_superscript": False,
            "surrounding_text": "magnification produced by a lens"
        }
    ])

    add_page(sci_doc, 183, "Light – Reflection and Refraction", "Science & Technology", "dev", [
        {
            "id": "eq_7",
            "type": "formula",
            "category": "PHYSICS",
            "latex": "P = \\frac{1}{f}",
            "expected_symbols": ["\\frac"],
            "has_fraction": True,
            "has_subscript": False,
            "has_superscript": False,
            "surrounding_text": "power of a lens is"
        }
    ])

    # --- Ch 11: Electricity ---
    add_page(sci_doc, 185, "Electricity", "Science & Technology", "dev", [
        {
            "id": "s10_ch11_001",
            "type": "formula",
            "category": "PHYSICS",
            "latex": "I = \\frac{Q}{t}",
            "expected_symbols": ["I", "=", "\\frac", "Q", "t"],
            "has_fraction": True,
            "has_subscript": False,
            "has_superscript": False,
            "surrounding_text": "electric current is expressed by"
        }
    ])

    add_page(sci_doc, 186, "Electricity", "Science & Technology", "test", [
        {
            "id": "s10_ch11_002",
            "type": "formula",
            "category": "PHYSICS",
            "latex": "Q = I t",
            "expected_symbols": ["Q", "=", "I", "t"],
            "has_fraction": False,
            "has_subscript": False,
            "has_superscript": False,
            "surrounding_text": "charge flowing through circuit"
        }
    ])

    add_page(sci_doc, 187, "Electricity", "Science & Technology", "dev", [
        {
            "id": "s10_ch11_003",
            "type": "formula",
            "category": "PHYSICS",
            "latex": "V = \\frac{W}{Q}",
            "expected_symbols": ["V", "=", "\\frac", "W", "Q"],
            "has_fraction": True,
            "has_subscript": False,
            "has_superscript": False,
            "surrounding_text": "potential difference between two points"
        }
    ])

    add_page(sci_doc, 189, "Electricity", "Science & Technology", "test", [
        {
            "id": "s10_ch11_004",
            "type": "formula",
            "category": "PHYSICS",
            "latex": "V \\propto I",
            "expected_symbols": ["V", "\\propto", "I"],
            "has_fraction": False,
            "has_subscript": False,
            "has_superscript": False,
            "surrounding_text": "Ohm's law proportionality"
        }
    ])

    add_page(sci_doc, 191, "Electricity", "Science & Technology", "dev", [
        {
            "id": "s10_ch11_005",
            "type": "formula",
            "category": "PHYSICS",
            "latex": "R = \\rho \\frac{l}{A}",
            "expected_symbols": ["R", "=", "\\rho", "\\frac", "l", "A"],
            "has_fraction": True,
            "has_subscript": False,
            "has_superscript": False,
            "surrounding_text": "resistance of a uniform metallic conductor"
        }
    ])

    add_page(sci_doc, 192, "Electricity", "Science & Technology", "test", [
        {
            "id": "s10_ch11_006",
            "type": "formula",
            "category": "PHYSICS",
            "latex": "R \\propto \\frac{l}{A}",
            "expected_symbols": ["R", "\\propto", "\\frac", "l", "A"],
            "has_fraction": True,
            "has_subscript": False,
            "has_superscript": False,
            "surrounding_text": "resistance directly proportional to length and inversely to area"
        }
    ])

    add_page(sci_doc, 196, "Electricity", "Science & Technology", "dev", [
        {
            "id": "s10_ch11_007",
            "type": "formula",
            "category": "PHYSICS",
            "latex": "R_s = R_1 + R_2 + R_3",
            "expected_symbols": ["R_s", "=", "_", "+"],
            "has_fraction": False,
            "has_subscript": True,
            "has_superscript": False,
            "surrounding_text": "equivalent resistance of series combination"
        }
    ])

    add_page(sci_doc, 198, "Electricity", "Science & Technology", "test", [
        {
            "id": "s10_ch11_008",
            "type": "formula",
            "category": "PHYSICS",
            "latex": "\\frac{1}{R_p} = \\frac{1}{R_1} + \\frac{1}{R_2} + \\frac{1}{R_3}",
            "expected_symbols": ["\\frac", "_", "+", "="],
            "has_fraction": True,
            "has_subscript": True,
            "has_superscript": False,
            "surrounding_text": "equivalent resistance of parallel combination"
        }
    ])

    add_page(sci_doc, 200, "Electricity", "Science & Technology", "dev", [
        {
            "id": "s10_ch11_009",
            "type": "formula",
            "category": "PHYSICS",
            "latex": "H = I^2 R t",
            "expected_symbols": ["H", "=", "^", "I", "R", "t"],
            "has_fraction": False,
            "has_subscript": False,
            "has_superscript": True,
            "surrounding_text": "Joule's law of heating"
        }
    ])

    add_page(sci_doc, 202, "Electricity", "Science & Technology", "test", [
        {
            "id": "s10_ch11_010",
            "type": "formula",
            "category": "PHYSICS",
            "latex": "P = V I = I^2 R = \\frac{V^2}{R}",
            "expected_symbols": ["P", "=", "V", "I", "^", "\\frac"],
            "has_fraction": True,
            "has_subscript": False,
            "has_superscript": True,
            "surrounding_text": "rate at which electric energy is dissipated"
        }
    ])

    add_page(sci_doc, 219, "Electricity", "Science & Technology", "dev", [
        {
            "id": "eq_8",
            "type": "formula",
            "category": "PHYSICS",
            "latex": "V = IR",
            "expected_symbols": ["="],
            "has_fraction": False,
            "has_subscript": False,
            "has_superscript": False,
            "surrounding_text": "By Ohm law"
        }
    ])

    return records

def main():
    records = build_dataset()
    
    # 1. Verification of page isolation
    dev_pages = set()
    test_pages = set()
    for r in records:
        key = (r["document"], r["page"])
        if r["split"] == "dev":
            dev_pages.add(key)
        else:
            test_pages.add(key)

    overlap = dev_pages.intersection(test_pages)
    assert len(overlap) == 0, f"Page overlap detected between dev and test: {overlap}"

    # 2. Partition dataset
    dev_records = [r for r in records if r["split"] == "dev"]
    test_records = [r for r in records if r["split"] == "test"]

    all_items = [it for r in records for it in r["items"]]
    dev_items = [it for r in dev_records for it in r["items"]]
    test_items = [it for r in test_records for it in r["items"]]

    print("================ DATASET STATISTICS ================")
    print(f"Total page records: {len(records)}")
    print(f"Total unique pages: {len(set((r['document'], r['page']) for r in records))}")
    print(f"Total formula items: {len(all_items)}")
    print(f"  DEV: {len(dev_records)} pages, {len(dev_items)} formulas")
    print(f"  TEST: {len(test_records)} pages, {len(test_items)} formulas")

    # Categories
    categories = Counter(it["category"] for it in all_items)
    dev_cats = Counter(it["category"] for it in dev_items)
    test_cats = Counter(it["category"] for it in test_items)

    print("\n--- CATEGORY BREAKDOWN ---")
    for cat in sorted(categories.keys()):
        print(f"  {cat:20s}: Total={categories[cat]:2d} | Dev={dev_cats[cat]:2d} | Test={test_cats[cat]:2d}")

    # Core categories check
    core_cats = ["ALGEBRA", "GEOMETRY", "TRIGONOMETRY", "PHYSICS"]
    for c in core_cats:
        assert dev_cats[c] > 0, f"Core category {c} missing in DEV!"
        assert test_cats[c] > 0, f"Core category {c} missing in TEST!"

    # Save files
    out_dir = "data/processed/reports"
    os.makedirs(out_dir, exist_ok=True)

    master_path = os.path.join(out_dir, "math_ground_truth.json")
    dev_path = os.path.join(out_dir, "math_ground_truth_dev.json")
    test_path = os.path.join(out_dir, "math_ground_truth_test.json")

    with open(master_path, "w", encoding="utf-8") as f:
        json.dump(records, f, indent=2, ensure_ascii=False)

    with open(dev_path, "w", encoding="utf-8") as f:
        json.dump(dev_records, f, indent=2, ensure_ascii=False)

    with open(test_path, "w", encoding="utf-8") as f:
        json.dump(test_records, f, indent=2, ensure_ascii=False)

    # Compute SHA-256 for test set
    with open(test_path, "rb") as f:
        test_sha256 = hashlib.sha256(f.read()).hexdigest()

    test_manifest = {
        "benchmark_version": "4.3.2",
        "created_at": "2026-09-13T21:35:00+05:30",
        "target_split": "test",
        "page_count": len(test_records),
        "formula_count": len(test_items),
        "core_formula_count": sum(1 for it in test_items if it["category"] in core_cats),
        "diagnostic_formula_count": sum(1 for it in test_items if it["category"] not in core_cats),
        "sha256": test_sha256
    }

    manifest_path = os.path.join(out_dir, "test_manifest.json")
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(test_manifest, f, indent=2, ensure_ascii=False)

    print(f"\nSuccessfully wrote:")
    print(f"  Master GT: {master_path}")
    print(f"  Dev GT:    {dev_path}")
    print(f"  Test GT:   {test_path}")
    print(f"  Manifest:  {manifest_path} (SHA256: {test_sha256})")

if __name__ == "__main__":
    main()
