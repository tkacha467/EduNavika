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


def test_formative_practice_telemetry_flow(client, seed_data, db_session):
    student = seed_data["student_profile"]
    topic = seed_data["topic"]

    # Practice question telemetry without assessment_id (as sent from frontend QuizRunner)
    payload = {
        "student_id": student.id,
        "mcq_id": "mcq-real-numbers-1",
        "topic_id": topic.id,
        "selected_option": "A",
        "is_correct": False,
        "score": 0,
        "response_time_ms": 1600,
        "hint_requested": False,
    }

    res = client.post("/api/v1/attempts", json=payload)
    assert res.status_code == 201
    data = res.json()
    assert data["student_id"] == student.id
    assert data["selected_option"] == "A"
    assert data["is_correct"] is False
    assert data["score"] == 0.0
    assert data["status"] == "SUBMITTED"
    assert data["id"] is not None

    # Verify auto-provisioning when user_id is passed instead of student_profile_id
    user = seed_data["student_user"]
    payload_with_user_id = {
        "student_id": user.id,
        "mcq_id": "mcq-real-numbers-2",
        "topic_id": topic.id,
        "selected_option": "B",
        "is_correct": True,
        "score": 100,
        "response_time_ms": 2100,
        "hint_requested": False,
    }
    res2 = client.post("/api/v1/attempts", json=payload_with_user_id)
    assert res2.status_code == 201
    data2 = res2.json()
    assert data2["is_correct"] is True
    assert data2["score"] == 100.0

