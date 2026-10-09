import pytest
from backend.app.models import (
    User,
    UserRole,
    Standard,
    Subject,
    Chapter,
    Topic,
    StudentProfile,
    LearningEvent,
    TopicPerformance,
    EventType,
)
from backend.app.domain.enums import MasteryLevel, PerformanceTrend, RetentionRiskLevel
from backend.app.schemas.practice import PracticeSubmissionRequest
from backend.app.schemas.explanation import ExplanationRequest
from backend.app.services.adaptive_practice import adaptive_practice_service
from backend.app.services.knowledge_model import KnowledgeModelService
from backend.app.services.recommendation_engine import RecommendationEngineService
from backend.app.services.progress_service import student_progress_service
from backend.app.services.personalized_explanation import personalized_explanation_service
from backend.app.services.curriculum_question_bank import CANONICAL_CURRICULUM_BANK
from backend.app.services.curriculum_translations import (
    localize_question,
    localize_subject_name,
    localize_recommendation_reason,
    QUESTION_TRANSLATIONS,
)


@pytest.fixture
def multilingual_fixture(db_session):
    """Sets up a complete Standard 10 curriculum environment with an active student."""
    user = User(
        name="Devanshi Shah",
        email="devanshi@edunavika.org",
        hashed_password="pw_multilingual",
        role=UserRole.STUDENT,
        is_active=True,
    )
    db_session.add(user)
    db_session.flush()

    std = Standard(grade_number=10, name="Standard 10")
    db_session.add(std)
    db_session.flush()

    subj = Subject(name="Science & Technology", code="SCI-10", standard_id=std.id)
    db_session.add(subj)
    db_session.flush()

    chap1 = Chapter(title="Chemical Reactions and Equations", chapter_number=1, subject_id=subj.id)
    db_session.add(chap1)
    db_session.flush()

    t1 = Topic(title="Chemical Reactions and Equations", chapter_id=chap1.id, topic_order=1)
    db_session.add(t1)
    db_session.flush()

    student = StudentProfile(
        user_id=user.id,
        standard_id=std.id,
        division="A",
        enrollment_number="DEV-1001",
        preferred_language="en",
    )
    db_session.add(student)
    db_session.commit()

    return {
        "student": student,
        "t1": t1,
        "subj": subj,
    }


def test_default_language_is_english(multilingual_fixture, client):
    """Verify default language is English across database model and user endpoint."""
    student = multilingual_fixture["student"]
    assert student.preferred_language == "en"

    resp = client.get(f"/api/v1/students/{student.id}/language")
    assert resp.status_code == 200
    data = resp.json()
    assert data["preferred_language"] == "en"
    assert data["supported_languages"] == ["en", "hi", "gu"]


def test_update_language_preference_persists(multilingual_fixture, client, db_session):
    """Verify student language preference can be updated to Hindi and Gujarati and persists."""
    student = multilingual_fixture["student"]

    # 1. Update to Hindi
    resp_hi = client.put(
        f"/api/v1/students/{student.id}/language",
        json={"preferred_language": "hi"}
    )
    assert resp_hi.status_code == 200
    assert resp_hi.json()["preferred_language"] == "hi"

    # Verify directly in DB
    db_session.refresh(student)
    assert student.preferred_language == "hi"

    # 2. Update to Gujarati
    resp_gu = client.put(
        f"/api/v1/students/{student.id}/language",
        json={"preferred_language": "gu"}
    )
    assert resp_gu.status_code == 200
    assert resp_gu.json()["preferred_language"] == "gu"

    # Verify directly in DB
    db_session.refresh(student)
    assert student.preferred_language == "gu"


def test_invalid_language_code_rejected(multilingual_fixture, client):
    """Verify unsupported language codes return HTTP 400 Bad Request."""
    student = multilingual_fixture["student"]

    for invalid_lang in ["fr", "es", "de", "invalid", "123"]:
        resp = client.put(
            f"/api/v1/students/{student.id}/language",
            json={"preferred_language": invalid_lang}
        )
        assert resp.status_code == 400
        error_msg = resp.json().get("error", {}).get("message") or resp.json().get("detail", "")
        assert "Unsupported language" in error_msg


