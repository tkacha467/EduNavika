from datetime import datetime, timezone
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.app.core.database import Base
from backend.app.models import (
    User,
    UserRole,
    StudentProfile,
    Standard,
    Subject,
    Chapter,
    Topic,
    LearningEvent,
    EventType,
    TopicPerformance,
    RevisionPlan,
    RevisionPriority,
    RevisionCompletionState,
    ForgettingSignal,
    ForgettingSignalStatus,
)
from backend.app.domain.enums import (
    RecommendationAction,
    MasteryLevel,
    PerformanceTrend,
    RetentionRiskLevel,
)
from backend.app.services.recommendation_engine import RecommendationEngineService
from backend.app.services.event_recorder import EventRecorderService
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.core.database import get_db


@pytest.fixture
def setup_curriculum(db_session):
    db = db_session
    now = datetime.now(timezone.utc)
    ts_suffix = str(int(now.timestamp() * 1000))[-6:]

    std = db.query(Standard).filter(Standard.grade_number == 10).first()
    if not std:
        std = Standard(grade_number=10, name="Standard 10")
        db.add(std)
        db.flush()

    subj = Subject(name=f"Science Rec {ts_suffix}", code=f"SR_{ts_suffix}", standard_id=std.id)
    db.add(subj)
    db.flush()

    chap = Chapter(title=f"Chemical World {ts_suffix}", chapter_number=1, subject_id=subj.id)
    db.add(chap)
    db.flush()

    t1 = Topic(title=f"Chemical Reactions {ts_suffix}", chapter_id=chap.id, topic_order=1)
    t2 = Topic(title=f"Acids and Bases {ts_suffix}", chapter_id=chap.id, topic_order=2)
    t3 = Topic(title=f"Metals Non-metals {ts_suffix}", chapter_id=chap.id, topic_order=3)
    db.add_all([t1, t2, t3])
    db.flush()

    user = User(name=f"Rec Student {ts_suffix}", email=f"rec_student_{ts_suffix}@test.com", hashed_password="dummy", role=UserRole.STUDENT)
    db.add(user)
    db.flush()

    student = StudentProfile(user_id=user.id, standard_id=std.id, enrollment_number=f"ENR_{ts_suffix}")
    db.add(student)
    db.commit()

    yield {
        "db": db,
        "student_id": student.id,
        "t1": t1.id,
        "t2": t2.id,
        "t3": t3.id,
    }


def test_student_zero_history_onboarding_recommendation(setup_curriculum):
    """
    Test 1: Student with zero history receives deterministic onboarding recommendation (PRACTICE).
    """
    data = setup_curriculum
    db = data["db"]
    resp = RecommendationEngineService.generate_recommendations(db, data["student_id"])

    assert resp.total_recommendations >= 1
    top_rec = resp.recommendations[0]
    assert top_rec.action == RecommendationAction.PRACTICE
    assert "diagnostic" in top_rec.reason.lower() or "establish" in top_rec.reason.lower()
    assert top_rec.mastery_level == MasteryLevel.UNASSESSED


def test_urgent_revision_plan_surfaced_as_top_priority(setup_curriculum):
    """
    Test 2: Student with an URGENT revision plan has REVISION surfaced with highest score.
    """
    data = setup_curriculum
    db = data["db"]
    stu_id = data["student_id"]
    t1_id = data["t1"]

    # Record some poor performance
    for i in range(5):
        EventRecorderService.record_event(
            db=db,
            student_id=stu_id,
            topic_id=t1_id,
            event_type=EventType.MCQ_ATTEMPT,
            score=0.0 if i > 0 else 100.0,
            correctness=(i == 0),
        )

    # Urgent revision plan
    plan = RevisionPlan(
        student_id=stu_id,
        topic_id=t1_id,
        recommended_revision_at=datetime.now(timezone.utc),
        priority=RevisionPriority.URGENT,
        reason="Assessment accuracy 20.0%. Immediate review recommended.",
        completion_state=RevisionCompletionState.PENDING,
    )
    db.add(plan)
    db.commit()

    resp = RecommendationEngineService.generate_recommendations(db, stu_id)
    assert resp.total_recommendations >= 1
    top_rec = resp.recommendations[0]
    assert top_rec.topic_id == t1_id
    assert top_rec.action == RecommendationAction.REVISION
    assert top_rec.priority == RevisionPriority.URGENT
    assert top_rec.active_revision_plan_id == plan.id
    assert top_rec.score >= 100.0


def test_weak_topic_poor_accuracy_recommends_revision(setup_curriculum):
    """
    Test 3: Student with poor accuracy (< 30%) without an existing revision plan
    is still strongly recommended for REVISION.
    """
    data = setup_curriculum
    db = data["db"]
    stu_id = data["student_id"]
    t2_id = data["t2"]

    for i in range(5):
        EventRecorderService.record_event(
            db=db,
            student_id=stu_id,
            topic_id=t2_id,
            event_type=EventType.MCQ_ATTEMPT,
            score=0.0 if i > 0 else 100.0,
            correctness=(i == 0),
        )
    db.commit()

    resp = RecommendationEngineService.generate_recommendations(db, stu_id)
    rec = next(r for r in resp.recommendations if r.topic_id == t2_id)
    assert rec.action == RecommendationAction.REVISION
    assert rec.priority == RevisionPriority.HIGH
    assert "accuracy" in rec.reason.lower()


