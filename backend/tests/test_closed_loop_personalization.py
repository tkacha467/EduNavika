import pytest
from datetime import datetime, timezone, timedelta
from unittest.mock import MagicMock

from backend.app.models import (
    User, UserRole, Standard, Subject, Chapter, Topic,
    StudentProfile, LearningContent, EventType, ForgettingSignal, ForgettingSignalStatus
)
from backend.app.domain.enums import MasteryLevel, PerformanceTrend, RetentionRiskLevel
from backend.app.services.event_recorder import EventRecorderService
from backend.app.services.knowledge_model import KnowledgeModelService
from backend.app.services.recommendation_engine import RecommendationEngineService
from backend.app.services.adaptive_practice import AdaptivePracticeService, PracticeSubmissionRequest
from backend.app.services.personalized_explanation import PersonalizedExplanationService
from backend.app.schemas.explanation import ExplanationRequest
from backend.app.services.curriculum_question_bank import CANONICAL_CURRICULUM_BANK


@pytest.fixture
def closed_loop_setup(db_session):
    """Sets up a complete 3-topic curriculum environment."""
    user = User(name="Closed Loop Student", email="loop_test@edunavika.org", hashed_password="pw", role=UserRole.STUDENT, is_active=True)
    db_session.add(user)
    db_session.flush()

    std = Standard(grade_number=10, name="Standard 10")
    db_session.add(std)
    db_session.flush()

    student = StudentProfile(id="student-test-loop-01", user_id=user.id, standard_id=std.id)
    db_session.add(student)
    db_session.flush()

    sub_sci = Subject(name="Science & Technology", code="SCI-10", standard_id=std.id)
    sub_math = Subject(name="Mathematics", code="MATH-10", standard_id=std.id)
    db_session.add_all([sub_sci, sub_math])
    db_session.flush()

    ch_chem = Chapter(title="Chemical Reactions and Equations", chapter_number=1, subject_id=sub_sci.id)
    ch_elec = Chapter(title="Electricity", chapter_number=11, subject_id=sub_sci.id)
    ch_quad = Chapter(title="Quadratic Equations", chapter_number=4, subject_id=sub_math.id)
    db_session.add_all([ch_chem, ch_elec, ch_quad])
    db_session.flush()

    t_chem = Topic(id="5a321a44-bc06-4db4-a50f-5e53f913b612", title="Chemical Reactions and Equations", chapter_id=ch_chem.id, topic_order=1)
    t_elec = Topic(id="ea3cb4fd-f34d-409b-b0f6-d69b70db05b0", title="Electricity", chapter_id=ch_elec.id, topic_order=2)
    t_quad = Topic(id="c3dd6779-9b5b-411c-9ade-07e241713835", title="Quadratic Equations", chapter_id=ch_quad.id, topic_order=3)
    db_session.add_all([t_chem, t_elec, t_quad])
    db_session.flush()

    # Seed learning contents for curriculum retrieval
    seen_chunk_ids = set()
    for tid in [t_chem.id, t_elec.id, t_quad.id]:
        qlist = CANONICAL_CURRICULUM_BANK.get(tid, [])
        for q in qlist:
            cid = q["source_chunk_id"]
            if cid in seen_chunk_ids:
                continue
            seen_chunk_ids.add(cid)
            c = LearningContent(
                id=cid,
                topic_id=tid,
                title=f"{q['topic_title']} Chunk",
                content_text=q["source_text"],
                source_document=q["source_document"],
                source_page=q["source_page"],
            )
            db_session.add(c)
    db_session.commit()

    return {
        "student": student,
        "chem": t_chem,
        "elec": t_elec,
        "quad": t_quad,
    }