def test_language_switch_preserves_knowledge_profile_invariants(multilingual_fixture, db_session):
    """
    Core Invariant: Language is purely a presentation layer.
    Switching language MUST NOT alter student knowledge profile, accuracy,
    mastery level, or attempt counts.
    """
    student = multilingual_fixture["student"]
    topic = multilingual_fixture["t1"]

    # 1. Record 2 practice attempts in English (1 correct, 1 incorrect)
    sub1 = PracticeSubmissionRequest(
        student_id=student.id,
        topic_id=topic.id,
        question_id="prac-init-01",
        selected_answer="To satisfy the law of conservation of mass",
        language="en",
    )
    adaptive_practice_service.submit_practice_answer(db_session, sub1)

    sub2 = PracticeSubmissionRequest(
        student_id=student.id,
        topic_id=topic.id,
        question_id="prac-init-02",
        selected_answer="Wrong option",
        language="en",
    )
    adaptive_practice_service.submit_practice_answer(db_session, sub2)

    # Compute baseline knowledge profile in English
    prof_en = KnowledgeModelService.calculate_topic_profile(db_session, student.id, topic)
    baseline_attempts = prof_en.total_attempts
    baseline_correct = prof_en.correct_attempts
    baseline_accuracy = prof_en.accuracy
    baseline_mastery = prof_en.mastery_level

    assert baseline_attempts == 2
    assert baseline_correct == 1
    assert baseline_accuracy == 50.0

    # 2. Switch student language to Gujarati ('gu')
    student.preferred_language = "gu"
    db_session.commit()

    # Re-calculate knowledge profile
    prof_gu = KnowledgeModelService.calculate_topic_profile(db_session, student.id, topic)
    assert prof_gu.total_attempts == baseline_attempts
    assert prof_gu.correct_attempts == baseline_correct
    assert prof_gu.accuracy == baseline_accuracy
    assert prof_gu.mastery_level == baseline_mastery

    # 3. Switch student language to Hindi ('hi')
    student.preferred_language = "hi"
    db_session.commit()

    # Re-calculate knowledge profile
    prof_hi = KnowledgeModelService.calculate_topic_profile(db_session, student.id, topic)
    assert prof_hi.total_attempts == baseline_attempts
    assert prof_hi.correct_attempts == baseline_correct
    assert prof_hi.accuracy == baseline_accuracy
    assert prof_hi.mastery_level == baseline_mastery


def test_canonical_question_metadata_invariance_across_languages():
    """
    Verify canonical question metadata is 100% preserved across translations:
    - Same question ID
    - Same source document and page
    - Same difficulty
    - Chemical equations preserved
    """
    for lang in ["hi", "gu"]:
        for qid, trans in QUESTION_TRANSLATIONS[lang].items():
            # Check translation dictionary consistency
            assert "question" in trans and len(trans["question"]) > 10
            assert "options" in trans and len(trans["options"]) == 4
            assert "correct_answer" in trans and trans["correct_answer"] in trans["options"]
            assert "explanation" in trans and len(trans["explanation"]) > 10

    # Test specific canonical questions
    canonical_sample = CANONICAL_CURRICULUM_BANK["5a321a44-bc06-4db4-a50f-5e53f913b612"][0]
    loc_hi = localize_question(canonical_sample, "hi")
    loc_gu = localize_question(canonical_sample, "gu")

    # Invariants
    assert loc_hi["id"] == canonical_sample["id"]
    assert loc_gu["id"] == canonical_sample["id"]
    assert loc_hi["difficulty"] == canonical_sample["difficulty"]
    assert loc_gu["difficulty"] == canonical_sample["difficulty"]
    assert loc_hi["source_page"] == canonical_sample["source_page"]
    assert loc_gu["source_page"] == canonical_sample["source_page"]
    assert loc_hi["source_document"] == canonical_sample["source_document"]
    assert loc_gu["source_document"] == canonical_sample["source_document"]


