import pytest
from datetime import datetime, timedelta, timezone
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.core.database import SessionLocal
from backend.app.models import (
    User, UserRole, StudentProfile, Standard, Subject, Chapter, Topic,
    LearningEvent, EventType, TopicPerformance, ForgettingSignal, ForgettingSignalStatus
)
from backend.app.domain.enums import MasteryLevel, PerformanceTrend, RetentionRiskLevel
from backend.app.services.knowledge_model import KnowledgeModelService


@pytest.fixture
def test_setup():
    db = SessionLocal()
    # Unique timestamp for isolation
    now = datetime.now(timezone.utc)
    ts_suffix = str(int(now.timestamp() * 1000))[-6:]

    # 1. Create standard curriculum hierarchy
    std = db.query(Standard).filter(Standard.grade_number == 10).first()
    if not std:
        std = Standard(grade_number=10, name="Standard 10")
        db.add(std)
        db.flush()

    subj = Subject(name=f"Science Test {ts_suffix}", code=f"SCI_{ts_suffix}", standard_id=std.id)
    db.add(subj)
    db.flush()

    chap = Chapter(title=f"Chemical Reactions {ts_suffix}", chapter_number=1, subject_id=subj.id)
    db.add(chap)
    db.flush()

    topic_chem = Topic(title=f"Chemical Reactions & Equations {ts_suffix}", chapter_id=chap.id, topic_order=1)
    db.add(topic_chem)
    db.flush()

    # 2. Student user & profile
    user = User(
        name="Test Student",
        email=f"test_student_{ts_suffix}@edunavika.com",
        hashed_password="hashed_pw",
        role=UserRole.STUDENT,
    )
    db.add(user)
    db.flush()

    student = StudentProfile(user_id=user.id, standard_id=std.id, enrollment_number=f"EN_{ts_suffix}")
    db.add(student)
    db.commit()

    yield {
        "db": db,
        "student": student,
        "topic": topic_chem,
        "now": now,
    }

    db.close()


def test_knowledge_profile_student_with_no_history(test_setup):
    """Test 1: Student with zero activity should have UNASSESSED mastery and INSUFFICIENT_DATA trend."""
    db = test_setup["db"]
    student = test_setup["student"]
    topic = test_setup["topic"]

    profile = KnowledgeModelService.calculate_topic_profile(db, student.id, topic)
    assert profile.topic_id == topic.id
    assert profile.total_attempts == 0
    assert profile.correct_attempts == 0
    assert profile.accuracy == 0.0
    assert profile.mastery_level == MasteryLevel.UNASSESSED
    assert profile.trend == PerformanceTrend.INSUFFICIENT_DATA
    assert profile.retention_risk == RetentionRiskLevel.UNASSESSED
    assert profile.recent_accuracy is None


def test_knowledge_profile_poor_performance(test_setup):
    """Test 2: Student with 5 attempts, 1 correct (20% score) should be NOVICE with HIGH retention risk."""
    db = test_setup["db"]
    student = test_setup["student"]
    topic = test_setup["topic"]
    now = test_setup["now"]

    # Record 5 events (1 correct, 4 incorrect)
    for i in range(5):
        is_corr = (i == 0)
        ev = LearningEvent(
            student_id=student.id,
            topic_id=topic.id,
            event_type=EventType.PRACTICE,
            timestamp=now + timedelta(minutes=i),
            score=100.0 if is_corr else 0.0,
            correctness=is_corr,
            response_time_ms=3000,
        )
        db.add(ev)
    
    # Add TopicPerformance
    perf = TopicPerformance(
        student_id=student.id,
        topic_id=topic.id,
        total_attempts=5,
        correct_attempts=1,
        accuracy=20.0,
        average_response_time=3000.0,
        mastery_state="NOVICE",
    )
    db.add(perf)
    db.commit()

    profile = KnowledgeModelService.calculate_topic_profile(db, student.id, topic)
    assert profile.total_attempts == 5
    assert profile.correct_attempts == 1
    assert profile.accuracy == 20.0
    assert profile.recent_accuracy == 20.0
    assert profile.mastery_level == MasteryLevel.NOVICE
    assert profile.retention_risk == RetentionRiskLevel.HIGH
    assert profile.average_response_time_ms == 3000.0


def test_knowledge_profile_improving_trend(test_setup):
    """Test 3: Student with poor early performance and strong recent performance exhibits IMPROVING trend."""
    db = test_setup["db"]
    student = test_setup["student"]
    topic = test_setup["topic"]
    now = test_setup["now"]

    # 4 early failures (0% accuracy)
    for i in range(4):
        db.add(LearningEvent(
            student_id=student.id,
            topic_id=topic.id,
            event_type=EventType.PRACTICE,
            timestamp=now - timedelta(days=2) + timedelta(minutes=i),
            score=0.0,
            correctness=False,
            response_time_ms=5000,
        ))

    # 4 recent successes (100% accuracy)
    for i in range(4):
        db.add(LearningEvent(
            student_id=student.id,
            topic_id=topic.id,
            event_type=EventType.PRACTICE,
            timestamp=now + timedelta(minutes=i),
            score=100.0,
            correctness=True,
            response_time_ms=2500,
        ))

    perf = TopicPerformance(
        student_id=student.id,
        topic_id=topic.id,
        total_attempts=8,
        correct_attempts=4,
        accuracy=50.0,
        average_response_time=3750.0,
        mastery_state="DEVELOPING",
    )
    db.add(perf)
    db.commit()

    profile = KnowledgeModelService.calculate_topic_profile(db, student.id, topic)
    assert profile.total_attempts == 8
    assert profile.correct_attempts == 4
    assert profile.accuracy == 50.0
    assert profile.mastery_level == MasteryLevel.DEVELOPING
    # Recent accuracy (last 5: 1 fail + 4 success = 80%)
    assert profile.recent_accuracy == 80.0
    # Trend: early 0% -> recent 100% -> diff +100% >= 15% -> IMPROVING
    assert profile.trend == PerformanceTrend.IMPROVING


def test_knowledge_profile_api_endpoint(test_setup):
    """Test 4: GET /api/v1/adaptive/knowledge-profile/{student_id} returns structured profile."""
    client = TestClient(app)
    student = test_setup["student"]
    topic = test_setup["topic"]

    # 1. Unassessed student query
    res = client.get(f"/api/v1/adaptive/knowledge-profile/{student.id}")
    assert res.status_code == 200
    data = res.json()
    assert data["student_id"] == student.id
    assert data["total_topics_tracked"] == 0

    # 2. Query with specific topic_id
    res_topic = client.get(f"/api/v1/adaptive/knowledge-profile/{student.id}?topic_id={topic.id}")
    assert res_topic.status_code == 200
    data_topic = res_topic.json()
    assert data_topic["total_topics_tracked"] == 1
    assert data_topic["profiles"][0]["topic_id"] == topic.id
    assert data_topic["profiles"][0]["mastery_level"] == "UNASSESSED"
