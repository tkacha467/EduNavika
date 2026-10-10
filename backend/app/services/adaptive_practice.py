import os
import re
import uuid
import time
import logging
from typing import List, Optional, Dict, Any, Tuple
from sqlalchemy.orm import Session

logger = logging.getLogger("adaptive_practice")

from backend.app.models import Topic, StudentProfile, LearningEvent, EventType
from backend.app.domain.enums import MasteryLevel, PerformanceTrend, RetentionRiskLevel
from backend.app.schemas.knowledge_profile import TopicKnowledgeProfile
from backend.app.schemas.retrieval import RetrievalSearchRequest, RetrievedContentItem
from backend.app.schemas.practice import (
    AdaptivePracticeQuestion,
    AdaptivePracticeResponse,
    PracticeSubmissionRequest,
    PracticeSubmissionResponse,
    PracticeRecommendation,
)
from backend.app.services.knowledge_model import KnowledgeModelService
from backend.app.services.recommendation_engine import RecommendationEngineService
from backend.app.services.curriculum_retrieval import CurriculumRetrievalService
from backend.app.services.event_recorder import EventRecorderService
from backend.app.services.explanation_engine import OnDeviceLLMExplanationEngine
from backend.app.api.v1.endpoints.attempts import _resolve_topic
from backend.app.services.curriculum_question_bank import (
    CurriculumQuestionValidator,
    CANONICAL_CURRICULUM_BANK,
    get_canonical_questions_for_topic,
    get_canonical_question_by_id,
    canonical_question_matches_topic,
)
from backend.app.services.curriculum_translations import (
    localize_question,
    localize_subject_name,
    localize_recommendation_reason,
)