def test_mastery_changes_after_attempt(db_session, closed_loop_setup):
    """
    Test 1: Verifies that after valid curriculum attempts, knowledge profile updates
    total attempts, correct attempts, accuracy, and transitions mastery levels.
    """
    student = closed_loop_setup["student"]
    topic = closed_loop_setup["chem"]

    # Initial state
    p0 = KnowledgeModelService.calculate_topic_profile(db_session, student.id, topic)
    assert p0.mastery_level == MasteryLevel.UNASSESSED
    assert p0.total_attempts == 0

    # 2 wrong attempts -> NOVICE
    for _ in range(2):
        EventRecorderService.record_event(
            db=db_session,
            student_id=student.id,
            topic_id=topic.id,
            event_type=EventType.PRACTICE,
            correctness=False,
            auto_commit=True,
        )

    p1 = KnowledgeModelService.calculate_topic_profile(db_session, student.id, topic)
    assert p1.mastery_level == MasteryLevel.NOVICE
    assert p1.total_attempts == 2
    assert p1.accuracy == 0.0

    # 4 correct attempts -> DEVELOPING (4/6 = 66.7%)
    for _ in range(4):
        EventRecorderService.record_event(
            db=db_session,
            student_id=student.id,
            topic_id=topic.id,
            event_type=EventType.PRACTICE,
            correctness=True,
            auto_commit=True,
        )

    p2 = KnowledgeModelService.calculate_topic_profile(db_session, student.id, topic)
    assert p2.mastery_level == MasteryLevel.DEVELOPING
    assert p2.total_attempts == 6
    assert p2.accuracy == 66.67
    assert p2.trend == PerformanceTrend.IMPROVING


def test_weak_topic_is_detected(db_session, closed_loop_setup):
    """
    Test 2: Verifies that a topic with low accuracy (1/5) is flagged as a weakness with HIGH retention risk.
    """
    student = closed_loop_setup["student"]
    topic = closed_loop_setup["chem"]

    for i in range(5):
        EventRecorderService.record_event(
            db=db_session,
            student_id=student.id,
            topic_id=topic.id,
            event_type=EventType.PRACTICE,
            correctness=(i == 0),
            auto_commit=True,
        )

    prof = KnowledgeModelService.calculate_topic_profile(db_session, student.id, topic)
    assert prof.accuracy == 20.0
    assert prof.mastery_level == MasteryLevel.NOVICE
    assert prof.retention_risk == RetentionRiskLevel.HIGH


def test_strong_topic_is_detected(db_session, closed_loop_setup):
    """
    Test 3: Verifies that a topic with high accuracy (5/5) is identified as a strength (MASTERED).
    """
    student = closed_loop_setup["student"]
    topic = closed_loop_setup["quad"]

    for _ in range(5):
        EventRecorderService.record_event(
            db=db_session,
            student_id=student.id,
            topic_id=topic.id,
            event_type=EventType.PRACTICE,
            correctness=True,
            auto_commit=True,
        )

    prof = KnowledgeModelService.calculate_topic_profile(db_session, student.id, topic)
    assert prof.accuracy == 100.0
    assert prof.mastery_level == MasteryLevel.MASTERED
    assert prof.retention_risk == RetentionRiskLevel.LOW


def test_difficulty_adapts_to_mastery(db_session, closed_loop_setup):
    """
    Test 4: Verifies that question generation selects the difficulty matching the student's profile.
    """
    student = closed_loop_setup["student"]
    topic = closed_loop_setup["chem"]
    svc = AdaptivePracticeService()

    # Novice profile (0% acc) -> FOUNDATIONAL
    EventRecorderService.record_event(
        db=db_session,
        student_id=student.id,
        topic_id=topic.id,
        event_type=EventType.PRACTICE,
        correctness=False,
        auto_commit=True,
    )
    p_novice = KnowledgeModelService.calculate_topic_profile(db_session, student.id, topic)
    diff_novice, _ = svc.determine_difficulty(p_novice, p_novice.retention_risk, p_novice.trend)
    assert diff_novice == "FOUNDATIONAL"

    # Proficient profile -> APPLICATION
    p_prof = p_novice.model_copy()
    p_prof.mastery_level = MasteryLevel.PROFICIENT
    p_prof.accuracy = 80.0
    p_prof.recent_accuracy = 80.0
    diff_prof, _ = svc.determine_difficulty(p_prof, RetentionRiskLevel.LOW, PerformanceTrend.IMPROVING)
    assert diff_prof == "APPLICATION"


