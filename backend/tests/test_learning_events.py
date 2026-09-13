from datetime import datetime, timezone
from backend.app.models.learning_event import LearningEvent, EventType
from backend.app.models.performance import TopicPerformance
from backend.app.services.event_recorder import EventRecorderService


def test_learning_event_recording_and_evidence_aggregation(db_session, seed_data):
    student = seed_data["student_profile"]
    topic = seed_data["topic"]

    # 1. Log a LEARN event
    event1 = EventRecorderService.record_event(
        db=db_session,
        student_id=student.id,
        topic_id=topic.id,
        event_type=EventType.LEARN,
        auto_commit=True,
    )
    assert event1.id is not None
    assert event1.event_type == EventType.LEARN

    # Check initial TopicPerformance
    perf = db_session.query(TopicPerformance).filter_by(student_id=student.id, topic_id=topic.id).first()
    assert perf is not None
    assert perf.total_attempts == 0
    assert perf.accuracy == 0.0

    # 2. Log 3 correct MCQ attempts
    for i in range(3):
        EventRecorderService.record_event(
            db=db_session,
            student_id=student.id,
            topic_id=topic.id,
            event_type=EventType.MCQ_ATTEMPT,
            correctness=True,
            response_time_ms=12000,
            hint_used=False,
            auto_commit=True,
        )

    db_session.refresh(perf)
    assert perf.total_attempts == 3
    assert perf.correct_attempts == 3
    assert perf.accuracy == 100.0
    assert perf.average_response_time == 12000.0
    assert perf.mastery_state == "PRACTICING"

    # 3. Log 2 incorrect MCQ attempts with hints
    for i in range(2):
        EventRecorderService.record_event(
            db=db_session,
            student_id=student.id,
            topic_id=topic.id,
            event_type=EventType.MCQ_ATTEMPT,
            correctness=False,
            response_time_ms=18000,
            hint_used=True,
            auto_commit=True,
        )

    db_session.refresh(perf)
    assert perf.total_attempts == 5
    assert perf.correct_attempts == 3
    assert perf.accuracy == 60.0
    assert perf.hint_usage_count == 2
    assert perf.mastery_state == "PRACTICING"

    # Verify all 6 events are preserved immutably
    events = db_session.query(LearningEvent).filter_by(student_id=student.id, topic_id=topic.id).all()
    assert len(events) == 6
