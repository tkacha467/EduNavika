from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session

from backend.app.models import RevisionPlan, Topic, TopicPerformance, StudentProfile, Chapter, Subject
from backend.app.domain.enums import (
    RecommendationAction,
    RevisionPriority,
    RevisionCompletionState,
    MasteryLevel,
    PerformanceTrend,
    RetentionRiskLevel,
)
from backend.app.schemas.knowledge_profile import TopicKnowledgeProfile
from backend.app.schemas.recommendation import TopicRecommendation, RecommendationResponse
from backend.app.services.knowledge_model import KnowledgeModelService
from backend.app.services.curriculum_translations import (
    localize_subject_name,
    localize_recommendation_reason,
)


class RecommendationEngineService:
    """
    Deterministic Adaptive Recommendation Engine for Next-Step Learning.
    
    Synthesizes active RevisionPlans and the Student Knowledge Profile to calculate
    explainable next-step actions (REVISION, PRACTICE, REVIEW) prioritized by urgency.
    Does not persist recommendations in a table; computes them dynamically on demand.
    """

    @staticmethod
    def is_eligible_curriculum_topic(
        db: Session,
        student: Optional[StudentProfile],
        topic: Topic,
        exam_code: Optional[str] = None,
    ) -> bool:
        """
        Validates whether a topic is an authentic pedagogical curriculum topic eligible
        for adaptive student recommendations.
        
        Eligibility Rules:
        1. Exclude synthetic / placeholder topics (e.g. 'General Content', 'General Curriculum Content').
        2. Standard/grade alignment: If student has an assigned standard, topic must belong to that standard.
        3. Active topic & curriculum check: topic must be active and have a valid chapter hierarchy.
        4. Exam-specific applicability: If exam_code is provided, verify an active association in exam_topics.
        """
        if not topic.is_active:
            return False

        # Rule 1: Exclude placeholder / legacy non-pedagogical topics
        title_clean = (topic.title or "").strip().lower()
        if "general content" in title_clean or "general curriculum" in title_clean:
            return False

        chap_clean = (topic.chapter.title or "").strip().lower() if topic.chapter else ""
        if "general content" in chap_clean or "general curriculum" in chap_clean:
            return False

        # Rule 2: Student standard alignment
        if student and student.standard_id:
            if topic.chapter and topic.chapter.subject:
                if topic.chapter.subject.standard_id != student.standard_id:
                    return False

        # Rule 4: Exam-specific applicability
        if exam_code:
            from backend.app.models.competitive_models import ExamTopic
            has_exam_topics = (
                db.query(ExamTopic.id)
                .filter(ExamTopic.exam_code == exam_code)
                .first()
                is not None
            )
            if has_exam_topics:
                has_link = db.query(ExamTopic).filter(
                    ExamTopic.exam_code == exam_code,
                    ExamTopic.topic_id == topic.id,
                    ExamTopic.inclusion_status == "ACTIVE"
                ).first()
                if not has_link:
                    return False

        return True

    @staticmethod
    def generate_recommendations(
        db: Session,
        student_id: str,
        limit: int = 10,
        language: Optional[str] = "en",
        exam_code: Optional[str] = None,
    ) -> RecommendationResponse:
        """
        Generates deterministic, explainable recommendations for a student.
        Supports English, Hindi, and Gujarati localization while preserving exact score ranking.
        """
        from backend.app.services.topic_resolver import get_or_create_student_profile

        student = get_or_create_student_profile(db, student_id)
        target_student_id = student.id if student else student_id
        target_lang = language or (student.preferred_language if student else "en") or "en"

        # 1. Fetch student's knowledge profile across active topics
        profile_response = KnowledgeModelService.get_student_knowledge_profiles(db, target_student_id)
        raw_profiles = profile_response.profiles

        # Filter profiles for curriculum eligibility
        active_profiles: List[TopicKnowledgeProfile] = []
        for prof in raw_profiles:
            topic_record = db.query(Topic).filter(Topic.id == prof.topic_id).first()
            if topic_record and RecommendationEngineService.is_eligible_curriculum_topic(db, student, topic_record, exam_code=exam_code):
                active_profiles.append(prof)

        # 2. Fetch student's active pending revision plans (filtering for eligible topics)
        all_pending_plans = (
            db.query(RevisionPlan)
            .filter(
                RevisionPlan.student_id == target_student_id,
                RevisionPlan.completion_state == RevisionCompletionState.PENDING,
            )
            .all()
        )
        plan_by_topic: Dict[str, RevisionPlan] = {}
        for p in all_pending_plans:
            t = db.query(Topic).filter(Topic.id == p.topic_id).first()
            if t and RecommendationEngineService.is_eligible_curriculum_topic(db, student, t, exam_code=exam_code):
                plan_by_topic[p.topic_id] = p

        # 3. Handle Edge Case: Student with zero activity or no eligible history
        if not active_profiles and not plan_by_topic:
            # Pick standard/curriculum starter topic if available
            starter_query = (
                db.query(Topic)
                .join(Topic.chapter)
                .join(Chapter.subject)
                .filter(Topic.is_active == True)
            )
            if student and student.standard_id:
                starter_query = starter_query.filter(Subject.standard_id == student.standard_id)

            candidate_starters = starter_query.order_by(Topic.topic_order.asc()).all()
            starter_topic = next(
                (t for t in candidate_starters if RecommendationEngineService.is_eligible_curriculum_topic(db, student, t, exam_code=exam_code)),
                None
            )

            if not starter_topic:
                # General fallback to any topic satisfying eligibility
                all_candidates = db.query(Topic).filter(Topic.is_active == True).order_by(Topic.topic_order.asc()).all()
                starter_topic = next(
                    (t for t in all_candidates if RecommendationEngineService.is_eligible_curriculum_topic(db, student, t, exam_code=exam_code)),
                    None
                )

            if starter_topic:
                subject_name = "Science & Technology"
                if starter_topic.chapter and starter_topic.chapter.subject:
                    subject_name = starter_topic.chapter.subject.name

                onboarding_reason = "Start with an initial diagnostic practice set to establish your knowledge profile."
                if target_lang == "hi":
                    onboarding_reason = "अपना ज्ञान प्रोफाइल स्थापित करने के लिए एक प्रारंभिक नैदानिक अभ्यास सेट से शुरुआत करें।"
                elif target_lang == "gu":
                    onboarding_reason = "તમારી જ્ઞાન પ્રોફાઇલ સ્થાપિત કરવા માટે પ્રારંભિક નિદાન અભ્યાસ સેટથી શરૂઆત કરો."

                onboarding_rec = TopicRecommendation(
                    topic_id=starter_topic.id,
                    topic_title=starter_topic.title,
                    subject_name=localize_subject_name(subject_name, target_lang),
                    action=RecommendationAction.PRACTICE,
                    priority=RevisionPriority.MEDIUM,
                    reason=onboarding_reason,
                    score=50.0,
                    mastery_level=MasteryLevel.UNASSESSED,
                    accuracy=0.0,
                    recent_accuracy=None,
                    retention_risk=RetentionRiskLevel.UNASSESSED,
                    trend=PerformanceTrend.INSUFFICIENT_DATA,
                    active_revision_plan_id=None,
                )
                return RecommendationResponse(
                    student_id=student_id,
                    total_recommendations=1,
                    recommendations=[onboarding_rec],
                )
            else:
                return RecommendationResponse(
                    student_id=student_id,
                    total_recommendations=0,
                    recommendations=[],
                )

        # 4. We have profiles and/or pending plans.
        # Ensure any topic that has an eligible pending revision plan is represented even if not in active_profiles.
        profile_map: Dict[str, TopicKnowledgeProfile] = {p.topic_id: p for p in active_profiles}
        for topic_id, plan in plan_by_topic.items():
            if topic_id not in profile_map:
                topic_record = db.query(Topic).filter(Topic.id == topic_id).first()
                if topic_record and RecommendationEngineService.is_eligible_curriculum_topic(db, student, topic_record, exam_code=exam_code):
                    profile_map[topic_id] = KnowledgeModelService.calculate_topic_profile(
                        db, student_id, topic_record
                    )

        recommendations: List[TopicRecommendation] = []

        # 5. Evaluate each topic deterministically
        for topic_id, prof in profile_map.items():
            plan = plan_by_topic.get(topic_id)
            rec = RecommendationEngineService._evaluate_topic_recommendation(prof, plan)
            if target_lang in ("hi", "gu"):
                rec.subject_name = localize_subject_name(rec.subject_name, target_lang)
                rec.reason = localize_recommendation_reason(
                    action=rec.action.value if hasattr(rec.action, "value") else str(rec.action),
                    topic_title=rec.topic_title,
                    mastery=rec.mastery_level.value if hasattr(rec.mastery_level, "value") else str(rec.mastery_level),
                    risk=rec.retention_risk.value if hasattr(rec.retention_risk, "value") else str(rec.retention_risk),
                    lang=target_lang,
                )
            recommendations.append(rec)

        # 6. Sort recommendations descending by score, tie-breaking by lowest accuracy
        recommendations.sort(key=lambda r: (r.score, -r.accuracy if r.accuracy is not None else 0), reverse=True)

        if limit > 0:
            recommendations = recommendations[:limit]

        return RecommendationResponse(
            student_id=student_id,
            total_recommendations=len(recommendations),
            recommendations=recommendations,
        )

    @staticmethod
    def _evaluate_topic_recommendation(
        prof: TopicKnowledgeProfile,
        plan: Optional[RevisionPlan],
    ) -> TopicRecommendation:
        """
        Scores and formulates an actionable recommendation for a topic.
        
        Priority Rules Hierarchy:
        1. URGENT revision due now (score 100+, action REVISION)
        2. HIGH revision due now (score 80+, action REVISION)
        3. HIGH retention risk detected (score 70+, action REVIEW)
        4. Low accuracy (< 30%) with attempts (score 65+, action REVISION)
        5. Moderate accuracy (< 50%) or Novice (score 50+, action PRACTICE)
        6. Declining trend (score 45+, action PRACTICE)
        7. Moderate retention risk (score 35+, action REVIEW)
        8. Developing mastery (score 25+, action PRACTICE)
        9. Proficient mastery (score 10+, action PRACTICE)
        10. Mastered (score 0, action REVIEW)
        """
        score = 0.0
        action = RecommendationAction.PRACTICE
        priority = RevisionPriority.LOW
        reasons: List[str] = []
        plan_id: Optional[str] = None

        if plan:
            plan_id = plan.id
            if plan.priority == RevisionPriority.URGENT:
                score += 100.0
                action = RecommendationAction.REVISION
                priority = RevisionPriority.URGENT
                reasons.append(plan.reason or "Immediate urgent revision required.")
            elif plan.priority == RevisionPriority.HIGH:
                score += 80.0
                action = RecommendationAction.REVISION
                priority = RevisionPriority.HIGH
                reasons.append(plan.reason or "High-priority revision scheduled.")
            else:
                score += 40.0
                action = RecommendationAction.REVISION
                priority = plan.priority
                reasons.append(plan.reason or "Scheduled revision item.")

        # Evaluate retention risk
        if prof.retention_risk == RetentionRiskLevel.HIGH:
            score += 70.0
            if action != RecommendationAction.REVISION:
                action = RecommendationAction.REVIEW
                if priority != RevisionPriority.URGENT:
                    priority = RevisionPriority.HIGH
            reasons.append("High retention risk detected from recent performance decay.")
        elif prof.retention_risk == RetentionRiskLevel.MODERATE:
            score += 30.0
            if action not in (RecommendationAction.REVISION, RecommendationAction.REVIEW):
                action = RecommendationAction.REVIEW
                if priority == RevisionPriority.LOW:
                    priority = RevisionPriority.MEDIUM
            reasons.append("Moderate retention risk; brief concept review recommended.")

        # Evaluate accuracy & mastery
        if prof.total_attempts > 0:
            effective_acc = prof.recent_accuracy if prof.recent_accuracy is not None else prof.accuracy
            if effective_acc <= 30.0:
                score += 60.0
                if action != RecommendationAction.REVISION:
                    action = RecommendationAction.REVISION
                    if priority != RevisionPriority.URGENT:
                        priority = RevisionPriority.HIGH
                reasons.append(f"Low accuracy ({effective_acc:.1f}%). Remediate fundamental concepts.")
            elif effective_acc < 50.0:
                score += 45.0
                if action == RecommendationAction.PRACTICE and priority == RevisionPriority.LOW:
                    priority = RevisionPriority.MEDIUM
                reasons.append(f"Developing understanding ({effective_acc:.1f}%). Additional targeted practice needed.")
            elif effective_acc < 70.0:
                score += 25.0
                reasons.append("Reinforce concepts to advance toward proficiency.")
            elif effective_acc >= 85.0:
                score += 5.0
                reasons.append("High accuracy achieved. Periodic maintenance recommended.")

        # Evaluate performance trend
        if prof.trend == PerformanceTrend.DECLINING:
            score += 40.0
            if priority == RevisionPriority.LOW:
                priority = RevisionPriority.MEDIUM
            reasons.append("Recent performance is declining compared to prior attempts.")
        elif prof.trend == PerformanceTrend.IMPROVING:
            score += 10.0
            reasons.append("Performance is improving; keep up the positive momentum!")

        # Mastery tier adjustment
        if prof.mastery_level == MasteryLevel.NOVICE:
            score += 20.0
        elif prof.mastery_level == MasteryLevel.DEVELOPING:
            score += 15.0
        elif prof.mastery_level == MasteryLevel.PROFICIENT:
            score += 5.0
        elif prof.mastery_level == MasteryLevel.MASTERED:
            # Mastered topics are low urgency unless retention decayed
            score = max(score - 10.0, 0.0)
            if not plan and prof.retention_risk == RetentionRiskLevel.LOW:
                action = RecommendationAction.REVIEW
                priority = RevisionPriority.LOW

        # Ensure a default reason if none matched
        if not reasons:
            reasons.append("Continue standard curriculum practice.")

        final_reason = " ".join(reasons)

        return TopicRecommendation(
            topic_id=prof.topic_id,
            topic_title=prof.topic_title,
            subject_name=prof.subject_name,
            action=action,
            priority=priority,
            reason=final_reason,
            score=round(score, 2),
            mastery_level=prof.mastery_level,
            accuracy=prof.accuracy,
            recent_accuracy=prof.recent_accuracy,
            retention_risk=prof.retention_risk,
            trend=prof.trend,
            active_revision_plan_id=plan_id,
        )
