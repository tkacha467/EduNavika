// TypeScript Definitions for EduNavika Frontend & API Contracts

export type Role = 'student' | 'teacher';

export interface User {
  id: string;
  email: string;
  full_name: string;
  name?: string;
  role: Role;
  is_active: boolean;
  initials?: string;
  grade?: string;
  section?: string;
  school?: string;
  streak?: number;
  weeklyGoal?: number;
  todayGoal?: number;
  roll?: string;
  joined?: string;
  subjects?: string;
}

export interface StudentProfile {
  id: string;
  user_id: string;
  standard_id?: string;
  stream?: string;
  target_exam?: string;
  learning_streak_days?: number;
}

export interface TeacherProfile {
  id: string;
  user_id: string;
  department?: string;
  assigned_standards?: string[];
}

export interface Standard {
  id: string;
  grade_number: number;
  curriculum_framework: string;
  academic_year: string;
}

export interface Chapter {
  id: string;
  standard_id: string;
  chapter_number: number;
  title: string;
  description?: string;
  subject?: string;
}

export interface Topic {
  id: string;
  name: string;
  title?: string;
  chapter_id?: string;
  order_index?: number;
  mastery: number;
  kh: number;
  risk: string;
  last: string;
  next: string;
  status: string;
  done?: number;
}

export interface Subject {
  id: string;
  name: string;
  code: string;
  color: string;
  bg: string;
  mastery: number;
  kh: number;
  risk: 'low' | 'medium' | 'high';
  topics: number;
  done: number;
  topicList: Topic[];
}

export interface LearningContent {
  id: string;
  topic_id: string;
  title: string;
  content_type: string;
  text_body: string;
  reading_time_minutes?: number;
}

export interface MCQQuestion {
  id: string;
  topic_id: string;
  question_text: string;
  options: {
    A: string;
    B: string;
    C: string;
    D: string;
  };
  correct_option: 'A' | 'B' | 'C' | 'D';
  explanation?: string;
  difficulty_level?: number;
}

export interface Assessment {
  id: string;
  title: string;
  topic_id?: string;
  subject?: string;
  total_questions: number;
  time_limit_minutes: number;
  status: 'draft' | 'published' | 'completed';
}

export interface StudentAttempt {
  id: string;
  student_id: string;
  mcq_id: string;
  topic_id: string;
  selected_option: string;
  is_correct: boolean;
  score: number;
  response_time_ms: number;
  hint_requested: boolean;
}

export interface TopicKnowledgeProfile {
  topic_id: string;
  topic_title: string;
  subject_name: string;
  mastery_level: 'UNASSESSED' | 'NOVICE' | 'DEVELOPING' | 'PROFICIENT' | 'MASTERED';
  accuracy: number;
  total_attempts: number;
  correct_attempts: number;
  recent_accuracy?: number | null;
  trend: 'IMPROVING' | 'STABLE' | 'DECLINING' | 'INSUFFICIENT_DATA';
  retention_risk: 'LOW' | 'MODERATE' | 'HIGH' | 'UNASSESSED';
  average_response_time_ms?: number | null;
  hint_usage_count: number;
  last_activity_at?: string | null;
  last_success_at?: string | null;
  learning_pace?: string | null;
  current_difficulty?: string | null;
}

export interface StudentKnowledgeProfileResponse {
  student_id: string;
  total_topics_tracked: number;
  profiles: TopicKnowledgeProfile[];
}

export type RecommendationAction = 'REVISION' | 'PRACTICE' | 'REVIEW';

export interface TopicRecommendation {
  topic_id: string;
  topic_title: string;
  subject_name: string;
  action: RecommendationAction;
  priority: 'LOW' | 'MEDIUM' | 'HIGH' | 'URGENT';
  reason: string;
  score: number;
  mastery_level: 'UNASSESSED' | 'NOVICE' | 'DEVELOPING' | 'PROFICIENT' | 'MASTERED';
  accuracy: number;
  recent_accuracy?: number | null;
  retention_risk: 'LOW' | 'MODERATE' | 'HIGH' | 'UNASSESSED';
  trend: 'IMPROVING' | 'STABLE' | 'DECLINING' | 'INSUFFICIENT_DATA';
  active_revision_plan_id?: string | null;
}

