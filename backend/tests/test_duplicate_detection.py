from backend.app.models import MCQQuestion, QuestionDifficulty, OptionKey, QuestionStatus
from backend.app.services.duplicate_detection import (
    normalize_text,
    compute_text_hash,
    ExactDuplicateDetector,
    SemanticDuplicateDetectorInterface,
)


def test_normalize_text_and_hashing():
    raw_1 = "What is the product when Calcium Oxide reacts with Water?"
    raw_2 = "  what  is the product   when calcium oxide reacts with water?   "
    raw_3 = "What is the product, when Calcium Oxide reacts with Water?!"

    norm_1 = normalize_text(raw_1)
    norm_2 = normalize_text(raw_2)
    norm_3 = normalize_text(raw_3)

    assert norm_1 == norm_2 == norm_3
    assert compute_text_hash(raw_1) == compute_text_hash(raw_2) == compute_text_hash(raw_3)


def test_exact_duplicate_detection(db_session, seed_data):
    topic = seed_data["topic"]

    question_text = "Which of the following is a decomposition reaction?"
    
    # 1. First check: should not be a duplicate
    check_1 = ExactDuplicateDetector.check_duplicate(db_session, question_text)
    assert check_1.is_exact_duplicate is False
    assert check_1.existing_question_id is None

    # 2. Create the question
    mcq = MCQQuestion(
        topic_id=topic.id,
        question_text=question_text,
        option_a="2H2 + O2 -> 2H2O",
        option_b="CaCO3 -> CaO + CO2",
        option_c="C + O2 -> CO2",
        option_d="Na + Cl -> NaCl",
        correct_option=OptionKey.B,
        difficulty=QuestionDifficulty.EASY,
        status=QuestionStatus.APPROVED,
    )
    db_session.add(mcq)
    db_session.flush()

    # Record history
    history = ExactDuplicateDetector.record_history(db_session, mcq)
    db_session.commit()

    assert history.text_hash == compute_text_hash(question_text)

    # 3. Second check with slight punctuation / casing differences: should detect exact duplicate
    variation = "   WHICH of the following is a decomposition reaction?   "
    check_2 = ExactDuplicateDetector.check_duplicate(db_session, variation)
    assert check_2.is_exact_duplicate is True
    assert check_2.existing_question_id == mcq.id
    assert check_2.duplicate_type == "EXACT"


def test_semantic_interface_contract():
    # Verify that the semantic interface contract exists and enforces abstract methods
    class DummyDetector(SemanticDuplicateDetectorInterface):
        def check_semantic_duplicate(self, db, normalized_text, threshold=0.85):
            return ("simulated-q-id", 0.92)

    detector = DummyDetector()
    res = detector.check_semantic_duplicate(None, "dummy text")
    assert res == ("simulated-q-id", 0.92)
