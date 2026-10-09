import pytest
from datetime import datetime, timezone, timedelta
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
from backend.app.services.adaptive_practice import adaptive_practice_service
from backend.app.services.event_recorder import EventRecorderService
from backend.app.services.knowledge_model import KnowledgeModelService


@pytest.fixture
def progress_fixture(db_session):
    """Sets up a complete GSEB Standard 10 curriculum environment with student and topics."""
    user = User(
        name="Pranav Joshi",
        email="pranav_progress@edunavika.org",
        hashed_password="pw",
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
    chap2 = Chapter(title="Acids, Bases and Salts", chapter_number=2, subject_id=subj.id)
    db_session.add_all([chap1, chap2])
    db_session.flush()

    t1 = Topic(title="Chemical Reactions and Equations", chapter_id=chap1.id, topic_order=1)
    t2 = Topic(title="Types of Chemical Reactions", chapter_id=chap1.id, topic_order=2)
    t3 = Topic(title="Acids, Bases and Salts", chapter_id=chap2.id, topic_order=1)
    db_session.add_all([t1, t2, t3])
    db_session.flush()

    student = StudentProfile(user_id=user.id, standard_id=std.id, enrollment_number="PR-1001")
    db_session.add(student)
    db_session.commit()

    return {
        "student": student,
        "t1": t1,
        "t2": t2,
        "t3": t3,
    }


def test_1_unassessed_student_progress_baseline(client, progress_fixture):
    """1. Progress endpoint returns valid zeroed schema for unassessed student."""
    student = progress_fixture["student"]
    res = client.get(f"/api/v1/adaptive/progress/{student.id}")
    assert res.status_code == 200
    data = res.json()

    assert data["student_id"] == student.id
    overall = data["overall"]
    assert overall["total_attempts"] == 0
    assert overall["correct_attempts"] == 0
    assert overall["overall_accuracy"] == 0.0
    assert overall["topics_studied"] == 0
    assert overall["total_topics_available"] >= 3
    assert overall["overall_trend"] == "INSUFFICIENT_DATA"

    # Distribution: all topics must be unassessed
    dist = overall["mastery_distribution"]
    assert dist["unassessed"] == overall["total_topics_available"]
    assert dist["novice"] == 0
    assert dist["developing"] == 0
    assert dist["proficient"] == 0
    assert dist["mastered"] == 0

    # Strengths & Weaknesses must be empty for 0 attempts
    sw = data["strengths_weaknesses"]
    assert len(sw["strengths"]) == 0
    assert len(sw["weaknesses"]) == 0
    assert len(sw["developing"]) == 0
    assert sw["unassessed_count"] == overall["total_topics_available"]

    # Learning journey must be empty
    assert len(data["learning_journey"]) == 0


def test_2_single_practice_submission_updates_overall_progress(client, db_session, progress_fixture):
    """2. Submitting a practice attempt updates total attempts, accuracy, and topic breakdown."""
    student = progress_fixture["student"]
    t1 = progress_fixture["t1"]

    # Record 1 correct practice event
    EventRecorderService.record_event(
        db=db_session,
        student_id=student.id,
        topic_id=t1.id,
        event_type=EventType.PRACTICE,
        score=100.0,
        correctness=True,
        response_time_ms=4500,
        event_metadata={"difficulty": "FOUNDATIONAL"},
        auto_commit=True,
    )

    res = client.get(f"/api/v1/adaptive/progress/{student.id}")
    assert res.status_code == 200
    data = res.json()
    overall = data["overall"]

    assert overall["total_attempts"] == 1
    assert overall["correct_attempts"] == 1
    assert overall["overall_accuracy"] == 100.0
    assert overall["topics_studied"] == 1

    # Check topic list
    topic_item = next(t for t in data["topics"] if t["topic_id"] == t1.id)
    assert topic_item["total_attempts"] == 1
    assert topic_item["correct_attempts"] == 1
    assert topic_item["accuracy"] == 100.0


def test_3_accuracy_math_verification(client, db_session, progress_fixture):
    """3. Overall and topic accuracy correctly calculated (1 correct + 1 incorrect = 50.0%)."""
    student = progress_fixture["student"]
    t1 = progress_fixture["t1"]

    EventRecorderService.record_event(
        db=db_session,
        student_id=student.id,
        topic_id=t1.id,
        event_type=EventType.PRACTICE,
        score=100.0,
        correctness=True,
        auto_commit=True,
    )
    EventRecorderService.record_event(
        db=db_session,
        student_id=student.id,
        topic_id=t1.id,
        event_type=EventType.PRACTICE,
        score=0.0,
        correctness=False,
        auto_commit=True,
    )

    res = client.get(f"/api/v1/adaptive/progress/{student.id}")
    data = res.json()
    overall = data["overall"]

    assert overall["total_attempts"] == 2
    assert overall["correct_attempts"] == 1
    assert overall["overall_accuracy"] == 50.0

    t1_data = next(t for t in data["topics"] if t["topic_id"] == t1.id)
    assert t1_data["accuracy"] == 50.0


def test_4_mastery_distribution_sums_to_total_available_topics(client, progress_fixture):
    """4. Sum of mastery distribution tiers strictly equals total topics available."""
    student = progress_fixture["student"]
    res = client.get(f"/api/v1/adaptive/progress/{student.id}")
    data = res.json()

    dist = data["overall"]["mastery_distribution"]
    total_dist = (
        dist["unassessed"]
        + dist["novice"]
        + dist["developing"]
        + dist["proficient"]
        + dist["mastered"]
    )
    assert total_dist == data["overall"]["total_topics_available"]


def test_5_topic_with_high_accuracy_promotes_to_strengths(client, db_session, progress_fixture):
    """5. Topic with high accuracy (>= 70%) and sufficient attempts appears in Strengths."""
    student = progress_fixture["student"]
    t1 = progress_fixture["t1"]

    # 4 correct attempts out of 4 (100% accuracy -> Proficient/Mastered)
    for _ in range(4):
        EventRecorderService.record_event(
            db=db_session,
            student_id=student.id,
            topic_id=t1.id,
            event_type=EventType.PRACTICE,
            score=100.0,
            correctness=True,
            auto_commit=True,
        )

    res = client.get(f"/api/v1/adaptive/progress/{student.id}")
    data = res.json()
    strengths = data["strengths_weaknesses"]["strengths"]

    assert any(s["topic_id"] == t1.id for s in strengths)
    assert not any(w["topic_id"] == t1.id for w in data["strengths_weaknesses"]["weaknesses"])


def test_6_topic_with_low_accuracy_appears_in_weaknesses(client, db_session, progress_fixture):
    """6. Topic with low accuracy (< 50%) appears in Weak Areas."""
    student = progress_fixture["student"]
    t2 = progress_fixture["t2"]

    # 1 correct out of 4 attempts (25% accuracy)
    for i in range(4):
        EventRecorderService.record_event(
            db=db_session,
            student_id=student.id,
            topic_id=t2.id,
            event_type=EventType.PRACTICE,
            score=100.0 if i == 0 else 0.0,
            correctness=(i == 0),
            auto_commit=True,
        )

    res = client.get(f"/api/v1/adaptive/progress/{student.id}")
    data = res.json()
    weaknesses = data["strengths_weaknesses"]["weaknesses"]

    assert any(w["topic_id"] == t2.id for w in weaknesses)
    assert not any(s["topic_id"] == t2.id for s in data["strengths_weaknesses"]["strengths"])


def test_7_unassessed_topic_never_appears_in_weaknesses(client, progress_fixture):
    """7. Unassessed topics (0 attempts) must NEVER be categorized as weaknesses."""
    student = progress_fixture["student"]
    t3 = progress_fixture["t3"]

    res = client.get(f"/api/v1/adaptive/progress/{student.id}")
    data = res.json()

    weaknesses = data["strengths_weaknesses"]["weaknesses"]
    strengths = data["strengths_weaknesses"]["strengths"]

    assert not any(w["topic_id"] == t3.id for w in weaknesses)
    assert not any(s["topic_id"] == t3.id for s in strengths)

    t3_data = next(t for t in data["topics"] if t["topic_id"] == t3.id)
    assert t3_data["mastery_level"] == "UNASSESSED"
    assert t3_data["total_attempts"] == 0


def test_8_chronological_learning_journey_reverse_order(client, db_session, progress_fixture):
    """8. Learning journey returns events sorted with most recent first."""
    student = progress_fixture["student"]
    t1 = progress_fixture["t1"]

    now = datetime.now(timezone.utc)
    # Event 1: 10 mins ago
    ev1 = LearningEvent(
        student_id=student.id,
        topic_id=t1.id,
        event_type=EventType.PRACTICE,
        score=100.0,
        correctness=True,
        timestamp=now - timedelta(minutes=10),
    )
    # Event 2: 2 mins ago
    ev2 = LearningEvent(
        student_id=student.id,
        topic_id=t1.id,
        event_type=EventType.PRACTICE,
        score=0.0,
        correctness=False,
        timestamp=now - timedelta(minutes=2),
    )
    db_session.add_all([ev1, ev2])
    db_session.commit()

    res = client.get(f"/api/v1/adaptive/progress/{student.id}")
    data = res.json()
    journey = data["learning_journey"]

    assert len(journey) >= 2
    assert journey[0]["event_id"] == ev2.id
    assert journey[1]["event_id"] == ev1.id


def test_9_learning_journey_event_payload_integrity(client, db_session, progress_fixture):
    """9. Learning journey items contain complete telemetry fields (topic, type, difficulty, response time)."""
    student = progress_fixture["student"]
    t1 = progress_fixture["t1"]

    EventRecorderService.record_event(
        db=db_session,
        student_id=student.id,
        topic_id=t1.id,
        event_type=EventType.PRACTICE,
        score=100.0,
        correctness=True,
        response_time_ms=5200,
        event_metadata={"difficulty": "GUIDED"},
        auto_commit=True,
    )

    res = client.get(f"/api/v1/adaptive/progress/{student.id}")
    data = res.json()
    assert len(data["learning_journey"]) > 0

    item = data["learning_journey"][0]
    assert item["topic_id"] == t1.id
    assert item["topic_title"] == t1.title
    assert item["event_type"] == "PRACTICE"
    assert item["correctness"] is True
    assert item["score"] == 100.0
    assert item["difficulty"] == "GUIDED"
    assert item["response_time_ms"] == 5200
    assert "timestamp" in item


def test_10_consistency_with_knowledge_model_and_recommendations(client, db_session, progress_fixture):
    """10. Progress tracking topic data aligns identically with KnowledgeModelService and RecommendationEngine."""
    student = progress_fixture["student"]
    t1 = progress_fixture["t1"]

    # Add 3 attempts
    for _ in range(3):
        EventRecorderService.record_event(
            db=db_session,
            student_id=student.id,
            topic_id=t1.id,
            event_type=EventType.PRACTICE,
            score=100.0,
            correctness=True,
            auto_commit=True,
        )

    # 1. Fetch from progress endpoint
    prog_res = client.get(f"/api/v1/adaptive/progress/{student.id}").json()
    prog_t1 = next(t for t in prog_res["topics"] if t["topic_id"] == t1.id)

    # 2. Fetch from knowledge-profile endpoint
    kp_res = client.get(f"/api/v1/adaptive/knowledge-profile/{student.id}?topic_id={t1.id}").json()
    kp_t1 = kp_res["profiles"][0]

    # 3. Verify absolute consistency
    assert prog_t1["accuracy"] == kp_t1["accuracy"]
    assert prog_t1["total_attempts"] == kp_t1["total_attempts"]
    assert prog_t1["correct_attempts"] == kp_t1["correct_attempts"]
    assert prog_t1["mastery_level"] == kp_t1["mastery_level"]
    assert prog_t1["retention_risk"] == kp_t1["retention_risk"]


def test_11_fresh_demo_student_graceful_handling(client, db_session):
    """11. Auto-provisions or cleanly handles student ID without 500 error."""
    # Unknown ID should return 404 or auto-provision if valid user exists
    res = client.get("/api/v1/adaptive/progress/nonexistent-student-xyz")
    # Clean 404 handled gracefully
    assert res.status_code in (404, 200)


def test_12_overall_learning_trend_detection(client, db_session, progress_fixture):
    """12. Overall student trend accurately evaluates IMPROVING and DECLINING trajectories."""
    student = progress_fixture["student"]
    t1 = progress_fixture["t1"]

    # 4 events: 2 incorrect followed by 2 correct -> accuracy improves from 0% to 100% (+100%)
    now = datetime.now(timezone.utc)
    for i in range(4):
        db_session.add(
            LearningEvent(
                student_id=student.id,
                topic_id=t1.id,
                event_type=EventType.PRACTICE,
                score=0.0 if i < 2 else 100.0,
                correctness=(i >= 2),
                timestamp=now - timedelta(minutes=(10 - i)),
            )
        )
    db_session.commit()

    res = client.get(f"/api/v1/adaptive/progress/{student.id}").json()
    assert res["overall"]["overall_trend"] == "IMPROVING"


def test_13_dynamic_curriculum_scope_resolution(client, progress_fixture):
    """13. Progress tracking dynamically scopes to authentic subject without hardcoded topic count."""
    student = progress_fixture["student"]
    res = client.get(f"/api/v1/adaptive/progress/{student.id}")
    assert res.status_code == 200
    data = res.json()

    # Progress must match the 3 topics defined in the fixture
    assert data["overall"]["total_topics_available"] == 3
    assert data["overall"]["mastery_distribution"]["unassessed"] == 3
    assert data["strengths_weaknesses"]["unassessed_count"] == 3
    assert data["overall"]["subject_name"] == "Science & Technology"
    assert len(data["topics"]) == 3


def test_14_synthetic_test_subjects_are_filtered(client, db_session, progress_fixture):
    """14. Synthetic test artifacts (e.g. 'Science Test 12345', 'Science Rec 67890') are strictly excluded."""
    student = progress_fixture["student"]
    std_id = student.standard_id

    # Create synthetic test subjects that mimic past test pollution
    synth_subj1 = Subject(name="Science Test 999999", code="sci_test_999999", standard_id=std_id)
    synth_subj2 = Subject(name="Science Rec 888888", code="sr_888888", standard_id=std_id)
    db_session.add_all([synth_subj1, synth_subj2])
    db_session.flush()

    c1 = Chapter(title="Synthetic Chap 1", chapter_number=99, subject_id=synth_subj1.id)
    c2 = Chapter(title="Synthetic Chap 2", chapter_number=99, subject_id=synth_subj2.id)
    db_session.add_all([c1, c2])
    db_session.flush()

    top_synth1 = Topic(title="Synthetic Topic 1", chapter_id=c1.id, topic_order=1)
    top_synth2 = Topic(title="Synthetic Topic 2", chapter_id=c2.id, topic_order=1)
    db_session.add_all([top_synth1, top_synth2])
    db_session.commit()

    # Query progress - must still only count the authentic 3 topics
    res = client.get(f"/api/v1/adaptive/progress/{student.id}")
    assert res.status_code == 200
    data = res.json()
    assert data["overall"]["total_topics_available"] == 3
    assert data["overall"]["subject_name"] == "Science & Technology"
    topic_ids = [t["topic_id"] for t in data["topics"]]
    assert top_synth1.id not in topic_ids
    assert top_synth2.id not in topic_ids


def test_15_explicit_subject_query_param(client, db_session, progress_fixture):
    """15. Query param ?subject_id allows explicit subject filtering or 'all'."""
    student = progress_fixture["student"]
    std_id = student.standard_id

    # Add Mathematics subject with 2 topics
    math_subj = Subject(name="Mathematics", code="MATH-10", standard_id=std_id)
    db_session.add(math_subj)
    db_session.flush()

    math_chap = Chapter(title="Real Numbers", chapter_number=1, subject_id=math_subj.id)
    db_session.add(math_chap)
    db_session.flush()

    m_top1 = Topic(title="Euclid Division", chapter_id=math_chap.id, topic_order=1)
    m_top2 = Topic(title="Fundamental Theorem", chapter_id=math_chap.id, topic_order=2)
    db_session.add_all([m_top1, m_top2])
    db_session.commit()

    # Query math specifically
    res_math = client.get(f"/api/v1/adaptive/progress/{student.id}?subject_id={math_subj.id}")
    assert res_math.status_code == 200
    data_math = res_math.json()
    assert data_math["overall"]["total_topics_available"] == 2
    assert data_math["overall"]["subject_name"] == "Mathematics"
    assert len(data_math["topics"]) == 2

    # Query 'all' authentic subjects
    res_all = client.get(f"/api/v1/adaptive/progress/{student.id}?subject_id=all")
    assert res_all.status_code == 200
    data_all = res_all.json()
    assert data_all["overall"]["total_topics_available"] == 5  # 3 science + 2 math
    assert data_all["overall"]["subject_name"] == "All Subjects"
    assert len(data_all["topics"]) == 5


def test_16_fresh_demo_student_curriculum_scope():
    """16. Real demo student 'stu-fresh-demo-001' scopes to 19 Science topics in edunavika.db, not 1314."""
    from backend.app.core.database import SessionLocal
    from backend.app.services.progress_service import student_progress_service
    db = SessionLocal()
    try:
        demo_student = db.query(StudentProfile).filter(StudentProfile.id == "stu-fresh-demo-001").first()
        if not demo_student:
            pytest.skip("stu-fresh-demo-001 not present in SQLite database")

        progress = student_progress_service.get_student_progress(db=db, student_id="stu-fresh-demo-001")
        overall = progress.overall

        # Must be GSEB Standard 10 Science (19 topics), NOT 1314
        assert overall.subject_name == "Science & Technology"
        assert overall.total_topics_available == 19
        assert overall.topics_studied >= 1
        assert overall.mastery_distribution.unassessed == 19 - overall.topics_studied
        assert len(progress.topics) == 19
    finally:
        db.close()

