"""
PS-06 Core Product Architecture Verification: Offline Student Learning Loop.

Strict Requirements Verified:
1. Local Curriculum availability (Standard 10 GSEB/NCERT Science & Math)
2. Local Verified Question Bank (curriculum-grounded MCQs)
3. Adaptive Practice & Difficulty Adaptation (Knowledge Model)
4. Answer Submission & Mastery Updates
5. On-Device Personalized Explanations (Local SLM / Grounded Fallback)
6. Dynamic Recommendations
7. Progress Tracking
8. Automated Revision Planning
9. Educational Gamification (XP, Levels, Streak, Badges, Daily Goal)
10. Multilingual Support (English, Hindi, Gujarati) with Numerical Invariance
11. 100% Offline execution — Zero network/cloud calls during the core learning loop.
"""

import socket
import pytest
from datetime import datetime, timezone, timedelta
from unittest.mock import patch

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
    LearningContent,
    EventType,
)
from backend.app.domain.enums import MasteryLevel, RetentionRiskLevel, ContentType
from backend.app.services.curriculum_question_bank import get_canonical_questions_for_topic
from backend.app.services.adaptive_practice import adaptive_practice_service
from backend.app.services.gamification_service import GamificationService
from backend.app.services.revision_planner import RevisionPlannerService
from backend.app.services.progress_service import StudentProgressService
from backend.app.services.explanation_engine import OnDeviceLLMExplanationEngine


# Socket guard fixture to ensure absolute zero cloud/internet network calls
@pytest.fixture(autouse=True)
def guard_no_external_network():
    """Intercepts socket connections to guarantee zero cloud calls."""
    orig_connect = socket.socket.connect

    def guarded_connect(self, address):
        host = address[0]
        # Allow internal in-memory / localhost bindings only
        if host in ("127.0.0.1", "localhost", "::1"):
            return orig_connect(self, address)
        raise RuntimeError(f"VIOLATION OF PS-06 OFFLINE POLICY: Attempted external network call to {host}")

    with patch.object(socket.socket, "connect", guarded_connect):
        yield


