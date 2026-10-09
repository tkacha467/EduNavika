import pytest
from datetime import datetime, timezone
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.core.database import SessionLocal
from backend.app.models import (
    Standard,
    Subject,
    Chapter,
    Topic,
    LearningContent,
    ContentType,
    StudentProfile,
    User,
    UserRole,
    LearningEvent,
    EventType,
    TopicPerformance,
)
from backend.app.domain.enums import MasteryLevel, PerformanceTrend, RetentionRiskLevel
from backend.app.schemas.explanation import ExplanationRequest
from backend.app.services.personalized_explanation import (
    PersonalizedExplanationService,
)
from backend.app.services.explanation_engine import DeterministicExplanationEngine
from backend.app.services.event_recorder import EventRecorderService

# Explicitly test deterministic engine contracts in unit test
personalized_explanation_service = PersonalizedExplanationService(engine=DeterministicExplanationEngine())


@pytest.fixture
def explanation_fixture():
    db = SessionLocal()
    now = datetime.now(timezone.utc)
    ts = str(int(now.timestamp() * 1000))[-6:]

    std = db.query(Standard).filter(Standard.grade_number == 10).first()
    if not std:
        std = Standard(grade_number=10, name="Standard 10")
        db.add(std)
        db.flush()

    subj = Subject(name=f"Science Exp {ts}", code=f"SE_{ts}", standard_id=std.id)
    db.add(subj)
    db.flush()

    chap = Chapter(title=f"Chemical Reactions {ts}", chapter_number=1, subject_id=subj.id)
    db.add(chap)
    db.flush()

    topic = Topic(title=f"Chemical Reactions and Equations {ts}", chapter_id=chap.id, topic_order=1)
    db.add(topic)
    db.flush()

    # Add verified learning content
    c1 = LearningContent(
        topic_id=topic.id,
        content_type=ContentType.TEXT,
        title=f"Balancing Chemical Equations {ts}",
        content_text="To balance a chemical equation, first draw boxes around each formula. Do not change anything inside the boxes while balancing the equation.",
        source_document="STD-10/Std-10_Science_English Medium.pdf",
        source_page=17,
    )
    db.add(c1)
    db.flush()

    user = User(name=f"Exp Student {ts}", email=f"exp_student_{ts}@test.com", hashed_password="dummy", role=UserRole.STUDENT)
    db.add(user)
    db.flush()

    student = StudentProfile(user_id=user.id, standard_id=std.id, enrollment_number=f"EXP_{ts}")
    db.add(student)
    db.commit()

    yield {
        "db": db,
        "student_id": student.id,
        "topic_id": topic.id,
        "topic_title": topic.title,
    }
    db.close()


def test_novice_student_receives_foundational_explanation(explanation_fixture):
    """
    Test 1: NOVICE / accuracy < 50% receives foundational remediation explanation.
    """
    data = explanation_fixture
    db = data["db"]
    stu_id = data["student_id"]
    top_id = data["topic_id"]

    # 1 correct out of 5 (20% accuracy)
    for i in range(5):
        EventRecorderService.record_event(
            db=db,
            student_id=stu_id,
            topic_id=top_id,
            event_type=EventType.MCQ_ATTEMPT,
            score=100.0 if i == 0 else 0.0,
            correctness=(i == 0),
        )
    db.commit()

    req = ExplanationRequest(student_id=stu_id, topic_id=top_id, query="I dont understand balancing equations")
    res = personalized_explanation_service.generate_explanation(db, req)

    assert res.teaching_level == "FOUNDATIONAL_REMEDIATION"
    assert res.personalization.mastery_level == MasteryLevel.NOVICE
    assert res.personalization.accuracy == 20.0
    assert "fundamentals" in res.structured_explanation.title.lower() or "building" in res.structured_explanation.title.lower()
    assert len(res.structured_explanation.step_by_step) >= 3
    assert res.structured_explanation.common_mistake is not None
    assert res.structured_explanation.quick_check.question is not None