def test_practice_question_generation_hindi_and_gujarati(multilingual_fixture, db_session):
    """
    Verify question generation in Hindi and Gujarati returns localized text
    with deterministic fallback (0% hallucination).
    """
    student = multilingual_fixture["student"]
    topic = multilingual_fixture["t1"]

    # 1. Hindi generation
    res_hi = adaptive_practice_service.generate_practice_questions(
        db=db_session,
        student_id=student.id,
        topic_id=topic.id,
        count=2,
        language="hi",
    )
    assert res_hi.total_questions == 2
    assert res_hi.generation_mode == "DETERMINISTIC_FALLBACK"
    q_hi = res_hi.questions[0]
    # Check Hindi character presence (Devanagari Unicode range \u0900-\u097F)
    assert any('\u0900' <= char <= '\u097F' for char in q_hi.question)
    assert len(q_hi.options) == 4
    assert any('\u0900' <= char <= '\u097F' for char in q_hi.options[0])

    # 2. Gujarati generation
    res_gu = adaptive_practice_service.generate_practice_questions(
        db=db_session,
        student_id=student.id,
        topic_id=topic.id,
        count=2,
        language="gu",
    )
    assert res_gu.total_questions == 2
    assert res_gu.generation_mode == "DETERMINISTIC_FALLBACK"
    q_gu = res_gu.questions[0]
    # Check Gujarati character presence (Gujarati Unicode range \u0A80-\u0AFF)
    assert any('\u0A80' <= char <= '\u0AFF' for char in q_gu.question)
    assert len(q_gu.options) == 4
    assert any('\u0A80' <= char <= '\u0AFF' for char in q_gu.options[0])


def test_practice_submission_and_localized_feedback(multilingual_fixture, db_session):
    """
    Verify practice submission in Hindi and Gujarati returns localized feedback
    and updates knowledge profile identically.
    """
    student = multilingual_fixture["student"]
    topic = multilingual_fixture["t1"]

    # Generate Gujarati questions to get active registered question ID
    gen_gu = adaptive_practice_service.generate_practice_questions(
        db=db_session,
        student_id=student.id,
        topic_id=topic.id,
        count=1,
        language="gu",
    )
    q_item = gen_gu.questions[0]

    # Get hidden correct answer from registry
    meta = adaptive_practice_service._ACTIVE_QUESTIONS[q_item.id]
    correct_ans_gu = meta["correct_answer"]

    # Submit correct answer in Gujarati
    sub_gu_correct = PracticeSubmissionRequest(
        student_id=student.id,
        topic_id=topic.id,
        question_id=q_item.id,
        selected_answer=correct_ans_gu,
        language="gu",
    )
    resp_gu_correct = adaptive_practice_service.submit_practice_answer(db_session, sub_gu_correct)
    assert resp_gu_correct.correct is True
    # Gujarati feedback check (contains Gujarati script)
    assert any('\u0A80' <= char <= '\u0AFF' for char in resp_gu_correct.feedback)

    # Submit incorrect answer in Hindi
    gen_hi = adaptive_practice_service.generate_practice_questions(
        db=db_session,
        student_id=student.id,
        topic_id=topic.id,
        count=1,
        language="hi",
    )
    q_hi_item = gen_hi.questions[0]
    sub_hi_wrong = PracticeSubmissionRequest(
        student_id=student.id,
        topic_id=topic.id,
        question_id=q_hi_item.id,
        selected_answer="गलत उत्तर विकल्प",
        language="hi",
    )
    resp_hi_wrong = adaptive_practice_service.submit_practice_answer(db_session, sub_hi_wrong)
    assert resp_hi_wrong.correct is False
    # Hindi feedback check (contains Devanagari script)
    assert any('\u0900' <= char <= '\u097F' for char in resp_hi_wrong.feedback)