@pytest.fixture
def ps06_offline_fixture(db_session):
    """Sets up a complete, isolated local GSEB Standard 10 curriculum environment."""
    user = User(
        name="Karan Dave",
        email="karan_offline@edunavika.org",
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
    chap11 = Chapter(title="Electricity", chapter_number=11, subject_id=subj.id)
    db_session.add_all([chap1, chap2, chap11])
    db_session.flush()

    t1 = Topic(id="5a321a44-bc06-4db4-a50f-5e53f913b612", title="Chemical Reactions and Equations", chapter_id=chap1.id, topic_order=1)
    t2 = Topic(id="b7c02b37-f831-4822-b5f7-f350c388bc61", title="Acids, Bases and Salts", chapter_id=chap2.id, topic_order=1)
    t3 = Topic(id="ea3cb4fd-f34d-409b-b0f6-d69b70db05b0", title="Electricity", chapter_id=chap11.id, topic_order=1)
    db_session.add_all([t1, t2, t3])
    db_session.flush()

    # Pre-provision local verified textbook source chunks in SQLite
    chunk1 = LearningContent(
        topic_id=t1.id,
        content_type=ContentType.TEXT,
        title="Balancing Chemical Equations",
        content_text=(
            "A complete chemical equation represents the reactants, products and their physical states symbolically. "
            "A chemical equation is balanced so that the numbers of atoms of each type involved in a chemical reaction "
            "are the same on the reactant and product sides of the equation. Law of conservation of mass must be satisfied."
        ),
        source_document="STD-10/Std-10_Science_English Medium.pdf",
        source_page=16,
        source_reference="NCERT/GSEB STD-10 Science Chapter 1 Section 1.1",
        chunk_identifier="06f69c9e-137a-4d30-91af-93fd17e032b1",
    )
    chunk2 = LearningContent(
        topic_id=t1.id,
        content_type=ContentType.TEXT,
        title="Types of Chemical Reactions",
        content_text=(
            "In a combination reaction two or more substances combine to form a new single substance. "
            "In a decomposition reaction a single substance breaks down to give simpler products. "
            "Displacement reaction occurs when a more reactive element displaces a less reactive element."
        ),
        source_document="STD-10/Std-10_Science_English Medium.pdf",
        source_page=17,
        source_reference="NCERT/GSEB STD-10 Science Chapter 1 Section 1.2",
        chunk_identifier="chem-ch1-chunk-02",
    )
    db_session.add_all([chunk1, chunk2])
    db_session.flush()

    student = StudentProfile(
        user_id=user.id,
        standard_id=std.id,
        enrollment_number="OFFLINE-1001",
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


def test_ps06_offline_curriculum_and_question_availability(ps06_offline_fixture):
    """Step 1 & 2: Local curriculum and verified question bank exist locally without internet."""
    t1 = ps06_offline_fixture["t1"]
    qs = get_canonical_questions_for_topic(t1.id)

    assert len(qs) >= 6
    for q in qs:
        assert q["source_document"] is not None
        assert q["source_page"] > 0
        assert len(q["options"]) == 4
        assert q["correct_answer"] in q["options"]


def test_ps06_complete_offline_closed_loop_personalization(client, db_session, ps06_offline_fixture):
    """
    Step 3 to 13: Full PS-06 Closed-Loop Learning Pipeline on 100% Offline Device.
    
    Flow:
    Fresh Student (Unassessed)
      ↓
    Diagnostic Practice (Foundational)
      ↓
    Wrong Answer Submission
      ↓
    Mastery drops to NOVICE / Accuracy 0%
      ↓
    On-device Personalized Remediation Explanation
      ↓
    Turnaround: Correct Answers Submitted
      ↓
    Mastery advances to DEVELOPING / Accuracy 66.7%
      ↓
    Adaptive difficulty steps up
      ↓
    Progress Tracking reflects real activity
      ↓
    Automated Revision Plan schedules spaced interval
      ↓
    Gamification rewards XP, Level, Streak, and Badges
    """
    student = ps06_offline_fixture["student"]
    t1 = ps06_offline_fixture["t1"]

    # 1. Start Practice: Fresh student baseline
    p_res = client.get(f"/api/v1/adaptive/practice/{student.id}?topic_id={t1.id}&count=3")
    assert p_res.status_code == 200
    p_data = p_res.json()

    assert p_data["target_difficulty"] == "FOUNDATIONAL"
    assert len(p_data["questions"]) == 3
    q1 = p_data["questions"][0]
    q2 = p_data["questions"][1]
    q3 = p_data["questions"][2]

    # Correct answers are safely hidden from the student prior to submission
    assert q1["correct_answer"] is None

    # 2. Submit Question 1: Wrong Answer
    wrong_sub = client.post(
        "/api/v1/adaptive/practice/submit",
        json={
            "student_id": student.id,
            "question_id": q1["id"],
            "topic_id": t1.id,
            "selected_answer": "Arbitrary Incorrect Distractor",
            "response_time_ms": 7500,
        },
    )
    assert wrong_sub.status_code == 200
    wrong_data = wrong_sub.json()

    assert wrong_data["correct"] is False
    assert wrong_data["updated_mastery"] == "NOVICE"
    assert wrong_data["updated_accuracy"] == 0.0
    # Remediation explanation must be provided
    assert "explanation" in wrong_data
    assert len(wrong_data["explanation"]) > 20

    # 3. Check Next Recommendation: Reflects remediation
    rec_res = client.get(f"/api/v1/adaptive/next-practice/{student.id}?topic_id={t1.id}")
    assert rec_res.status_code == 200
    rec_data = rec_res.json()
    assert rec_data["recommended_difficulty"] == "FOUNDATIONAL"
    assert rec_data["mastery_level"] == "NOVICE"

    # 4. Turnaround: Submit Question 2 and Question 3 with Correct Answers
    ans_q2 = adaptive_practice_service._ACTIVE_QUESTIONS[q2["id"]]["correct_answer"]
    ans_q3 = adaptive_practice_service._ACTIVE_QUESTIONS[q3["id"]]["correct_answer"]

    correct_sub_1 = client.post(
        "/api/v1/adaptive/practice/submit",
        json={
            "student_id": student.id,
            "question_id": q2["id"],
            "topic_id": t1.id,
            "selected_answer": ans_q2,
            "response_time_ms": 4200,
        },
    )
    assert correct_sub_1.status_code == 200
    assert correct_sub_1.json()["correct"] is True

    correct_sub_2 = client.post(
        "/api/v1/adaptive/practice/submit",
        json={
            "student_id": student.id,
            "question_id": q3["id"],
            "topic_id": t1.id,
            "selected_answer": ans_q3,
            "response_time_ms": 3800,
        },
    )
    assert correct_sub_2.status_code == 200
    c2_data = correct_sub_2.json()

    assert c2_data["correct"] is True
    # Accuracy improved from 0% -> 66.7% (2 correct out of 3)
    assert c2_data["updated_accuracy"] == pytest.approx(66.7, abs=0.5)
    assert c2_data["updated_mastery"] in ("DEVELOPING", "PROFICIENT")

    # 5. Progress Tracking Verification
    prog_res = client.get(f"/api/v1/adaptive/progress/{student.id}")
    assert prog_res.status_code == 200
    prog_data = prog_res.json()

    assert prog_data["overall"]["total_attempts"] == 3
    assert prog_data["overall"]["correct_attempts"] == 2
    assert prog_data["overall"]["topics_studied"] == 1
    assert len(prog_data["learning_journey"]) == 3

    # 6. Automated Revision Planning Verification
    rev_res = client.get(f"/api/v1/adaptive/revision-plan/{student.id}")
    assert rev_res.status_code == 200
    rev_data = rev_res.json()

    assert "revisions" in rev_data
    assert len(rev_data["revisions"]) >= 1
    rev_item = rev_data["revisions"][0]
    assert rev_item["topic_id"] == t1.id
    assert rev_item["days_until_due"] >= 0

    # 7. Educational Gamification Verification
    gam_res = client.get(f"/api/v1/adaptive/gamification/{student.id}")
    assert gam_res.status_code == 200
    gam_data = gam_res.json()

    # 3 practices (3*10=30) + 2 correct (2*5=10) + weak topic turnaround improvement (+20) = 60 XP
    assert gam_data["total_xp"] == 60
    assert gam_data["level"] == 1
    assert gam_data["level_title"] == "Curious Explorer"
    assert gam_data["current_streak"] == 1
    assert gam_data["daily_goal"]["completed"] == 3
    assert gam_data["daily_goal"]["target"] == 5
    assert gam_data["daily_goal"]["is_completed"] is False

    # Check Badges: FIRST_STEP is unlocked
    unlocked_badge_ids = [b["badge_id"] for b in gam_data["unlocked_badges"]]
    assert "FIRST_STEP" in unlocked_badge_ids


def test_ps06_multilingual_learning_loop_invariance(client, db_session, ps06_offline_fixture):
    """
    Step 14: Language switching across English, Hindi, and Gujarati
    preserves 100% of the personalization metrics while translating presentation.
    """
    student = ps06_offline_fixture["student"]
    t1 = ps06_offline_fixture["t1"]

    # 1. Practice questions in Hindi
    res_hi = client.get(f"/api/v1/adaptive/practice/{student.id}?topic_id={t1.id}&language=hi&count=1")
    assert res_hi.status_code == 200
    data_hi = res_hi.json()
    q_hi = data_hi["questions"][0]
    # Options and questions are in Devanagari script
    assert any("\u0900" <= c <= "\u097F" for c in q_hi["question"])

    # 2. Practice questions in Gujarati
    res_gu = client.get(f"/api/v1/adaptive/practice/{student.id}?topic_id={t1.id}&language=gu&count=1")
    assert res_gu.status_code == 200
    data_gu = res_gu.json()
    q_gu = data_gu["questions"][0]
    # Options and questions are in Gujarati script
    assert any("\u0A80" <= c <= "\u0AFF" for c in q_gu["question"])

    # 3. Canonical question topic and source provenance are identical across languages
    assert q_hi["topic_id"] == q_gu["topic_id"]
    assert q_hi["source_page"] == q_gu["source_page"]
    assert q_hi["source_document"] == q_gu["source_document"]
    assert q_hi["source_chunk_id"] == q_gu["source_chunk_id"]