export interface RecommendationResponse {
  student_id: string;
  total_recommendations: number;
  recommendations: TopicRecommendation[];
}

export interface RetrievalSearchRequest {
  student_id?: string;
  topic_id?: string;
  query: string;
  top_k?: number;
}

export interface RetrievedContentItem {
  content_id: string;
  topic_id: string;
  topic_title: string;
  chapter_title?: string | null;
  subject_name?: string | null;
  content_type: string;
  source_document?: string | null;
  source_page?: number | null;
  source_reference?: string | null;
  content_text: string;
  score: number;
}

export interface RetrievalSearchResponse {
  query: string;
  topic_id?: string | null;
  topic_title?: string | null;
  total_results: number;
  results: RetrievedContentItem[];
}

export interface ExplanationRequest {
  student_id: string;
  topic_id: string;
  query?: string;
  top_k?: number;
}

export interface ExplanationSource {
  source_document?: string | null;
  source_page?: number | null;
  source_reference?: string | null;
  content_type?: string | null;
  relevance_score: number;
}

export interface QuickCheckItem {
  question: string;
  expected_concept: string;
}

export interface StructuredExplanation {
  title: string;
  why_this_matters: string;
  core_concept: string;
  step_by_step: string[];
  common_mistake: string;
  quick_check: QuickCheckItem;
}

export interface PersonalizationContext {
  mastery_level: string;
  accuracy: number;
  recent_accuracy?: number | null;
  trend: string;
  retention_risk: string;
}

export interface ExplanationResponse {
  student_id: string;
  topic_id: string;
  topic_title: string;
  explanation: string;
  structured_explanation: StructuredExplanation;
  teaching_level: string;
  personalization: PersonalizationContext;
  sources: ExplanationSource[];
  next_action: string;
  generation_mode?: 'LOCAL_LLM' | 'DETERMINISTIC_FALLBACK';
  model_name?: string | null;
  inference_time_ms?: number | null;
}

export interface AdaptivePracticeQuestion {
  id: string;
  student_id: string;
  topic_id: string;
  topic_title: string;
  difficulty: string;
  question_type: string;
  question: string;
  options: string[];
  correct_answer?: string | null;
  explanation?: string | null;
  source_document?: string | null;
  source_page?: number | null;
  skill_target: string;
  personalization_reason: string;
}

export interface AdaptivePracticeResponse {
  student_id: string;
  topic_id: string;
  topic_title: string;
  target_difficulty: string;
  generation_mode: 'LOCAL_LLM' | 'DETERMINISTIC_FALLBACK';
  model_name?: string | null;
  total_questions: number;
  questions: AdaptivePracticeQuestion[];
}

export interface PracticeSubmissionRequest {
  student_id: string;
  question_id: string;
  topic_id: string;
  selected_answer: string;
  response_time_ms?: number | null;
  hint_used?: boolean;
}

export interface PracticeSubmissionResponse {
  correct: boolean;
  correct_answer: string;
  selected_answer: string;
  feedback: string;
  explanation: string;
  next_recommended_action: string;
  updated_mastery: string;
  updated_accuracy: number;
  source_document?: string | null;
  source_page?: number | null;
  event_id: string;
}

export interface PracticeRecommendation {
  topic_id: string;
  topic_title: string;
  subject_name?: string | null;
  mastery_level: string;
  accuracy: number;
  recent_accuracy?: number | null;
  trend: string;
  retention_risk: string;
  recommended_action: string;
  recommended_difficulty: string;
  reason: string;
}


export interface RevisionPlan {
  id: string;
  student_id: string;
  topic_id: string;
  topic_title?: string;
  subject_name?: string;
  recommended_revision_at: string;
  priority: 'LOW' | 'MEDIUM' | 'HIGH' | 'URGENT';
  reason?: string;
  completion_state: 'PENDING' | 'COMPLETED' | 'DISMISSED';
  created_at?: string;
  updated_at?: string;
}

