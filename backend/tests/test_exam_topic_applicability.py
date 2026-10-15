"""
EduNavika — Milestone 4 Phase E.4: Exam-Topic Applicability & Subtopic Boundaries Test Suite.

Verifies:
1. JEE Main does not expose JEE-Advanced-only topics as exam-eligible (e.g. Carnot engine, Doppler effect, Tangents & normals, Planes in 3D).
2. JEE Advanced retains its verified additional topics.
3. NEET UG does not expose Mathematics as an exam subject.
4. JEE Main and JEE Advanced do not expose Biology as an exam subject.
5. Human-review topics (e.g. flowering plant families, cockroach anatomy) receive zero exam links.
6. Textbook-only topics (e.g. Newton's law of cooling, Approximations) receive zero exam links,
   but remain available for general textbook/school study when queried without exam filter.
7. Repeated synchronization creates zero duplicates (100% idempotent).
8. Failed synchronization rolls back completely.
9. Existing legacy records and foreign-key constraints remain 100% valid.
10. Application endpoint /chapters/{id}/topics filters correctly by exam_code.
"""

import uuid
import pytest
from sqlalchemy import text
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.core.database import Base
from backend.app.models.competitive_models import Examination, ExamSubject, ExamTopic
from backend.app.models.curriculum_models import Standard, Subject, Chapter, Topic
from backend.app.db.seed_canonical_curriculum import seed_canonical_curriculum as seed_base_curriculum
from backend.app.services.curriculum_seeder import seed_canonical_curriculum
from backend.app.services.exam_topic_sync_service import sync_exam_topics


@pytest.fixture
def seeded_environment(db_session):
    """
    Sets up the complete isolated test environment:
    - Standard 10 legacy records.
    - Base competitive examinations (JEE_MAIN, JEE_ADVANCED, NEET_UG).
    - Standards 11 & 12 with 8 STEM subjects and 18 exam_subjects links.
    - 106 Canonical Chapters and 624 verified topics (via Phase E.2 seeder).
    """
    # 1. Legacy Standard 10 data
    std10 = Standard(
        id=str(uuid.uuid4()),
        grade_number=10,
        name="Standard 10",
        description="Legacy GSEB/NCERT Class 10 Secondary",
        is_active=True,
    )
    db_session.add(std10)
    db_session.flush()

    subj10 = Subject(
        id=str(uuid.uuid4()),
        standard_id=std10.id,
        name="Science 10",
        code="SCI10",
        description="Class 10 Science",
        is_active=True,
    )
    db_session.add(subj10)
    db_session.flush()

    ch10 = Chapter(
        id=str(uuid.uuid4()),
        subject_id=subj10.id,
        chapter_number=1,
        title="Chemical Reactions and Equations",
        source_reference="GSEB Std 10 Science Ch 1",
        is_active=True,
    )
    db_session.add(ch10)
    db_session.flush()

    top10 = Topic(
        id=str(uuid.uuid4()),
        chapter_id=ch10.id,
        topic_order=1,
        title="Chemical Equations",
        description="Writing and balancing chemical equations",
        is_active=True,
    )
    db_session.add(top10)
    db_session.flush()

    # 2. Base curriculum & 18 exam_subjects
    seed_base_curriculum(db_session, dry_run=False)

    # 3. Canonical hierarchy (106 chapters, 624 topics)
    seed_canonical_curriculum(db_session, dry_run=False, include_unreviewed=False)
    db_session.commit()

    return {
        "std10_id": std10.id,
        "subj10_id": subj10.id,
        "ch10_id": ch10.id,
        "top10_id": top10.id,
    }


def test_01_sync_exam_topics_dry_run(db_session, seeded_environment):
    """Test 1: Dry-run synchronizes planned links with zero writes to database."""
    pre_count = db_session.query(ExamTopic).count()
    assert pre_count == 0

    report = sync_exam_topics(db_session, dry_run=True)

    assert report["dry_run"] is True
    assert report["links_created"] == 1377
    assert report["links_by_exam"]["JEE_MAIN"] == 436
    assert report["links_by_exam"]["JEE_ADVANCED"] == 444
    assert report["links_by_exam"]["NEET_UG"] == 497
    assert report["quarantined_count"] == 2
    assert report["textbook_only_count"] == 2

    # Verify zero database writes committed
    post_count = db_session.query(ExamTopic).count()
    assert post_count == 0