def test_high_retention_risk_triggers_revision(db_session, closed_loop_setup):
    """
    Test 5: Verifies that an unresolved forgetting signal triggers HIGH retention risk and revision recommendation.
    """
    student = closed_loop_setup["student"]
    topic = closed_loop_setup["elec"]

    # Record normal performance first
    for _ in range(4):
        EventRecorderService.record_event(
            db=db_session,
            student_id=student.id,
            topic_id=topic.id,
            event_type=EventType.PRACTICE,
            correctness=True,
            auto_commit=True,
        )

    # Add forgetting signal
    sig = ForgettingSignal(
        student_id=student.id,
        topic_id=topic.id,
        evidence_type="LONG_GAP",
        evidence_strength="STRONG",
        status=ForgettingSignalStatus.UNRESOLVED,
        detected_at=datetime.now(timezone.utc),
    )
    db_session.add(sig)
    db_session.commit()

    prof = KnowledgeModelService.calculate_topic_profile(db_session, student.id, topic)
    assert prof.retention_risk == RetentionRiskLevel.HIGH

    recs = RecommendationEngineService.generate_recommendations(db_session, student.id).recommendations
    elec_rec = next((r for r in recs if r.topic_id == topic.id), None)
    assert elec_rec is not None
    assert elec_rec.action.value in ("REVISION", "REVIEW")
    assert elec_rec.priority.value in ("HIGH", "URGENT")


def test_weak_topic_gets_higher_recommendation_priority(db_session, closed_loop_setup):
    """
    Test 6: Verifies that weak topics are prioritized over mastered topics in recommendations.
    """
    student = closed_loop_setup["student"]
    t_chem = closed_loop_setup["chem"]
    t_quad = closed_loop_setup["quad"]

    # Chem is weak: 1/5 correct
    for i in range(5):
        EventRecorderService.record_event(
            db=db_session,
            student_id=student.id,
            topic_id=t_chem.id,
            event_type=EventType.PRACTICE,
            correctness=(i == 0),
            auto_commit=True,
        )

    # Quad is strong: 5/5 correct
    for _ in range(5):
        EventRecorderService.record_event(
            db=db_session,
            student_id=student.id,
            topic_id=t_quad.id,
            event_type=EventType.PRACTICE,
            correctness=True,
            auto_commit=True,
        )

    recs = RecommendationEngineService.generate_recommendations(db_session, student.id).recommendations
    assert len(recs) >= 2
    # First recommendation must be the weak Chemistry topic
    assert recs[0].topic_id == t_chem.id
    assert recs[0].score > recs[1].score


def test_recommendation_is_student_specific(db_session, closed_loop_setup):
    """
    Test 7: Verifies that recommendations differ across students with different strengths and weaknesses.
    """
    std = closed_loop_setup["student"]
    t_chem = closed_loop_setup["chem"]
    t_quad = closed_loop_setup["quad"]

    # Student 2 who is weak in Math and strong in Chem
    user2 = User(name="Other Student", email="other@edunavika.org", hashed_password="pw", role=UserRole.STUDENT, is_active=True)
    db_session.add(user2)
    db_session.flush()
    student2 = StudentProfile(id="student-test-loop-02", user_id=user2.id, standard_id=std.standard_id)
    db_session.add(student2)
    db_session.commit()

    # Student 1: Weak Chem (1/5), Strong Math (5/5)
    for i in range(5):
        EventRecorderService.record_event(db=db_session, student_id=std.id, topic_id=t_chem.id, event_type=EventType.PRACTICE, correctness=(i == 0), auto_commit=True)
        EventRecorderService.record_event(db=db_session, student_id=std.id, topic_id=t_quad.id, event_type=EventType.PRACTICE, correctness=True, auto_commit=True)

    # Student 2: Strong Chem (5/5), Weak Math (1/5)
    for i in range(5):
        EventRecorderService.record_event(db=db_session, student_id=student2.id, topic_id=t_chem.id, event_type=EventType.PRACTICE, correctness=True, auto_commit=True)
        EventRecorderService.record_event(db=db_session, student_id=student2.id, topic_id=t_quad.id, event_type=EventType.PRACTICE, correctness=(i == 0), auto_commit=True)

    recs1 = RecommendationEngineService.generate_recommendations(db_session, std.id).recommendations
    recs2 = RecommendationEngineService.generate_recommendations(db_session, student2.id).recommendations

    assert recs1[0].topic_id == t_chem.id
    assert recs2[0].topic_id == t_quad.id


