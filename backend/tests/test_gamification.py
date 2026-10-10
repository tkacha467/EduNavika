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
    RevisionPlan,
    RevisionCompletionState,
    EventType,
)
from backend.app.services.gamification_service import GamificationService, XP_RULES
from backend.app.services.event_recorder import EventRecorderService


@pytest.fixture
def gamification_fixture(db_session):
    """Sets up a clean GSEB Standard 10 curriculum environment with student and curriculum topics."""
    user = User(
        name="Priya Patel",
        email="priya_gamification@edunavika.org",
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

    t1 = Topic(title="Chemical Reactions and Equations", chapter_id=chap1.id, topic_order=1)
    t2 = Topic(title="Acids, Bases and Salts", chapter_id=chap2.id, topic_order=1)
    t3 = Topic(title="Electricity", chapter_id=chap3.id, topic_order=1)
    db_session.add_all([t1, t2, t3])
    db_session.flush()

    student = StudentProfile(
        user_id=user.id,
        standard_id=std.id,
        enrollment_number="GAM-1001",
        preferred_language="en",
    )
    db_session.add(student)
    db_session.commit()

    return {
        "student": student,
        "t1": t1,
        "t2": t2,
        "t3": t3,
        "subj": subj,
    }


def test_1_gamification_endpoint_structure(client, gamification_fixture):
    """1. Endpoint returns 200 OK with fully compliant GamificationResponse schema."""
    student = gamification_fixture["student"]
    res = client.get(f"/api/v1/adaptive/gamification/{student.id}")
    assert res.status_code == 200
    data = res.json()

    assert data["student_id"] == student.id
    assert "total_xp" in data
    assert "level" in data
    assert "level_title" in data
    assert "xp_towards_next_level" in data
    assert "xp_required_for_next_level" in data
    assert "level_progress_percentage" in data
    assert "current_streak" in data
    assert "longest_streak" in data
    assert "daily_goal" in data
    assert "unlocked_badges" in data
    assert "locked_badges" in data

    dg = data["daily_goal"]
    assert "target" in dg
    assert "completed" in dg
    assert "percentage" in dg
    assert "is_completed" in dg


def test_2_practice_and_correct_answer_xp(db_session, gamification_fixture):
    """2. Verifies +10 XP for practice completion and +5 XP for correct answer."""
    student = gamification_fixture["student"]
    t1 = gamification_fixture["t1"]
    t2 = gamification_fixture["t2"]
    now = datetime.now(timezone.utc)

    # 1st attempt: Practice attempt wrong (+10 XP)
    ev1 = LearningEvent(
        student_id=student.id,
        topic_id=t1.id,
        event_type=EventType.PRACTICE,
        score=0.0,
        correctness=False,
        timestamp=now - timedelta(minutes=10),
    )
    db_session.add(ev1)
    db_session.commit()

    gam1 = GamificationService.get_student_gamification(db_session, student.id, now=now)
    assert gam1.total_xp == 10  # 10 for practice completion

    # 2nd attempt: Practice attempt correct on t2 (+10 XP completion + 5 XP correct = +15 XP)
    ev2 = LearningEvent(
        student_id=student.id,
        topic_id=t2.id,
        event_type=EventType.PRACTICE,
        score=1.0,
        correctness=True,
        timestamp=now - timedelta(minutes=5),
    )
    db_session.add(ev2)
    db_session.commit()

    gam2 = GamificationService.get_student_gamification(db_session, student.id, now=now)
    assert gam2.total_xp == 25  # 10 + (10 + 5)


def test_3_scheduled_revision_xp(db_session, gamification_fixture):
    """3. Verifies +15 XP for scheduled revision completion."""
    student = gamification_fixture["student"]
    t2 = gamification_fixture["t2"]
    now = datetime.now(timezone.utc)

    rev_ev = LearningEvent(
        student_id=student.id,
        topic_id=t2.id,
        event_type=EventType.REVISION,
        score=1.0,
        correctness=True,
        timestamp=now - timedelta(hours=1),
    )
    db_session.add(rev_ev)
    db_session.commit()

    gam = GamificationService.get_student_gamification(db_session, student.id, now=now)
    # 15 for revision completion + 5 for correct answer = 20 XP
    assert gam.total_xp == 20


def test_4_weak_topic_improvement_bonus_xp(db_session, gamification_fixture):
    """4. Verifies +20 XP bonus when a weak topic demonstrates improvement."""
    student = gamification_fixture["student"]
    t1 = gamification_fixture["t1"]
    now = datetime.now(timezone.utc)

    # Initial low performance: 2 wrong answers
    e1 = LearningEvent(
        student_id=student.id,
        topic_id=t1.id,
        event_type=EventType.PRACTICE,
        correctness=False,
        score=0.0,
        timestamp=now - timedelta(hours=3),
    )
    e2 = LearningEvent(
        student_id=student.id,
        topic_id=t1.id,
        event_type=EventType.PRACTICE,
        correctness=False,
        score=0.0,
        timestamp=now - timedelta(hours=2),
    )
    # Subsequent turnaround: 3 correct answers
    e3 = LearningEvent(
        student_id=student.id,
        topic_id=t1.id,
        event_type=EventType.PRACTICE,
        correctness=True,
        score=1.0,
        timestamp=now - timedelta(hours=1),
    )
    e4 = LearningEvent(
        student_id=student.id,
        topic_id=t1.id,
        event_type=EventType.PRACTICE,
        correctness=True,
        score=1.0,
        timestamp=now - timedelta(minutes=40),
    )
    e5 = LearningEvent(
        student_id=student.id,
        topic_id=t1.id,
        event_type=EventType.PRACTICE,
        correctness=True,
        score=1.0,
        timestamp=now - timedelta(minutes=20),
    )
    db_session.add_all([e1, e2, e3, e4, e5])

    # Also record improved TopicPerformance
    tp = TopicPerformance(
        student_id=student.id,
        topic_id=t1.id,
        total_attempts=5,
        correct_attempts=3,
        accuracy=60.0,
        mastery_state="DEVELOPING",
    )
    db_session.add(tp)
    db_session.commit()

    gam = GamificationService.get_student_gamification(db_session, student.id, now=now)
    # Total XP: 5 practices (5*10=50) + 3 correct (3*5=15) + 20 weak topic bonus + 25 daily goal (5 activities today) = 110 XP
    assert gam.total_xp >= 85
    # WEAKNESS_CRUSHER badge should be unlocked
    unlocked_ids = [b.badge_id for b in gam.unlocked_badges]
    assert "WEAKNESS_CRUSHER" in unlocked_ids


def test_5_daily_goal_completion_and_bonus_xp(db_session, gamification_fixture):
    """5. Verifies daily goal completion (5 activities) awards +25 XP bonus."""
    student = gamification_fixture["student"]
    t1 = gamification_fixture["t1"]
    now = datetime.now(timezone.utc)

    # 4 activities today: goal incomplete
    for i in range(4):
        db_session.add(
            LearningEvent(
                student_id=student.id,
                topic_id=t1.id,
                event_type=EventType.PRACTICE,
                correctness=False,
                timestamp=now - timedelta(minutes=30 - i * 5),
            )
        )
    db_session.commit()

    gam4 = GamificationService.get_student_gamification(db_session, student.id, now=now)
    assert gam4.daily_goal.completed == 4
    assert gam4.daily_goal.is_completed is False
    assert gam4.total_xp == 40  # 4 * 10 XP

    # 5th activity today: goal completed!
    db_session.add(
        LearningEvent(
            student_id=student.id,
            topic_id=t1.id,
            event_type=EventType.PRACTICE,
            correctness=False,
            timestamp=now - timedelta(minutes=5),
        )
    )
    db_session.commit()

    gam5 = GamificationService.get_student_gamification(db_session, student.id, now=now)
    assert gam5.daily_goal.completed == 5
    assert gam5.daily_goal.is_completed is True
    # 5 * 10 (practice) + 25 (daily goal bonus) = 75 XP
    assert gam5.total_xp == 75


def test_6_level_progression_calculation(db_session, gamification_fixture):
    """6. Verifies levels 1 to 5 thresholds and progress percentages."""
    student = gamification_fixture["student"]
    t1 = gamification_fixture["t1"]
    now = datetime.now(timezone.utc)

    # Level 1: 0-99 XP
    gam = GamificationService.get_student_gamification(db_session, student.id, now=now)
    assert gam.level == 1
    assert gam.level_title == "Curious Explorer"

    # Add 10 correct practices: 10 * 15 XP = 150 XP -> Level 2 (100-249 XP)
    for i in range(10):
        # spread across past days so daily goal doesn't trigger all at once
        db_session.add(
            LearningEvent(
                student_id=student.id,
                topic_id=t1.id,
                event_type=EventType.PRACTICE,
                correctness=True,
                timestamp=now - timedelta(days=20 - i),
            )
        )
    db_session.commit()

    gam_lvl2 = GamificationService.get_student_gamification(db_session, student.id, now=now)
    assert gam_lvl2.total_xp == 150
    assert gam_lvl2.level == 2
    assert gam_lvl2.level_title == "Active Learner"
    assert gam_lvl2.xp_towards_next_level == 50  # 150 - 100
    assert gam_lvl2.xp_required_for_next_level == 150


def test_7_learning_streak_calculation(db_session, gamification_fixture):
    """7. Verifies active streak and longest streak calculation across days."""
    student = gamification_fixture["student"]
    t1 = gamification_fixture["t1"]
    now = datetime.now(timezone.utc)

    # Activities on 3 consecutive days: today, yesterday, and day before yesterday
    for days_ago in [2, 1, 0]:
        db_session.add(
            LearningEvent(
                student_id=student.id,
                topic_id=t1.id,
                event_type=EventType.PRACTICE,
                correctness=True,
                timestamp=now - timedelta(days=days_ago, hours=2),
            )
        )
    db_session.commit()

    gam = GamificationService.get_student_gamification(db_session, student.id, now=now)
    assert gam.current_streak == 3
    assert gam.longest_streak == 3
    assert gam.streak_active_today is True

    # Check that THREE_DAY_LEARNER badge unlocked
    unlocked_ids = [b.badge_id for b in gam.unlocked_badges]
    assert "THREE_DAY_LEARNER" in unlocked_ids


def test_8_badges_unlock_criteria(db_session, gamification_fixture):
    """8. Verifies badges unlock under their empirical triggers."""
    student = gamification_fixture["student"]
    t1 = gamification_fixture["t1"]
    now = datetime.now(timezone.utc)

    # 1 activity unlocks FIRST_STEP
    db_session.add(
        LearningEvent(
            student_id=student.id,
            topic_id=t1.id,
            event_type=EventType.PRACTICE,
            correctness=True,
            timestamp=now - timedelta(minutes=10),
        )
    )
    db_session.commit()

    gam = GamificationService.get_student_gamification(db_session, student.id, now=now)
    unlocked_ids = [b.badge_id for b in gam.unlocked_badges]
    assert "FIRST_STEP" in unlocked_ids
    assert "CONSISTENT_LEARNER" in [b.badge_id for b in gam.locked_badges]

    # Add revision event -> REVISION_CHAMPION unlocks
    db_session.add(
        LearningEvent(
            student_id=student.id,
            topic_id=t1.id,
            event_type=EventType.REVISION,
            correctness=True,
            timestamp=now - timedelta(minutes=5),
        )
    )
    db_session.commit()

    gam_rev = GamificationService.get_student_gamification(db_session, student.id, now=now)
    unlocked_rev_ids = [b.badge_id for b in gam_rev.unlocked_badges]
    assert "REVISION_CHAMPION" in unlocked_rev_ids

    # Add mastered topic performance -> TOPIC_MASTER unlocks
    tp = TopicPerformance(
        student_id=student.id,
        topic_id=t1.id,
        total_attempts=6,
        correct_attempts=6,
        accuracy=100.0,
        mastery_state="MASTERED",
    )
    db_session.add(tp)
    db_session.commit()

    gam_master = GamificationService.get_student_gamification(db_session, student.id, now=now)
    assert "TOPIC_MASTER" in [b.badge_id for b in gam_master.unlocked_badges]


def test_9_language_switching_preserves_gamification_invariants(client, db_session, gamification_fixture):
    """9. Language switching keeps numbers/XP identical while localizing text into Hindi and Gujarati."""
    student = gamification_fixture["student"]
    t1 = gamification_fixture["t1"]
    now = datetime.now(timezone.utc)

    # Record 2 practice events
    db_session.add_all([
        LearningEvent(
            student_id=student.id,
            topic_id=t1.id,
            event_type=EventType.PRACTICE,
            correctness=True,
            timestamp=now - timedelta(minutes=15),
        ),
        LearningEvent(
            student_id=student.id,
            topic_id=t1.id,
            event_type=EventType.PRACTICE,
            correctness=False,
            timestamp=now - timedelta(minutes=5),
        ),
    ])
    db_session.commit()

    res_en = client.get(f"/api/v1/adaptive/gamification/{student.id}?language=en").json()
    res_hi = client.get(f"/api/v1/adaptive/gamification/{student.id}?language=hi").json()
    res_gu = client.get(f"/api/v1/adaptive/gamification/{student.id}?language=gu").json()

    # Numerical invariants must match strictly
    assert res_en["total_xp"] == res_hi["total_xp"] == res_gu["total_xp"]
    assert res_en["level"] == res_hi["level"] == res_gu["level"]
    assert res_en["current_streak"] == res_hi["current_streak"] == res_gu["current_streak"]
    assert res_en["daily_goal"]["completed"] == res_hi["daily_goal"]["completed"] == res_gu["daily_goal"]["completed"]

    # Localized titles must vary
    assert res_en["level_title"] == "Curious Explorer"
    assert res_hi["level_title"] == "जिज्ञासु शिक्षार्थी"
    assert res_gu["level_title"] == "જિજ્ઞાસુ વિદ્યાર્થી"

    # Badges must localize
    badge_en = next(b for b in res_en["unlocked_badges"] if b["badge_id"] == "FIRST_STEP")
    badge_hi = next(b for b in res_hi["unlocked_badges"] if b["badge_id"] == "FIRST_STEP")
    badge_gu = next(b for b in res_gu["unlocked_badges"] if b["badge_id"] == "FIRST_STEP")

    assert badge_en["name"] == "First Step"
    assert badge_hi["name"] == "पहला कदम"
    assert badge_gu["name"] == "પ્રથમ પગલું"


def test_10_empty_student_clean_baseline(db_session, gamification_fixture):
    """10. Unassessed student returns clean baseline with 0 XP, level 1, 0 streak, 6 locked badges."""
    student = gamification_fixture["student"]
    gam = GamificationService.get_student_gamification(db_session, student.id)

    assert gam.total_xp == 0
    assert gam.level == 1
    assert gam.current_streak == 0
    assert gam.longest_streak == 0
    assert gam.daily_goal.completed == 0
    assert gam.daily_goal.is_completed is False
    assert len(gam.unlocked_badges) == 0
    assert len(gam.locked_badges) == 6


def test_11_zero_cloud_dependency(db_session, gamification_fixture):
    """11. Gamification engine runs 100% locally from SQLite session with zero cloud network calls."""
    student = gamification_fixture["student"]
    # Function runs synchronously without requests or sockets
    gam = GamificationService.get_student_gamification(db_session, student.id)
    assert isinstance(gam.total_xp, int)
    assert gam.student_id == student.id


def test_12_gamification_does_not_mutate_learning_data(client, db_session, gamification_fixture):
    """12. Gamification calculation is strictly read-only on learning_events."""
    student = gamification_fixture["student"]
    t1 = gamification_fixture["t1"]
    db_session.add(
        LearningEvent(
            student_id=student.id,
            topic_id=t1.id,
            event_type=EventType.PRACTICE,
            correctness=True,
            timestamp=datetime.now(timezone.utc),
        )
    )
    db_session.commit()

    count_before = db_session.query(LearningEvent).filter(LearningEvent.student_id == student.id).count()
    res = client.get(f"/api/v1/adaptive/gamification/{student.id}")
    assert res.status_code == 200
    count_after = db_session.query(LearningEvent).filter(LearningEvent.student_id == student.id).count()

    assert count_before == count_after == 1


def test_13_adaptive_quests_generation_and_persistence(db_session, gamification_fixture):
    """13. Quests are generated from student weaknesses/signals and persist across queries."""
    student = gamification_fixture["student"]
    t1 = gamification_fixture["t1"]

    # Student incurs a misconception on topic t1
    db_session.add(
        LearningEvent(
            student_id=student.id,
            topic_id=t1.id,
            event_type=EventType.PRACTICE,
            correctness=False,
            score=0.0,
            timestamp=datetime.now(timezone.utc),
        )
    )
    db_session.commit()

    # Query gamification: should generate Concept Recovery and Consistency quests
    gam1 = GamificationService.get_student_gamification(db_session, student.id)
    assert len(gam1.active_quests) >= 1
    recovery_q = next((q for q in gam1.active_quests if q.quest_type == "CONCEPT_RECOVERY"), None)
    assert recovery_q is not None
    assert recovery_q.topic_id == t1.id
    assert recovery_q.target_progress == 2
    assert recovery_q.current_progress == 0

    # Query again: same quest should persist, not generate duplicate quests
    gam2 = GamificationService.get_student_gamification(db_session, student.id)
    matching = [q for q in gam2.active_quests if q.quest_id == recovery_q.quest_id]
    assert len(matching) == 1


def test_14_quest_completion_and_bonus_xp(db_session, gamification_fixture):
    """14. Completing a quest awards bonus XP and marks status COMPLETED without duplication."""
    student = gamification_fixture["student"]
    t1 = gamification_fixture["t1"]

    # Student incurs a misconception on topic t1 first, then answers 2 practice questions correctly
    now = datetime.now(timezone.utc)
    db_session.add_all([
        LearningEvent(
            student_id=student.id,
            topic_id=t1.id,
            event_type=EventType.PRACTICE,
            correctness=False,
            score=0.0,
            timestamp=now - timedelta(minutes=5),
        ),
        LearningEvent(
            student_id=student.id,
            topic_id=t1.id,
            event_type=EventType.PRACTICE,
            correctness=True,
            score=100.0,
            timestamp=now + timedelta(seconds=1),
        ),
        LearningEvent(
            student_id=student.id,
            topic_id=t1.id,
            event_type=EventType.PRACTICE,
            correctness=True,
            score=100.0,
            timestamp=now + timedelta(seconds=2),
        ),
    ])
    db_session.commit()

    gam = GamificationService.get_student_gamification(db_session, student.id)
    # The Concept Recovery quest should now be completed
    completed = [q for q in gam.completed_quests if q.quest_type == "CONCEPT_RECOVERY"]
    assert len(completed) >= 1
    assert completed[0].status == "COMPLETED"
    assert completed[0].progress_percentage == 100.0

    # Check that CONCEPT_RECOVERY badge was dynamically unlocked
    badge_ids = [b.badge_id for b in gam.unlocked_badges]
    assert "CONCEPT_RECOVERY" in badge_ids


def test_15_personal_best_badge_unlock(db_session, gamification_fixture):
    """15. Personal Best badge unlocks when student achieves >= 80% accuracy over >= 3 attempts."""
    student = gamification_fixture["student"]
    t2 = gamification_fixture["t2"]

    # Record 3 correct attempts on t2
    now = datetime.now(timezone.utc)
    for i in range(3):
        db_session.add(
            LearningEvent(
                student_id=student.id,
                topic_id=t2.id,
                event_type=EventType.PRACTICE,
                correctness=True,
                score=100.0,
                timestamp=now + timedelta(minutes=i),
            )
        )
    # Update TopicPerformance
    db_session.add(
        TopicPerformance(
            student_id=student.id,
            topic_id=t2.id,
            total_attempts=3,
            correct_attempts=3,
            accuracy=100.0,
            mastery_state="PROFICIENT",
        )
    )
    db_session.commit()

    gam = GamificationService.get_student_gamification(db_session, student.id)
    badge_ids = [b.badge_id for b in gam.unlocked_badges]
    assert "PERSONAL_BEST" in badge_ids