export interface RevisionPlanItem {
  plan_id?: string | null;
  topic_id: string;
  topic_title: string;
  subject_id?: string | null;
  subject_name: string;
  chapter_id?: string | null;
  chapter_title?: string | null;
  mastery_level: 'UNASSESSED' | 'NOVICE' | 'DEVELOPING' | 'PROFICIENT' | 'MASTERED';
  accuracy: number;
  recent_accuracy?: number | null;
  retention_risk: 'LOW' | 'MODERATE' | 'HIGH' | 'UNASSESSED';
  priority: 'LOW' | 'MEDIUM' | 'HIGH' | 'URGENT';
  scheduled_date: string;
  recommended_revision_at: string;
  days_until_due: number;
  is_due_today: boolean;
  is_overdue: boolean;
  urgency_tier: 'TODAY' | 'THIS_WEEK' | 'UPCOMING';
  reason: string;
  recommended_action: string;
  recommended_difficulty: string;
  source_document?: string | null;
  source_page?: number | null;
}

export interface RevisionPlanResponse {
  student_id: string;
  generated_at: string;
  total_revisions: number;
  due_today_count: number;
  due_this_week_count: number;
  upcoming_count: number;
  urgent_count: number;
  high_count: number;
  medium_count: number;
  low_count: number;
  revisions: RevisionPlanItem[];
}

export interface NavItem {
  id: string;
  label: string;
  icon: string;
  badge?: string;
}

export interface NavGroup {
  group: string;
  items: NavItem[];
}

export interface ToastMessage {
  id: string;
  title: string;
  sub?: string;
  type?: 'good' | 'warn' | 'bad' | 'teal' | 'info';
}

export interface MasteryDistribution {
  unassessed: number;
  novice: number;
  developing: number;
  proficient: number;
  mastered: number;
}

export interface OverallProgressSummary {
  total_attempts: number;
  correct_attempts: number;
  overall_accuracy: number;
  topics_studied: number;
  total_topics_available: number;
  mastery_distribution: MasteryDistribution;
  overall_trend: string;
  recent_activity_at?: string | null;
  subject_id?: string | null;
  subject_name?: string | null;
}

export interface TopicProgressItem {
  topic_id: string;
  topic_title: string;
  subject_name: string;
  total_attempts: number;
  correct_attempts: number;
  accuracy: number;
  mastery_level: string;
  recent_accuracy?: number | null;
  trend: string;
  retention_risk: string;
  recommended_action: string;
  recommended_difficulty: string;
}

export interface StrengthsWeaknessesSummary {
  strengths: TopicProgressItem[];
  weaknesses: TopicProgressItem[];
  developing: TopicProgressItem[];
  unassessed_count: number;
}

export interface LearningJourneyItem {
  event_id: string;
  timestamp: string;
  topic_id: string;
  topic_title: string;
  subject_name: string;
  event_type: string;
  correctness?: boolean | null;
  score?: number | null;
  difficulty?: string | null;
  response_time_ms?: number | null;
}

export interface StudentProgressResponse {
  student_id: string;
  overall: OverallProgressSummary;
  topics: TopicProgressItem[];
  strengths_weaknesses: StrengthsWeaknessesSummary;
  learning_journey: LearningJourneyItem[];
}

export interface DailyGoalSummary {
  target: number;
  completed: number;
  percentage: number;
  is_completed: boolean;
}

export interface BadgeItem {
  badge_id: string;
  name: string;
  description: string;
  icon: string;
  is_unlocked: boolean;
  unlocked_at?: string | null;
  progress: number;
  target: number;
}

export interface QuestItem {
  quest_id: string;
  quest_type: string;
  title: string;
  description: string;
  topic_id?: string | null;
  topic_title?: string | null;
  current_progress: number;
  target_progress: number;
  progress_percentage: number;
  status: 'ACTIVE' | 'COMPLETED' | 'EXPIRED';
  xp_reward: number;
  reward_badge_id?: string | null;
  can_launch: boolean;
}

export interface GamificationResponse {
  student_id: string;
  total_xp: number;
  level: number;
  level_title: string;
  xp_towards_next_level: number;
  xp_required_for_next_level: number;
  level_progress_percentage: number;
  current_streak: number;
  longest_streak: number;
  last_learning_date?: string | null;
  streak_active_today: boolean;
  daily_goal: DailyGoalSummary;
  unlocked_badges: BadgeItem[];
  locked_badges: BadgeItem[];
  recently_earned_badges: BadgeItem[];
  active_quests?: QuestItem[];
  completed_quests?: QuestItem[];
}

