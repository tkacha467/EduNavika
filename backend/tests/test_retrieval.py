import pytest
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
)
from backend.app.schemas.retrieval import RetrievalSearchRequest
from backend.app.services.curriculum_retrieval import CurriculumRetrievalService


@pytest.fixture
def retrieval_fixture(db_session):
    db = db_session
    # Check if Chemical Reactions exists in DB
    topic_chem = db.query(Topic).filter(Topic.id == "5a321a44-bc06-4db4-a50f-5e53f913b612").first()
    if not topic_chem:
        # Create synthetic curriculum setup if testing against blank DB
        std = db.query(Standard).filter(Standard.grade_number == 10).first()
        if not std:
            std = Standard(grade_number=10, name="Standard 10")
            db.add(std)
            db.flush()
        subj = Subject(name="Science & Technology", code="SCI-10", standard_id=std.id)
        db.add(subj)
        db.flush()
        chap = Chapter(title="Chemical Reactions and Equations", chapter_number=1, subject_id=subj.id)
        db.add(chap)
        db.flush()
        topic_chem = Topic(
            id="5a321a44-bc06-4db4-a50f-5e53f913b612",
            title="Chemical Reactions and Equations",
            chapter_id=chap.id,
            topic_order=1,
        )
        db.add(topic_chem)
        db.flush()

        # Add real content chunk
        c1 = LearningContent(
            topic_id=topic_chem.id,
            content_type=ContentType.TEXT,
            title="Writing a Chemical Equation",
            content_text="Chemical Reactions and Equations: A complete chemical equation represents the reactants, products and their physical states.",
            source_document="STD-10/Std-10_Science_English Medium.pdf",
            source_page=16,
        )
        db.add(c1)
        db.flush()

    # Ensure demo student profile exists for live test student id
    live_student_id = "e09699dd-0c64-44cc-82ef-ab41a832e072"
    stu = db.query(StudentProfile).filter(StudentProfile.id == live_student_id).first()
    if not stu:
        u = User(name="Retrieval Demo Student", email="retrieval_demo@test.org", hashed_password="pw", role=UserRole.STUDENT)
        db.add(u)
        db.flush()
        std10 = db.query(Standard).filter(Standard.grade_number == 10).first()
        stu = StudentProfile(id=live_student_id, user_id=u.id, standard_id=std10.id if std10 else None, enrollment_number="RET-DEMO")
        db.add(stu)
        db.flush()

    db.commit()

    yield {
        "db": db,
        "topic_id": topic_chem.id,
        "topic_title": topic_chem.title,
    }


def test_chemical_reactions_query_returns_content(retrieval_fixture):
    """
    Test 1: Chemical Reactions query returns authentic curriculum chunks.
    """
    db = retrieval_fixture["db"]
    topic_id = retrieval_fixture["topic_id"]

    req = RetrievalSearchRequest(
        topic_id=topic_id,
        query="chemical reactions and equations balanced equation reactants",
        top_k=3,
    )
    res = CurriculumRetrievalService.search(db, req)

    assert res.total_results >= 1
    assert res.topic_id == topic_id
    assert res.topic_title == "Chemical Reactions and Equations"
    top_item = res.results[0]
    assert top_item.topic_id == topic_id
    assert "chemical" in top_item.content_text.lower()
    assert top_item.source_document is not None
    assert top_item.score > 0.0


def test_topic_id_filtering_prevents_unrelated_topics(retrieval_fixture):
    """
    Test 2: Specifying topic_id strictly constrains retrieval to that topic only.
    """
    db = retrieval_fixture["db"]
    topic_id = retrieval_fixture["topic_id"]

    req = RetrievalSearchRequest(
        topic_id=topic_id,
        query="chemical reaction",
        top_k=5,
    )
    res = CurriculumRetrievalService.search(db, req)

    for item in res.results:
        assert item.topic_id == topic_id
        assert item.topic_title == "Chemical Reactions and Equations"


