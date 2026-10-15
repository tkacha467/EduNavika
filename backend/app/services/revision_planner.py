import logging
from datetime import datetime, timezone, timedelta
from typing import List, Optional, Dict, Any, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import desc

from backend.app.models import (
    StudentProfile,
    Topic,
    Chapter,
    Subject,
    LearningEvent,
    TopicPerformance,
    RevisionPlan,
)
from backend.app.domain.enums import (
    MasteryLevel,
    PerformanceTrend,
    RetentionRiskLevel,
    RevisionPriority,
    RevisionCompletionState,
)
from backend.app.schemas.knowledge_profile import TopicKnowledgeProfile
from backend.app.schemas.revision_plan import RevisionPlanItem, RevisionPlanResponse
from backend.app.services.knowledge_model import KnowledgeModelService
from backend.app.services.recommendation_engine import RecommendationEngineService
from backend.app.services.curriculum_question_bank import (
    CANONICAL_CURRICULUM_BANK,
    get_canonical_questions_for_topic,
)
from backend.app.services.curriculum_translations import (
    localize_subject_name,
    localize_revision_reason,
)

logger = logging.getLogger("revision_planner")

PRIORITY_WEIGHT: Dict[RevisionPriority, int] = {
    RevisionPriority.URGENT: 4,
    RevisionPriority.HIGH: 3,
    RevisionPriority.MEDIUM: 2,
    RevisionPriority.LOW: 1,
}


