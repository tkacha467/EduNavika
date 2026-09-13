def test_assessment_and_student_attempt_flow(client, seed_data):
    teacher = seed_data["teacher_profile"]
    student = seed_data["student_profile"]
    topic = seed_data["topic"]

    # 1. Create a question
    mcq_res = client.post("/api/v1/mcqs", json={
        "topic_id": topic.id,
        "question_text": "What is formed when hydrogen burns in oxygen?",
        "option_a": "Water",
        "option_b": "Hydrogen peroxide",
        "option_c": "Ozone",
        "option_d": "Hydroxide",
        "correct_option": "A",
        "difficulty": "EASY",
        "status": "APPROVED",
    })
    assert mcq_res.status_code == 201
    q_id = mcq_res.json()["id"]

    # 2. Teacher creates assessment
    assessment_res = client.post("/api/v1/assessments", json={
        "teacher_id": teacher.id,
        "title": "Topic 1 Chemical Reactions Quiz",
        "topic_id": topic.id,
        "questions": [
            {"question_id": q_id, "question_order": 1, "points": 5.0}
        ]
    })
    assert assessment_res.status_code == 201
    assessment_id = assessment_res.json()["id"]

    # 3. Publish assessment
    pub_res = client.post(f"/api/v1/assessments/{assessment_id}/publish")
    assert pub_res.status_code == 200
    assert pub_res.json()["status"] == "PUBLISHED"

    # 4. Student starts attempt
    att_res = client.post("/api/v1/attempts", json={
        "student_id": student.id,
        "assessment_id": assessment_id,
    })
    assert att_res.status_code == 201
    attempt_id = att_res.json()["id"]
    assert att_res.json()["status"] == "STARTED"

    # 5. Student submits answer (correct option A)
    ans_res = client.post(f"/api/v1/attempts/{attempt_id}/answers", json={
        "question_id": q_id,
        "selected_option": "A",
        "response_time_ms": 15400,
        "hint_used": False,
    })
    assert ans_res.status_code == 201
    assert ans_res.json()["is_correct"] is True
    assert ans_res.json()["response_time_ms"] == 15400

    # 6. Finalize attempt
    submit_res = client.post(f"/api/v1/attempts/{attempt_id}/submit")
    assert submit_res.status_code == 200
    submit_data = submit_res.json()
    assert submit_data["status"] == "SUBMITTED"
    assert submit_data["total_score"] == 5.0
    assert submit_data["percentage"] == 100.0
    assert submit_data["submitted_at"] is not None