def test_explanation_depth_matches_knowledge_level(db_session, closed_loop_setup):
    """
    Test 8: Verifies that explanation adapts teaching level (FOUNDATIONAL vs SYNTHESIS) based on mastery.
    """
    student = closed_loop_setup["student"]
    t_chem = closed_loop_setup["chem"]
    exp_svc = PersonalizedExplanationService()

    # Weak knowledge profile
    for i in range(3):
        EventRecorderService.record_event(db=db_session, student_id=student.id, topic_id=t_chem.id, event_type=EventType.PRACTICE, correctness=False, auto_commit=True)

    req_weak = ExplanationRequest(student_id=student.id, topic_id=t_chem.id, query="Explain balancing")
    resp_weak = exp_svc.generate_explanation(db_session, req_weak)
    assert resp_weak.teaching_level == "FOUNDATIONAL_REMEDIATION"

    # Advance student to high mastery
    for _ in range(10):
        EventRecorderService.record_event(db=db_session, student_id=student.id, topic_id=t_chem.id, event_type=EventType.PRACTICE, correctness=True, auto_commit=True)

    req_strong = ExplanationRequest(student_id=student.id, topic_id=t_chem.id, query="Explain balancing")
    resp_strong = exp_svc.generate_explanation(db_session, req_strong)
    assert resp_strong.teaching_level in ("ADVANCED_APPLICATION", "SYNTHESIS_AND_MASTERY")


def test_closed_loop_personalization(db_session, closed_loop_setup):
    """
    Test 9: Full closed-loop test from initial errors to remediation to upgraded difficulty.
    """
    student = closed_loop_setup["student"]
    topic = closed_loop_setup["chem"]
    practice_svc = AdaptivePracticeService()

    # Step A: 2 wrong answers
    for _ in range(2):
        q = CANONICAL_CURRICULUM_BANK[topic.id][0]
        practice_svc._ACTIVE_QUESTIONS[q["id"]] = {
            "student_id": student.id,
            "topic_id": topic.id,
            "difficulty": q["difficulty"],
            "correct_answer": q["correct_answer"],
            "explanation": q["explanation"],
            "source_document": q["source_document"],
            "source_page": q["source_page"],
        }
        sub = PracticeSubmissionRequest(
            student_id=student.id,
            topic_id=topic.id,
            question_id=q["id"],
            selected_answer="Wrong answer",
            response_time_ms=7000,
        )
        practice_svc.submit_practice_answer(db_session, sub)

    rec_after_errors = practice_svc.recommend_next_practice(db_session, student.id, topic.id)
    assert rec_after_errors.recommended_difficulty == "FOUNDATIONAL"

    # Step B: 4 correct answers
    for _ in range(4):
        q = CANONICAL_CURRICULUM_BANK[topic.id][1]
        practice_svc._ACTIVE_QUESTIONS[q["id"]] = {
            "student_id": student.id,
            "topic_id": topic.id,
            "difficulty": q["difficulty"],
            "correct_answer": q["correct_answer"],
            "explanation": q["explanation"],
            "source_document": q["source_document"],
            "source_page": q["source_page"],
        }
        sub = PracticeSubmissionRequest(
            student_id=student.id,
            topic_id=topic.id,
            question_id=q["id"],
            selected_answer=q["correct_answer"],
            response_time_ms=5000,
        )
        practice_svc.submit_practice_answer(db_session, sub)

    prof_after_correct = KnowledgeModelService.calculate_topic_profile(db_session, student.id, topic)
    assert prof_after_correct.mastery_level == MasteryLevel.DEVELOPING
    assert prof_after_correct.trend == PerformanceTrend.IMPROVING

    rec_upgraded = practice_svc.recommend_next_practice(db_session, student.id, topic.id)
    assert rec_upgraded.recommended_difficulty == "GUIDED"
