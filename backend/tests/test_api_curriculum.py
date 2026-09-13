def test_curriculum_endpoints(client, seed_data):
    standard = seed_data["standard"]
    subject = seed_data["subject"]
    chapter = seed_data["chapter"]
    topic = seed_data["topic"]

    # 1. Standards
    res = client.get("/api/v1/standards")
    assert res.status_code == 200
    data = res.json()
    assert len(data) >= 1
    assert data[0]["grade_number"] == 10

    # 2. Subjects by Standard
    res = client.get(f"/api/v1/standards/{standard.id}/subjects")
    assert res.status_code == 200
    subjects = res.json()
    assert len(subjects) == 1
    assert subjects[0]["code"] == "SCI-10"

    # 3. Chapters by Subject
    res = client.get(f"/api/v1/subjects/{subject.id}/chapters")
    assert res.status_code == 200
    chapters = res.json()
    assert len(chapters) == 1
    assert chapters[0]["chapter_number"] == 1

    # 4. Topics by Chapter
    res = client.get(f"/api/v1/chapters/{chapter.id}/topics")
    assert res.status_code == 200
    topics = res.json()
    assert len(topics) == 1
    assert topics[0]["title"] == "Types of Chemical Reactions"

    # 5. Get Topic by ID
    res = client.get(f"/api/v1/topics/{topic.id}")
    assert res.status_code == 200
    assert res.json()["id"] == topic.id

    # 6. Negative test: invalid standard ID
    res = client.get("/api/v1/standards/invalid-uuid/subjects")
    assert res.status_code == 404
    assert res.json()["success"] is False


def test_create_standard_and_subject(client):
    # Create Standard 11
    res = client.post("/api/v1/standards", json={
        "grade_number": 11,
        "name": "Standard 11",
        "description": "GSEB Higher Secondary Class 11",
        "is_active": True
    })
    assert res.status_code == 201
    std_id = res.json()["id"]

    # Create Physics Subject
    res = client.post("/api/v1/subjects", json={
        "standard_id": std_id,
        "name": "Physics",
        "code": "PHY-11",
        "description": "GSEB Standard 11 Physics",
        "is_active": True
    })
    assert res.status_code == 201
    assert res.json()["code"] == "PHY-11"