def test_general_content_not_returned_for_chemical_reactions(retrieval_fixture):
    """
    Test 3: Unrelated 'General Content' placeholder records are never returned.
    """
    db = retrieval_fixture["db"]
    topic_id = retrieval_fixture["topic_id"]

    req = RetrievalSearchRequest(
        topic_id=topic_id,
        query="general content curriculum overview",
        top_k=10,
    )
    res = CurriculumRetrievalService.search(db, req)

    for item in res.results:
        assert item.topic_id != "199dc81b-55c9-4678-ae50-7c575c64288f"
        assert "general content" not in item.topic_title.lower()
        assert item.topic_id == topic_id


def test_empty_query_handled_safely(retrieval_fixture):
    """
    Test 4: Empty / blank query gracefully returns the leading chapter content by page number.
    """
    db = retrieval_fixture["db"]
    topic_id = retrieval_fixture["topic_id"]

    req = RetrievalSearchRequest(
        topic_id=topic_id,
        query="   ",
        top_k=3,
    )
    res = CurriculumRetrievalService.search(db, req)

    assert res.total_results >= 1
    assert len(res.results) <= 3
    for item in res.results:
        assert item.topic_id == topic_id
        assert len(item.content_text) > 0


def test_unknown_topic_id_returns_empty_results(retrieval_fixture):
    """
    Test 5: An invalid / unknown topic_id safely returns an empty results payload.
    """
    db = retrieval_fixture["db"]

    req = RetrievalSearchRequest(
        topic_id="nonexistent-topic-uuid-12345",
        query="reactions and equations",
        top_k=5,
    )
    res = CurriculumRetrievalService.search(db, req)

    assert res.total_results == 0
    assert len(res.results) == 0


def test_results_contain_source_document_provenance(retrieval_fixture):
    """
    Test 6: All returned curriculum chunks contain source document and page number.
    """
    db = retrieval_fixture["db"]
    topic_id = retrieval_fixture["topic_id"]

    req = RetrievalSearchRequest(
        topic_id=topic_id,
        query="chemical equations",
        top_k=3,
    )
    res = CurriculumRetrievalService.search(db, req)

    assert res.total_results >= 1
    for item in res.results:
        assert item.source_document is not None
        assert "pdf" in item.source_document.lower()
        assert item.source_page is not None
        assert item.source_page >= 1


def test_retrieval_is_deterministic(retrieval_fixture):
    """
    Test 7: Repeated searches return identical ordering and identical relevance scores.
    """
    db = retrieval_fixture["db"]
    topic_id = retrieval_fixture["topic_id"]

    req = RetrievalSearchRequest(
        topic_id=topic_id,
        query="oxidation and reduction balanced equation",
        top_k=4,
    )
    res1 = CurriculumRetrievalService.search(db, req)
    res2 = CurriculumRetrievalService.search(db, req)

    assert res1.total_results == res2.total_results
    assert [r.content_id for r in res1.results] == [r.content_id for r in res2.results]
    assert [r.score for r in res1.results] == [r.score for r in res2.results]


def test_retrieval_api_endpoint(retrieval_fixture):
    """
    Test 8: POST /api/v1/retrieval/search returns 200 with grounded schema compliance.
    """
    client = TestClient(app)
    payload = {
        "student_id": "e09699dd-0c64-44cc-82ef-ab41a832e072",
        "topic_id": "5a321a44-bc06-4db4-a50f-5e53f913b612",
        "query": "chemical reactions and equations",
        "top_k": 3,
    }
    response = client.post("/api/v1/retrieval/search", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["topic_id"] == "5a321a44-bc06-4db4-a50f-5e53f913b612"
    assert data["total_results"] >= 1
    assert len(data["results"]) >= 1

    first = data["results"][0]
    assert first["topic_id"] == "5a321a44-bc06-4db4-a50f-5e53f913b612"
    assert first["source_document"] is not None
    assert first["source_page"] is not None
    assert len(first["content_text"]) > 0
    assert first["score"] > 0.0