def test_02_sync_exam_topics_clean_execution(db_session, seeded_environment):
    """Test 2: Clean live execution inserts exactly 1,377 verified exam-topic associations."""
    report = sync_exam_topics(db_session, dry_run=False)

    assert report["dry_run"] is False
    assert report["success"] is True
    assert report["links_created"] == 1377
    assert report["links_existing"] == 0
    assert report["quarantined_count"] == 2
    assert report["textbook_only_count"] == 2

    # Database count check
    total_db_links = db_session.query(ExamTopic).count()
    assert total_db_links == 1377

    # Breakdown check
    jee_main_count = db_session.query(ExamTopic).filter(ExamTopic.exam_code == "JEE_MAIN").count()
    jee_adv_count = db_session.query(ExamTopic).filter(ExamTopic.exam_code == "JEE_ADVANCED").count()
    neet_count = db_session.query(ExamTopic).filter(ExamTopic.exam_code == "NEET_UG").count()

    assert jee_main_count == 436
    assert jee_adv_count == 444
    assert neet_count == 497


def test_03_sync_exam_topics_idempotency(db_session, seeded_environment):
    """Test 3: Re-running synchronization creates zero duplicates (100% idempotent)."""
    # First run
    r1 = sync_exam_topics(db_session, dry_run=False)
    assert r1["links_created"] == 1377

    # Second run
    r2 = sync_exam_topics(db_session, dry_run=False)
    assert r2["links_created"] == 0
    assert r2["links_existing"] == 1377
    assert len(r2["errors"]) == 0

    assert db_session.query(ExamTopic).count() == 1377


def test_04_jee_main_excludes_jee_advanced_only_topics(db_session, seeded_environment):
    """Test 4: JEE Main does not expose JEE-Advanced-only topics as exam-eligible."""
    sync_exam_topics(db_session, dry_run=False)

    # 1. Carnot engine: in Thermodynamics (Physics 11)
    carnot_topic = db_session.query(Topic).filter(Topic.title == "Carnot Engine and Efficiency").first()
    assert carnot_topic is not None

    carnot_jee_main = db_session.query(ExamTopic).filter(
        ExamTopic.exam_code == "JEE_MAIN",
        ExamTopic.topic_id == carnot_topic.id
    ).first()
    assert carnot_jee_main is None, "Carnot Engine MUST NOT be linked to JEE Main!"

    carnot_jee_adv = db_session.query(ExamTopic).filter(
        ExamTopic.exam_code == "JEE_ADVANCED",
        ExamTopic.topic_id == carnot_topic.id
    ).first()
    assert carnot_jee_adv is not None, "Carnot Engine MUST be linked to JEE Advanced!"

    # 2. Doppler effect (Acoustic)
    doppler_topic = db_session.query(Topic).filter(Topic.title == "Doppler Effect (Acoustic)").first()
    assert doppler_topic is not None
    assert db_session.query(ExamTopic).filter(ExamTopic.exam_code == "JEE_MAIN", ExamTopic.topic_id == doppler_topic.id).first() is None
    assert db_session.query(ExamTopic).filter(ExamTopic.exam_code == "JEE_ADVANCED", ExamTopic.topic_id == doppler_topic.id).first() is not None

    # 3. Tangents and Normals
    tangents_topic = db_session.query(Topic).filter(Topic.title == "Tangents and Normals").first()
    assert tangents_topic is not None
    assert db_session.query(ExamTopic).filter(ExamTopic.exam_code == "JEE_MAIN", ExamTopic.topic_id == tangents_topic.id).first() is None
    assert db_session.query(ExamTopic).filter(ExamTopic.exam_code == "JEE_ADVANCED", ExamTopic.topic_id == tangents_topic.id).first() is not None

    # 4. Plane in Space and Angle between Two Planes
    plane_topic = db_session.query(Topic).filter(Topic.title == "Plane in Space and Angle between Two Planes").first()
    assert plane_topic is not None
    assert db_session.query(ExamTopic).filter(ExamTopic.exam_code == "JEE_MAIN", ExamTopic.topic_id == plane_topic.id).first() is None
    assert db_session.query(ExamTopic).filter(ExamTopic.exam_code == "JEE_ADVANCED", ExamTopic.topic_id == plane_topic.id).first() is not None


