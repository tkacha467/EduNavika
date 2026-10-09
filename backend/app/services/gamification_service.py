import logging
from datetime import datetime, timezone, timedelta
from typing import List, Optional, Dict, Any, Set, Tuple
from sqlalchemy.orm import Session

from backend.app.models import (
    StudentProfile,
    LearningEvent,
    TopicPerformance,
    Topic,
    RevisionPlan,
    RevisionCompletionState,
    EventType,
)
from backend.app.domain.enums import MasteryLevel
from backend.app.schemas.gamification import (
    GamificationResponse,
    DailyGoalSummary,
    BadgeItem,
)
from backend.app.services.curriculum_translations import (
    localize_level_title,
    localize_badge,
)

logger = logging.getLogger("gamification_service")

DAILY_GOAL_TARGET = 5

XP_RULES = {
    "PRACTICE_COMPLETION": 10,
    "CORRECT_ANSWER": 5,
    "REVISION_COMPLETION": 15,
    "WEAK_TOPIC_IMPROVEMENT": 20,
    "DAILY_GOAL_ACHIEVED": 25,
    "CONCEPTUAL_REVIEW": 5,
}

LEVEL_THRESHOLDS: List[Tuple[int, int, int]] = [
    # (level, min_xp, max_xp)
    (1, 0, 99),
    (2, 100, 249),
    (3, 250, 499),
    (4, 500, 999),
    (5, 1000, 9999999),
]