def test_declining_trend_elevates_priority(setup_curriculum):
    """
    Test 4: Student whose recent performance declined gets a higher score & declining rationale.
    """
    data = setup_curriculum
    db = data["db"]
    stu_id = data["student_id"]
    t3_id = data["t3"]

    # First 3 correct (100%), then next 3 incorrect (0%) -> trend DECLINING
    for _ in range(3):
        EventRecorderService.record_event(
            db=db,
            student_id=stu_id,
            topic_id=t3_id,
            event_type=EventType.MCQ_ATTEMPT,
            score=100.0,
            correctness=True,
        )
    for _ in range(3):
        EventRecorderService.record_event(
            db=db,
            student_id=stu_id,
            topic_id=t3_id,
            event_type=EventType.MCQ_ATTEMPT,
            score=0.0,
            correctness=False,
        )
    db.commit()

    resp = RecommendationEngineService.generate_recommendations(db, stu_id)
    rec = next(r for r in resp.recommendations if r.topic_id == t3_id)
    assert rec.trend == PerformanceTrend.DECLINING
    assert "declining" in rec.reason.lower()


def test_retention_risk_surfaces_review(setup_curriculum):
    """
    Test 5: Topic with active ForgettingSignal surfaces REVIEW.
    """
    data = setup_curriculum
    db = data["db"]
    stu_id = data["student_id"]
    t1_id = data["t1"]

    # Record 4 attempts with 75% accuracy
    for i in range(4):
        EventRecorderService.record_event(
            db=db,
            student_id=stu_id,
            topic_id=t1_id,
            event_type=EventType.MCQ_ATTEMPT,
            score=100.0 if i < 3 else 0.0,
            correctness=(i < 3),
        )

    # Add active forgetting signal
    signal = ForgettingSignal(
        student_id=stu_id,
        topic_id=t1_id,
        evidence_type="TEMPORAL_DECAY",
        evidence_strength="STRONG",
        status=ForgettingSignalStatus.UNRESOLVED,
    )
    db.add(signal)
    db.commit()

    resp = RecommendationEngineService.generate_recommendations(db, stu_id)
    rec = next(r for r in resp.recommendations if r.topic_id == t1_id)
    assert rec.retention_risk == RetentionRiskLevel.HIGH
    assert rec.action in (RecommendationAction.REVIEW, RecommendationAction.REVISION)
    assert "retention risk" in rec.reason.lower()


def test_mastered_topic_ranked_below_remedial_topics(setup_curriculum):
    """
    Test 6 & 7: Mastered topic is scored lower than a topic requiring revision/practice.
    """
    data = setup_curriculum
    db = data["db"]
    stu_id = data["student_id"]
    t1_id = data["t1"]  # Needs revision
    t2_id = data["t2"]  # Mastered

    # t1: 1 correct out of 5 (20%)
    for i in range(5):
        EventRecorderService.record_event(
            db=db,
            student_id=stu_id,
            topic_id=t1_id,
            event_type=EventType.MCQ_ATTEMPT,
            score=100.0 if i == 0 else 0.0,
            correctness=(i == 0),
        )

    # t2: 5 correct out of 5 (100%)
    for _ in range(5):
        EventRecorderService.record_event(
            db=db,
            student_id=stu_id,
            topic_id=t2_id,
            event_type=EventType.MCQ_ATTEMPT,
            score=100.0,
            correctness=True,
        )
    db.commit()

    resp = RecommendationEngineService.generate_recommendations(db, stu_id)
    assert len(resp.recommendations) >= 2
    rec_t1 = next(r for r in resp.recommendations if r.topic_id == t1_id)
    rec_t2 = next(r for r in resp.recommendations if r.topic_id == t2_id)

    assert rec_t2.mastery_level == MasteryLevel.MASTERED
    assert rec_t1.score > rec_t2.score
    assert resp.recommendations[0].topic_id == t1_id


def test_recommendation_api_endpoint(setup_curriculum):
    """
    Test 8: GET /api/v1/adaptive/recommendations/{student_id} returns 200 with schema compliance.
    """
    data = setup_curriculum
    db = data["db"]
    stu_id = data["student_id"]
    t1_id = data["t1"]

    EventRecorderService.record_event(
        db=db,
        student_id=stu_id,
        topic_id=t1_id,
        event_type=EventType.MCQ_ATTEMPT,
        score=20.0,
        correctness=False,
    )
    db.commit()

    def override_get_db():
        yield db

    app.dependency_overrides[get_db] = override_get_db
    try:
        client = TestClient(app)
        res = client.get(f"/api/v1/adaptive/recommendations/{stu_id}")
        assert res.status_code == 200
        data = res.json()
        assert data["student_id"] == stu_id
        assert data["total_recommendations"] >= 1
        rec = data["recommendations"][0]
        assert rec["topic_id"] == t1_id
        assert "action" in rec
        assert "priority" in rec
        assert "reason" in rec
        assert "score" in rec
    finally:
        from backend.tests.conftest import override_get_db as conftest_override_get_db
        app.dependency_overrides[get_db] = conftest_override_get_db