def test_developing_student_receives_strengthening_explanation(explanation_fixture):
    """
    Test 2: DEVELOPING student (e.g. 60% accuracy) receives guided strengthening explanation.
    """
    data = explanation_fixture
    db = data["db"]
    stu_id = data["student_id"]
    top_id = data["topic_id"]

    # 3 correct out of 5 (60% accuracy)
    for i in range(5):
        EventRecorderService.record_event(
            db=db,
            student_id=stu_id,
            topic_id=top_id,
            event_type=EventType.MCQ_ATTEMPT,
            score=100.0 if i < 3 else 0.0,
            correctness=(i < 3),
        )
    db.commit()

    req = ExplanationRequest(student_id=stu_id, topic_id=top_id, query="How to balance complex reactions")
    res = personalized_explanation_service.generate_explanation(db, req)

    assert res.teaching_level == "GUIDED_STRENGTHENING"
    assert res.personalization.mastery_level == MasteryLevel.DEVELOPING
    assert res.personalization.accuracy == 60.0
    assert "strengthening" in res.structured_explanation.title.lower() or "mastery" in res.structured_explanation.title.lower()


def test_proficient_student_receives_application_explanation(explanation_fixture):
    """
    Test 3: PROFICIENT student (e.g. 80% accuracy) receives advanced application explanation.
    """
    data = explanation_fixture
    db = data["db"]
    stu_id = data["student_id"]
    top_id = data["topic_id"]

    # 4 correct out of 5 (80% accuracy)
    for i in range(5):
        EventRecorderService.record_event(
            db=db,
            student_id=stu_id,
            topic_id=top_id,
            event_type=EventType.MCQ_ATTEMPT,
            score=100.0 if i < 4 else 0.0,
            correctness=(i < 4),
        )
    db.commit()

    req = ExplanationRequest(student_id=stu_id, topic_id=top_id, query="Exam level redox questions")
    res = personalized_explanation_service.generate_explanation(db, req)

    assert res.teaching_level == "ADVANCED_APPLICATION"
    assert res.personalization.mastery_level == MasteryLevel.PROFICIENT
    assert res.personalization.accuracy == 80.0
    assert "application" in res.structured_explanation.title.lower() or "advanced" in res.structured_explanation.title.lower()


def test_explanation_uses_retrieved_curriculum_content(explanation_fixture):
    """
    Test 4: Grounded explanation directly references retrieved textbook concepts.
    """
    data = explanation_fixture
    db = data["db"]
    stu_id = data["student_id"]
    top_id = data["topic_id"]

    req = ExplanationRequest(student_id=stu_id, topic_id=top_id, query="balancing chemical equations")
    res = personalized_explanation_service.generate_explanation(db, req)

    assert len(res.sources) >= 1
    # Check that core concept references the textbook
    assert "curriculum" in res.structured_explanation.core_concept.lower() or "textbook" in res.structured_explanation.core_concept.lower()
    assert "draw boxes" in res.structured_explanation.core_concept.lower() or "reactants" in res.structured_explanation.core_concept.lower()


def test_source_document_and_page_returned(explanation_fixture):
    """
    Test 5: Source document and page number are preserved and returned.
    """
    data = explanation_fixture
    db = data["db"]
    stu_id = data["student_id"]
    top_id = data["topic_id"]

    req = ExplanationRequest(student_id=stu_id, topic_id=top_id, query="balancing equations")
    res = personalized_explanation_service.generate_explanation(db, req)

    assert len(res.sources) >= 1
    src = res.sources[0]
    assert src.source_document is not None
    assert "pdf" in src.source_document.lower()
    assert src.source_page is not None
    assert src.source_page == 17


def test_unrelated_or_invalid_topic_rejected(explanation_fixture):
    """
    Test 6: Requesting explanation for an unknown/invalid topic raises a clear error.
    """
    data = explanation_fixture
    db = data["db"]
    stu_id = data["student_id"]

    req = ExplanationRequest(student_id=stu_id, topic_id="invalid-topic-xyz-999", query="test")
    with pytest.raises(ValueError) as exc:
        personalized_explanation_service.generate_explanation(db, req)
    assert "could not be resolved" in str(exc.value).lower()