class AdaptivePracticeService:
    """
    Service for generating and evaluating personalized, adaptive practice questions
    grounded in official curriculum textbook material.
    Supports local quantized SLM (Qwen2.5-0.5B-Instruct) with robust deterministic fallback.
    """

    # In-memory session store for active generated questions (storing the hidden correct_answer and metadata)
    _ACTIVE_QUESTIONS: Dict[str, Dict[str, Any]] = {}

    def __init__(self, llm_engine: Optional[OnDeviceLLMExplanationEngine] = None):
        self.llm_engine = llm_engine or OnDeviceLLMExplanationEngine()

    @staticmethod
    def determine_difficulty(
        profile: TopicKnowledgeProfile,
        retention_risk: RetentionRiskLevel,
        trend: PerformanceTrend,
        recent_error_notes: Optional[List[str]] = None,
    ) -> Tuple[str, str]:
        """
        Deterministic rule-based difficulty selection adhering to student knowledge model.
        Returns (difficulty, personalization_reason).
        """
        mastery = profile.mastery_level
        accuracy = profile.accuracy
        recent_acc = profile.recent_accuracy if profile.recent_accuracy is not None else accuracy

        # 1. Base difficulty from empirical mastery and accuracy
        if mastery == MasteryLevel.UNASSESSED or profile.total_attempts == 0:
            difficulty = "FOUNDATIONAL"
            reason = "Student is unassessed on this topic — diagnostic and foundational practice recommended."
        elif mastery == MasteryLevel.NOVICE or recent_acc < 50.0:
            difficulty = "FOUNDATIONAL"
            reason = f"Mastery is {mastery.value} with {recent_acc:.1f}% accuracy — targeting foundational concepts."
        elif mastery == MasteryLevel.DEVELOPING or recent_acc < 70.0:
            difficulty = "GUIDED"
            reason = f"Mastery is DEVELOPING ({recent_acc:.1f}% accuracy) — guided practice with structured hints."
        elif mastery == MasteryLevel.PROFICIENT or recent_acc < 85.0:
            difficulty = "APPLICATION"
            reason = f"Mastery is PROFICIENT ({recent_acc:.1f}% accuracy) — application and exam-style problem solving."
        else:
            difficulty = "CHALLENGE"
            reason = f"Mastery is MASTERED ({recent_acc:.1f}% accuracy) — high-order challenge and synthesis."

        # 2. Rule: Trend adjustments
        if trend == PerformanceTrend.DECLINING:
            if difficulty == "CHALLENGE":
                difficulty = "APPLICATION"
                reason += " (Stepped down from Challenge due to declining recent trend)."
            elif difficulty == "APPLICATION":
                difficulty = "GUIDED"
                reason += " (Stepped down from Application due to declining recent trend)."
            elif difficulty == "GUIDED":
                difficulty = "FOUNDATIONAL"
                reason += " (Stepped down to Foundational to reinforce basic principles following recent decline)."
        elif trend == PerformanceTrend.IMPROVING and mastery in (MasteryLevel.DEVELOPING, MasteryLevel.PROFICIENT):
            reason += " Positive performance trend detected — encouraging forward progression."

        # 3. Rule: If retention risk is HIGH, prioritize retention / revision
        if retention_risk == RetentionRiskLevel.HIGH:
            reason += " High retention risk detected — prioritizing revision reinforcement."

        # 4. Rule: Recent incorrect errors
        if recent_error_notes:
            reason += f" Focusing on concepts missed in recent attempts: {', '.join(recent_error_notes[:2])}."

        return difficulty, reason

    def recommend_next_practice(
        self,
        db: Session,
        student_id: str,
        topic_id: Optional[str] = None,
        language: Optional[str] = "en",
    ) -> PracticeRecommendation:
        """
        Determines the next practice recommendation for a student.
        If topic_id is omitted, selects top-priority topic from RecommendationEngineService.
        """
        student = db.query(StudentProfile).filter(StudentProfile.id == student_id).first()
        if not student:
            raise ValueError(f"Student profile '{student_id}' not found.")

        target_lang = language or student.preferred_language or "en"

        target_topic = None
        if topic_id:
            target_topic = _resolve_topic(db, topic_id)
            if not target_topic:
                raise ValueError(f"Topic '{topic_id}' could not be resolved.")
        else:
            # Consult existing RecommendationEngineService
            rec_resp = RecommendationEngineService.generate_recommendations(db, student_id, limit=5, language=target_lang)
            if rec_resp.recommendations:
                top_rec = rec_resp.recommendations[0]
                target_topic = _resolve_topic(db, top_rec.topic_id)

        if not target_topic:
            # Fallback to first eligible curriculum topic for student's standard
            from backend.app.models import Subject, Chapter
            target_topic = (
                db.query(Topic)
                .join(Chapter, Topic.chapter_id == Chapter.id)
                .join(Subject, Chapter.subject_id == Subject.id)
                .filter(Subject.standard_id == student.standard_id)
                .first()
            )
            if not target_topic:
                raise ValueError("No eligible curriculum topic found for student.")

        # Ensure topic eligibility
        if not RecommendationEngineService.is_eligible_curriculum_topic(db, student, target_topic):
            raise ValueError(f"Topic '{target_topic.title}' is not an eligible curriculum topic for this student.")

        # Compute student knowledge profile
        profile = KnowledgeModelService.calculate_topic_profile(db, student_id, target_topic)

        # Retrieve recent errors if any
        error_events = (
            db.query(LearningEvent)
            .filter(
                LearningEvent.student_id == student_id,
                LearningEvent.topic_id == target_topic.id,
                LearningEvent.correctness == False,
            )
            .order_by(LearningEvent.timestamp.desc())
            .limit(3)
            .all()
        )
        recent_errors = []
        for e in error_events:
            if e.event_metadata and e.event_metadata.get("mcq_id"):
                recent_errors.append(f"Q-{e.event_metadata['mcq_id']}")

        diff, reason = self.determine_difficulty(
            profile=profile,
            retention_risk=profile.retention_risk,
            trend=profile.trend,
            recent_error_notes=recent_errors if recent_errors else None,
        )

        action_map = {
            "FOUNDATIONAL": "FOUNDATIONAL_PRACTICE",
            "GUIDED": "GUIDED_PRACTICE",
            "APPLICATION": "APPLICATION_PRACTICE",
            "CHALLENGE": "CHALLENGE_PRACTICE",
        }
        recommended_action = action_map.get(diff, "FOUNDATIONAL_PRACTICE")

        subject_disp = localize_subject_name(profile.subject_name, target_lang)
        localized_reason = localize_recommendation_reason(
            action=recommended_action,
            topic_title=target_topic.title,
            mastery=profile.mastery_level.value if hasattr(profile.mastery_level, "value") else str(profile.mastery_level),
            risk=profile.retention_risk.value if hasattr(profile.retention_risk, "value") else str(profile.retention_risk),
            lang=target_lang,
        ) if target_lang in ("hi", "gu") else reason

        return PracticeRecommendation(
            topic_id=target_topic.id,
            topic_title=target_topic.title,
            subject_name=subject_disp,
            mastery_level=profile.mastery_level,
            accuracy=profile.accuracy,
            recent_accuracy=profile.recent_accuracy,
            trend=profile.trend.value if hasattr(profile.trend, "value") else str(profile.trend),
            retention_risk=profile.retention_risk.value if hasattr(profile.retention_risk, "value") else str(profile.retention_risk),
            recommended_action=recommended_action,
            recommended_difficulty=diff,
            reason=localized_reason,
        )


    def generate_practice_questions(
        self,
        db: Session,
        student_id: str,
        topic_id: str,
        count: int = 3,
        language: Optional[str] = "en",
    ) -> AdaptivePracticeResponse:
        """
        Generates personalized practice questions tailored to the student's mastery profile.
        Grounded strictly in curriculum textbook excerpts.
        Supports English, Hindi, and Gujarati with zero hallucinations and full offline capability.
        """
        student = db.query(StudentProfile).filter(StudentProfile.id == student_id).first()
        topic = _resolve_topic(db, topic_id)
        if not topic:
            raise ValueError(f"Topic '{topic_id}' could not be resolved.")

        target_lang = language or student.preferred_language or "en"

        # Ensure topic eligibility
        if not RecommendationEngineService.is_eligible_curriculum_topic(db, student, topic):
            raise ValueError(f"Topic '{topic.title}' is not an eligible curriculum topic for this student.")

        # 1. Retrieve Knowledge Profile
        prof_resp = KnowledgeModelService.get_student_knowledge_profiles(db, student_id, topic_id=topic.id)
        if prof_resp.profiles:
            profile = prof_resp.profiles[0]
        else:
            profile = KnowledgeModelService.calculate_topic_profile(db, student_id, topic)

        # 2. Extract recent incorrect attempt context
        error_events = (
            db.query(LearningEvent)
            .filter(
                LearningEvent.student_id == student_id,
                LearningEvent.topic_id == topic.id,
                LearningEvent.correctness == False,
            )
            .order_by(LearningEvent.timestamp.desc())
            .limit(3)
            .all()
        )
        recent_errors = []
        for e in error_events:
            if e.event_metadata and e.event_metadata.get("mcq_id"):
                recent_errors.append(f"Q-{e.event_metadata['mcq_id']}")

        # 3. Determine target difficulty
        difficulty, personalization_reason = self.determine_difficulty(
            profile=profile,
            retention_risk=profile.retention_risk,
            trend=profile.trend,
            recent_error_notes=recent_errors if recent_errors else None,
        )

        # 4. Retrieve Grounded Curriculum Material
        search_query = f"{topic.title} {difficulty.lower()} core principles"
        ret_req = RetrievalSearchRequest(
            student_id=student_id,
            topic_id=topic.id,
            query=search_query,
            top_k=max(3, count * 2),
        )
        ret_res = CurriculumRetrievalService.search(db, ret_req)
        chunks = ret_res.results

        # 5. Attempt Generation (Local SLM or Deterministic Fallback)
        questions: List[AdaptivePracticeQuestion] = []
        generation_mode = "DETERMINISTIC_FALLBACK"
        model_name = None

        # For Hindi and Gujarati, strictly use verified deterministic curriculum translations
        # to ensure zero SLM hallucination, 100% textbook fidelity, and rapid offline execution.
        if target_lang == "en":
            llm = self.llm_engine._get_llm()
            if llm is not None:
                try:
                    llm_q = self._generate_with_local_llm(
                        llm=llm,
                        student_id=student_id,
                        topic=topic,
                        profile=profile,
                        difficulty=difficulty,
                        chunks=chunks,
                        personalization_reason=personalization_reason,
                    )
                    if llm_q:
                        questions.append(llm_q)
                        generation_mode = "LOCAL_LLM"
                        model_name = "Qwen2.5-0.5B-Instruct"
                except Exception as e:
                    pass

        # 6. Fill remaining requested questions with deterministic curriculum questions
        needed = count - len(questions)
        if needed > 0:
            fallback_qs = self._generate_deterministic_questions(
                student_id=student_id,
                topic=topic,
                difficulty=difficulty,
                chunks=chunks,
                personalization_reason=personalization_reason,
                count=needed,
                offset=len(questions),
                language=target_lang,
            )
            questions.extend(fallback_qs)

        # Store questions in active registry for submission validation
        for q in questions:
            self._ACTIVE_QUESTIONS[q.id] = {
                "student_id": q.student_id,
                "topic_id": q.topic_id,
                "difficulty": q.difficulty,
                "options": q.options,
                "correct_answer": q.correct_answer,
                "canonical_correct_answer": getattr(q, "canonical_correct_answer", q.correct_answer),
                "explanation": q.explanation,
                "source_document": q.source_document,
                "source_page": q.source_page,
                "language": target_lang,
            }

        # Hide correct_answer and explanation in student-facing response
        student_facing_qs: List[AdaptivePracticeQuestion] = []
        for q in questions:
            sanitized = q.model_copy()
            sanitized.correct_answer = None
            sanitized.explanation = None
            student_facing_qs.append(sanitized)

        msg = None
        if len(student_facing_qs) == 0:
            if target_lang == "hi":
                msg = "यह विषय वर्तमान में डिवाइस पर उपलब्ध कक्षा 10 के ऑफ़लाइन पाठ्यक्रम में शामिल नहीं है। कृपया समर्थित पाठ्यक्रम विषयों में से कोई विषय चुनें।"
            elif target_lang == "gu":
                msg = "આ વિષય હાલમાં ડિવાઇસ પર ઉપલબ્ધ ધોરણ 10 ના ઑફલાઇન અભ્યાસક્રમમાં સામેલ નથી. કૃપા કરીને સમર્થિત અભ્યાસક્રમ વિષયોમાંથી કોઈ વિષય પસંદ કરો."
            else:
                msg = "This topic is not currently included in the verified offline Standard 10 curriculum available on this device. No curriculum-grounded practice is currently available. Please select from the supported syllabus topics."

        return AdaptivePracticeResponse(
            student_id=student_id,
            topic_id=topic.id,
            topic_title=topic.title,
            target_difficulty=difficulty,
            generation_mode=generation_mode,
            model_name=model_name,
            total_questions=len(student_facing_qs),
            questions=student_facing_qs,
            message=msg,
        )

    def _generate_with_local_llm(
        self,
        llm: Any,
        student_id: str,
        topic: Topic,
        profile: TopicKnowledgeProfile,
        difficulty: str,
        chunks: List[RetrievedContentItem],
        personalization_reason: str,
    ) -> Optional[AdaptivePracticeQuestion]:
        """
        Prompts local Qwen2.5-0.5B-Instruct to construct a single MCQ from curriculum context.
        Validates structure before returning.
        """
        if chunks:
            top_chunk = chunks[0]
            context_snippet = " ".join(top_chunk.content_text.split()[:140])
            page_no = top_chunk.source_page or 14
            src_doc = top_chunk.source_document
        else:
            top_chunk = None
            context_snippet = f"Standard Class 10 curriculum principles on {topic.title}."
            page_no = 14
            src_doc = "STD-10/Std-10_Science_English Medium.pdf"

        system_prompt = (
            "You are EduNavika's on-device practice question generator. "
            "Generate ONE multiple choice question (MCQ) strictly grounded in the provided curriculum context. "
            "Output format:\n"
            "QUESTION: <question text>\n"
            "A) <option A>\n"
            "B) <option B>\n"
            "C) <option C>\n"
            "D) <option D>\n"
            "CORRECT: <A/B/C/D>\n"
            "EXPLANATION: <concise explanation grounded in context>"
        )

        user_prompt = (
            f"=== STUDENT PROFILE ===\n"
            f"Mastery: {profile.mastery_level.value}, Difficulty Needed: {difficulty}\n\n"
            f"=== CURRICULUM CONTEXT (Page {page_no}) ===\n"
            f"\"{context_snippet}\"\n\n"
            f"=== TASK ===\n"
            f"Generate ONE {difficulty} MCQ test question for Class 10 {topic.title}."
        )

        resp = llm.create_chat_completion(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            max_tokens=220,
            temperature=0.2,
            top_p=0.85,
        )
        raw_text = resp["choices"][0]["message"]["content"].strip()
        return self._parse_and_validate_mcq(
            raw_text=raw_text,
            student_id=student_id,
            topic=topic,
            difficulty=difficulty,
            top_chunk=top_chunk,
            personalization_reason=personalization_reason,
        )

    def _parse_and_validate_mcq(
        self,
        raw_text: str,
        student_id: str,
        topic: Topic,
        difficulty: str,
        top_chunk: RetrievedContentItem,
        personalization_reason: str,
    ) -> Optional[AdaptivePracticeQuestion]:
        """
        Parses and strictly validates generated MCQ fields through CurriculumQuestionValidator:
        - 4 distinct options
        - valid correct answer matching an option
        - non-empty question and explanation
        - no generic templates
        """
        lines = [line.strip() for line in raw_text.split("\n") if line.strip()]
        q_text = ""
        options = []
        correct_opt = ""
        explanation = ""

        for line in lines:
            if re.match(r"(?i)^question\s*[:\-]", line):
                q_text = re.sub(r"(?i)^question\s*[:\-]\s*", "", line).strip()
            elif re.match(r"^[A-D]\)", line) or re.match(r"^[A-D]\.", line):
                options.append(line)
            elif re.match(r"(?i)^correct\s*[:\-]", line):
                correct_opt = re.sub(r"(?i)^correct\s*[:\-]\s*", "", line).strip().upper()
                if correct_opt and correct_opt[0] in "ABCD":
                    correct_opt = correct_opt[0]
            elif re.match(r"(?i)^explanation\s*[:\-]", line):
                explanation = re.sub(r"(?i)^explanation\s*[:\-]\s*", "", line).strip()

        # Check required fields
        if not q_text or len(options) != 4 or correct_opt not in ("A", "B", "C", "D"):
            return None

        # Clean option texts
        clean_opts = []
        for o in options:
            cleaned = re.sub(r"^[A-D][\)\.]\s*", "", o).strip()
            if not cleaned or cleaned in clean_opts:
                return None  # No empty or duplicate options
            clean_opts.append(cleaned)

        opt_idx = ord(correct_opt) - ord("A")
        correct_answer_text = clean_opts[opt_idx]

        source_doc = top_chunk.source_document if top_chunk else "STD-10/Std-10_Science_English Medium.pdf"
        source_p = top_chunk.source_page if top_chunk else 14
        source_cid = getattr(top_chunk, "content_id", getattr(top_chunk, "id", "default-chunk-01")) if top_chunk else "default-chunk-01"
        source_txt = top_chunk.content_text if top_chunk else f"Standard Class 10 curriculum principles on {topic.title}."

        # Run 10-point Curriculum Validation
        candidate = {
            "question": q_text,
            "options": clean_opts,
            "correct_answer": correct_answer_text,
            "difficulty": difficulty,
            "explanation": explanation or f"Refer to textbook page {source_p} on {topic.title}.",
            "source_document": source_doc,
            "source_page": source_p,
            "source_chunk_id": source_cid,
            "source_text": source_txt,
        }
        is_valid, _ = CurriculumQuestionValidator.validate(candidate)
        if not is_valid:
            return None

        qid = f"prac-{uuid.uuid4().hex[:8]}"
        return AdaptivePracticeQuestion(
            id=qid,
            student_id=student_id,
            topic_id=topic.id,
            topic_title=topic.title,
            subject="Science & Technology",
            chapter=topic.title,
            difficulty=difficulty,
            question_type="MCQ",
            question=q_text,
            options=clean_opts,
            correct_answer=correct_answer_text,
            explanation=explanation or f"Refer to textbook page {source_p} on {topic.title}.",
            source_document=source_doc,
            source_page=source_p,
            source_chunk_id=source_cid,
            source_text=source_txt[:250],
            skill_target=f"{topic.title} Conceptual Understanding",
            personalization_reason=personalization_reason,
        )

    def _generate_deterministic_questions(
        self,
        student_id: str,
        topic: Topic,
        difficulty: str,
        chunks: List[RetrievedContentItem],
        personalization_reason: str,
        count: int,
        offset: int = 0,
        language: Optional[str] = "en",
    ) -> List[AdaptivePracticeQuestion]:
        """
        Generates deterministic, verified curriculum-grounded practice questions
        stratified by difficulty tier from CANONICAL_CURRICULUM_BANK.
        Supports authentic NCERT/GSEB translations for Hindi and Gujarati.
        If no curriculum questions exist for this topic, returns [] safely (no fake MCQs).
        """
        top_page = chunks[0].source_page if chunks else 14
        top_doc = chunks[0].source_document if chunks else "STD-10/Std-10_Science_English Medium.pdf"

        canonical_items = get_canonical_questions_for_topic(topic.id, difficulty=difficulty)
        if not canonical_items:
            # Try getting any difficulty for this topic
            canonical_items = get_canonical_questions_for_topic(topic.id)

        # Fallback topic mapping by normalized title match
        if not canonical_items:
            norm_title = topic.title.lower().replace('&', 'and').replace('—', '-').strip()
            for tid, qlist in CANONICAL_CURRICULUM_BANK.items():
                if qlist:
                    cand_title = qlist[0]["topic_title"].lower().replace('&', 'and').replace('—', '-').strip()
                    cand_chap = qlist[0]["chapter"].lower().replace('&', 'and').replace('—', '-').strip()
                    if norm_title in cand_title or cand_title in norm_title or norm_title in cand_chap or cand_chap in norm_title:
                        canonical_items = [q for q in qlist if q["difficulty"] == difficulty] or qlist
                        break

        # If still no curriculum-grounded questions exist for this topic, DO NOT generate fake MCQs
        if not canonical_items:
            logger.warning("[CURRICULUM_ASSESSMENT] No curriculum-grounded questions available for topic '%s' (%s). Returning safe empty set.", topic.title, topic.id)
            return []

        selected: List[AdaptivePracticeQuestion] = []
        for i in range(count):
            idx = (offset + i) % len(canonical_items)
            item = canonical_items[idx]
            localized_item = localize_question(item, language) if language in ("hi", "gu") else item
            qid = f"prac-det-{difficulty.lower()[:3]}-{uuid.uuid4().hex[:6]}"
            subj_disp = localize_subject_name(item.get("subject", "Science & Technology"), language)

            q = AdaptivePracticeQuestion(
                id=qid,
                student_id=student_id,
                topic_id=topic.id,
                topic_title=topic.title,
                subject=subj_disp,
                chapter=item.get("chapter", topic.title),
                difficulty=localized_item.get("difficulty", difficulty),
                question_type="MCQ",
                question=localized_item["question"],
                options=localized_item["options"],
                correct_answer=localized_item["correct_answer"],
                explanation=localized_item["explanation"],
                source_document=item.get("source_document", top_doc),
                source_page=item.get("source_page", top_page),
                source_chunk_id=item.get("source_chunk_id"),
                source_text=item.get("source_text", "")[:250],
                skill_target=item.get("skill_target", f"{topic.title} Core Competency"),
                personalization_reason=personalization_reason,
            )
            # Store in active questions mapping with both localized and canonical answers
            self._ACTIVE_QUESTIONS[qid] = {
                "student_id": q.student_id,
                "topic_id": q.topic_id,
                "difficulty": q.difficulty,
                "options": q.options,
                "correct_answer": q.correct_answer,
                "canonical_correct_answer": item.get("correct_answer"),
                "explanation": q.explanation,
                "source_document": q.source_document,
                "source_page": q.source_page,
                "language": language or "en",
            }
            selected.append(q)

        return selected

    def submit_practice_answer(
        self,
        db: Session,
        submission: PracticeSubmissionRequest,
    ) -> PracticeSubmissionResponse:
        """
        Evaluates student answer, generates personalized pedagogical feedback,
        records longitudinal LearningEvent, updates TopicPerformance, and computes next action.
        Maintains complete language-agnostic mastery invariants while returning localized pedagogical feedback.
        """
        student = db.query(StudentProfile).filter(StudentProfile.id == submission.student_id).first()
        topic = _resolve_topic(db, submission.topic_id)
        if not topic:
            raise ValueError(f"Topic '{submission.topic_id}' could not be resolved.")

        target_lang = submission.language or (student.preferred_language if student else "en") or "en"

        # 1. Retrieve Question Metadata from Active Registry, Canonical Bank, or DB
        q_meta = self._ACTIVE_QUESTIONS.get(submission.question_id)
        canonical_q = get_canonical_question_by_id(submission.question_id)
        options = []
        if q_meta and q_meta.get("topic_id") == topic.id:
            correct_answer = q_meta["correct_answer"]
            base_explanation = q_meta["explanation"]
            difficulty = q_meta.get("difficulty", "FOUNDATIONAL")
            src_doc = q_meta.get("source_document")
            src_page = q_meta.get("source_page")
            canonical_answer = q_meta.get("canonical_correct_answer", correct_answer)
            options = q_meta.get("options", [])
        elif canonical_q:
            if not canonical_question_matches_topic(canonical_q, topic.id, topic.title):
                raise ValueError("Practice question does not belong to the submitted curriculum topic.")
            correct_answer = canonical_q["correct_answer"]
            base_explanation = canonical_q.get("explanation", f"Grounded in curriculum page {canonical_q.get('source_page', 1)}.")
            difficulty = canonical_q.get("difficulty", "FOUNDATIONAL")
            src_doc = canonical_q.get("source_document")
            src_page = canonical_q.get("source_page")
            canonical_answer = correct_answer
            options = canonical_q.get("options", [])
        elif q_meta:
            # A session-only id from another topic must never be credited here.
            raise ValueError("Practice question does not belong to the submitted curriculum topic.")
        else:
            # Check MCQQuestion table in DB
            from backend.app.models import MCQQuestion
            mcq_record = db.query(MCQQuestion).filter(MCQQuestion.id == submission.question_id).first()
            if mcq_record:
                if mcq_record.topic_id != topic.id:
                    raise ValueError("Practice question does not belong to the submitted curriculum topic.")
                correct_answer = mcq_record.correct_option
                base_explanation = mcq_record.explanation or "No verified explanation is available for this question."
                difficulty = mcq_record.difficulty.value if hasattr(mcq_record.difficulty, "value") else "FOUNDATIONAL"
                src_doc = mcq_record.source_content.source_document if mcq_record.source_content else None
                src_page = mcq_record.source_content.source_page if mcq_record.source_content else None
                canonical_answer = correct_answer
                options = [mcq_record.option_a, mcq_record.option_b, mcq_record.option_c, mcq_record.option_d]
            else:
                raise ValueError("Question is not in the verified curriculum question bank.")

        # Compare answers (handles: exact text, stripped text, option letters 'A'/'B'/'C'/'D', option indices 0/1/2/3)
        selected_clean = submission.selected_answer.strip().lower()
        candidate_answers = set()
        if correct_answer:
            candidate_answers.add(correct_answer.strip().lower())
        if canonical_answer:
            candidate_answers.add(canonical_answer.strip().lower())
        # If student sent an option letter ('A', 'B', 'C', 'D') or index
        if selected_clean in ("a", "b", "c", "d") and options and len(options) >= 4:
            opt_idx = ord(selected_clean.upper()) - ord("A")
            if 0 <= opt_idx < len(options):
                candidate_answers.add(str(options[opt_idx]).strip().lower())
        elif selected_clean in ("0", "1", "2", "3") and options and len(options) >= 4:
            opt_idx = int(selected_clean)
            if 0 <= opt_idx < len(options):
                candidate_answers.add(str(options[opt_idx]).strip().lower())

        is_correct = (
            selected_clean in candidate_answers
            or (bool(correct_answer) and selected_clean == correct_answer.strip().lower())
            or (bool(canonical_answer) and selected_clean == canonical_answer.strip().lower())
        )

        # 2. Record atomic LearningEvent via EventRecorderService (100% language-invariant)
        event = EventRecorderService.record_event(
            db=db,
            student_id=submission.student_id,
            topic_id=topic.id,
            event_type=EventType.PRACTICE,
            score=100.0 if is_correct else 0.0,
            correctness=is_correct,
            response_time_ms=submission.response_time_ms,
            hint_used=submission.hint_used,
            event_metadata={
                "question_id": submission.question_id,
                "difficulty": difficulty,
                "selected_answer": submission.selected_answer,
                "correct_answer": correct_answer,
                "language": target_lang,
            },
            auto_commit=True,
        )

        # 3. Retrieve updated Knowledge Profile (computed empirically from LearningEvents)
        updated_profile = KnowledgeModelService.calculate_topic_profile(db, submission.student_id, topic)

        # 4. Generate Personalized Pedagogical Feedback
        feedback, next_action = self._build_personalized_feedback(
            is_correct=is_correct,
            selected_answer=submission.selected_answer,
            correct_answer=correct_answer,
            difficulty=difficulty,
            profile=updated_profile,
            topic_title=topic.title,
            source_page=src_page,
            language=target_lang,
        )

        return PracticeSubmissionResponse(
            correct=is_correct,
            correct_answer=correct_answer,
            selected_answer=submission.selected_answer,
            feedback=feedback,
            explanation=base_explanation,
            next_recommended_action=next_action,
            updated_mastery=updated_profile.mastery_level,
            updated_accuracy=updated_profile.accuracy,
            source_document=src_doc,
            source_page=src_page,
            event_id=event.id,
        )

    def _build_personalized_feedback(
        self,
        is_correct: bool,
        selected_answer: str,
        correct_answer: str,
        difficulty: str,
        profile: TopicKnowledgeProfile,
        topic_title: str,
        source_page: Optional[int],
        language: Optional[str] = "en",
    ) -> Tuple[str, str]:
        """
        Constructs personalized pedagogical feedback based on student mastery and result.
        Supports localized pedagogical feedback in English, Hindi, and Gujarati.
        """
        lang = (language or "en").lower()
        page_ref_en = f" (Textbook Page {source_page})" if source_page else ""
        page_ref_hi = f" (पाठ्यपुस्तक पृष्ठ {source_page})" if source_page else ""
        page_ref_gu = f" (પાઠ્યપુસ્તક પાનું {source_page})" if source_page else ""
        mastery = profile.mastery_level

        # --- HINDI LOCALIZATION ---
        if lang == "hi":
            if is_correct:
                if mastery in (MasteryLevel.UNASSESSED, MasteryLevel.NOVICE):
                    feedback = (
                        f"शाबाश! आपने बुनियादी अवधारणा को सही ढंग से समझा है{page_ref_hi}। "
                        f"{topic_title} पर निरंतर सफलता आपके ज्ञान के आधार को मजबूत कर रही है।"
                    )
                    next_action = "अपनी समझ को पुख्ता करने के लिए एक और निर्देशित अभ्यास प्रश्न हल करें।"
                elif mastery == MasteryLevel.DEVELOPING:
                    feedback = (
                        f"बहुत अच्छा! आपने ठोस वैचारिक अनुप्रयोग प्रदर्शित किया{page_ref_hi}। "
                        f"आपकी दक्षता में सुधार हो रहा है।"
                    )
                    next_action = "अनुप्रयोग-स्तरीय समस्या की ओर आगे बढ़ें।"
                elif mastery == MasteryLevel.PROFICIENT:
                    feedback = (
                        f"अति उत्तम! आपने बहु-चरणीय तर्क का सटीक प्रयोग किया{page_ref_hi}। "
                        f"{topic_title} की आपकी समझ सुदृढ़ है।"
                    )
                    next_action = "बोर्ड परीक्षा स्तर की निपुणता के लिए एक चुनौतीपूर्ण प्रश्न हल करें।"
                else:  # MASTERED
                    feedback = (
                        f"दक्षता प्रमाणित! आपने पूर्ण सटीकता के साथ इस {difficulty.lower()} प्रश्न को हल किया{page_ref_hi}।"
                    )
                    next_action = "अध्यायों के समग्र संश्लेषण का अन्वेषण करें या निर्धारित पुनरावलोकन पूरा करें।"
            else:
                misconception = f"ध्यान दें कि सही सिद्धांत है: '{correct_answer}'{page_ref_hi}।"
                if mastery in (MasteryLevel.UNASSESSED, MasteryLevel.NOVICE):
                    feedback = (
                        f"कोई बात नहीं! {misconception} आगे बढ़ने से पहले बुनियादी अवधारणा की समीक्षा करें।"
                    )
                    next_action = f"{topic_title} के लिए व्यक्तिगत व्याख्या की समीक्षा करें या एक बुनियादी प्रश्न हल करें।"
                elif mastery == MasteryLevel.DEVELOPING:
                    feedback = (
                        f"अच्छा प्रयास, लेकिन विवरणों पर ध्यान दें! {misconception}"
                    )
                    next_action = f"इस भ्रांति को दूर करने के लिए {topic_title} पर एक और निर्देशित प्रश्न हल करें।"
                else:
                    feedback = (
                        f"छोटी सी चूक! {misconception} परीक्षा की परिस्थितियों में नियमों पर पूरा ध्यान दें।"
                    )
                    next_action = f"{topic_title} पर एक अन्य लक्षित अनुप्रयोग प्रश्न हल करें।"
            return feedback, next_action

        # --- GUJARATI LOCALIZATION ---
        if lang == "gu":
            if is_correct:
                if mastery in (MasteryLevel.UNASSESSED, MasteryLevel.NOVICE):
                    feedback = (
                        f"ખૂબ સરસ! તમે પાયાનો ખ્યાલ ચોકસાઈથી સમજી લીધો છે{page_ref_gu}। "
                        f"{topic_title} પર સતત સફળતા તમારા જ્ઞાનને મજબૂત બનાવી રહી છે."
                    )
                    next_action = "તમારી સમજ વધુ મજબૂત કરવા માટે બીજો માર્ગદર્શિત પ્રશ્ન ઉકેલો."
                elif mastery == MasteryLevel.DEVELOPING:
                    feedback = (
                        f"ઉત્તમ કાર્ય! તમે યોગ્ય વૈચારિક ઉપયોગ દર્શાવ્યો છે{page_ref_gu}। "
                        f"તમારી નિપુણતા પ્રગતિ કરી રહી છે."
                    )
                    next_action = "ઉપયોગ-સ્તરના (application-level) પ્રશ્ન તરફ આગળ વધો."
                elif mastery == MasteryLevel.PROFICIENT:
                    feedback = (
                        f"ખૂબ જ સરસ! તમે ચોકસાઈપૂર્વક તર્ક લાગુ કર્યો છે{page_ref_gu}। "
                        f"{topic_title} પર તમારી પકડ મજબૂત છે."
                    )
                    next_action = "બોર્ડ સ્તરની નિપુણતા માટે પડકારજનક પ્રશ્ન ઉકેલો."
                else:  # MASTERED
                    feedback = (
                        f"સંપૂર્ણ નિપુણતા! તમે આ {difficulty.lower()} પ્રશ્ન સંપૂર્ણ સચોટતાથી ઉકેલ્યો છે{page_ref_gu}."
                    )
                    next_action = "સમગ્ર પ્રકરણોના સંશ્લેષણનો અભ્યાસ કરો અથવા નિર્ધારિત પુનરાવર્તન પૂર્ણ કરો."
            else:
                misconception = f"ધ્યાનમાં રાખો કે સાચો સિદ્ધાંત છે: '{correct_answer}'{page_ref_gu}।"
                if mastery in (MasteryLevel.UNASSESSED, MasteryLevel.NOVICE):
                    feedback = (
                        f"નજીક હતા! {misconception} આગળ વધતા પહેલા પાયાના ખ્યાલનું પુનરાવર્તન કરો."
                    )
                    next_action = f"{topic_title} માટે વિગતવાર સમજૂતી વાંચો અથવા પાયાનો પ્રશ્ન ઉકેલો."
                elif mastery == MasteryLevel.DEVELOPING:
                    feedback = (
                        f"સારો પ્રયાસ, પરંતુ વિગતો પર ધ્યાન આપો! {misconception}"
                    )
                    next_action = f"આ ખ્યાલ સ્પષ્ટ કરવા માટે {topic_title} પર વધુ એક માર્ગદર્શિત પ્રશ્ન અજમાવો."
                else:
                    feedback = (
                        f"નાની ભૂલ! {misconception} પરીક્ષાના સમયે નિયમોનું ધ્યાન રાખો."
                    )
                    next_action = f"{topic_title} પર બીજો લક્ષિત પ્રશ્ન ઉકેલો."
            return feedback, next_action

        # --- ENGLISH DEFAULT ---
        if is_correct:
            if mastery in (MasteryLevel.UNASSESSED, MasteryLevel.NOVICE):
                feedback = (
                    f"Excellent! You accurately grasped the foundational concept{page_ref_en}. "
                    f"Building consistent success on {topic_title} is stabilizing your knowledge base."
                )
                next_action = "Attempt another guided practice question to consolidate your understanding."
            elif mastery == MasteryLevel.DEVELOPING:
                feedback = (
                    f"Great job! You demonstrated solid conceptual application{page_ref_en}. "
                    f"Your mastery is developing nicely towards proficiency."
                )
                next_action = "Step up to an application-level problem check."
            elif mastery == MasteryLevel.PROFICIENT:
                feedback = (
                    f"Very well done! You applied multi-step reasoning accurately{page_ref_en}. "
                    f"Your understanding of {topic_title} is consistent."
                )
                next_action = "Tackle an exam challenge question to solidify board mastery."
            else:  # MASTERED
                feedback = (
                    f"Mastery confirmed! You solved this {difficulty.lower()} question with complete precision{page_ref_en}."
                )
                next_action = "Explore cross-chapter synthesis or complete your scheduled revision."

        else:
            # Incorrect feedback
            if "formula" in selected_answer.lower() or "subscript" in selected_answer.lower():
                misconception = "You changed the chemical formula rather than adjusting coefficients. Remember: subscripts define compound identity; coefficients balance atoms."
            elif "speed" in selected_answer.lower() or "rate" in selected_answer.lower():
                misconception = "Balancing equations relates strictly to the conservation of mass, not the speed or kinetics of the reaction."
            else:
                misconception = f"Notice that the correct principle is '{correct_answer}'{page_ref_en}."

            if mastery in (MasteryLevel.UNASSESSED, MasteryLevel.NOVICE):
                feedback = (
                    f"Not quite. {misconception} "
                    f"Take a moment to review the foundational concept before continuing."
                )
                next_action = f"Review the personalized explanation for {topic_title} or solve a foundational practice question."
            elif mastery == MasteryLevel.DEVELOPING:
                feedback = (
                    f"Close attempt, but careful on the details! {misconception}"
                )
                next_action = f"Attempt another guided practice question on {topic_title} to correct this misconception."
            else:
                feedback = (
                    f"Minor slip! {misconception} Keep close attention to conservation rules under test conditions."
                )
                next_action = f"Try another targeted application question on {topic_title}."

        return feedback, next_action


# Global default service instance
adaptive_practice_service = AdaptivePracticeService()