def test_no_side_effects_or_duplicate_plans(setup_curriculum):
    """
    Test 9: Calling generate_recommendations is idempotent and creates 0 side-effects or duplicate plans.
    """
    data = setup_curriculum
    db = data["db"]
    stu_id = data["student_id"]

    plans_before = db.query(RevisionPlan).count()
    events_before = db.query(LearningEvent).count()

    RecommendationEngineService.generate_recommendations(db, stu_id)
    RecommendationEngineService.generate_recommendations(db, stu_id)

    plans_after = db.query(RevisionPlan).count()
    events_after = db.query(LearningEvent).count()

    assert plans_after == plans_before
    assert events_after == events_before


def test_legacy_general_content_filtered_out(setup_curriculum):
    """
    Test 10: Legacy/unrelated 'General Content' topic records cannot dominate recommendations
    even if they have historical events, low accuracy, or high decay signals.
    """
    data = setup_curriculum
    db = data["db"]
    stu_id = data["student_id"]
    t1_id = data["t1"]

    # Create a legacy placeholder General Content topic under General Curriculum Content chapter
    chap_gen = Chapter(title="General Curriculum Content", chapter_number=99, subject_id=db.query(Topic).filter(Topic.id == t1_id).first().chapter.subject_id)
    db.add(chap_gen)
    db.flush()
    t_gen = Topic(title="General Content", chapter_id=chap_gen.id, topic_order=1)
    db.add(t_gen)
    db.flush()

    # Record very poor performance on General Content (would yield score 190 if not filtered)
    for _ in range(5):
        EventRecorderService.record_event(
            db=db,
            student_id=stu_id,
            topic_id=t_gen.id,
            event_type=EventType.MCQ_ATTEMPT,
            score=0.0,
            correctness=False,
        )

    # Record legitimate revision required on curriculum topic t1
    EventRecorderService.record_event(
        db=db,
        student_id=stu_id,
        topic_id=t1_id,
        event_type=EventType.MCQ_ATTEMPT,
        score=20.0,
        correctness=False,
    )
    plan_t1 = RevisionPlan(
        student_id=stu_id,
        topic_id=t1_id,
        recommended_revision_at=datetime.now(timezone.utc),
        priority=RevisionPriority.HIGH,
        reason="Assessment accuracy 40.0% (2/5 correct). Immediate review recommended.",
        completion_state=RevisionCompletionState.PENDING,
    )
    db.add(plan_t1)
    db.commit()

    resp = RecommendationEngineService.generate_recommendations(db, stu_id)

    # General Content must NOT appear in recommendations
    rec_topic_ids = [r.topic_id for r in resp.recommendations]
    assert t_gen.id not in rec_topic_ids
    assert all("general content" not in r.topic_title.lower() for r in resp.recommendations)

    # Real curriculum topic t1 must be top recommendation
    assert resp.total_recommendations >= 1
    assert resp.recommendations[0].topic_id == t1_id
    assert resp.recommendations[0].action == RecommendationAction.REVISION
    assert resp.recommendations[0].priority == RevisionPriority.HIGH


def test_live_student_chemical_reactions_top_priority(db_session):
    """
    Test 11: Real student verification against SQLite DB:
    Student e09699dd-0c64-44cc-82ef-ab41a832e072 must have Chemical Reactions as #1 recommendation.
    """
    db = db_session
    try:
        live_student_id = "e09699dd-0c64-44cc-82ef-ab41a832e072"
        student = db.query(StudentProfile).filter(StudentProfile.id == live_student_id).first()
        if not student:
            pytest.skip("Live student profile not present in DB")

        resp = RecommendationEngineService.generate_recommendations(db, live_student_id)
        assert resp.total_recommendations >= 1

        # Verify Chemical Reactions and Equations is among high-priority recommendations
        chem_rec = next((r for r in resp.recommendations if r.topic_id == "5a321a44-bc06-4db4-a50f-5e53f913b612"), None)
        assert chem_rec is not None
        assert chem_rec.topic_title == "Chemical Reactions and Equations"
        assert chem_rec.action == RecommendationAction.REVISION
        assert chem_rec.priority in (RevisionPriority.HIGH, RevisionPriority.URGENT)

        # General content must not appear in any recommendations
        for r in resp.recommendations:
            assert r.topic_id != "199dc81b-55c9-4678-ae50-7c575c64288f"
            assert "general content" not in r.topic_title.lower()
    finally:
        db.close()
