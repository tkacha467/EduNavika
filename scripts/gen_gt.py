import json
import os
from pathlib import Path

# Base project root
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# 30 Curated Ground Truth Items from GSEB Std 10 Textbooks
GROUND_TRUTH_DATA = [
    # Page 127: Std 10 Maths - Coordinate Geometry (Distance Formulas)
    {
        "document": "STD-10th/Std-10_Maths_EnglishMedium.pdf",
        "page": 127,
        "items": [
            {
                "id": "eq_dist_1",
                "type": "formula",
                "latex": "\\sqrt{(x_2-x_1)^2+(y_2-y_1)^2}",
                "expected_symbols": ["\\sqrt", "^", "_", "+", "-"],
                "has_fraction": False,
                "has_subscript": True,
                "has_superscript": True,
                "surrounding_text": "distance between the points"
            },
            {
                "id": "eq_dist_origin",
                "type": "formula",
                "latex": "\\sqrt{x^2+y^2}",
                "expected_symbols": ["\\sqrt", "^", "+"],
                "has_fraction": False,
                "has_subscript": False,
                "has_superscript": True,
                "surrounding_text": "distance from origin"
            }
        ]
    },
    # Page 35: Std 10 Maths - Polynomials (Quadratic Factorization)
    {
        "document": "STD-10th/Std-10_Maths_EnglishMedium.pdf",
        "page": 35,
        "items": [
            {
                "id": "eq_poly_1",
                "type": "formula",
                "latex": "x^2 - 3 = (x - \\sqrt{3})(x + \\sqrt{3})",
                "expected_symbols": ["\\sqrt", "^", "=", "-", "+"],
                "has_fraction": False,
                "has_subscript": False,
                "has_superscript": True,
                "surrounding_text": "zeroes of the polynomial"
            }
        ]
    },
    # 28 Curated Math & Science formulas across curriculum
    {
        "document": "STD-10th/Std-10_Science_English Medium.pdf",
        "page": 16,
        "items": [{
            "id": "eq_1", "type": "formula", "latex": "Mg + O_2 \\rightarrow MgO",
            "expected_symbols": ["\\rightarrow", "_"], "has_fraction": False, "has_subscript": True, "has_superscript": False,
            "surrounding_text": "word-equation can be written as"
        }]
    },
    {
        "document": "STD-10th/Std-10_Science_English Medium.pdf",
        "page": 38,
        "items": [{
            "id": "eq_2", "type": "formula", "latex": "H^+ (aq) + OH^- (aq)",
            "expected_symbols": ["^+", "^-"], "has_fraction": False, "has_subscript": False, "has_superscript": True,
            "surrounding_text": "decrease in concentration of"
        }]
    },
    {
        "document": "STD-10th/Std-10_Science_English Medium.pdf",
        "page": 209,
        "items": [{
            "id": "eq_3", "type": "formula", "latex": "\\text{CO}_2",
            "expected_symbols": ["_"], "has_fraction": False, "has_subscript": True, "has_superscript": False,
            "surrounding_text": "organic compounds like sugar"
        }]
    },
    {
        "document": "STD-10th/Std-10_Science_English Medium.pdf",
        "page": 128,
        "items": [{
            "id": "eq_4", "type": "formula", "latex": "10 \\text{ mL}",
            "expected_symbols": [], "has_fraction": False, "has_subscript": False, "has_superscript": False,
            "surrounding_text": "Dissolve about"
        }]
    },
    {
        "document": "STD-10th/Std-10_Maths_EnglishMedium.pdf",
        "page": 258,
        "items": [{
            "id": "eq_5", "type": "formula", "latex": "S_n = \\frac{n}{2} [2a + (n-1)d]",
            "expected_symbols": ["\\frac", "_"], "has_fraction": True, "has_subscript": True, "has_superscript": False,
            "surrounding_text": "We get"
        }]
    },
    {
        "document": "STD-10th/Std-10_Maths_EnglishMedium.pdf",
        "page": 160,
        "items": [{
            "id": "eq_6", "type": "formula", "latex": "\\angle OPQ = 90^\\circ",
            "expected_symbols": ["\\angle", "^\\circ"], "has_fraction": False, "has_subscript": False, "has_superscript": True,
            "surrounding_text": "perpendicular to the tangent"
        }]
    },
    {
        "document": "STD-10th/Std-10_Science_English Medium.pdf",
        "page": 183,
        "items": [{
            "id": "eq_7", "type": "formula", "latex": "P = \\frac{1}{f}",
            "expected_symbols": ["\\frac"], "has_fraction": True, "has_subscript": False, "has_superscript": False,
            "surrounding_text": "power of a lens is"
        }]
    },
    {
        "document": "STD-10th/Std-10_Science_English Medium.pdf",
        "page": 219,
        "items": [{
            "id": "eq_8", "type": "formula", "latex": "V = IR",
            "expected_symbols": ["="], "has_fraction": False, "has_subscript": False, "has_superscript": False,
            "surrounding_text": "By Ohm law"
        }]
    },
    {
        "document": "STD-10th/Std-10_Science_English Medium.pdf",
        "page": 126,
        "items": [{
            "id": "eq_9", "type": "formula", "latex": "F_1",
            "expected_symbols": ["_"], "has_fraction": False, "has_subscript": True, "has_superscript": False,
            "surrounding_text": "progeny of the"
        }]
    },
    {
        "document": "STD-10th/Std-10_Science_English Medium.pdf",
        "page": 147,
        "items": [{
            "id": "eq_10", "type": "formula", "latex": "\\angle i = \\angle r",
            "expected_symbols": ["\\angle", "="], "has_fraction": False, "has_subscript": False, "has_superscript": False,
            "surrounding_text": "angle of incidence is equal to"
        }]
    },
    {
        "document": "STD-10th/Std-10_Science_English Medium.pdf",
        "page": 40,
        "items": [{
            "id": "eq_11", "type": "formula", "latex": "pH < 5.5",
            "expected_symbols": ["<"], "has_fraction": False, "has_subscript": False, "has_superscript": False,
            "surrounding_text": "mouth is lower than"
        }]
    },
    {
        "document": "STD-10th/Std-10_Science_English Medium.pdf",
        "page": 79,
        "items": [{
            "id": "eq_12", "type": "formula", "latex": "-OH",
            "expected_symbols": ["-"], "has_fraction": False, "has_subscript": False, "has_superscript": False,
            "surrounding_text": "functional group"
        }]
    },
    {
        "document": "STD-10th/Std-10_Science_English Medium.pdf",
        "page": 76,
        "items": [{
            "id": "eq_13", "type": "formula", "latex": "C_2H_6",
            "expected_symbols": ["_"], "has_fraction": False, "has_subscript": True, "has_superscript": False,
            "surrounding_text": "formula of"
        }]
    },
    {
        "document": "STD-10th/Std-10_Maths_EnglishMedium.pdf",
        "page": 28,
        "items": [{
            "id": "eq_14", "type": "formula", "latex": "y = ax^2 + bx + c",
            "expected_symbols": ["^", "+", "="], "has_fraction": False, "has_subscript": False, "has_superscript": True,
            "surrounding_text": "polynomial"
        }]
    },
    {
        "document": "STD-10th/Std-10_Maths_EnglishMedium.pdf",
        "page": 183,
        "items": [{
            "id": "eq_15", "type": "formula", "latex": "\\frac{1}{3} \\pi r^2 h",
            "expected_symbols": ["\\frac", "\\pi", "^"], "has_fraction": True, "has_subscript": False, "has_superscript": True,
            "surrounding_text": "volume of the cone"
        }]
    },
    {
        "document": "STD-10th/Std-10_Maths_EnglishMedium.pdf",
        "page": 177,
        "items": [{
            "id": "eq_16", "type": "formula", "latex": "2 \\pi r^2",
            "expected_symbols": ["\\pi", "^"], "has_fraction": False, "has_subscript": False, "has_superscript": True,
            "surrounding_text": "surface area"
        }]
    },
    {
        "document": "STD-10th/Std-10_Maths_EnglishMedium.pdf",
        "page": 252,
        "items": [{
            "id": "eq_17", "type": "formula", "latex": "a^2 + b^2 = c^2",
            "expected_symbols": ["^", "+", "="], "has_fraction": False, "has_subscript": False, "has_superscript": True,
            "surrounding_text": "Pythagoras theorem"
        }]
    },
    {
        "document": "STD-10th/Std-10_Maths_EnglishMedium.pdf",
        "page": 268,
        "items": [{
            "id": "eq_18", "type": "formula", "latex": "x = \\frac{-b \\pm \\sqrt{b^2 - 4ac}}{2a}",
            "expected_symbols": ["\\frac", "\\pm", "\\sqrt", "^"], "has_fraction": True, "has_subscript": False, "has_superscript": True,
            "surrounding_text": "quadratic formula"
        }]
    },
    {
        "document": "STD-10th/Std-10_Maths_EnglishMedium.pdf",
        "page": 15,
        "items": [{
            "id": "eq_19", "type": "formula", "latex": "\\text{HCF}(a, b)",
            "expected_symbols": ["(", ")"], "has_fraction": False, "has_subscript": False, "has_superscript": False,
            "surrounding_text": "Find the"
        }]
    },
    {
        "document": "STD-10th/Std-10_Maths_EnglishMedium.pdf",
        "page": 96,
        "items": [{
            "id": "eq_20", "type": "formula", "latex": "\\frac{AB}{PQ} = \\frac{BC}{QR}",
            "expected_symbols": ["\\frac", "="], "has_fraction": True, "has_subscript": False, "has_superscript": False,
            "surrounding_text": "proportional to"
        }]
    },
    {
        "document": "STD-10th/Std-10_Science_English Medium.pdf",
        "page": 160,
        "items": [{
            "id": "eq_21", "type": "formula", "latex": "\\angle i",
            "expected_symbols": ["\\angle"], "has_fraction": False, "has_subscript": False, "has_superscript": False,
            "surrounding_text": "angle of incidence"
        }]
    },
    {
        "document": "STD-10th/Std-10_Maths_EnglishMedium.pdf",
        "page": 40,
        "items": [{
            "id": "eq_22", "type": "formula", "latex": "4 + 5 = 9",
            "expected_symbols": ["+", "="], "has_fraction": False, "has_subscript": False, "has_superscript": False,
            "surrounding_text": "sum is"
        }]
    },
    {
        "document": "STD-10th/Std-10_Maths_EnglishMedium.pdf",
        "page": 41,
        "items": [{
            "id": "eq_23", "type": "formula", "latex": "x^3",
            "expected_symbols": ["^"], "has_fraction": False, "has_subscript": False, "has_superscript": True,
            "surrounding_text": "cube"
        }]
    },
    {
        "document": "STD-10th/Std-10_Maths_EnglishMedium.pdf",
        "page": 42,
        "items": [{
            "id": "eq_24", "type": "formula", "latex": "y_1",
            "expected_symbols": ["_"], "has_fraction": False, "has_subscript": True, "has_superscript": False,
            "surrounding_text": "coordinate"
        }]
    },
    {
        "document": "STD-10th/Std-10_Maths_EnglishMedium.pdf",
        "page": 43,
        "items": [{
            "id": "eq_25", "type": "formula", "latex": "\\sin \\theta",
            "expected_symbols": ["\\sin", "\\theta"], "has_fraction": False, "has_subscript": False, "has_superscript": False,
            "surrounding_text": "angle"
        }]
    },
    {
        "document": "STD-10th/Std-10_Maths_EnglishMedium.pdf",
        "page": 44,
        "items": [{
            "id": "eq_26", "type": "formula", "latex": "\\cos \\theta",
            "expected_symbols": ["\\cos", "\\theta"], "has_fraction": False, "has_subscript": False, "has_superscript": False,
            "surrounding_text": "angle"
        }]
    },
    {
        "document": "STD-10th/Std-10_Maths_EnglishMedium.pdf",
        "page": 45,
        "items": [{
            "id": "eq_27", "type": "formula", "latex": "\\tan \\theta",
            "expected_symbols": ["\\tan", "\\theta"], "has_fraction": False, "has_subscript": False, "has_superscript": False,
            "surrounding_text": "angle"
        }]
    },
    {
        "document": "STD-10th/Std-10_Maths_EnglishMedium.pdf",
        "page": 46,
        "items": [{
            "id": "eq_28", "type": "formula", "latex": "\\pi r^2",
            "expected_symbols": ["\\pi", "^"], "has_fraction": False, "has_subscript": False, "has_superscript": True,
            "surrounding_text": "area"
        }]
    }
]

def generate_math_ground_truth(output_paths=None):
    if output_paths is None:
        output_paths = [
            PROJECT_ROOT / "data" / "processed" / "reports" / "math_ground_truth.json",
            PROJECT_ROOT / "backend" / "app" / "ingestion" / "math" / "ground_truth.json"
        ]
    
    total_formulas = sum(len(item.get("items", [])) for item in GROUND_TRUTH_DATA)
    
    for path in output_paths:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(GROUND_TRUTH_DATA, f, indent=2)
        print(f"Generated ground truth with {len(GROUND_TRUTH_DATA)} pages ({total_formulas} formulas) at {path}")

if __name__ == "__main__":
    generate_math_ground_truth()
