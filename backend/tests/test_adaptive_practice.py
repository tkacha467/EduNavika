import pytest
from unittest.mock import MagicMock, patch

from backend.app.domain.enums import MasteryLevel, PerformanceTrend, RetentionRiskLevel
from backend.app.schemas.knowledge_profile import TopicKnowledgeProfile
from backend.app.schemas.retrieval import RetrievedContentItem
from backend.app.schemas.practice import (
    AdaptivePracticeQuestion,
    AdaptivePracticeResponse,
    PracticeSubmissionRequest,
    PracticeSubmissionResponse,
)
from backend.app.services.adaptive_practice import (
    AdaptivePracticeService,
    adaptive_practice_service,
)
from backend.app.models import LearningEvent, TopicPerformance, Topic, StudentProfile, EventType


@pytest.fixture
def base_profile():
    return TopicKnowledgeProfile(
        topic_id="5a321a44-bc06-4db4-a50f-5e53f913b612",
        topic_title="Chemical Reactions and Equations",
        subject_name="Science",
        mastery_level=MasteryLevel.NOVICE,
        accuracy=33.3,
        total_attempts=6,
        correct_attempts=2,
        trend=PerformanceTrend.STABLE,
        retention_risk=RetentionRiskLevel.LOW,
        recent_accuracy=33.3,
        average_response_time_ms=12000,
    )


@pytest.fixture
def practice_fixture(db_session):
    from backend.app.models import User, UserRole, Standard, Subject, Chapter, Topic, StudentProfile
    user = User(
        name="Test Student Practice",
        email="test_prac@edunavika.org",
        hashed_password="pw",
        role=UserRole.STUDENT,
        is_active=True,
    )
    db_session.add(user)
    db_session.flush()

    std = Standard(grade_number=10, name="Standard 10")
    db_session.add(std)
    db_session.flush()

    subj = Subject(name="Science", code="SCI-10", standard_id=std.id)
    db_session.add(subj)
    db_session.flush()

    chap = Chapter(title="Chemical Reactions and Equations", chapter_number=1, subject_id=subj.id)
    db_session.add(chap)
    db_session.flush()

    topic = Topic(title="Chemical Reactions and Equations", chapter_id=chap.id, topic_order=1)
    db_session.add(topic)
    db_session.flush()

    from backend.app.models import LearningContent
    chunk = LearningContent(
        id="06f69c9e-137a-4d30-91af-93fd17e032b1",
        topic_id=topic.id,
        title="Chemical Reactions and Equations Textbook Excerpt",
        content_text="Recall the law of conservation of mass that you studied in Class IX; mass can neither be created nor destroyed in a chemical reaction. That is, the total mass of the elements present in the products of a chemical reaction has to be equal to the total mass of the elements present in the reactants.",
        source_document="STD-10/Std-10_Science_English Medium.pdf",
        source_page=16,
    )
    db_session.add(chunk)
    db_session.flush()

    student = StudentProfile(user_id=user.id, standard_id=std.id)
    db_session.add(student)
    db_session.commit()

    return {
        "student": student,
        "topic": topic,
    }



def test_1_novice_gets_foundational_difficulty(base_profile):
    """Novice student with < 50% accuracy receives FOUNDATIONAL difficulty."""
    diff, reason = AdaptivePracticeService.determine_difficulty(
        profile=base_profile,
        retention_risk=RetentionRiskLevel.LOW,
        trend=PerformanceTrend.STABLE,
    )
    assert diff == "FOUNDATIONAL"
    assert "foundational" in reason.lower()


def test_2_developing_gets_guided_difficulty(base_profile):
    """Developing student with 50-69% accuracy receives GUIDED difficulty."""
    base_profile.mastery_level = MasteryLevel.DEVELOPING
    base_profile.accuracy = 60.0
    base_profile.recent_accuracy = 60.0

    diff, reason = AdaptivePracticeService.determine_difficulty(
        profile=base_profile,
        retention_risk=RetentionRiskLevel.LOW,
        trend=PerformanceTrend.STABLE,
    )
    assert diff == "GUIDED"
    assert "guided" in reason.lower()