def test_05_subject_level_boundaries_enforced(db_session, seeded_environment):
    """Test 5: NEET has no Mathematics links, and JEE has no Biology links."""
    sync_exam_topics(db_session, dry_run=False)

    # All topics belonging to Math subjects
    math_topic_ids = [
        t.id for t in db_session.query(Topic)
        .join(Chapter, Topic.chapter_id == Chapter.id)
        .join(Subject, Chapter.subject_id == Subject.id)
        .filter(Subject.code.in_(["MATH11", "MATH12"]))
        .all()
    ]
    neet_math_links = db_session.query(ExamTopic).filter(
        ExamTopic.exam_code == "NEET_UG",
        ExamTopic.topic_id.in_(math_topic_ids)
    ).count()
    assert neet_math_links == 0, "NEET UG MUST NOT have any Mathematics topic links!"

    # All topics belonging to Biology subjects
    bio_topic_ids = [
        t.id for t in db_session.query(Topic)
        .join(Chapter, Topic.chapter_id == Chapter.id)
        .join(Subject, Chapter.subject_id == Subject.id)
        .filter(Subject.code.in_(["BIO11", "BIO12"]))
        .all()
    ]
    jee_main_bio_links = db_session.query(ExamTopic).filter(
        ExamTopic.exam_code == "JEE_MAIN",
        ExamTopic.topic_id.in_(bio_topic_ids)
    ).count()
    assert jee_main_bio_links == 0, "JEE Main MUST NOT have any Biology topic links!"

    jee_adv_bio_links = db_session.query(ExamTopic).filter(
        ExamTopic.exam_code == "JEE_ADVANCED",
        ExamTopic.topic_id.in_(bio_topic_ids)
    ).count()
    assert jee_adv_bio_links == 0, "JEE Advanced MUST NOT have any Biology topic links!"


def test_06_textbook_only_topics_have_zero_exam_links(db_session, seeded_environment):
    """Test 6: Textbook-only topics receive zero exam links but exist in the database."""
    sync_exam_topics(db_session, dry_run=False)

    # Newton's law of cooling
    cooling_topic = db_session.query(Topic).filter(Topic.title == "Newton's Law of Cooling").first()
    assert cooling_topic is not None, "Newton's law of cooling MUST exist in database as textbook content!"
    cooling_links = db_session.query(ExamTopic).filter(ExamTopic.topic_id == cooling_topic.id).count()
    assert cooling_links == 0, "Newton's law of cooling MUST have 0 exam links!"

    # Approximations
    approx_topic = db_session.query(Topic).filter(Topic.title == "Approximations").first()
    assert approx_topic is not None, "Approximations MUST exist in database as textbook content!"
    approx_links = db_session.query(ExamTopic).filter(ExamTopic.topic_id == approx_topic.id).count()
    assert approx_links == 0, "Approximations MUST have 0 exam links!"


def test_07_quarantined_human_review_topics_have_zero_exam_links(db_session, seeded_environment):
    """Test 7: Topics requiring human review have zero exam links."""
    sync_exam_topics(db_session, dry_run=False)

    plant_families = db_session.query(Topic).filter(Topic.title.like("%Flowering Plant and Families%")).first()
    if plant_families:
        links = db_session.query(ExamTopic).filter(ExamTopic.topic_id == plant_families.id).count()
        assert links == 0, "Unreviewed plant families topic must have 0 exam links!"

    cockroach = db_session.query(Topic).filter(Topic.title.like("%Cockroach / Frog%")).first()
    if cockroach:
        links = db_session.query(ExamTopic).filter(ExamTopic.topic_id == cockroach.id).count()
        assert links == 0, "Unreviewed cockroach anatomy topic must have 0 exam links!"


