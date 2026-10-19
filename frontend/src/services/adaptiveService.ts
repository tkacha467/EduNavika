import { api } from './api';
import { getLanguage } from '../utils/i18n';
import { getSelectedExamCode } from './examService';
import {
  RevisionPlan,
  RevisionPlanResponse,
  StudentKnowledgeProfileResponse,
  RecommendationResponse,
  PracticeRecommendation,
  StudentProgressResponse,
  GamificationResponse,
} from '../types';

export class AdaptiveService {
  public async getNextPracticeRecommendation(
    studentId: string,
    topicId?: string,
    lang?: string,
    examCode?: string | null
  ): Promise<PracticeRecommendation | null> {
    try {
      const selectedLang = lang || getLanguage();
      const code = examCode !== undefined ? examCode : getSelectedExamCode();
      const params = new URLSearchParams();
      if (topicId) params.append('topic_id', topicId);
      if (selectedLang) params.append('language', selectedLang);
      if (code) params.append('exam_code', code);
      const q = params.toString() ? `?${params.toString()}` : '';
      return await api.get<PracticeRecommendation>(`/adaptive/next-practice/${encodeURIComponent(studentId)}${q}`);
    } catch (err) {
      console.warn('Failed to retrieve next practice recommendation:', err);
      return null;
    }
  }

  public async getRevisionPlan(
    studentId: string,
    subjectId?: string,
    lang?: string,
    examCode?: string | null
  ): Promise<RevisionPlanResponse | null> {
    try {
      const selectedLang = lang || getLanguage();
      const code = examCode !== undefined ? examCode : getSelectedExamCode();
      const params = new URLSearchParams();
      if (subjectId) params.append('subject_id', subjectId);
      if (selectedLang) params.append('language', selectedLang);
      if (code) params.append('exam_code', code);
      const q = params.toString() ? `?${params.toString()}` : '';
      return await api.get<RevisionPlanResponse>(`/adaptive/revision-plan/${encodeURIComponent(studentId)}${q}`);
    } catch (err) {
      console.warn('Failed to retrieve student revision plan:', err);
      return null;
    }
  }

  public async getRevisionPlans(studentId: string, examCode?: string | null): Promise<RevisionPlan[]> {
    try {
      const code = examCode !== undefined ? examCode : getSelectedExamCode();
      const examParam = code ? `&exam_code=${encodeURIComponent(code)}` : '';
      return await api.get<RevisionPlan[]>(`/revision/plans?student_id=${encodeURIComponent(studentId)}${examParam}`);
    } catch {
      return [];
    }
  }

  public async getRecommendations(
    studentId: string,
    limit: number = 10,
    lang?: string,
    examCode?: string | null
  ): Promise<RecommendationResponse | null> {
    try {
      const selectedLang = lang || getLanguage();
      const code = examCode !== undefined ? examCode : getSelectedExamCode();
      const params = new URLSearchParams();
      params.append('limit', String(limit));
      if (selectedLang) params.append('language', selectedLang);
      if (code) params.append('exam_code', code);
      return await api.get<RecommendationResponse>(`/adaptive/recommendations/${encodeURIComponent(studentId)}?${params.toString()}`);
    } catch (err) {
      console.warn('Failed to retrieve student recommendations:', err);
      return null;
    }
  }

  public async getKnowledgeProfile(studentId: string, topicId?: string): Promise<StudentKnowledgeProfileResponse | null> {
    try {
      const query = topicId ? `?topic_id=${encodeURIComponent(topicId)}` : '';
      return await api.get<StudentKnowledgeProfileResponse>(`/adaptive/knowledge-profile/${encodeURIComponent(studentId)}${query}`);
    } catch (err) {
      console.warn('Failed to retrieve student knowledge profile:', err);
      return null;
    }
  }

  public async completeAssessment(payload: {
    student_id: string;
    topic_id: string;
    score: number;
    total_questions: number;
    correct_answers: number;
  }): Promise<any> {
    try {
      return await api.post('/adaptive/complete-assessment', payload);
    } catch (err) {
      console.warn('Complete assessment evaluation failed:', err);
      return null;
    }
  }

  public async triggerAdaptiveRevision(studentId: string, topicId: string, performanceRating: number): Promise<any> {
    try {
      return await api.post('/adaptive/revision', {
        student_id: studentId,
        topic_id: topicId,
        performance_rating: performanceRating,
      });
    } catch (err) {
      console.warn('Adaptive revision request failed:', err);
      return null;
    }
  }

  public async getPracticeQuestions(
    studentId: string,
    topicId: string,
    count: number = 3,
    lang?: string,
    examCode?: string | null
  ): Promise<any> {
    try {
      const selectedLang = lang || getLanguage();
      const code = examCode !== undefined ? examCode : getSelectedExamCode();
      const params = new URLSearchParams();
      params.append('topic_id', topicId);
      params.append('count', String(count));
      if (selectedLang) params.append('language', selectedLang);
      if (code) params.append('exam_code', code);
      return await api.get(`/adaptive/practice/${encodeURIComponent(studentId)}?${params.toString()}`);
    } catch (err) {
      console.warn('Failed to retrieve adaptive practice questions:', err);
      return null;
    }
  }

  public async submitPracticeAnswer(payload: {
    student_id: string;
    question_id: string;
    topic_id: string;
    selected_answer: string;
    response_time_ms?: number;
    hint_used?: boolean;
    language?: string;
    confidence_level?: string;
  }): Promise<any> {
    try {
      const submission = {
        ...payload,
        language: payload.language || getLanguage(),
      };
      return await api.post('/adaptive/practice/submit', submission);
    } catch (err) {
      console.warn('Failed to submit practice answer:', err);
      return null;
    }
  }

  public async getProgress(
    studentId: string,
    subjectId?: string,
    lang?: string,
    examCode?: string | null
  ): Promise<StudentProgressResponse | null> {
    try {
      const selectedLang = lang || getLanguage();
      const code = examCode !== undefined ? examCode : getSelectedExamCode();
      const params = new URLSearchParams();
      if (subjectId) params.append('subject_id', subjectId);
      if (selectedLang) params.append('language', selectedLang);
      if (code) params.append('exam_code', code);
      const q = params.toString() ? `?${params.toString()}` : '';
      return await api.get<StudentProgressResponse>(`/adaptive/progress/${encodeURIComponent(studentId)}${q}`);
    } catch (err) {
      console.warn('Failed to retrieve student progress:', err);
      return null;
    }
  }

  public async getGamification(
    studentId: string,
    lang?: string,
    examCode?: string | null
  ): Promise<GamificationResponse | null> {
    try {
      const selectedLang = lang || getLanguage();
      const code = examCode !== undefined ? examCode : getSelectedExamCode();
      const params = new URLSearchParams();
      if (selectedLang) params.append('language', selectedLang);
      if (code) params.append('exam_code', code);
      const q = params.toString() ? `?${params.toString()}` : '';
      return await api.get<GamificationResponse>(`/adaptive/gamification/${encodeURIComponent(studentId)}${q}`);
    } catch (err) {
      console.warn('Failed to retrieve gamification profile:', err);
      return null;
    }
  }
}

export const adaptiveService = new AdaptiveService();

