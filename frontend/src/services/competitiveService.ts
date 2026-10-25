// Competitive Examination & Assessment Client Service for EduNavika

import { api } from './api';

export interface ExamInfo {
  code: string;
  name: string;
  conducting_body: string;
  description: string;
  subjects: string[];
  total_exam_topics: number;
  total_papers: number;
}

export interface ChapterCoverage {
  chapter_id: string;
  chapter_number: number;
  chapter_title: string;
  subject_name: string;
  grade: number;
  exam_code: string;
  total_topics: number;
  total_questions: number;
  eligible_question_count: number;
  authentic_pyq_count: number;
  textbook_generated_count: number;
  verified_answers_count: number;
  unverified_answers_count: number;
  quarantined_or_rejected_count: number;
  target_coverage: number;
  shortfall: number;
  is_coverage_met: boolean;
}

export interface CoverageReport {
  exam_code: string;
  total_chapters_audited: number;
  chapters_meeting_target: number;
  chapters_with_shortfall: number;
  target_per_chapter: number;
  total_eligible_questions: number;
  total_shortfall: number;
  chapters: ChapterCoverage[];
}

export interface ExamPaperItem {
  id: string;
  paper_identifier: string;
  exam_code: string;
  exam_year: number;
  session_or_shift: string;
  paper_code?: string;
  total_questions: number;
  has_pdf: boolean;
  questions_count: number;
}

export interface AssessmentSession {
  session_id: string;
  exam_code: string;
  mode: string;
  status: string;
  started_at: string;
  expires_at: string;
  duration_seconds: number;
  remaining_seconds: number;
  total_questions: number;
  questions: Array<{
    question_id: string;
    order: number;
    question_type: string;
    question_text: string;
    diagram_asset_url?: string;
    options: Array<{ option_key: string; option_text: string }>;
    topic_title: string;
    subject_name: string;
  }>;
  responses: Record<string, any>;
}

export interface AssessmentSubmission {
  session_id: string;
  status: string;
  auto_expired: boolean;
  exam_code: string;
  mode: string;
  total_score: number;
  max_possible_score: number;
  percentage: number;
  total_questions: number;
  correct_count: number;
  incorrect_count: number;
  unattempted_count: number;
  total_time_spent_seconds: number;
  subject_breakdown: Record<string, { score: number; max_score: number; correct: number; total: number }>;
  questions_review: Array<{
    question_id: string;
    order: number;
    question_text: string;
    question_type: string;
    options: Array<{ option_key: string; option_text: string }>;
    subject_name: string;
    topic_title: string;
    user_selected_option?: string;
    user_selected_options?: string[];
    user_numerical_value?: number;
    correct_answer: string;
    points_awarded: number;
    max_points: number;
    is_correct: boolean;
    is_attempted: boolean;
    time_spent_seconds: number;
    solution_text: string;
    ncert_citation?: string;
  }>;
  submitted_at: string;
}

export const competitiveService = {
  getExaminations: async (): Promise<ExamInfo[]> => {
    return api.get<ExamInfo[]>('/competitive/exams');
  },

  getCurriculumCoverage: async (examCode?: string): Promise<CoverageReport> => {
    const q = examCode ? `?exam_code=${encodeURIComponent(examCode)}` : '';
    return api.get<CoverageReport>(`/competitive/coverage${q}`);
  },

  getExamPapers: async (examCode?: string, year?: number): Promise<ExamPaperItem[]> => {
    const params = new URLSearchParams();
    if (examCode) params.set('exam_code', examCode);
    if (year) params.set('year', String(year));
    const qs = params.toString() ? `?${params.toString()}` : '';
    return api.get<ExamPaperItem[]>(`/competitive/papers${qs}`);
  },

  getPaperQuestions: async (paperId: string): Promise<any> => {
    return api.get<any>(`/competitive/papers/${paperId}/questions`);
  },

  getChapterQuestions: async (chapterId: string, limit: number = 20): Promise<any[]> => {
    return api.get<any[]>(`/competitive/chapters/${chapterId}/questions?limit=${limit}`);
  },

  startAssessment: async (params: {
    exam_code: string;
    mode?: string;
    chapter_id?: string;
    duration_minutes?: number;
    total_questions?: number;
  }): Promise<AssessmentSession> => {
    return api.post<AssessmentSession>('/competitive/assessments/start', params);
  },

  getAssessmentStatus: async (sessionId: string): Promise<AssessmentSession> => {
    return api.get<AssessmentSession>(`/competitive/assessments/${sessionId}`);
  },

  saveAssessmentResponse: async (sessionId: string, payload: {
    question_id: string;
    selected_option?: string;
    selected_options?: string[];
    numerical_value?: number;
    status?: string;
    time_spent_seconds?: number;
  }): Promise<any> => {
    return api.post<any>(`/competitive/assessments/${sessionId}/save`, payload);
  },

  submitAssessment: async (sessionId: string): Promise<AssessmentSubmission> => {
    return api.post<AssessmentSubmission>(`/competitive/assessments/${sessionId}/submit`, {});
  },
};