def test_general_content_cannot_contaminate_explanation(explanation_fixture):
    """
    Test 7: Legacy placeholder 'General Content' is rejected and cannot be requested as an explanation topic.
    """
    data = explanation_fixture
    db = data["db"]
    stu_id = data["student_id"]

    # Even if topic exists in DB with title 'General Content'
    chap_gen = Chapter(title="General Curriculum Content", chapter_number=99, subject_id=db.query(Topic).filter(Topic.id == data["topic_id"]).first().chapter.subject_id)
    db.add(chap_gen)
    db.flush()
    t_gen = Topic(title="General Content", chapter_id=chap_gen.id, topic_order=1)
    db.add(t_gen)
    db.commit()

    req = ExplanationRequest(student_id=stu_id, topic_id=t_gen.id, query="explain general content")
    with pytest.raises(ValueError) as exc:
        personalized_explanation_service.generate_explanation(db, req)
    assert "not an eligible curriculum topic" in str(exc.value).lower()


def test_student_no_history_receives_safe_onboarding_explanation(explanation_fixture):
    """
    Test 8: Student with zero attempt history receives a safe, foundational onboarding explanation.
    """
    data = explanation_fixture
    db = data["db"]
    top_id = data["topic_id"]

    # Fresh student with 0 events
    sub_ts = str(int(datetime.now(timezone.utc).timestamp() * 1000))[-6:]
    user2 = User(name="Brand New Student", email=f"new_student_{sub_ts}@test.com", hashed_password="dummy", role=UserRole.STUDENT)
    db.add(user2)
    db.flush()
    stu2 = StudentProfile(user_id=user2.id, enrollment_number=f"NEW_EXP_{sub_ts}")
    db.add(stu2)
    db.commit()

    req = ExplanationRequest(student_id=stu2.id, topic_id=top_id, query="Tell me about this topic")
    res = personalized_explanation_service.generate_explanation(db, req)

    assert res.teaching_level == "FOUNDATIONAL_REMEDIATION"
    assert res.personalization.mastery_level == MasteryLevel.UNASSESSED
    assert res.personalization.accuracy == 0.0
    assert res.structured_explanation.title is not None
    assert len(res.structured_explanation.step_by_step) >= 3


def test_explanation_generation_is_deterministic(explanation_fixture):
    """
    Test 9: Identical inputs produce identical structured explanations.
    """
    data = explanation_fixture
    db = data["db"]
    stu_id = data["student_id"]
    top_id = data["topic_id"]

    req = ExplanationRequest(student_id=stu_id, topic_id=top_id, query="explain balancing")
    res1 = personalized_explanation_service.generate_explanation(db, req)
    res2 = personalized_explanation_service.generate_explanation(db, req)

    assert res1.teaching_level == res2.teaching_level
    assert res1.explanation == res2.explanation
    assert res1.next_action == res2.next_action


def test_explanation_api_endpoint(explanation_fixture):
    """
    Test 10: POST /api/v1/adaptive/explanation returns 200 with schema compliance.
    """
    data = explanation_fixture
    stu_id = data["student_id"]
    top_id = data["topic_id"]

    client = TestClient(app)
    payload = {
        "student_id": stu_id,
        "topic_id": top_id,
        "query": "I don't understand how to balance equations",
        "top_k": 2,
    }
    response = client.post("/api/v1/adaptive/explanation", json=payload)
    assert response.status_code == 200
    res_data = response.json()
    assert res_data["student_id"] == stu_id
    assert res_data["topic_id"] == top_id
    assert "explanation" in res_data
    assert "structured_explanation" in res_data
    assert "teaching_level" in res_data
    assert "personalization" in res_data
    assert "sources" in res_data
    assert "next_action" in res_data
