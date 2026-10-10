"""
Unit Tests for School LAN Offline-First Curriculum Distribution (Problem Statement 06, Section 4).
Verifies:
1. Exporting versioned curriculum package with deterministic SHA-256 checksum.
2. Manifest completeness (counts of subjects, chapters, topics, contents).
3. Cryptographic integrity check: rejection of tampered packages.
4. Idempotent import into local database.
5. REST API endpoints /api/v1/curriculum/package/export and /api/v1/curriculum/package/import.
"""

import pytest
from backend.app.models import Standard, Subject, Chapter, Topic, LearningContent
from backend.app.domain.enums import ContentType
from backend.app.services.curriculum_package_service import CurriculumPackageService


@pytest.fixture
def package_curriculum_fixture(db_session):
    """Sets up a complete GSEB Standard 10 curriculum fixture."""
    std = Standard(grade_number=10, name="Standard 10", description="Standard 10 GSEB Curriculum")
    db_session.add(std)
    db_session.flush()

    subj = Subject(name="Science & Technology", code="SCI-10-TEST", standard_id=std.id)
    db_session.add(subj)
    db_session.flush()

    chap = Chapter(title="Chemical Reactions and Equations", chapter_number=1, subject_id=subj.id)
    db_session.add(chap)
    db_session.flush()

    top = Topic(title="Chemical Reactions and Equations", chapter_id=chap.id, topic_order=1)
    db_session.add(top)
    db_session.flush()

    content = LearningContent(
        topic_id=top.id,
        title="Balancing Chemical Equations",
        content_type=ContentType.TEXT,
        content_text="Total mass of reactants equals total mass of products in a chemical reaction.",
        source_document="STD-10/Std-10_Science_English Medium.pdf",
        source_page=16,
        chunk_identifier="chunk-chem-01",
    )
    db_session.add(content)
    db_session.commit()

    return {
        "standard": std,
        "subject": subj,
        "chapter": chap,
        "topic": top,
        "content": content,
    }


def test_export_package_structure_and_checksum(package_curriculum_fixture, db_session):
    """Verifies exported package contains valid manifest, payload, and SHA-256 checksum."""
    pkg = CurriculumPackageService.export_package(db_session, grade=10)

    assert "manifest" in pkg
    assert "payload" in pkg

    manifest = pkg["manifest"]
    payload = pkg["payload"]

    assert manifest["standard_grade"] == 10
    assert manifest["total_subjects"] >= 1
    assert manifest["total_chapters"] >= 1
    assert manifest["total_topics"] >= 1
    assert manifest["total_contents"] >= 1
    assert manifest["checksum_algorithm"] == "SHA-256"
    assert len(manifest["checksum"]) == 64

    # Verify checksum matches payload exactly
    expected = CurriculumPackageService.calculate_checksum(payload)
    assert manifest["checksum"] == expected


def test_import_package_integrity_and_tamper_rejection(package_curriculum_fixture, db_session):
    """Verifies that tampered packages with mismatched checksum are strictly rejected."""
    pkg = CurriculumPackageService.export_package(db_session, grade=10)

    # Tamper with payload content without updating checksum
    tampered_pkg = json_copy(pkg)
    tampered_pkg["payload"]["subjects"][0]["name"] = "Tampered Subject Name"

    with pytest.raises(ValueError, match="integrity check failed"):
        CurriculumPackageService.import_package(db_session, tampered_pkg)


def test_import_package_idempotent_installation(package_curriculum_fixture, db_session):
    """Verifies successful package import installs curriculum data idempotently."""
    pkg = CurriculumPackageService.export_package(db_session, grade=10)

    # Re-import identical package
    result = CurriculumPackageService.import_package(db_session, pkg)

    assert result["status"] == "SUCCESS"
    assert result["checksum_verified"] is True
    assert result["standard_grade"] == 10


def test_api_export_and_import_endpoints(package_curriculum_fixture, client):
    """Verifies FastAPI REST endpoints for package distribution over LAN."""
    # 1. Export package
    export_resp = client.get("/api/v1/curriculum/package/export?grade=10")
    assert export_resp.status_code == 200
    pkg_data = export_resp.json()

    assert "manifest" in pkg_data
    assert "payload" in pkg_data
    assert pkg_data["manifest"]["checksum"]

    # 2. Import package
    import_resp = client.post("/api/v1/curriculum/package/import", json=pkg_data)
    assert import_resp.status_code == 200
    import_result = import_resp.json()

    assert import_result["status"] == "SUCCESS"
    assert import_result["checksum_verified"] is True


def json_copy(data):
    import json
    return json.loads(json.dumps(data))
