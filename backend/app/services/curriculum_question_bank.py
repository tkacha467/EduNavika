"""
Curriculum Question Bank and Validation Service for EduNavika.
Phase 12: Curriculum-Grounded Question Generation & Assessment.

Ensures every question shown to a student is strictly traceable to
official GSEB/NCERT Standard 10 textbook content, with exact document,
page, chunk ID, and cognitive difficulty tier.
Rejects generic placeholders, ungrounded templates, and invalid formats.
"""

import re
import logging
from typing import Dict, List, Any, Optional, Tuple
from pydantic import BaseModel

logger = logging.getLogger("curriculum_assessment")


class ValidatedCurriculumQuestion(BaseModel):
    id: str
    topic_id: str
    topic_title: str
    subject: str
    chapter: str
    difficulty: str  # FOUNDATIONAL | GUIDED | APPLICATION | CHALLENGE
    question_type: str = "MCQ"
    question: str
    options: List[str]
    correct_answer: str
    explanation: str
    source_document: str
    source_page: int
    source_chunk_id: str
    source_text: str
    skill_target: str


class CurriculumQuestionValidator:
    """
    10-Point Validation Engine for Curriculum-Grounded Questions.
    Ensures absolute integrity against GSEB/NCERT syllabus requirements.
    """

    GENERIC_PATTERNS = [
        re.compile(r"which of the following best describes", re.IGNORECASE),
        re.compile(r"which of the following best defines", re.IGNORECASE),
        re.compile(r"a key idea in .* is", re.IGNORECASE),
        re.compile(r"a common application of .* is", re.IGNORECASE),
        re.compile(r"the best way to strengthen .* is", re.IGNORECASE),
        re.compile(r"a frequent mistake with .* is", re.IGNORECASE),
        re.compile(r"core concept covered in this chapter", re.IGNORECASE),
        re.compile(r"practise varied questions", re.IGNORECASE),
        re.compile(r"an unrelated topic", re.IGNORECASE),
        re.compile(r"only used in labs", re.IGNORECASE),
        re.compile(r"real-world problem solving", re.IGNORECASE),
        re.compile(r"none of these", re.IGNORECASE),
    ]

    @classmethod
    def validate(cls, item: Dict[str, Any], known_chunk_ids: Optional[set] = None) -> Tuple[bool, List[str]]:
        """
        Validates a question candidate against the 10-point curriculum rubric:
        1. Non-empty, specific question text (at least 15 chars).
        2. Exactly 4 non-empty, distinct options.
        3. Single correct answer that exactly matches one of the options.
        4. Valid difficulty tier (FOUNDATIONAL, GUIDED, APPLICATION, CHALLENGE).
        5. Valid, non-generic explanation grounded in concept.
        6. Valid source document (.pdf or canonical path).
        7. Valid positive source page number (> 0).
        8. Valid source chunk ID.
        9. Non-empty source text snippet supporting the question.
        10. Rejection of generic template phrasing.
        """
        reasons: List[str] = []

        q_text = (item.get("question") or "").strip()
        if len(q_text) < 15:
            reasons.append("Question text too short or empty (min 15 chars).")

        # Check for generic question patterns
        for pat in cls.GENERIC_PATTERNS:
            if pat.search(q_text):
                reasons.append(f"Question text matches banned generic pattern: '{pat.pattern}'.")
                break

        options = item.get("options") or []
        if not isinstance(options, list) or len(options) != 4:
            reasons.append(f"Expected exactly 4 options, got {len(options) if isinstance(options, list) else 0}.")
        else:
            cleaned_opts = [str(o).strip() for o in options]
            if any(len(o) == 0 for o in cleaned_opts):
                reasons.append("Contains empty options.")
            if len(set(cleaned_opts)) != 4:
                reasons.append("Options contain duplicates.")
            for o in cleaned_opts:
                for pat in cls.GENERIC_PATTERNS:
                    if pat.search(o):
                        reasons.append(f"Option matches generic filler pattern: '{o}'.")
                        break

        correct = (item.get("correct_answer") or item.get("correct") or "").strip()
        if not correct:
            reasons.append("Missing correct answer.")
        elif options and isinstance(options, list):
            cleaned_opts = [str(o).strip() for o in options]
            if correct not in cleaned_opts:
                reasons.append(f"Correct answer '{correct}' is not among provided options.")

        diff = (item.get("difficulty") or "").upper()
        if diff not in ("FOUNDATIONAL", "GUIDED", "APPLICATION", "CHALLENGE"):
            reasons.append(f"Invalid difficulty tier '{diff}'.")

        expl = (item.get("explanation") or "").strip()
        if len(expl) < 10:
            reasons.append("Explanation too short or missing.")

        doc = (item.get("source_document") or "").strip()
        if not doc or not (doc.endswith(".pdf") or "STD-10" in doc or "Science" in doc or "Math" in doc):
            reasons.append(f"Invalid source document reference '{doc}'.")

        page = item.get("source_page") or item.get("page")
        if not isinstance(page, int) or page <= 0:
            reasons.append(f"Invalid source page number '{page}'.")

        chunk_id = (item.get("source_chunk_id") or "").strip()
        if not chunk_id:
            reasons.append("Missing source chunk ID.")
        elif known_chunk_ids and chunk_id not in known_chunk_ids:
            reasons.append(f"Source chunk ID '{chunk_id}' not found in canonical LearningContent repository.")

        src_text = (item.get("source_text") or "").strip()
        if len(src_text) < 15:
            reasons.append("Missing or insufficient source text snippet from textbook.")
        else:
            # Perform Content Support Validation (Step 3: Source text must support question & answer)
            cs_valid, cs_reasons = cls.verify_content_support(item)
            if not cs_valid:
                reasons.extend(cs_reasons)

        is_valid = len(reasons) == 0
        if not is_valid:
            logger.warning("[CURRICULUM_VALIDATION] REJECTED question '%s': %s", q_text[:50], "; ".join(reasons))
        else:
            logger.info("[CURRICULUM_VALIDATION] PASSED question '%s' (Page %s, Chunk %s)", q_text[:50], page, chunk_id[:8])

        return is_valid, reasons

    @classmethod
    def verify_content_support(cls, item: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Content Support Test (Phase 12.5):
        Verifies that the cited source text contains semantic keywords/tokens
        necessary to independently derive the question, correct answer, and explanation.
        Prevents metadata-only spoofing or attaching arbitrary valid source chunks.
        """
        reasons: List[str] = []

        def normalize_math_text(text: str) -> str:
            t = text.lower()
            # Normalize exponents & superscripts to standard digits
            t = t.replace("²", "2").replace("³", "3").replace("⁶", "6").replace("⁴", "4").replace("⁵", "5")
            # Normalize multiplication & minus symbols
            t = t.replace("×", "x").replace("–", "-").replace("—", "-").replace("·", ".")
            # Remove caret exponent markers
            t = t.replace("^", "")
            return t

        src = normalize_math_text(item.get("source_text") or "")
        q_text = normalize_math_text(item.get("question") or "")
        ans = normalize_math_text(item.get("correct_answer") or item.get("correct") or "")
        exp = normalize_math_text(item.get("explanation") or "")

        # Stop words to ignore during overlap verification
        STOP_WORDS = {
            "what", "which", "where", "when", "why", "how", "does", "is", "are", "the",
            "a", "an", "of", "in", "to", "for", "with", "on", "at", "by", "from", "and",
            "or", "as", "that", "this", "these", "those", "it", "its", "into", "than"
        }

        # 1. Answer overlap check: Extract key words/tokens from correct answer
        ans_tokens = re.findall(r"[a-zA-Z0-9]+", ans)
        key_ans_tokens = [w for w in ans_tokens if w not in STOP_WORDS and (len(w) >= 3 or any(c.isdigit() for c in w))]

        # Direct token match or compressed formula match (e.g. 'hi2rt' in 'hi2rt')
        src_compact = re.sub(r"[^a-zA-Z0-9]", "", src)
        ans_compact = re.sub(r"[^a-zA-Z0-9]", "", ans)
        has_compact_match = len(ans_compact) >= 4 and ans_compact in src_compact

        matched_ans_tokens = [w for w in key_ans_tokens if w in src]
        if key_ans_tokens and len(matched_ans_tokens) == 0 and not has_compact_match:
            reasons.append(f"Correct answer '{ans}' has no conceptual presence in the cited source text.")

        # 2. Question overlap check: Extract key tokens from question
        q_tokens = re.findall(r"[a-zA-Z0-9]+", q_text)
        key_q_tokens = [w for w in q_tokens if len(w) >= 4 and w not in STOP_WORDS]
        matched_q_tokens = [w for w in key_q_tokens if w in src]
        if key_q_tokens and len(matched_q_tokens) == 0:
            reasons.append("Question subject concepts have no conceptual overlap with cited source text.")

        # 3. Explanation overlap check
        exp_tokens = re.findall(r"[a-zA-Z0-9]+", exp)
        key_exp_tokens = [w for w in exp_tokens if len(w) >= 4 and w not in STOP_WORDS]
        matched_exp_tokens = [w for w in key_exp_tokens if w in src]
        if key_exp_tokens and len(matched_exp_tokens) == 0:
            reasons.append("Explanation concepts have no conceptual overlap with cited source text.")

        is_supported = len(reasons) == 0
        return is_supported, reasons


# ==============================================================================
# CANONICAL GSEB/NCERT CURRICULUM QUESTION REPOSITORY
# Mapped directly to verified LearningContent chunks in edunavika.db
# ==============================================================================

CANONICAL_CURRICULUM_BANK: Dict[str, List[Dict[str, Any]]] = {
    # -------------------------------------------------------------------------
    # Topic 1: Chemical Reactions and Equations (Std 10 Science, Ch 1)
    # Topic ID: 5a321a44-bc06-4db4-a50f-5e53f913b612
    # -------------------------------------------------------------------------
    "5a321a44-bc06-4db4-a50f-5e53f913b612": [
        # Foundational
        {
            "id": "chem-ch1-f01",
            "topic_id": "5a321a44-bc06-4db4-a50f-5e53f913b612",
            "topic_title": "Chemical Reactions and Equations",
            "subject": "Science & Technology",
            "chapter": "Chemical Reactions and Equations",
            "difficulty": "FOUNDATIONAL",
            "question": "Why must chemical equations be balanced in accordance with the Law of Conservation of Mass?",
            "options": [
                "Total mass of elements in products must equal total mass in reactants",
                "To accelerate the reaction speed without altering mass",
                "To change the chemical formulae of reactants into simpler states",
                "To equalize the volume of gases participating in the reaction"
            ],
            "correct_answer": "Total mass of elements in products must equal total mass in reactants",
            "explanation": "Mass can neither be created nor destroyed in a chemical reaction. Therefore, the total mass and number of atoms in products must equal that in reactants (Textbook Page 16).",
            "source_document": "STD-10/Std-10_Science_English Medium.pdf",
            "source_page": 16,
            "source_chunk_id": "17b99fdc-d74c-49a0-9e48-9af8388849d0",
            "source_text": "Recall the law of conservation of mass that you studied in Class IX; mass can neither be created nor destroyed in a chemical reaction. That is, the total mass of the elements present in the products of a chemical reaction has to be equal to the total mass of the elements present in the reactants.",
            "skill_target": "Chemical Reactions and Equations Conservation Principles"
        },
        {
            "id": "chem-ch1-f02",
            "topic_id": "5a321a44-bc06-4db4-a50f-5e53f913b612",
            "topic_title": "Chemical Reactions and Equations",
            "subject": "Science & Technology",
            "chapter": "Chemical Reactions and Equations",
            "difficulty": "FOUNDATIONAL",
            "question": "Which of the following physical observations confirms that a chemical reaction has occurred?",
            "options": [
                "Change in state, colour, temperature, or evolution of a gas",
                "Simple change in container shape with constant temperature",
                "Reversible thermal expansion without colour change",
                "Mechanical mixing of substances without energetic change"
            ],
            "correct_answer": "Change in state, colour, temperature, or evolution of a gas",
            "explanation": "Observations that help determine a chemical reaction: change in state, change in colour, evolution of a gas, change in temperature (Textbook Page 15).",
            "source_document": "STD-10/Std-10_Science_English Medium.pdf",
            "source_page": 15,
            "source_chunk_id": "fe6d06de-d4e7-4214-80e6-41996bfcf837",
            "source_text": "From the above three activities, we can say that any of the following observations helps us to determine whether a chemical reaction has taken place: change in state, change in colour, evolution of a gas, change in temperature.",
            "skill_target": "Chemical Reactions and Equations Observable Indicators"
        },
        # Guided
        {
            "id": "chem-ch1-g01",
            "topic_id": "5a321a44-bc06-4db4-a50f-5e53f913b612",
            "topic_title": "Chemical Reactions and Equations",
            "subject": "Science & Technology",
            "chapter": "Chemical Reactions and Equations",
            "difficulty": "GUIDED",
            "question": "In the reaction 2Mg(s) + O2(g) -> 2MgO(s), what type of chemical reaction is taking place?",
            "options": [
                "Combination reaction",
                "Decomposition reaction",
                "Double displacement reaction",
                "Neutralisation reaction"
            ],
            "correct_answer": "Combination reaction",
            "explanation": "When two or more substances combine to form a single product, the reaction is defined as a combination reaction (Textbook Page 19).",
            "source_document": "STD-10/Std-10_Science_English Medium.pdf",
            "source_page": 19,
            "source_chunk_id": "16365587-1b56-4f7b-bb1c-6345f90255e7",
            "source_text": "Such a reaction in which a single product is formed from two or more reactants is known as a combination reaction. Calcium oxide reacts vigorously with water to produce slaked lime releasing a large amount of heat.",
            "skill_target": "Chemical Reactions and Equations Reaction Classification"
        },
        {
            "id": "chem-ch1-g02",
            "topic_id": "5a321a44-bc06-4db4-a50f-5e53f913b612",
            "topic_title": "Chemical Reactions and Equations",
            "subject": "Science & Technology",
            "chapter": "Chemical Reactions and Equations",
            "difficulty": "GUIDED",
            "question": "When balancing the equation Fe + H2O -> Fe3O4 + H2, what coefficient is required before H2O to balance oxygen atoms?",
            "options": [
                "4",
                "2",
                "3",
                "1"
            ],
            "correct_answer": "4",
            "explanation": "Fe3O4 contains 4 oxygen atoms on the product side; hence 4 molecules of H2O are required on the reactant side (Textbook Page 17).",
            "source_document": "STD-10/Std-10_Science_English Medium.pdf",
            "source_page": 17,
            "source_chunk_id": "4b5794b0-4c02-4bb6-8f7c-cd5f62b6357b",
            "source_text": "To equalise the number of oxygen atoms we can put coefficient 4 as 4 H2O and not H2O4 or (H2O)4. Now the partly balanced equation becomes: Fe + 4 H2O -> Fe3O4 + H2.",
            "skill_target": "Chemical Reactions and Equations Stepwise Balancing"
        },
        # Application
        {
            "id": "chem-ch1-a01",
            "topic_id": "5a321a44-bc06-4db4-a50f-5e53f913b612",
            "topic_title": "Chemical Reactions and Equations",
            "subject": "Science & Technology",
            "chapter": "Chemical Reactions and Equations",
            "difficulty": "APPLICATION",
            "question": "When iron nails are placed in a copper sulphate solution, what causes the blue colour of the solution to fade to green?",
            "options": [
                "Iron displaces copper forming iron(II) sulphate solution",
                "Copper displaces iron producing basic copper carbonate",
                "Both metals undergo thermal decomposition simultaneously",
                "Precipitation of insoluble blue copper hydroxide"
            ],
            "correct_answer": "Iron displaces copper forming iron(II) sulphate solution",
            "explanation": "Iron is more reactive than copper and displaces it from CuSO4 to form green FeSO4 while copper deposits on the nail (Textbook Page 24).",
            "source_document": "STD-10/Std-10_Science_English Medium.pdf",
            "source_page": 24,
            "source_chunk_id": "06032f51-2201-4f6e-8205-2682f87e1d3a",
            "source_text": "Why does the iron nail become brownish in colour and the blue colour of copper sulphate solution fades? Fe(s) + CuSO4(aq) -> FeSO4(aq) + Cu(s). In this reaction, iron has displaced or removed another element, copper, from copper sulphate solution. This reaction is known as displacement reaction.",
            "skill_target": "Chemical Reactions and Equations Displacement Reactions"
        },
        {
            "id": "chem-ch1-a02",
            "topic_id": "5a321a44-bc06-4db4-a50f-5e53f913b612",
            "topic_title": "Chemical Reactions and Equations",
            "subject": "Science & Technology",
            "chapter": "Chemical Reactions and Equations",
            "difficulty": "APPLICATION",
            "question": "In the reaction CuO + H2 -> Cu + H2O, which substance undergoes oxidation and which undergoes reduction?",
            "options": [
                "H2 is oxidised to H2O and CuO is reduced to Cu",
                "CuO is oxidised to Cu and H2 is reduced to H2O",
                "Both CuO and H2 are oxidised simultaneously",
                "Neither substance undergoes change in oxygen content"
            ],
            "correct_answer": "H2 is oxidised to H2O and CuO is reduced to Cu",
            "explanation": "H2 gains oxygen and is oxidised; CuO loses oxygen and is reduced, making it a redox reaction (Textbook Page 25).",
            "source_document": "STD-10/Std-10_Science_English Medium.pdf",
            "source_page": 25,
            "source_chunk_id": "4ed6649a-0565-4fd4-b95e-7745716cf5d1",
            "source_text": "If a substance gains oxygen during a reaction, it is said to be oxidised. If a substance loses oxygen during a reaction, it is said to be reduced. In this reaction, copper(II) oxide is losing oxygen and is being reduced. The hydrogen is gaining oxygen and is being oxidised.",
            "skill_target": "Chemical Reactions and Equations Redox Dynamics"
        },
        # Challenge
        {
            "id": "chem-ch1-c01",
            "topic_id": "5a321a44-bc06-4db4-a50f-5e53f913b612",
            "topic_title": "Chemical Reactions and Equations",
            "subject": "Science & Technology",
            "chapter": "Chemical Reactions and Equations",
            "difficulty": "CHALLENGE",
            "question": "Why are commercially packaged potato chips flushed with unreactive nitrogen gas?",
            "options": [
                "To prevent rancidity by stopping aerial oxidation of fats and oils",
                "To accelerate chemical ripening of the fried potato slices",
                "To absorb atmospheric moisture and retain salt hydration",
                "To catalyze endothermic preservation reactions in the pouch"
            ],
            "correct_answer": "To prevent rancidity by stopping aerial oxidation of fats and oils",
            "explanation": "Flushing chip bags with nitrogen gas provides an inert atmosphere that protects fats and oils from aerial oxidation and prevents rancidity (Textbook Page 26).",
            "source_document": "STD-10/Std-10_Science_English Medium.pdf",
            "source_page": 26,
            "source_chunk_id": "0e628449-d3d7-4d39-b315-e0696373496b",
            "source_text": "When fats and oils are oxidised, they become rancid and their smell and taste change. Usually substances which prevent oxidation (antioxidants) are added to foods containing fats and oil. Keeping food in air tight containers helps to slow down oxidation. Manufacturers of chips usually flush bags of chips with gas such as nitrogen to prevent the chips from getting oxidised.",
            "skill_target": "Chemical Reactions and Equations Rancidity Prevention"
        },
        {
            "id": "chem-ch1-c02",
            "topic_id": "5a321a44-bc06-4db4-a50f-5e53f913b612",
            "topic_title": "Chemical Reactions and Equations",
            "subject": "Science & Technology",
            "chapter": "Chemical Reactions and Equations",
            "difficulty": "CHALLENGE",
            "question": "When sodium sulphate solution reacts with barium chloride solution, what is the chemical identity of the insoluble white precipitate formed?",
            "options": [
                "Barium sulphate (BaSO4)",
                "Sodium chloride (NaCl)",
                "Barium sulphite (BaSO3)",
                "Sodium peroxide (Na2O2)"
            ],
            "correct_answer": "Barium sulphate (BaSO4)",
            "explanation": "Ba2+ ions react with SO4(2-) ions to form an insoluble white precipitate of barium sulphate (BaSO4) in a double displacement reaction (Textbook Page 24).",
            "source_document": "STD-10/Std-10_Science_English Medium.pdf",
            "source_page": 24,
            "source_chunk_id": "06032f51-2201-4f6e-8205-2682f87e1d3a",
            "source_text": "Na2SO4(aq) + BaCl2(aq) -> BaSO4(s) + 2NaCl(aq). You will observe that a white substance, which is insoluble in water, is formed. This insoluble substance formed is known as a precipitate. The white precipitate of BaSO4 is formed by the reaction of SO4(2-) and Ba(2+).",
            "skill_target": "Chemical Reactions and Equations Precipitation Mechanisms"
        }
    ],

    # -------------------------------------------------------------------------
    # Topic 2: Acids, Bases and Salts (Std 10 Science, Ch 2)
    # Topic ID: efee2da2-bd20-42bb-ad01-df2516530b1f
    # -------------------------------------------------------------------------
    "efee2da2-bd20-42bb-ad01-df2516530b1f": [
        # Foundational
        {
            "id": "chem-ch2-f01",
            "topic_id": "efee2da2-bd20-42bb-ad01-df2516530b1f",
            "topic_title": "Acids, Bases and Salts",
            "subject": "Science & Technology",
            "chapter": "Acids, Bases and Salts",
            "difficulty": "FOUNDATIONAL",
            "question": "Which ions do all acids and all bases generate respectively in an aqueous solution?",
            "options": [
                "Acids generate H+(aq) ions and bases generate OH-(aq) ions",
                "Acids generate OH-(aq) ions and bases generate H+(aq) ions",
                "Both acids and bases generate chloride Cl-(aq) ions",
                "Both acids and bases generate oxide O2-(aq) ions"
            ],
            "correct_answer": "Acids generate H+(aq) ions and bases generate OH-(aq) ions",
            "explanation": "All acids generate H+(aq) ions and all bases generate OH-(aq) ions in solution, leading to neutralization: H+(aq) + OH-(aq) -> H2O(l) (Textbook Page 37).",
            "source_document": "STD-10/Std-10_Science_English Medium.pdf",
            "source_page": 37,
            "source_chunk_id": "9d024491-83c8-440e-af1a-6fe856fde0b7",
            "source_text": "Bases generate hydroxide (OH–) ions in water. Now as we have identified that all acids generate H +(aq) and all bases generate OH – (aq), we can view the neutralisation reaction as follows – Acid + Base -> Salt + Water, H+(aq) + OH–(aq) -> H2O(l).",
            "skill_target": "Acids Bases and Salts Ionic Dissociation"
        },
        # Guided
        {
            "id": "chem-ch2-g01",
            "topic_id": "efee2da2-bd20-42bb-ad01-df2516530b1f",
            "topic_title": "Acids, Bases and Salts",
            "subject": "Science & Technology",
            "chapter": "Acids, Bases and Salts",
            "difficulty": "GUIDED",
            "question": "On the universal pH scale ranging from 0 to 14, what does a pH value of exactly 7 represent?",
            "options": [
                "A neutral solution such as pure water",
                "A strongly acidic solution",
                "A strongly alkaline solution",
                "A saturated salt solution only"
            ],
            "correct_answer": "A neutral solution such as pure water",
            "explanation": "A pH of 7 represents a neutral solution. Values below 7 represent an acidic solution, while values from 7 to 14 represent an alkaline solution (Textbook Page 38).",
            "source_document": "STD-10/Std-10_Science_English Medium.pdf",
            "source_page": 38,
            "source_chunk_id": "1adeee51-9cc0-4a4b-993d-6aaeb25997a1",
            "source_text": "The p in pH stands for 'potenz' in German, meaning power. On the pH scale we can measure pH generally from 0 (very acidic) to 14 (very alkaline). Neutral solution has a pH of 7. Values less than 7 represent an acidic solution.",
            "skill_target": "Acids Bases and Salts pH Metric Scale"
        },
        # Application
        {
            "id": "chem-ch2-a01",
            "topic_id": "efee2da2-bd20-42bb-ad01-df2516530b1f",
            "topic_title": "Acids, Bases and Salts",
            "subject": "Science & Technology",
            "chapter": "Acids, Bases and Salts",
            "difficulty": "APPLICATION",
            "question": "Why does an electric bulb glow in an aqueous solution of hydrochloric acid but not in aqueous glucose or alcohol solutions?",
            "options": [
                "Hydrochloric acid dissociates into free conducting ions while glucose does not",
                "Glucose absorbs the electric charge from the battery",
                "Hydrochloric acid has higher viscosity allowing mechanical conduction",
                "Alcohol completely neutralizes the electrode potential"
            ],
            "correct_answer": "Hydrochloric acid dissociates into free conducting ions while glucose does not",
            "explanation": "The glowing of the bulb indicates an electric current carries through the solution by free ions. Acids produce H+ ions in solution, whereas glucose and alcohol do not ionize (Textbook Page 36).",
            "source_document": "STD-10/Std-10_Science_English Medium.pdf",
            "source_page": 36,
            "source_chunk_id": "a0005cbd-c43b-466a-bb7c-304ab5a96401",
            "source_text": "The bulb will start glowing in the case of acids, as shown in Fig. 2.3. But you will observe that glucose and alcohol solutions do not conduct electricity. Glowing of the bulb indicates that there is a flow of electric current through the solution. The electric current is carried through the acidic solution by ions.",
            "skill_target": "Acids Bases and Salts Electrolytic Conduction"
        },
        # Challenge
        {
            "id": "chem-ch2-c01",
            "topic_id": "efee2da2-bd20-42bb-ad01-df2516530b1f",
            "topic_title": "Acids, Bases and Salts",
            "subject": "Science & Technology",
            "chapter": "Acids, Bases and Salts",
            "difficulty": "CHALLENGE",
            "question": "What is the chemical formula of Plaster of Paris, and why must it be stored in moisture-proof containers?",
            "options": [
                "CaSO4·1/2H2O; it reacts with moisture to set into hard gypsum (CaSO4·2H2O)",
                "CaSO4·2H2O; it loses water molecules upon contact with air",
                "CaCO3·1/2H2O; it releases carbon dioxide gas upon humidification",
                "CaOCl2; it hydrolyzes into gaseous chlorine upon exposure to water"
            ],
            "correct_answer": "CaSO4·1/2H2O; it reacts with moisture to set into hard gypsum (CaSO4·2H2O)",
            "explanation": "Plaster of Paris is calcium sulphate hemihydrate (CaSO4·1/2H2O). On mixing with water, it sets into a hard solid mass by forming gypsum (Textbook Page 46).",
            "source_document": "STD-10/Std-10_Science_English Medium.pdf",
            "source_page": 46,
            "source_chunk_id": "a11aa2ec-aa0e-4884-a5e9-31ee708869d3",
            "source_text": "On heating gypsum at 373 K, it loses water molecules and becomes calcium sulphate hemihydrate (CaSO4. 1/2 H2O). This is called Plaster of Paris, the substance which doctors use as plaster for supporting fractured bones in the right position. Plaster of Paris is a white powder and on mixing with water, it changes to gypsum once again giving a hard solid mass.",
            "skill_target": "Acids Bases and Salts Crystallisation Hydration"
        }
    ],

    # -------------------------------------------------------------------------
    # Topic 3: Electricity (Std 10 Science, Ch 11)
    # Topic ID: ea3cb4fd-f34d-409b-b0f6-d69b70db05b0
    # -------------------------------------------------------------------------
    "ea3cb4fd-f34d-409b-b0f6-d69b70db05b0": [
        # Foundational
        {
            "id": "phys-ch11-f01",
            "topic_id": "ea3cb4fd-f34d-409b-b0f6-d69b70db05b0",
            "topic_title": "Electricity",
            "subject": "Science & Technology",
            "chapter": "Electricity",
            "difficulty": "FOUNDATIONAL",
            "question": "According to Joule's law of heating, how is heat generated in a conductor related to current (I), resistance (R), and time (t)?",
            "options": [
                "H = I²Rt",
                "H = IRt",
                "H = I²R / t",
                "H = V / (IRt)"
            ],
            "correct_answer": "H = I²Rt",
            "explanation": "Joule's law of heating explicitly states H = I²Rt, implying heat produced is directly proportional to the square of current, resistance, and time (Textbook Page 202).",
            "source_document": "STD-10/Std-10_Science_English Medium.pdf",
            "source_page": 202,
            "source_chunk_id": "7003bfd0-7681-4366-b52f-e743ba2c51ae",
            "source_text": "Applying Ohm’s law [Eq. (11.5)], we get H = I2 Rt (11.21). This is known as Joule’s law of heating. The law implies that heat produced in a resistor is (i) directly proportional to the square of current for a given resistance, (ii) directly proportional to resistance for a given current, and (iii) directly proportional to the time for which the current flows through the resistor.",
            "skill_target": "Electricity Joule Heating Principles"
        },
        # Guided
        {
            "id": "phys-ch11-g01",
            "topic_id": "ea3cb4fd-f34d-409b-b0f6-d69b70db05b0",
            "topic_title": "Electricity",
            "subject": "Science & Technology",
            "chapter": "Electricity",
            "difficulty": "GUIDED",
            "question": "Which metal is almost exclusively used for filaments of electric lamps due to its exceptionally high melting point (3380 °C)?",
            "options": [
                "Tungsten",
                "Copper",
                "Aluminium",
                "Lead"
            ],
            "correct_answer": "Tungsten",
            "explanation": "Tungsten has an extremely high melting point of 3380 °C, retaining thermal energy and glowing incandescently without melting (Textbook Page 203).",
            "source_document": "STD-10/Std-10_Science_English Medium.pdf",
            "source_page": 203,
            "source_chunk_id": "c2533663-9e08-4f56-be4b-bd0f40598e5f",
            "source_text": "The electric heating is also used to produce light, as in an electric bulb. Here, the filament must retain as much of the heat generated as is possible, so that it gets very hot and emits light. It must not melt at such high temperatures. A strong metal with high melting point such as tungsten (melting point 3380 C) is used for making bulb filaments.",
            "skill_target": "Electricity Filament Material Properties"
        },
        # Application
        {
            "id": "phys-ch11-a01",
            "topic_id": "ea3cb4fd-f34d-409b-b0f6-d69b70db05b0",
            "topic_title": "Electricity",
            "subject": "Science & Technology",
            "chapter": "Electricity",
            "difficulty": "APPLICATION",
            "question": "How does an electric fuse function to protect domestic appliances from excessive current surges?",
            "options": [
                "It melts and breaks the circuit when current exceeds the safe rating",
                "It increases circuit voltage to dissipate surplus amperage",
                "It acts as a step-down transformer under high load",
                "It converts excess electric charge into chemical potential energy"
            ],
            "correct_answer": "It melts and breaks the circuit when current exceeds the safe rating",
            "explanation": "A fuse is placed in series with appliances; when excessive current flows, Joule heating melts the fuse wire and breaks the circuit safely (Textbook Page 203).",
            "source_document": "STD-10/Std-10_Science_English Medium.pdf",
            "source_page": 203,
            "source_chunk_id": "c2533663-9e08-4f56-be4b-bd0f40598e5f",
            "source_text": "Another common application of Joule’s heating is the fuse used in electric circuits. It protects circuits and appliances by stopping the flow of any unduly high electric current. The fuse is placed in series with the device. If a current larger than the specified value flows through the circuit, the temperature of the fuse wire increases. This melts the fuse wire and breaks the circuit.",
            "skill_target": "Electricity Circuit Safety Mechanisms"
        },
        # Challenge
        {
            "id": "phys-ch11-c01",
            "topic_id": "ea3cb4fd-f34d-409b-b0f6-d69b70db05b0",
            "topic_title": "Electricity",
            "subject": "Science & Technology",
            "chapter": "Electricity",
            "difficulty": "CHALLENGE",
            "question": "What is the commercial unit of electrical energy (1 kilowatt hour or 1 kWh) expressed in standard SI Joules?",
            "options": [
                "3.6 × 10⁶ Joules",
                "3.6 × 10⁵ Joules",
                "1.0 × 10³ Joules",
                "7.2 × 10⁶ Joules"
            ],
            "correct_answer": "3.6 × 10⁶ Joules",
            "explanation": "1 kWh = 1000 W × 3600 s = 3.6 × 10⁶ W·s = 3.6 × 10⁶ J (Textbook Page 204).",
            "source_document": "STD-10/Std-10_Science_English Medium.pdf",
            "source_page": 204,
            "source_chunk_id": "24169a26-16a2-4010-8f53-83cf7fdb8b15",
            "source_text": "The commercial unit of electric energy is kilowatt hour (kW h), commonly known as 'unit'. 1 kW h = 1000 watt x 3600 second = 3.6 x 10^6 watt second = 3.6 x 10^6 joule (J).",
            "skill_target": "Electricity Electrical Energy Quantification"
        }
    ],

    # -------------------------------------------------------------------------
    # Topic 4: Real Numbers & Polynomials (Std 10 Mathematics, Ch 1)
    # Topic ID: e84e1b11-f928-4b38-93ad-738af5c0b1e5
    # -------------------------------------------------------------------------
    "e84e1b11-f928-4b38-93ad-738af5c0b1e5": [
        # Foundational
        {
            "id": "math-ch1-f01",
            "topic_id": "e84e1b11-f928-4b38-93ad-738af5c0b1e5",
            "topic_title": "1.2 The Fundamental Theorem of Arithmetic",
            "subject": "Mathematics",
            "chapter": "Polynomials / Real Numbers",
            "difficulty": "FOUNDATIONAL",
            "question": "What does the Fundamental Theorem of Arithmetic assert regarding composite numbers?",
            "options": [
                "Every composite number can be uniquely expressed as a product of primes, apart from the order of factors",
                "Every natural number is a prime number",
                "The product of two irrational numbers is always rational",
                "Composite numbers cannot be factorised into prime components"
            ],
            "correct_answer": "Every composite number can be uniquely expressed as a product of primes, apart from the order of factors",
            "explanation": "The Fundamental Theorem of Arithmetic states that every composite number can be expressed (factorised) as a product of primes uniquely, up to the order in which prime factors occur (Textbook Page 18).",
            "source_document": "STD-10/Std-10_Maths_EnglishMedium.pdf",
            "source_page": 18,
            "source_chunk_id": "ff25fec3-625b-4592-a890-4aa96551392d",
            "source_text": "Theorem 1.1 (Fundamental Theorem of Arithmetic) : Every composite number can be expressed (factorised) as a product of primes, and this factorisation is unique, apart from the order in which the prime factors occur.",
            "skill_target": "Fundamental Theorem of Arithmetic Prime Factorisation"
        },
        # Guided
        {
            "id": "math-ch1-g01",
            "topic_id": "e84e1b11-f928-4b38-93ad-738af5c0b1e5",
            "topic_title": "1.2 The Fundamental Theorem of Arithmetic",
            "subject": "Mathematics",
            "chapter": "Polynomials / Real Numbers",
            "difficulty": "GUIDED",
            "question": "For any two positive integers a and b, what is the exact mathematical relationship between their HCF and LCM?",
            "options": [
                "HCF(a, b) × LCM(a, b) = a × b",
                "HCF(a, b) + LCM(a, b) = a + b",
                "HCF(a, b) / LCM(a, b) = a / b",
                "HCF(a, b) × LCM(a, b) = (a × b)²"
            ],
            "correct_answer": "HCF(a, b) × LCM(a, b) = a × b",
            "explanation": "For any two positive integers a and b, HCF(a, b) × LCM(a, b) = a × b (Textbook Page 20).",
            "source_document": "STD-10/Std-10_Maths_EnglishMedium.pdf",
            "source_page": 20,
            "source_chunk_id": "e05b516b-c241-4d3d-a7db-5f56d86b6820",
            "source_text": "Notice that 96 x 404 = 38784. Also, HCF x LCM = 4 x 9696 = 38784. Hence, HCF x LCM = product of the two numbers. This is a very useful result: For any two positive integers a and b, HCF (a, b) x LCM (a, b) = a x b.",
            "skill_target": "Fundamental Theorem of Arithmetic HCF-LCM Relationship"
        },
        # Application
        {
            "id": "math-ch1-a01",
            "topic_id": "e84e1b11-f928-4b38-93ad-738af5c0b1e5",
            "topic_title": "1.2 The Fundamental Theorem of Arithmetic",
            "subject": "Mathematics",
            "chapter": "Polynomials / Real Numbers",
            "difficulty": "APPLICATION",
            "question": "If the prime factorisation of 96 is 2⁵ × 3 and 404 is 2² × 101, what is the Highest Common Factor (HCF) of 96 and 404?",
            "options": [
                "4",
                "2",
                "8",
                "12"
            ],
            "correct_answer": "4",
            "explanation": "HCF is the product of the smallest power of each common prime factor: 2² = 4 (Textbook Page 20).",
            "source_document": "STD-10/Std-10_Maths_EnglishMedium.pdf",
            "source_page": 20,
            "source_chunk_id": "e05b516b-c241-4d3d-a7db-5f56d86b6820",
            "source_text": "Solution : The prime factorisation of 96 and 404 gives : 96 = 2^5 x 3, 404 = 2^2 x 101. Therefore, the HCF of these two integers is 4.",
            "skill_target": "Fundamental Theorem of Arithmetic Factor Calculation"
        },
        # Challenge
        {
            "id": "math-ch1-c01",
            "topic_id": "e84e1b11-f928-4b38-93ad-738af5c0b1e5",
            "topic_title": "1.2 The Fundamental Theorem of Arithmetic",
            "subject": "Mathematics",
            "chapter": "Polynomials / Real Numbers",
            "difficulty": "CHALLENGE",
            "question": "Why can the number 4ⁿ (where n is a natural number) never end with the digit 0?",
            "options": [
                "Its prime factorisation contains only 2, whereas ending in 0 requires prime factor 5",
                "4 is an even number and cannot be divided by 2",
                "The power n must be negative to terminate in 0",
                "4ⁿ generates only irrational numbers for natural values of n"
            ],
            "correct_answer": "Its prime factorisation contains only 2, whereas ending in 0 requires prime factor 5",
            "explanation": "A number ending in 0 must have 2 and 5 in its prime factorisation. Since 4ⁿ = (2²)ⁿ = 2²ⁿ, 5 is not a prime factor, so 4ⁿ cannot end in 0 (Textbook Page 19).",
            "source_document": "STD-10/Std-10_Maths_EnglishMedium.pdf",
            "source_page": 19,
            "source_chunk_id": "ddd921db-0dd1-4ff9-a93b-6e7183ea0d3e",
            "source_text": "Consider the numbers 4^n, where n is a natural number. Check whether there is any value of n for which 4^n ends with the digit zero. If the number 4^n, for any n, were to end with the digit zero, then it would be divisible by 5. That is, the prime factorisation of 4^n would contain the prime 5. This is not possible because 4^n = (2)^2n; so the only prime in the factorisation of 4^n is 2.",
            "skill_target": "Fundamental Theorem of Arithmetic Divisibility Analysis"
        }
    ],

    # -------------------------------------------------------------------------
    # Topic 5: Quadratic Equations (Std 10 Mathematics, Ch 4)
    # Topic ID: c3dd6779-9b5b-411c-9ade-07e241713835
    # -------------------------------------------------------------------------
    "c3dd6779-9b5b-411c-9ade-07e241713835": [
        # Foundational
        {
            "id": "math-ch4-f01",
            "topic_id": "c3dd6779-9b5b-411c-9ade-07e241713835",
            "topic_title": "4.2 Quadratic Equations",
            "subject": "Mathematics",
            "chapter": "Quadratic Equations",
            "difficulty": "FOUNDATIONAL",
            "question": "What is the standard algebraic form of a quadratic equation in variable x?",
            "options": [
                "ax² + bx + c = 0, where a, b, c are real numbers and a ≠ 0",
                "ax + b = 0, where a ≠ 0",
                "ax³ + bx² + cx + d = 0, where a ≠ 0",
                "a/x² + b/x + c = 0, where a ≠ 0"
            ],
            "correct_answer": "ax² + bx + c = 0, where a, b, c are real numbers and a ≠ 0",
            "explanation": "A quadratic equation in the variable x is an equation of the form ax² + bx + c = 0, where a, b, c are real numbers and a ≠ 0 (Textbook Page 54).",
            "source_document": "STD-10/Std-10_Maths_EnglishMedium.pdf",
            "source_page": 53,
            "source_chunk_id": "672fcef8-da86-4c63-9f18-72efcbf475ec",
            "source_text": "A quadratic equation in the variable x is an equation of the form ax2 + bx + c = 0, where a, b, c are real numbers and a != 0. In fact, any equation of the form p(x) = 0, where p(x) is a polynomial of degree 2, is a quadratic equation.",
            "skill_target": "Quadratic Equations Standard Form"
        },
        # Guided
        {
            "id": "math-ch4-g01",
            "topic_id": "c3dd6779-9b5b-411c-9ade-07e241713835",
            "topic_title": "4.2 Quadratic Equations",
            "subject": "Mathematics",
            "chapter": "Quadratic Equations",
            "difficulty": "GUIDED",
            "question": "What is the quadratic formula derived by ancient mathematician Sridharacharya to find roots of ax² + bx + c = 0?",
            "options": [
                "x = (-b ± √(b² - 4ac)) / (2a)",
                "x = (-b ± √(b² + 4ac)) / (2a)",
                "x = (b ± √(b² - 4ac)) / a",
                "x = (-b ± 2√(ac)) / (4a)"
            ],
            "correct_answer": "x = (-b ± √(b² - 4ac)) / (2a)",
            "explanation": "The quadratic formula gives roots x = (-b ± √(b² - 4ac)) / (2a) provided b² - 4ac ≥ 0 (Textbook Page 54).",
            "source_document": "STD-10/Std-10_Maths_EnglishMedium.pdf",
            "source_page": 53,
            "source_chunk_id": "672fcef8-da86-4c63-9f18-72efcbf475ec",
            "source_text": "Sridharacharya (C.E. 1025) derived a formula, now known as the quadratic formula, (as quoted by Bhaskara II) for solving a quadratic equation by the method of completing the square: x = (-b +- sqrt(b^2 - 4ac)) / (2a).",
            "skill_target": "Quadratic Equations Sridharacharya Formula"
        },
        # Application
        {
            "id": "math-ch4-a01",
            "topic_id": "c3dd6779-9b5b-411c-9ade-07e241713835",
            "topic_title": "4.2 Quadratic Equations",
            "subject": "Mathematics",
            "chapter": "Quadratic Equations",
            "difficulty": "APPLICATION",
            "question": "If John and Jivanti have 45 marbles, both lose 5 marbles, and the product of remaining marbles is 124, what quadratic equation mathematically models the problem?",
            "options": [
                "x² - 45x + 324 = 0",
                "x² - 55x + 750 = 0",
                "x² + 45x - 324 = 0",
                "x² - 40x + 200 = 0"
            ],
            "correct_answer": "x² - 45x + 324 = 0",
            "explanation": "Let John have x marbles. Then (x - 5)(40 - x) = 124, which simplifies directly to x² - 45x + 324 = 0 (Textbook Page 55).",
            "source_document": "STD-10/Std-10_Maths_EnglishMedium.pdf",
            "source_page": 55,
            "source_chunk_id": "1f5a3404-1459-40b5-b9d2-9907f137bae1",
            "source_text": "So, – x2 + 45x – 200 = 124 (Given that product = 124)\ni.e., – x2 + 45x – 324 = 0\ni.e.,x2 – 45x + 324 = 0\nTherefore, the number of marbles John had, satisfies the quadratic equation x2 – 45x + 324 = 0.",
            "skill_target": "Quadratic Equations Mathematical Modeling"
        },
        # Challenge
        {
            "id": "math-ch4-c01",
            "topic_id": "c3dd6779-9b5b-411c-9ade-07e241713835",
            "topic_title": "4.2 Quadratic Equations",
            "subject": "Mathematics",
            "chapter": "Quadratic Equations",
            "difficulty": "CHALLENGE",
            "question": "What is the nature of the roots of a quadratic equation ax² + bx + c = 0 when discriminant D = b² - 4ac < 0?",
            "options": [
                "No real roots exist (there is no real number whose square is negative)",
                "Two distinct real roots exist",
                "Two equal real roots exist",
                "Exactly one rational root exists"
            ],
            "correct_answer": "No real roots exist (there is no real number whose square is negative)",
            "explanation": "When b² - 4ac < 0, there is no real number whose square is b² - 4ac; hence no real roots exist for the quadratic equation (Textbook Page 59).",
            "source_document": "STD-10/Std-10_Maths_EnglishMedium.pdf",
            "source_page": 59,
            "source_chunk_id": "ac274551-0f6d-472a-a5e9-f4822efdbfe3",
            "source_text": "If b2 – 4ac < 0, then there is no real number whose square is b2 – 4ac. Therefore, there are no real roots for the given quadratic equation in this case. Since b2 – 4ac determines whether the quadratic equation ax2 + bx + c = 0 has real roots or not, b2 – 4ac is called the discriminant.",
            "skill_target": "Quadratic Equations Discriminant Analysis"
        }
    ]
}


def get_canonical_question_by_id(question_id: str) -> Optional[Dict[str, Any]]:
    """
    Looks up a question across all topics in CANONICAL_CURRICULUM_BANK by question id.
    Handles exact id match (e.g. 'chem-ch1-f01') or substring/session id matches.
    """
    if not question_id:
        return None
    for tid, qlist in CANONICAL_CURRICULUM_BANK.items():
        for q in qlist:
            if q.get("id") == question_id:
                return q
            if q.get("id") and q.get("id") in question_id:
                return q
    return None


def get_canonical_questions_for_topic(topic_id: str, difficulty: Optional[str] = None, topic_title: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Retrieves verified curriculum questions for a topic ID, optionally filtered by difficulty tier.
    """
    questions = CANONICAL_CURRICULUM_BANK.get(topic_id)
    search_keys = []
    if topic_title:
        search_keys.append(topic_title)
    if topic_id:
        search_keys.append(topic_id)

    if not questions:
        for sk in search_keys:
            clean_k = sk.lower().replace('&', 'and').replace('—', '-').replace('–', '-').replace('?', '-').strip()
            for k, qlist in CANONICAL_CURRICULUM_BANK.items():
                if qlist:
                    t_title = qlist[0].get("topic_title", "").lower().replace('&', 'and').replace('—', '-').replace('–', '-').strip()
                    c_title = qlist[0].get("chapter", "").lower().replace('&', 'and').replace('—', '-').replace('–', '-').strip()
                    if (len(clean_k) >= 4 and (clean_k in t_title or clean_k in c_title)) or (len(t_title) >= 4 and t_title in clean_k):
                        questions = qlist
                        break
            if questions:
                break

    questions = questions or []
    if difficulty:
        diff_upper = difficulty.upper()
        matching = [q for q in questions if q.get("difficulty") == diff_upper]
        if matching:
            return matching
    return questions


def canonical_question_matches_topic(
    question: Dict[str, Any], topic_id: str, topic_title: Optional[str] = None,
) -> bool:
    """Return true only when a canonical question is in the resolved topic's bank.

    A question id alone is not sufficient evidence of scope: clients also submit a
    topic id, and recording a valid question against a different topic corrupts the
    learner model.  Compare against the resolved topic list so database UUID aliases
    and human-readable topic names continue to work without cross-topic fallback.
    """
    question_id = question.get("id")
    return any(
        candidate.get("id") == question_id
        for candidate in get_canonical_questions_for_topic(topic_id, topic_title=topic_title)
    )


# Alias real SQLite database topic IDs to ensure seamless retrieval
CANONICAL_CURRICULUM_BANK["f35b0ee4-25e9-428e-b90b-391767cc35c7"] = CANONICAL_CURRICULUM_BANK["5a321a44-bc06-4db4-a50f-5e53f913b612"]
CANONICAL_CURRICULUM_BANK["d11470ef-41a7-432f-abc1-5d95a62aca38"] = CANONICAL_CURRICULUM_BANK["efee2da2-bd20-42bb-ad01-df2516530b1f"]
CANONICAL_CURRICULUM_BANK["aae5ca86-d399-41ad-a26c-09070df208ea"] = CANONICAL_CURRICULUM_BANK["ea3cb4fd-f34d-409b-b0f6-d69b70db05b0"]
CANONICAL_CURRICULUM_BANK["7edd3f20-4360-49be-9d5a-b521225013c9"] = CANONICAL_CURRICULUM_BANK["e84e1b11-f928-4b38-93ad-738af5c0b1e5"]