def test_3_proficient_gets_application_difficulty(base_profile):
    """Proficient student with 70-84% accuracy receives APPLICATION difficulty."""
    base_profile.mastery_level = MasteryLevel.PROFICIENT
    base_profile.accuracy = 75.0
    base_profile.recent_accuracy = 75.0

    diff, reason = AdaptivePracticeService.determine_difficulty(
        profile=base_profile,
        retention_risk=RetentionRiskLevel.LOW,
        trend=PerformanceTrend.STABLE,
    )
    assert diff == "APPLICATION"
    assert "application" in reason.lower()


def test_4_mastered_gets_challenge_difficulty(base_profile):
    """Mastered student with >= 85% accuracy receives CHALLENGE difficulty."""
    base_profile.mastery_level = MasteryLevel.MASTERED
    base_profile.accuracy = 90.0
    base_profile.recent_accuracy = 90.0

    diff, reason = AdaptivePracticeService.determine_difficulty(
        profile=base_profile,
        retention_risk=RetentionRiskLevel.LOW,
        trend=PerformanceTrend.STABLE,
    )
    assert diff == "CHALLENGE"
    assert "challenge" in reason.lower()


def test_5_high_retention_risk_prioritizes_revision(base_profile):
    """High retention risk is explicitly noted and prioritizes revision."""
    diff, reason = AdaptivePracticeService.determine_difficulty(
        profile=base_profile,
        retention_risk=RetentionRiskLevel.HIGH,
        trend=PerformanceTrend.STABLE,
    )
    assert "High retention risk detected" in reason


def test_6_declining_trend_lowers_difficulty(base_profile):
    """Declining performance trend steps down difficulty to rebuild foundational mastery."""
    base_profile.mastery_level = MasteryLevel.PROFICIENT
    base_profile.accuracy = 75.0
    base_profile.recent_accuracy = 75.0

    diff, reason = AdaptivePracticeService.determine_difficulty(
        profile=base_profile,
        retention_risk=RetentionRiskLevel.LOW,
        trend=PerformanceTrend.DECLINING,
    )
    # Stepped down from APPLICATION to GUIDED
    assert diff == "GUIDED"
    assert "Stepped down from Application" in reason


def test_7_question_is_curriculum_grounded_with_source_page(db_session, practice_fixture):
    """Generated practice questions strictly return source document and page number."""
    student = practice_fixture["student"]
    topic = practice_fixture["topic"]

    res = adaptive_practice_service.generate_practice_questions(
        db=db_session,
        student_id=student.id,
        topic_id=topic.id,
        count=3,
    )
    assert isinstance(res, AdaptivePracticeResponse)
    assert len(res.questions) == 3
    for q in res.questions:
        assert q.source_document is not None
        assert q.source_page is not None
        assert q.source_page in (12, 14, 15, 16, 17, 18, 20, 21, 22, 23)
        assert q.correct_answer is None  # Hidden from student endpoint before submission


def test_8_mcq_has_exactly_four_distinct_options(db_session, practice_fixture):
    """Every generated MCQ has exactly 4 non-empty, distinct options."""
    student = practice_fixture["student"]
    topic = practice_fixture["topic"]

    res = adaptive_practice_service.generate_practice_questions(
        db=db_session,
        student_id=student.id,
        topic_id=topic.id,
        count=2,
    )
    for q in res.questions:
        assert len(q.options) == 4
        assert len(set(q.options)) == 4


def test_9_correct_answer_matches_an_option(db_session, practice_fixture):
    """The underlying verified correct answer matches one of the 4 options."""
    student = practice_fixture["student"]
    topic = practice_fixture["topic"]

    res = adaptive_practice_service.generate_practice_questions(
        db=db_session,
        student_id=student.id,
        topic_id=topic.id,
        count=1,
    )
    q = res.questions[0]
    meta = adaptive_practice_service._ACTIVE_QUESTIONS[q.id]
    assert meta["correct_answer"] in q.options