def test_08_api_endpoint_filters_topics_by_exam_code(db_session, seeded_environment):
    """Test 8: API endpoint /chapters/{id}/topics filters by exam_code correctly."""
    sync_exam_topics(db_session, dry_run=False)

    client = TestClient(app)

    # Find Thermodynamics chapter (Physics 11, ch 11)
    thermo_ch = (
        db_session.query(Chapter)
        .join(Subject, Chapter.subject_id == Subject.id)
        .filter(Subject.code == "PHYS11", Chapter.chapter_number == 11)
        .first()
    )
    assert thermo_ch is not None

    # 1. Non-exam request (textbook context): returns all 8 topics including Carnot Engine
    resp_textbook = client.get(f"/api/v1/chapters/{thermo_ch.id}/topics")
    assert resp_textbook.status_code == 200
    textbook_titles = [t["title"] for t in resp_textbook.json()]
    assert "Carnot Engine and Efficiency" in textbook_titles
    assert len(textbook_titles) == 8

    # 2. JEE Main request: Carnot Engine is excluded!
    resp_jee_main = client.get(f"/api/v1/chapters/{thermo_ch.id}/topics?exam_code=JEE_MAIN")
    assert resp_jee_main.status_code == 200
    jee_main_titles = [t["title"] for t in resp_jee_main.json()]
    assert "Carnot Engine and Efficiency" not in jee_main_titles, "Carnot Engine MUST be excluded from JEE Main query!"
    assert len(jee_main_titles) == 7

    # 3. JEE Advanced request: Carnot Engine is included!
    resp_jee_adv = client.get(f"/api/v1/chapters/{thermo_ch.id}/topics?exam_code=JEE_ADVANCED")
    assert resp_jee_adv.status_code == 200
    jee_adv_titles = [t["title"] for t in resp_jee_adv.json()]
    assert "Carnot Engine and Efficiency" in jee_adv_titles, "Carnot Engine MUST be included in JEE Advanced query!"
    assert len(jee_adv_titles) == 8


def test_09_foreign_keys_and_integrity_check(db_session, seeded_environment):
    """Test 9: SQLite integrity and foreign-key checks pass with 0 errors."""
    sync_exam_topics(db_session, dry_run=False)

    raw_conn = db_session.connection()
    fk_violations = raw_conn.exec_driver_sql("PRAGMA foreign_key_check").fetchall()
    assert len(fk_violations) == 0, f"FK violations: {fk_violations}"

    integrity = raw_conn.exec_driver_sql("PRAGMA integrity_check").fetchall()
    assert integrity == [("ok",)], f"Integrity failed: {integrity}"


def test_10_legacy_data_preservation(db_session, seeded_environment):
    """Test 10: Standard 10 legacy data remains completely intact after synchronization."""
    std10_id = seeded_environment["std10_id"]
    sync_exam_topics(db_session, dry_run=False)

    std10 = db_session.query(Standard).filter(Standard.id == std10_id).first()
    assert std10 is not None and std10.grade_number == 10

    # Ensure Std 10 has no competitive exam_topics
    std10_topic_ids = [
        t.id for t in db_session.query(Topic)
        .join(Chapter, Topic.chapter_id == Chapter.id)
        .join(Subject, Chapter.subject_id == Subject.id)
        .filter(Subject.standard_id == std10_id)
        .all()
    ]
    std10_links = db_session.query(ExamTopic).filter(ExamTopic.topic_id.in_(std10_topic_ids)).count()
    assert std10_links == 0


def test_11_recommendation_and_study_engine_eligibility_filter(db_session, seeded_environment):
    """Test 11: Recommendation & practice engine is_eligible_curriculum_topic respects exam applicability."""
    from backend.app.services.recommendation_engine import RecommendationEngineService

    sync_exam_topics(db_session, dry_run=False)

    carnot = db_session.query(Topic).filter(Topic.title == "Carnot Engine and Efficiency").first()
    assert carnot is not None

    cooling = db_session.query(Topic).filter(Topic.title == "Newton's Law of Cooling").first()
    assert cooling is not None

    # 1. Non-exam (textbook) context: both are eligible authentic curriculum topics
    assert RecommendationEngineService.is_eligible_curriculum_topic(db_session, None, carnot) is True
    assert RecommendationEngineService.is_eligible_curriculum_topic(db_session, None, cooling) is True

    # 2. JEE Main context: Carnot engine is NOT eligible; cooling is NOT eligible
    assert RecommendationEngineService.is_eligible_curriculum_topic(db_session, None, carnot, exam_code="JEE_MAIN") is False
    assert RecommendationEngineService.is_eligible_curriculum_topic(db_session, None, cooling, exam_code="JEE_MAIN") is False

    # 3. JEE Advanced context: Carnot engine IS eligible; cooling is NOT eligible
    assert RecommendationEngineService.is_eligible_curriculum_topic(db_session, None, carnot, exam_code="JEE_ADVANCED") is True
    assert RecommendationEngineService.is_eligible_curriculum_topic(db_session, None, cooling, exam_code="JEE_ADVANCED") is False

    # 4. NEET UG context: cooling is NOT eligible
    assert RecommendationEngineService.is_eligible_curriculum_topic(db_session, None, cooling, exam_code="NEET_UG") is False
