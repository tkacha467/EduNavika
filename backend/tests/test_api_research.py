from datetime import datetime, timedelta, timezone


def test_research_endpoints_and_evidence_contracts(client, seed_data):
    teacher = seed_data["teacher_profile"]
    student = seed_data["student_profile"]
    topic = seed_data["topic"]

    # 1. Post LearningEvent directly
    ev_res = client.post("/api/v1/learning-events", json={
        "student_id": student.id,
        "topic_id": topic.id,
        "event_type": "PRACTICE",
        "score": 8.0,
        "correctness": True,
        "response_time_ms": 14200,
        "hint_used": False,
        "attempt_number": 1,
        "event_metadata": {"source": "self_practice_mode"}
    })
    assert ev_res.status_code == 201
    assert ev_res.json()["event_type"] == "PRACTICE"

    # 2. Query longitudinal learning events with pagination
    query_res = client.get(f"/api/v1/students/{student.id}/learning-events?topic_id={topic.id}&page=1&page_size=10")
    assert query_res.status_code == 200
    paged = query_res.json()
    assert paged["metadata"]["total_count"] >= 1
    assert len(paged["items"]) >= 1

    # 3. Query Topic Performance evidence
    perf_res = client.get(f"/api/v1/students/{student.id}/topics/{topic.id}/performance")
    assert perf_res.status_code == 200
    perf_data = perf_res.json()
    assert perf_data["student_id"] == student.id
    assert perf_data["topic_id"] == topic.id
    assert perf_data["practice_count"] >= 1

    # 4. Create and retrieve Revision Plan
    rev_time = (datetime.now(timezone.utc) + timedelta(days=3)).isoformat()
    rev_create = client.post("/api/v1/revision-plans", json={
        "student_id": student.id,
        "topic_id": topic.id,
        "recommended_revision_at": rev_time,
        "priority": "HIGH",
        "reason": "Scheduled spaced repetition review",
    })
    assert rev_create.status_code == 201

    rev_list = client.get(f"/api/v1/students/{student.id}/revision-plan")
    assert rev_list.status_code == 200
    assert len(rev_list.json()) >= 1

    # 5. Create and retrieve empirical Forgetting Signal
    signal_res = client.post("/api/v1/forgetting-signals", json={
        "student_id": student.id,
        "topic_id": topic.id,
        "evidence_type": "ACCURACY_DROP_AFTER_INTERVAL",
        "prior_performance_ref": {"accuracy": 100.0, "sample_size": 5},
        "later_performance_ref": {"accuracy": 20.0, "sample_size": 5},
        "status": "UNRESOLVED",
        "confidence_metadata": {"elapsed_days": 14, "attempt_gap": 10}
    })
    assert signal_res.status_code == 201
    assert signal_res.json()["evidence_type"] == "ACCURACY_DROP_AFTER_INTERVAL"

    signals_list = client.get(f"/api/v1/students/{student.id}/forgetting-signals")
    assert signals_list.status_code == 200
    assert len(signals_list.json()) >= 1

    # 6. Create and retrieve Teacher Action
    act_res = client.post("/api/v1/teacher-actions", json={
        "teacher_id": teacher.id,
        "student_id": student.id,
        "topic_id": topic.id,
        "action_type": "RECOMMEND_REVISION",
        "note": "Advised student to review balancing equations",
    })
    assert act_res.status_code == 201
    assert act_res.json()["action_type"] == "RECOMMEND_REVISION"

    teacher_acts = client.get(f"/api/v1/teachers/{teacher.id}/actions")
    assert teacher_acts.status_code == 200
    assert len(teacher_acts.json()) >= 1
