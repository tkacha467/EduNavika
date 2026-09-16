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

export interface TopicPerformance {
  id: string;
  student_id: string;
  topic_id: string;
  mastery_score: number;
  confidence_score: number;
  decay_rate: number;
  review_priority: number;
  stability_estimate: number;
  last_evaluated_at: string;
}

export interface RevisionPlan {
  id: string;
  student_id: string;
  topic_id: string;
  scheduled_revision_date: string;
  urgency_score: number;
  status: 'SCHEDULED' | 'COMPLETED' | 'OVERDUE' | 'DISMISSED';
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
