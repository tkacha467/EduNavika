def test_mcq_lifecycle_and_duplicate_prevention(client, seed_data):
    topic = seed_data["topic"]

    mcq_payload = {
        "topic_id": topic.id,
        "question_text": "What type of reaction is 2Mg + O2 -> 2MgO?",
        "option_a": "Combination Reaction",
        "option_b": "Decomposition Reaction",
        "option_c": "Displacement Reaction",
        "option_d": "Double Displacement Reaction",
        "correct_option": "A",
        "explanation": "Two reactants combine to form a single product magnesium oxide.",
        "difficulty": "EASY",
        "generation_model": "test-generator-v1",
        "generation_version": "1.0.0",
        "status": "DRAFT",
    }

    # 1. Create MCQ
    res = client.post("/api/v1/mcqs", json=mcq_payload)
    assert res.status_code == 201
    data = res.json()
    q_id = data["id"]
    assert data["question_text"] == mcq_payload["question_text"]
    assert data["status"] == "DRAFT"

    # 2. Check exact duplicate detection rejection (409 Conflict)
    dup_payload = dict(mcq_payload)
    dup_payload["question_text"] = "  what type of reaction is 2mg + o2 -> 2mgo?  "
    res_dup = client.post("/api/v1/mcqs", json=dup_payload)
    assert res_dup.status_code == 409
    assert res_dup.json()["success"] is False
    assert "duplicate" in res_dup.json()["error"]["message"].lower()

    # 3. Retrieve by ID
    res_get = client.get(f"/api/v1/mcqs/{q_id}")
    assert res_get.status_code == 200
    assert res_get.json()["id"] == q_id

    # 4. List topic MCQs
    res_list = client.get(f"/api/v1/topics/{topic.id}/mcqs")
    assert res_list.status_code == 200
    assert len(res_list.json()) == 1

    # 5. Patch status to APPROVED
    res_patch = client.patch(f"/api/v1/mcqs/{q_id}/status", json={"status": "APPROVED"})
    assert res_patch.status_code == 200
    assert res_patch.json()["status"] == "APPROVED"