def test_10_incorrect_answer_produces_personalized_feedback(db_session, practice_fixture):
    """Submitting an incorrect answer produces specific conceptual feedback referencing misconceptions."""
    student = practice_fixture["student"]
    topic = practice_fixture["topic"]

    res = adaptive_practice_service.generate_practice_questions(
        db=db_session,
        student_id=student.id,
        topic_id=topic.id,
        count=1,
    )
    q = res.questions[0]
    meta = adaptive_practice_service._ACTIVE_QUESTIONS[q.id]
    wrong_opt = next(opt for opt in q.options if opt != meta["correct_answer"])

    sub_res = adaptive_practice_service.submit_practice_answer(
        db=db_session,
        submission=PracticeSubmissionRequest(
            student_id=student.id,
            question_id=q.id,
            topic_id=topic.id,
            selected_answer=wrong_opt,
            response_time_ms=8500,
        ),
    )
    assert sub_res.correct is False
    assert sub_res.correct_answer == meta["correct_answer"]
    assert "Not quite" in sub_res.feedback or "Close attempt" in sub_res.feedback or "slip" in sub_res.feedback
    assert len(sub_res.next_recommended_action) > 0


def test_11_correct_answer_produces_personalized_feedback(db_session, practice_fixture):
    """Submitting a correct answer acknowledges conceptual grasp and advises next action."""
    student = practice_fixture["student"]
    topic = practice_fixture["topic"]

    res = adaptive_practice_service.generate_practice_questions(
        db=db_session,
        student_id=student.id,
        topic_id=topic.id,
        count=1,
    )
    q = res.questions[0]
    meta = adaptive_practice_service._ACTIVE_QUESTIONS[q.id]
    correct_opt = meta["correct_answer"]

    sub_res = adaptive_practice_service.submit_practice_answer(
        db=db_session,
        submission=PracticeSubmissionRequest(
            student_id=student.id,
            question_id=q.id,
            topic_id=topic.id,
            selected_answer=correct_opt,
            response_time_ms=6200,
        ),
    )
    assert sub_res.correct is True
    assert sub_res.correct_answer == correct_opt
    assert "grasp" in sub_res.feedback.lower() or "job" in sub_res.feedback.lower() or "accurately" in sub_res.feedback.lower() or "excellent" in sub_res.feedback.lower()


def test_12_submission_creates_learning_event(db_session, practice_fixture):
    """Submitting practice response creates an atomic LearningEvent of type PRACTICE in database."""
    student = practice_fixture["student"]
    topic = practice_fixture["topic"]

    res = adaptive_practice_service.generate_practice_questions(
        db=db_session,
        student_id=student.id,
        topic_id=topic.id,
        count=1,
    )
    q = res.questions[0]
    meta = adaptive_practice_service._ACTIVE_QUESTIONS[q.id]

    initial_event_count = db_session.query(LearningEvent).filter(
        LearningEvent.student_id == student.id,
        LearningEvent.topic_id == topic.id,
        LearningEvent.event_type == EventType.PRACTICE,
    ).count()

    adaptive_practice_service.submit_practice_answer(
        db=db_session,
        submission=PracticeSubmissionRequest(
            student_id=student.id,
            question_id=q.id,
            topic_id=topic.id,
            selected_answer=meta["correct_answer"],
            response_time_ms=5000,
        ),
    )

    new_event_count = db_session.query(LearningEvent).filter(
        LearningEvent.student_id == student.id,
        LearningEvent.topic_id == topic.id,
        LearningEvent.event_type == EventType.PRACTICE,
    ).count()
    assert new_event_count == initial_event_count + 1