class RevisionPlannerService:
    """
    Automated, Personalized Revision Planning Engine for EduNavika.
    
    Synthesizes empirical student knowledge profiles, retention decay signals,
    longitudinal performance trends, and error recency to deterministically determine:
    - WHAT to revise (eligible curriculum topics with pending need)
    - WHY to revise (explainable pedagogical rationale)
    - WHEN to revise (deterministic spaced repetition intervals: Today, 1-2d, 3-5d, 7-14d)
    
    Invariants:
    - 100% offline execution with zero cloud calendar/API dependencies.
    - Completely language-agnostic scheduling (en, hi, gu produce identical topics,
      dates, priorities, and mastery decisions).
    - Idempotent synchronization with database RevisionPlan records.
    """

    @classmethod
    def get_provenance_for_topic(cls, topic: Topic) -> Tuple[Optional[str], Optional[int]]:
        """Extracts official textbook document and page provenance for a topic."""
        # 1. Check canonical curriculum bank
        canonical_items = get_canonical_questions_for_topic(topic.id)
        if not canonical_items:
            norm_title = topic.title.lower().replace('&', 'and').replace('—', '-').strip()
            for tid, qlist in CANONICAL_CURRICULUM_BANK.items():
                if qlist:
                    cand_title = qlist[0]["topic_title"].lower().replace('&', 'and').replace('—', '-').strip()
                    cand_chap = qlist[0]["chapter"].lower().replace('&', 'and').replace('—', '-').strip()
                    if norm_title in cand_title or cand_title in norm_title or norm_title in cand_chap or cand_chap in norm_title:
                        canonical_items = qlist
                        break

        if canonical_items:
            top_q = canonical_items[0]
            return top_q.get("source_document"), top_q.get("source_page")

        # 2. Default subject-based textbook mapping for Standard 10 GSEB
        subj_name = (topic.chapter.subject.name if topic.chapter and topic.chapter.subject else "").lower()
        if "math" in subj_name:
            return "STD-10/Std-10_Mathematics_English Medium.pdf", 14
        return "STD-10/Std-10_Science_English Medium.pdf", 16

    @classmethod
    def get_personalized_revision_plan(
        cls,
        db: Session,
        student_id: str,
        subject_id: Optional[str] = None,
        language: Optional[str] = "en",
        now: Optional[datetime] = None,
    ) -> RevisionPlanResponse:
        """Alias for get_or_create_revision_plan."""
        return cls.get_or_create_revision_plan(db, student_id, subject_id, language, now)

    @classmethod
    def get_or_create_revision_plan(
        cls,
        db: Session,
        student_id: str,
        subject_id: Optional[str] = None,
        language: Optional[str] = "en",
        now: Optional[datetime] = None,
    ) -> RevisionPlanResponse:
        """
        Computes and retrieves the complete, personalized revision plan for a student.
        """
        from backend.app.services.topic_resolver import get_or_create_student_profile

        student = get_or_create_student_profile(db, student_id)
        if not student:
            raise ValueError(f"Student profile '{student_id}' not found.")
        target_student_id = student.id

        target_lang = language or student.preferred_language or "en"
        current_time = now or datetime.now(timezone.utc)
        today_date_str = current_time.strftime("%Y-%m-%d")

        # 1. Fetch student's knowledge profile across active topics
        profile_response = KnowledgeModelService.get_student_knowledge_profiles(db, target_student_id)
        raw_profiles = profile_response.profiles

        # Filter profiles for curriculum eligibility
        active_profiles: List[TopicKnowledgeProfile] = []
        for prof in raw_profiles:
            topic_record = db.query(Topic).filter(Topic.id == prof.topic_id).first()
            if topic_record and RecommendationEngineService.is_eligible_curriculum_topic(db, student, topic_record):
                # Apply subject filter if specified
                if subject_id and subject_id.strip().lower() != "all":
                    t_subj_id = topic_record.chapter.subject_id if topic_record.chapter else None
                    if t_subj_id != subject_id and (topic_record.chapter and topic_record.chapter.subject.code != subject_id):
                        continue
                active_profiles.append(prof)

        # 2. Fetch student's active pending revision plans from database
        pending_plans = (
            db.query(RevisionPlan)
            .filter(
                RevisionPlan.student_id == target_student_id,
                RevisionPlan.completion_state == RevisionCompletionState.PENDING,
            )
            .all()
        )
        plan_by_topic: Dict[str, RevisionPlan] = {}
        for p in pending_plans:
            t = db.query(Topic).filter(Topic.id == p.topic_id).first()
            if t and RecommendationEngineService.is_eligible_curriculum_topic(db, student, t):
                plan_by_topic[p.topic_id] = p

        # 3. Handle Edge Case: Student with zero activity
        if not active_profiles and not plan_by_topic:
            return RevisionPlanResponse(
                student_id=student_id,
                generated_at=current_time,
                total_revisions=0,
                due_today_count=0,
                due_this_week_count=0,
                upcoming_count=0,
                urgent_count=0,
                high_count=0,
                medium_count=0,
                low_count=0,
                revisions=[],
            )

        # 4. Synthesize topics to schedule
        profile_map: Dict[str, TopicKnowledgeProfile] = {p.topic_id: p for p in active_profiles}
        for topic_id, plan in plan_by_topic.items():
            if topic_id not in profile_map:
                topic_record = db.query(Topic).filter(Topic.id == topic_id).first()
                if topic_record and RecommendationEngineService.is_eligible_curriculum_topic(db, student, topic_record):
                    profile_map[topic_id] = KnowledgeModelService.calculate_topic_profile(
                        db, target_student_id, topic_record
                    )

        revision_items: List[RevisionPlanItem] = []

        # 5. Evaluate each topic deterministically through the Spaced Repetition Scheduling Matrix
        for topic_id, prof in profile_map.items():
            # Skip topics with 0 attempts unless there is a pending plan
            existing_plan = plan_by_topic.get(topic_id)
            if prof.total_attempts == 0 and not existing_plan:
                continue

            topic_record = db.query(Topic).filter(Topic.id == topic_id).first()
            if not topic_record:
                continue

            # Provenance
            src_doc, src_page = cls.get_provenance_for_topic(topic_record)

            # Performance record for revision count and elapsed days
            perf = (
                db.query(TopicPerformance)
                .filter(TopicPerformance.student_id == target_student_id, TopicPerformance.topic_id == topic_id)
                .first()
            )
            rev_count = perf.revision_count if perf else 0
            last_activity = perf.last_activity_at if perf and perf.last_activity_at else current_time
            if last_activity.tzinfo is None:
                last_activity = last_activity.replace(tzinfo=timezone.utc)
            elapsed_days = max(0, (current_time - last_activity).days)

            # Evaluate Priority & Spaced Interval Offset
            priority, offset_days, action, diff = cls._determine_priority_and_spacing(
                prof=prof,
                existing_plan=existing_plan,
                elapsed_days=elapsed_days,
                rev_count=rev_count,
            )

            # Calculate recommended revision timestamp
            recommended_at = current_time + timedelta(days=offset_days)

            # Synchronize with database RevisionPlan (idempotent)
            db_plan = existing_plan
            if not db_plan and priority in (RevisionPriority.URGENT, RevisionPriority.HIGH, RevisionPriority.MEDIUM):
                db_plan = RevisionPlan(
                    student_id=target_student_id,
                    topic_id=topic_id,
                    recommended_revision_at=recommended_at,
                    priority=priority,
                    reason=f"Automated revision scheduled for {topic_record.title}.",
                    completion_state=RevisionCompletionState.PENDING,
                )
                db.add(db_plan)
                db.flush()
            elif db_plan:
                # Update existing plan with dynamic empirical priority and spacing
                db_plan.priority = priority
                db_plan.recommended_revision_at = recommended_at

            # Calculate deadline indicators
            sched_date_str = recommended_at.strftime("%Y-%m-%d")
            diff_days = (recommended_at.date() - current_time.date()).days
            is_due_today = (diff_days <= 0)
            is_overdue = (recommended_at < current_time and not is_due_today)

            if is_due_today:
                urgency_tier = "TODAY"
            elif diff_days < 7:
                urgency_tier = "THIS_WEEK"
            else:
                urgency_tier = "UPCOMING"

            # Explainable localized reason
            reason_text = localize_revision_reason(
                priority=priority.value,
                topic_title=topic_record.title,
                mastery=prof.mastery_level.value,
                risk=prof.retention_risk.value,
                source_page=src_page,
                lang=target_lang,
            )

            # Localized subject name
            subj_disp = localize_subject_name(prof.subject_name, target_lang)

            item = RevisionPlanItem(
                plan_id=db_plan.id if db_plan else None,
                topic_id=topic_id,
                topic_title=topic_record.title,
                subject_id=topic_record.chapter.subject_id if topic_record.chapter else None,
                subject_name=subj_disp,
                chapter_id=topic_record.chapter_id,
                chapter_title=topic_record.chapter.title if topic_record.chapter else None,
                mastery_level=prof.mastery_level,
                accuracy=prof.accuracy,
                recent_accuracy=prof.recent_accuracy,
                retention_risk=prof.retention_risk,
                priority=priority,
                scheduled_date=sched_date_str,
                recommended_revision_at=recommended_at,
                days_until_due=max(0, diff_days),
                is_due_today=is_due_today,
                is_overdue=is_overdue,
                urgency_tier=urgency_tier,
                reason=reason_text,
                recommended_action=action,
                recommended_difficulty=diff,
                source_document=src_doc,
                source_page=src_page,
            )
            revision_items.append(item)

        db.commit()

        # 6. Sort deterministically:
        # Priority descending (URGENT > HIGH > MEDIUM > LOW), then days_until_due ascending, then accuracy ascending
        revision_items.sort(
            key=lambda x: (
                -PRIORITY_WEIGHT.get(x.priority, 1),
                x.days_until_due,
                x.accuracy,
            )
        )

        # 7. Aggregation counts
        due_today = sum(1 for x in revision_items if x.is_due_today)
        due_this_week = sum(1 for x in revision_items if x.urgency_tier == "THIS_WEEK")
        upcoming = sum(1 for x in revision_items if x.urgency_tier == "UPCOMING")
        urg_cnt = sum(1 for x in revision_items if x.priority == RevisionPriority.URGENT)
        high_cnt = sum(1 for x in revision_items if x.priority == RevisionPriority.HIGH)
        med_cnt = sum(1 for x in revision_items if x.priority == RevisionPriority.MEDIUM)
        low_cnt = sum(1 for x in revision_items if x.priority == RevisionPriority.LOW)

        return RevisionPlanResponse(
            student_id=student_id,
            generated_at=current_time,
            total_revisions=len(revision_items),
            due_today_count=due_today,
            due_this_week_count=due_this_week,
            upcoming_count=upcoming,
            urgent_count=urg_cnt,
            high_count=high_cnt,
            medium_count=med_cnt,
            low_count=low_cnt,
            revisions=revision_items,
        )

    @classmethod
    def _determine_priority_and_spacing(
        cls,
        prof: TopicKnowledgeProfile,
        existing_plan: Optional[RevisionPlan],
        elapsed_days: int,
        rev_count: int,
    ) -> Tuple[RevisionPriority, int, str, str]:
        """
        Deterministic Rule-Based Spaced Repetition Scheduling Policy:
        Synthesizes mastery tier, retention risk, accuracy, recency, and trend.
        
        Returns: (priority, offset_days, action, difficulty)
        """
        eff_acc = prof.recent_accuracy if prof.recent_accuracy is not None else prof.accuracy
        mastery = prof.mastery_level
        risk = prof.retention_risk
        trend = prof.trend

        # Tier 1: URGENT (Due Today / 0-day offset)
        # Conditions:
        # - High retention risk on a weak/novice topic (imminent severe forgetting)
        # - Extremely low accuracy (<= 30%)
        # - Declining trend with poor recent accuracy (< 40%)
        # - Existing plan explicitly marked URGENT
        if (
            (risk == RetentionRiskLevel.HIGH and (mastery in (MasteryLevel.UNASSESSED, MasteryLevel.NOVICE) or eff_acc < 50.0))
            or (eff_acc <= 30.0 and prof.total_attempts > 0)
            or (trend == PerformanceTrend.DECLINING and eff_acc < 40.0)
        ):
            return RevisionPriority.URGENT, 0, "FOUNDATIONAL_PRACTICE", "FOUNDATIONAL"

        # Tier 2: HIGH (Due in 1-2 days)
        # Conditions:
        # - High retention risk on developing topic
        # - Moderate retention risk on novice topic
        # - Novice mastery (< 50% accuracy)
        # - Declining trend
        if (
            (risk == RetentionRiskLevel.HIGH)
            or (risk == RetentionRiskLevel.MODERATE and eff_acc < 50.0)
            or (mastery == MasteryLevel.NOVICE)
            or (trend == PerformanceTrend.DECLINING)
        ):
            offset = 1 if elapsed_days >= 2 else 2
            return RevisionPriority.HIGH, offset, "GUIDED_PRACTICE", "GUIDED"

        # Tier 3: MEDIUM (Due in 3-5 days)
        # Conditions:
        # - Developing mastery (50% - 70% accuracy)
        # - Moderate retention risk on proficient topic
        # - Normal progressive spaced review step
        if (
            (mastery == MasteryLevel.DEVELOPING)
            or (risk == RetentionRiskLevel.MODERATE)
            or (eff_acc < 70.0)
        ):
            # Progressive spacing: step 1 = 3d, step 2 = 4d, step 3+ = 5d
            offset = min(3 + rev_count, 5)
            return RevisionPriority.MEDIUM, offset, "APPLICATION_PRACTICE", "APPLICATION"

        # Tier 4: LOW (Due in 7-14 days / Spaced Maintenance)
        # Conditions:
        # - Proficient or Mastered topics with Low retention risk and >= 70% accuracy
        offset = 7 if rev_count <= 2 else 14
        return RevisionPriority.LOW, offset, "CHALLENGE_PRACTICE", "CHALLENGE"


revision_planner_service = RevisionPlannerService()
