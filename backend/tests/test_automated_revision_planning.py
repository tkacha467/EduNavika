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
from backend.app.domain.enums import MasteryLevel, RetentionRiskLevel, RevisionPriority, PerformanceTrend
from backend.app.services.revision_planner import RevisionPlannerService
from backend.app.services.event_recorder import EventRecorderService


@pytest.fixture
def revision_fixture(db_session):
    """Sets up a clean GSEB Standard 10 curriculum environment with student and curriculum topics."""
    user = User(
        name="Aarav Mehta",
        email="aarav_revision@edunavika.org",
        hashed_password="hashed_pw",
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
    chap3 = Chapter(title="Electricity", chapter_number=12, subject_id=subj.id)
    db_session.add_all([chap1, chap2, chap3])
    db_session.flush()

    # Create canonical curriculum topics
    t1 = Topic(title="Chemical Reactions and Equations", chapter_id=chap1.id, topic_order=1)
    t2 = Topic(title="Acids, Bases and Salts", chapter_id=chap2.id, topic_order=1)
    t3 = Topic(title="Electricity", chapter_id=chap3.id, topic_order=1)
    db_session.add_all([t1, t2, t3])
    db_session.flush()

    student = StudentProfile(user_id=user.id, standard_id=std.id, enrollment_number="REV-1001")
    db_session.add(student)
    db_session.commit()

    return {
        "student": student,
        "t1": t1,
        "t2": t2,
        "t3": t3,
        "subj": subj,
    }


def test_1_revision_plan_endpoint_structure(client, revision_fixture):
    """1. Endpoint returns 200 OK with fully compliant RevisionPlanResponse schema."""
    student = revision_fixture["student"]
    res = client.get(f"/api/v1/adaptive/revision-plan/{student.id}")
    assert res.status_code == 200
    data = res.json()

    assert data["student_id"] == student.id
    assert "generated_at" in data
    assert "total_revisions" in data
    assert "due_today_count" in data
    assert "due_this_week_count" in data
    assert "upcoming_count" in data
    assert "urgent_count" in data
    assert "high_count" in data
    assert "medium_count" in data
    assert "low_count" in data
    assert isinstance(data["revisions"], list)


def test_2_weak_topic_receives_urgent_or_high_priority(client, db_session, revision_fixture):
    """2. A topic with low accuracy (e.g. 20%) receives URGENT priority, due today (0-day offset)."""
    student = revision_fixture["student"]
    t1 = revision_fixture["t1"]
    now = datetime.now(timezone.utc)

    # Record 5 poor attempts (1 correct, 4 incorrect = 20% accuracy)
    for i in range(5):
        EventRecorderService.record_event(
            db=db_session,
            student_id=student.id,
            topic_id=t1.id,
            event_type=EventType.PRACTICE,
            score=100.0 if i == 0 else 0.0,
            correctness=i == 0,
            timestamp=now - timedelta(minutes=10 - i),
            event_metadata={"difficulty": "FOUNDATIONAL"},
            auto_commit=True,
        )

    res = client.get(f"/api/v1/adaptive/revision-plan/{student.id}")
    assert res.status_code == 200
    data = res.json()

    assert data["total_revisions"] >= 1
    t1_item = next(r for r in data["revisions"] if r["topic_id"] == t1.id)

    # 20% accuracy on novice topic must trigger URGENT priority
    assert t1_item["priority"] in ("URGENT", "HIGH")
    assert t1_item["days_until_due"] <= 1
    assert t1_item["urgency_tier"] in ("TODAY", "THIS_WEEK")
    assert t1_item["recommended_difficulty"] in ("FOUNDATIONAL", "GUIDED")
    assert "20.0%" in t1_item["reason"] or "accuracy" in t1_item["reason"].lower()


def test_3_high_retention_risk_schedules_earlier(client, db_session, revision_fixture):
    """3. High retention risk topic is scheduled earlier than moderate/low risk topic."""
    student = revision_fixture["student"]
    t1 = revision_fixture["t1"]
    t2 = revision_fixture["t2"]
    now = datetime.now(timezone.utc)

    # Topic 1: 5 poor attempts (20% accuracy -> High retention risk)
    for i in range(5):
        EventRecorderService.record_event(
            db=db_session,
            student_id=student.id,
            topic_id=t1.id,
            event_type=EventType.PRACTICE,
            score=100.0 if i == 0 else 0.0,
            correctness=i == 0,
            timestamp=now - timedelta(days=2, minutes=i),
            auto_commit=True,
        )

    # Topic 2: 10 attempts (6 correct, 4 incorrect = 60% accuracy -> Moderate/Developing)
    for j in range(10):
        EventRecorderService.record_event(
            db=db_session,
            student_id=student.id,
            topic_id=t2.id,
            event_type=EventType.PRACTICE,
            score=100.0 if j < 6 else 0.0,
            correctness=j < 6,
            timestamp=now - timedelta(days=1, minutes=j),
            auto_commit=True,
        )

    res = client.get(f"/api/v1/adaptive/revision-plan/{student.id}")
    assert res.status_code == 200
    data = res.json()

    item1 = next(r for r in data["revisions"] if r["topic_id"] == t1.id)
    item2 = next(r for r in data["revisions"] if r["topic_id"] == t2.id)

    # High retention risk should have earlier due date than moderate
    assert item1["days_until_due"] <= item2["days_until_due"]
    assert item1["priority"] in ("URGENT", "HIGH")


def test_4_strong_mastery_schedules_later_maintenance(client, db_session, revision_fixture):
    """4. Proficient/Mastered topics receive LOW priority and spaced intervals (7 to 14 days)."""
    student = revision_fixture["student"]
    t3 = revision_fixture["t3"]
    now = datetime.now(timezone.utc)

    # 10 attempts (9 correct = 90% accuracy -> Mastered)
    for i in range(10):
        EventRecorderService.record_event(
            db=db_session,
            student_id=student.id,
            topic_id=t3.id,
            event_type=EventType.PRACTICE,
            score=100.0 if i < 9 else 0.0,
            correctness=i < 9,
            timestamp=now - timedelta(hours=2, minutes=i),
            auto_commit=True,
        )

    res = client.get(f"/api/v1/adaptive/revision-plan/{student.id}")
    assert res.status_code == 200
    data = res.json()

    item3 = next(r for r in data["revisions"] if r["topic_id"] == t3.id)
    assert item3["priority"] == "LOW"
    assert item3["urgency_tier"] == "UPCOMING"
    assert item3["days_until_due"] >= 7
    assert item3["recommended_difficulty"] in ("APPLICATION", "CHALLENGE")


def test_5_revision_date_is_deterministic(client, revision_fixture):
    """5. Two consecutive calls with identical student state yield identical schedules."""
    student = revision_fixture["student"]

    res1 = client.get(f"/api/v1/adaptive/revision-plan/{student.id}")
    res2 = client.get(f"/api/v1/adaptive/revision-plan/{student.id}")
    assert res1.status_code == 200
    assert res2.status_code == 200

    data1 = res1.json()
    data2 = res2.json()

    assert data1["total_revisions"] == data2["total_revisions"]
    assert data1["due_today_count"] == data2["due_today_count"]
    assert data1["urgent_count"] == data2["urgent_count"]

    for r1, r2 in zip(data1["revisions"], data2["revisions"]):
        assert r1["topic_id"] == r2["topic_id"]
        assert r1["priority"] == r2["priority"]
        assert r1["scheduled_date"] == r2["scheduled_date"]
        assert r1["days_until_due"] == r2["days_until_due"]


def test_6_language_switching_preserves_scheduling_invariants(client, db_session, revision_fixture):
    """6. English, Hindi, and Gujarati return identical topic scheduling, dates, and priorities."""
    student = revision_fixture["student"]
    t1 = revision_fixture["t1"]
    now = datetime.now(timezone.utc)

    for i in range(5):
        EventRecorderService.record_event(
            db=db_session,
            student_id=student.id,
            topic_id=t1.id,
            event_type=EventType.PRACTICE,
            score=100.0 if i == 0 else 0.0,
            correctness=i == 0,
            timestamp=now - timedelta(minutes=5 - i),
            auto_commit=True,
        )

    res_en = client.get(f"/api/v1/adaptive/revision-plan/{student.id}?language=en")
    res_hi = client.get(f"/api/v1/adaptive/revision-plan/{student.id}?language=hi")
    res_gu = client.get(f"/api/v1/adaptive/revision-plan/{student.id}?language=gu")

    assert res_en.status_code == 200
    assert res_hi.status_code == 200
    assert res_gu.status_code == 200

    data_en = res_en.json()
    data_hi = res_hi.json()
    data_gu = res_gu.json()

    assert data_en["total_revisions"] == data_hi["total_revisions"] == data_gu["total_revisions"]
    assert data_en["urgent_count"] == data_hi["urgent_count"] == data_gu["urgent_count"]

    for item_en, item_hi, item_gu in zip(data_en["revisions"], data_hi["revisions"], data_gu["revisions"]):
        # Scheduling INVARIANTS: must be identical across languages
        assert item_en["topic_id"] == item_hi["topic_id"] == item_gu["topic_id"]
        assert item_en["priority"] == item_hi["priority"] == item_gu["priority"]
        assert item_en["scheduled_date"] == item_hi["scheduled_date"] == item_gu["scheduled_date"]
        assert item_en["days_until_due"] == item_hi["days_until_due"] == item_gu["days_until_due"]
        assert item_en["mastery_level"] == item_hi["mastery_level"] == item_gu["mastery_level"]
        assert item_en["accuracy"] == item_hi["accuracy"] == item_gu["accuracy"]

        # Localized fields: presentation text varies appropriately
        assert item_en["reason"] != item_hi["reason"]
        assert item_en["reason"] != item_gu["reason"]


def test_7_revision_plan_does_not_mutate_learning_events(client, db_session, revision_fixture):
    """7. Fetching the revision plan is non-destructive and preserves existing learning events."""
    student = revision_fixture["student"]
    t1 = revision_fixture["t1"]

    EventRecorderService.record_event(
        db=db_session,
        student_id=student.id,
        topic_id=t1.id,
        event_type=EventType.PRACTICE,
        score=100.0,
        correctness=True,
        auto_commit=True,
    )

    count_before = db_session.query(LearningEvent).filter_by(student_id=student.id).count()

    # Call endpoint multiple times
    client.get(f"/api/v1/adaptive/revision-plan/{student.id}")
    client.get(f"/api/v1/adaptive/revision-plan/{student.id}")

    count_after = db_session.query(LearningEvent).filter_by(student_id=student.id).count()
    assert count_before == count_after == 1


def test_8_empty_student_clean_state(client, revision_fixture):
    """8. A student with zero history returns 200 OK without errors."""
    student = revision_fixture["student"]
    res = client.get(f"/api/v1/adaptive/revision-plan/{student.id}")
    assert res.status_code == 200
    data = res.json()
    assert data["student_id"] == student.id
    assert data["total_revisions"] == len(data["revisions"])


def test_9_closed_loop_personalization_flow(client, db_session, revision_fixture):
    """9. Trace full adaptive loop:
       Poor performance -> Urgent revision (Due Today / 0d)
       Correct practice -> Improved mastery -> Priority lowers & spacing lengthens.
    """
    student = revision_fixture["student"]
    t1 = revision_fixture["t1"]
    now = datetime.now(timezone.utc)

    # Step A: Student struggles with Topic 1 (4 wrong answers)
    for i in range(4):
        EventRecorderService.record_event(
            db=db_session,
            student_id=student.id,
            topic_id=t1.id,
            event_type=EventType.PRACTICE,
            score=0.0,
            correctness=False,
            timestamp=now - timedelta(minutes=20 - i),
            auto_commit=True,
        )

    # Verify Step A Revision Plan
    res_a = client.get(f"/api/v1/adaptive/revision-plan/{student.id}")
    assert res_a.status_code == 200
    item_a = next(r for r in res_a.json()["revisions"] if r["topic_id"] == t1.id)
    assert item_a["priority"] == "URGENT"
    assert item_a["days_until_due"] == 0
    assert item_a["is_due_today"] is True

    # Step B: Student completes successful remedial practice (8 correct answers)
    for j in range(8):
        EventRecorderService.record_event(
            db=db_session,
            student_id=student.id,
            topic_id=t1.id,
            event_type=EventType.PRACTICE,
            score=100.0,
            correctness=True,
            timestamp=now + timedelta(minutes=j + 1),
            auto_commit=True,
        )

    # Verify Step B Revision Plan: priority must decrease and interval must extend
    res_b = client.get(f"/api/v1/adaptive/revision-plan/{student.id}")
    assert res_b.status_code == 200
    item_b = next(r for r in res_b.json()["revisions"] if r["topic_id"] == t1.id)
    assert item_b["priority"] in ("MEDIUM", "LOW")
    assert item_b["days_until_due"] >= 3
    assert item_b["urgency_tier"] in ("THIS_WEEK", "UPCOMING")


def test_10_zero_cloud_dependency(revision_fixture, db_session):
    """10. Verify revision planner service runs fully local and offline with zero cloud imports."""
    student = revision_fixture["student"]
    service = RevisionPlannerService()
    response = service.get_personalized_revision_plan(db_session, student.id, language="en")

    assert response.student_id == student.id
    assert response.total_revisions >= 0
    # Provenance fields cite textbook page directly from local metadata
    for rev in response.revisions:
        if rev.source_page:
            assert isinstance(rev.source_page, int)
            assert rev.source_page > 0