def test_13_mock_local_llm_mcq_generation(db_session, practice_fixture):
    """Mocking local LLM creates valid MCQ and labels generation_mode as LOCAL_LLM."""
    student = practice_fixture["student"]
    topic = practice_fixture["topic"]

    service = AdaptivePracticeService()
    mock_llm = MagicMock()
    mock_llm.create_chat_completion.return_value = {
        "choices": [
            {
                "message": {
                    "content": (
                        "QUESTION: What law explains why chemical equations must be balanced?\n"
                        "A) Law of conservation of mass\n"
                        "B) Law of constant proportions\n"
                        "C) Law of multiple proportions\n"
                        "D) Boyle's Law\n"
                        "CORRECT: A\n"
                        "EXPLANATION: Mass can neither be created nor destroyed during chemical change."
                    )
                }
            }
        ]
    }

    with patch.object(service.llm_engine, "_get_llm", return_value=mock_llm):
        res = service.generate_practice_questions(
            db=db_session,
            student_id=student.id,
            topic_id=topic.id,
            count=1,
        )

    assert res.generation_mode == "LOCAL_LLM"
    assert res.model_name == "Qwen2.5-0.5B-Instruct"
    assert len(res.questions) == 1
    assert "chemical equations" in res.questions[0].question.lower()
    assert "Law of conservation of mass" in res.questions[0].options
    assert len(res.questions[0].options) == 4


def test_14_missing_local_model_falls_back_safely(db_session, practice_fixture):
    """When local LLM is missing or unavailable, service seamlessly uses DETERMINISTIC_FALLBACK."""
    student = practice_fixture["student"]
    topic = practice_fixture["topic"]

    service = AdaptivePracticeService()
    with patch.object(service.llm_engine, "_get_llm", return_value=None):
        res = service.generate_practice_questions(
            db=db_session,
            student_id=student.id,
            topic_id=topic.id,
            count=2,
        )
    assert res.generation_mode == "DETERMINISTIC_FALLBACK"
    assert len(res.questions) == 2


def test_15_no_external_api_calls_in_practice_module():
    """Verify adaptive practice service contains zero cloud AI or HTTP networking clients."""
    import backend.app.services.adaptive_practice as ap_mod
    code = open(ap_mod.__file__, "r", encoding="utf-8").read()
    forbidden = ["openai", "google.generativeai", "anthropic", "requests.", "httpx.", "urllib.request"]
    for word in forbidden:
        assert word not in code, f"Found forbidden network client '{word}' in adaptive_practice.py"


def test_16_unassessed_student_gets_foundational_diagnostic(base_profile):
    """Unassessed student or 0 attempts recommends FOUNDATIONAL diagnostic practice."""
    unassessed_prof = base_profile.model_copy()
    unassessed_prof.mastery_level = MasteryLevel.UNASSESSED
    unassessed_prof.total_attempts = 0
    diff, reason = AdaptivePracticeService.determine_difficulty(
        profile=unassessed_prof,
        retention_risk=RetentionRiskLevel.LOW,
        trend=PerformanceTrend.STABLE,
    )
    assert diff == "FOUNDATIONAL"
    assert "unassessed" in reason.lower()


def test_17_recommend_next_practice_endpoint_logic(db_session, practice_fixture):
    """Test recommend_next_practice returns correct PracticeRecommendation schema and real topic."""
    student = practice_fixture["student"]
    topic = practice_fixture["topic"]

    rec = adaptive_practice_service.recommend_next_practice(
        db=db_session,
        student_id=student.id,
        topic_id=topic.id,
    )
    assert rec.topic_id == topic.id
    assert rec.topic_title == topic.title
    assert rec.recommended_difficulty == "FOUNDATIONAL"
    assert rec.recommended_action == "FOUNDATIONAL_PRACTICE"
    assert rec.mastery_level in (MasteryLevel.UNASSESSED, MasteryLevel.NOVICE)


def test_18_improving_trend_encourages_progression(base_profile):
    """Improving trend on developing mastery detects positive trend."""
    dev_prof = base_profile.model_copy()
    dev_prof.mastery_level = MasteryLevel.DEVELOPING
    dev_prof.accuracy = 65.0
    dev_prof.recent_accuracy = 65.0
    diff, reason = AdaptivePracticeService.determine_difficulty(
        profile=dev_prof,
        retention_risk=RetentionRiskLevel.LOW,
        trend=PerformanceTrend.IMPROVING,
    )
    assert diff == "GUIDED"
    assert "positive performance trend" in reason.lower()