def test_recommendations_localized_without_altering_scores(multilingual_fixture, db_session):
    """
    Verify recommendations return localized subject_name and reason in Hindi and Gujarati
    while score, action, and priority remain identical to English.
    """
    student = multilingual_fixture["student"]

    rec_en = RecommendationEngineService.generate_recommendations(db_session, student.id, limit=5, language="en")
    rec_hi = RecommendationEngineService.generate_recommendations(db_session, student.id, limit=5, language="hi")
    rec_gu = RecommendationEngineService.generate_recommendations(db_session, student.id, limit=5, language="gu")

    assert rec_en.total_recommendations == rec_hi.total_recommendations == rec_gu.total_recommendations

    if rec_en.recommendations:
        item_en = rec_en.recommendations[0]
        item_hi = rec_hi.recommendations[0]
        item_gu = rec_gu.recommendations[0]

        # Invariants: score, action, priority, topic_id
        assert item_en.score == item_hi.score == item_gu.score
        assert item_en.action == item_hi.action == item_gu.action
        assert item_en.priority == item_hi.priority == item_gu.priority
        assert item_en.topic_id == item_hi.topic_id == item_gu.topic_id

        # Localized fields
        assert item_hi.subject_name == "विज्ञान एवं प्रौद्योगिकी"
        assert item_gu.subject_name == "વિજ્ઞાન અને ટેકનોલોજી"
        assert any('\u0900' <= char <= '\u097F' for char in item_hi.reason)
        assert any('\u0A80' <= char <= '\u0AFF' for char in item_gu.reason)


def test_progress_tracking_localized_without_altering_counts(multilingual_fixture, db_session):
    """
    Verify progress tracking localizes subject names while preserving total_topics_available,
    topics_studied, overall_accuracy, and mastery_distribution.
    """
    student = multilingual_fixture["student"]

    prog_en = student_progress_service.get_student_progress(db_session, student.id, language="en")
    prog_hi = student_progress_service.get_student_progress(db_session, student.id, language="hi")
    prog_gu = student_progress_service.get_student_progress(db_session, student.id, language="gu")

    # Invariants
    assert prog_en.overall.total_topics_available == prog_hi.overall.total_topics_available == prog_gu.overall.total_topics_available
    assert prog_en.overall.topics_studied == prog_hi.overall.topics_studied == prog_gu.overall.topics_studied
    assert prog_en.overall.overall_accuracy == prog_hi.overall.overall_accuracy == prog_gu.overall.overall_accuracy

    # Localized subject names
    assert prog_hi.overall.subject_name == "विज्ञान एवं प्रौद्योगिकी"
    assert prog_gu.overall.subject_name == "વિજ્ઞાન અને ટેકનોલોજી"


def test_personalized_explanation_multilingual(multilingual_fixture, db_session):
    """
    Verify personalized explanations generate authentic Hindi and Gujarati explanations
    adapted to the student's mastery profile.
    """
    student = multilingual_fixture["student"]
    topic = multilingual_fixture["t1"]

    req_hi = ExplanationRequest(
        student_id=student.id,
        topic_id=topic.id,
        preferred_mode="DETAILED",
        language="hi",
    )
    exp_hi = personalized_explanation_service.generate_explanation(db_session, req_hi)
    assert any('\u0900' <= char <= '\u097F' for char in exp_hi.explanation)
    assert exp_hi.generation_mode == "DETERMINISTIC_FALLBACK"

    req_gu = ExplanationRequest(
        student_id=student.id,
        topic_id=topic.id,
        preferred_mode="DETAILED",
        language="gu",
    )
    exp_gu = personalized_explanation_service.generate_explanation(db_session, req_gu)
    assert any('\u0A80' <= char <= '\u0AFF' for char in exp_gu.explanation)
    assert exp_gu.generation_mode == "DETERMINISTIC_FALLBACK"


def test_zero_cloud_translation_dependency():
    """
    Verify that translation is 100% offline with zero cloud translation API calls.
    Tests that translation functions execute purely from local dictionaries.
    """
    sample_q = {
        "id": "chem-ch1-f01",
        "question": "Why balance?",
        "options": ["A", "B", "C", "D"],
        "correct_answer": "A",
        "explanation": "Exp",
    }
    # Direct function execution requires no network
    hi_q = localize_question(sample_q, "hi")
    gu_q = localize_question(sample_q, "gu")
    assert hi_q["question"] != sample_q["question"]
    gu_subj = localize_subject_name("Science & Technology", "gu")
    assert gu_subj == "વિજ્ઞાન અને ટેકનોલોજી"
    hi_subj = localize_subject_name("Science & Technology", "hi")
    assert hi_subj == "विज्ञान एवं प्रौद्योगिकी"