class GamificationService:
    """
    Deterministic Educational Gamification Engine for EduNavika.
    
    100% On-device, local execution.
    Synthesizes empirical LearningEvents, knowledge models, and longitudinal streaks
    into lightweight, motivating achievements and XP progression.
    """

    @classmethod
    def get_student_gamification(
        cls,
        db: Session,
        student_id: str,
        language: Optional[str] = "en",
        now: Optional[datetime] = None,
    ) -> GamificationResponse:
        from backend.app.api.v1.endpoints.attempts import _get_or_create_student_profile

        student = _get_or_create_student_profile(db, student_id)
        if not student:
            raise ValueError(f"Student profile '{student_id}' not found.")

        current_time = now or datetime.now(timezone.utc)
        if current_time.tzinfo is None:
            current_time = current_time.replace(tzinfo=timezone.utc)
        today_str = current_time.strftime("%Y-%m-%d")
        target_lang = (language or student.preferred_language or "en").lower()

        # 1. Fetch all student learning events ordered chronologically
        events = (
            db.query(LearningEvent)
            .filter(LearningEvent.student_id == student.id)
            .order_by(LearningEvent.timestamp.asc())
            .all()
        )

        # 2. XP & Meaningful Event Tracking
        total_xp = 0
        meaningful_events: List[LearningEvent] = []
        practice_count = 0
        revision_count = 0
        events_by_date: Dict[str, List[LearningEvent]] = {}
        events_by_topic: Dict[str, List[LearningEvent]] = {}

        for ev in events:
            # Normalize timestamp to UTC date
            ts = ev.timestamp
            if ts.tzinfo is None:
                ts = ts.replace(tzinfo=timezone.utc)
            date_str = ts.strftime("%Y-%m-%d")

            events_by_date.setdefault(date_str, []).append(ev)
            events_by_topic.setdefault(ev.topic_id, []).append(ev)

            # Evaluative & Practice Activities
            if ev.event_type in (EventType.PRACTICE, EventType.MCQ_ATTEMPT):
                meaningful_events.append(ev)
                practice_count += 1
                total_xp += XP_RULES["PRACTICE_COMPLETION"]
                if ev.correctness is True:
                    total_xp += XP_RULES["CORRECT_ANSWER"]

            elif ev.event_type == EventType.REVISION:
                meaningful_events.append(ev)
                revision_count += 1
                total_xp += XP_RULES["REVISION_COMPLETION"]
                if ev.correctness is True:
                    total_xp += XP_RULES["CORRECT_ANSWER"]

            elif ev.event_type in (EventType.LEARN, EventType.REVIEW):
                total_xp += XP_RULES["CONCEPTUAL_REVIEW"]

        # Check revision count from completed database RevisionPlans as well
        completed_plans = (
            db.query(RevisionPlan)
            .filter(
                RevisionPlan.student_id == student.id,
                RevisionPlan.completion_state == RevisionCompletionState.COMPLETED,
            )
            .count()
        )
        effective_revision_count = max(revision_count, completed_plans)

        # 3. Detect Weak Topic Improvements (+20 XP each)
        improved_weak_topics: Set[str] = set()
        for topic_id, topic_evs in events_by_topic.items():
            eval_evs = [e for e in topic_evs if e.correctness is not None]
            if len(eval_evs) >= 2:
                # Early phase: first 1-3 attempts
                early_slice = eval_evs[:min(3, len(eval_evs) // 2 or 1)]
                early_correct = sum(1 for e in early_slice if e.correctness is True)
                early_acc = (early_correct / len(early_slice)) * 100.0

                # Recent phase: last attempts
                recent_slice = eval_evs[len(early_slice):]
                if recent_slice:
                    recent_correct = sum(1 for e in recent_slice if e.correctness is True)
                    recent_acc = (recent_correct / len(recent_slice)) * 100.0
                    # Improved if early accuracy < 50% and recent accuracy >= 60%
                    if early_acc < 50.0 and recent_acc >= 60.0:
                        improved_weak_topics.add(topic_id)

        # Also check TopicPerformance records for topics that overcame weakness
        topic_perfs = (
            db.query(TopicPerformance)
            .filter(TopicPerformance.student_id == student.id)
            .all()
        )
        for tp in topic_perfs:
            if tp.total_attempts >= 3 and tp.correct_attempts < tp.total_attempts:
                if tp.accuracy >= 60.0 and tp.topic_id not in improved_weak_topics:
                    # Student had mistakes but reached >= 60% accuracy
                    improved_weak_topics.add(tp.topic_id)

        total_xp += len(improved_weak_topics) * XP_RULES["WEAK_TOPIC_IMPROVEMENT"]

        # 4. Daily Learning Goal & Goal Completion Bonus (+25 XP per day)
        daily_goals_achieved = 0
        for date_str, dev_list in events_by_date.items():
            meaningful_on_date = sum(
                1 for e in dev_list if e.event_type in (EventType.PRACTICE, EventType.REVISION, EventType.MCQ_ATTEMPT)
            )
            if meaningful_on_date >= DAILY_GOAL_TARGET:
                daily_goals_achieved += 1

        total_xp += daily_goals_achieved * XP_RULES["DAILY_GOAL_ACHIEVED"]

        # Today's daily goal status
        today_meaningful = sum(
            1 for e in events_by_date.get(today_str, [])
            if e.event_type in (EventType.PRACTICE, EventType.REVISION, EventType.MCQ_ATTEMPT)
        )
        today_goal_completed = (today_meaningful >= DAILY_GOAL_TARGET)
        today_goal_pct = min(100.0, round((today_meaningful / DAILY_GOAL_TARGET) * 100.0, 1))

        daily_goal_summary = DailyGoalSummary(
            target=DAILY_GOAL_TARGET,
            completed=today_meaningful,
            percentage=today_goal_pct,
            is_completed=today_goal_completed,
        )

        # 5. Level Calculation (Deterministic)
        level = 1
        xp_towards = total_xp
        xp_required = 100
        level_pct = 0.0

        if total_xp < 100:
            level = 1
            xp_towards = total_xp
            xp_required = 100
            level_pct = round((xp_towards / xp_required) * 100.0, 1)
        elif total_xp < 250:
            level = 2
            xp_towards = total_xp - 100
            xp_required = 150
            level_pct = round((xp_towards / xp_required) * 100.0, 1)
        elif total_xp < 500:
            level = 3
            xp_towards = total_xp - 250
            xp_required = 250
            level_pct = round((xp_towards / xp_required) * 100.0, 1)
        elif total_xp < 1000:
            level = 4
            xp_towards = total_xp - 500
            xp_required = 500
            level_pct = round((xp_towards / xp_required) * 100.0, 1)
        else:
            level = 5
            xp_towards = total_xp - 1000
            xp_required = 0
            level_pct = 100.0

        level_title = localize_level_title(level, target_lang)

        # 6. Learning Streak Calculation
        # Only meaningful practice/revision activities count towards streaks
        meaningful_dates = sorted({
            e.timestamp.replace(tzinfo=timezone.utc).strftime("%Y-%m-%d")
            for e in meaningful_events
        })

        longest_streak = 0
        current_streak = 0
        last_learning_date = meaningful_dates[-1] if meaningful_dates else None
        streak_active_today = (last_learning_date == today_str)

        if meaningful_dates:
            # Parse dates into datetime.date objects
            date_objs = sorted([datetime.strptime(d, "%Y-%m-%d").date() for d in meaningful_dates])

            # Calculate longest streak
            current_run = 1
            longest_streak = 1
            for i in range(1, len(date_objs)):
                if date_objs[i] == date_objs[i - 1] + timedelta(days=1):
                    current_run += 1
                elif date_objs[i] > date_objs[i - 1] + timedelta(days=1):
                    current_run = 1
                if current_run > longest_streak:
                    longest_streak = current_run

            # Calculate current streak ending today or yesterday
            today_date = current_time.date()
            yesterday_date = today_date - timedelta(days=1)
            latest_active_date = date_objs[-1]

            if latest_active_date in (today_date, yesterday_date):
                cur_run = 1
                cursor = latest_active_date
                idx = len(date_objs) - 1
                while idx > 0 and date_objs[idx - 1] == cursor - timedelta(days=1):
                    cur_run += 1
                    cursor = date_objs[idx - 1]
                    idx -= 1
                current_streak = cur_run
            else:
                current_streak = 0

        # Synchronize streak on student profile if attribute exists
        if hasattr(student, "learning_streak_days") and student.learning_streak_days != current_streak:
            student.learning_streak_days = current_streak
            db.flush()

        # 7. Badges Evaluation
        # Check Mastered topics
        mastered_count = sum(1 for tp in topic_perfs if tp.mastery_state == "MASTERED" or tp.accuracy >= 85.0 and tp.total_attempts >= 5)

        total_meaningful_count = len(meaningful_events)

        badge_definitions: List[Dict[str, Any]] = [
            {
                "id": "FIRST_STEP",
                "progress": min(1, practice_count),
                "target": 1,
                "unlocked": practice_count >= 1,
                "unlocked_at": meaningful_events[0].timestamp.isoformat() if meaningful_events else None,
            },
            {
                "id": "THREE_DAY_LEARNER",
                "progress": min(3, max(current_streak, longest_streak)),
                "target": 3,
                "unlocked": max(current_streak, longest_streak) >= 3,
                "unlocked_at": current_time.isoformat() if max(current_streak, longest_streak) >= 3 else None,
            },
            {
                "id": "WEAKNESS_CRUSHER",
                "progress": min(1, len(improved_weak_topics)),
                "target": 1,
                "unlocked": len(improved_weak_topics) >= 1,
                "unlocked_at": current_time.isoformat() if len(improved_weak_topics) >= 1 else None,
            },
            {
                "id": "REVISION_CHAMPION",
                "progress": min(1, effective_revision_count),
                "target": 1,
                "unlocked": effective_revision_count >= 1,
                "unlocked_at": current_time.isoformat() if effective_revision_count >= 1 else None,
            },
            {
                "id": "TOPIC_MASTER",
                "progress": min(1, mastered_count),
                "target": 1,
                "unlocked": mastered_count >= 1,
                "unlocked_at": current_time.isoformat() if mastered_count >= 1 else None,
            },
            {
                "id": "CONSISTENT_LEARNER",
                "progress": min(10, total_meaningful_count),
                "target": 10,
                "unlocked": total_meaningful_count >= 10,
                "unlocked_at": current_time.isoformat() if total_meaningful_count >= 10 else None,
            },
        ]

        unlocked_badges: List[BadgeItem] = []
        locked_badges: List[BadgeItem] = []

        for b in badge_definitions:
            name, desc, icon = localize_badge(b["id"], target_lang)
            item = BadgeItem(
                badge_id=b["id"],
                name=name,
                description=desc,
                icon=icon,
                is_unlocked=b["unlocked"],
                unlocked_at=b["unlocked_at"] if b["unlocked"] else None,
                progress=b["progress"],
                target=b["target"],
            )
            if item.is_unlocked:
                unlocked_badges.append(item)
            else:
                locked_badges.append(item)

        recently_earned = list(unlocked_badges)

        return GamificationResponse(
            student_id=student.id,
            total_xp=total_xp,
            level=level,
            level_title=level_title,
            xp_towards_next_level=xp_towards,
            xp_required_for_next_level=xp_required,
            level_progress_percentage=level_pct,
            current_streak=current_streak,
            longest_streak=longest_streak,
            last_learning_date=last_learning_date,
            streak_active_today=streak_active_today,
            daily_goal=daily_goal_summary,
            unlocked_badges=unlocked_badges,
            locked_badges=locked_badges,
            recently_earned_badges=recently_earned,
        )


gamification_service = GamificationService()
