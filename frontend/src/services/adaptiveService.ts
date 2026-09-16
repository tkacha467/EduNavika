// Adaptive Learning & Knowledge Decay Service

import { api } from './api';
import { RevisionPlan, TopicPerformance } from '../types';

export class AdaptiveService {
  public async getRevisionPlans(studentId: string): Promise<RevisionPlan[]> {
    try {
      return await api.get<RevisionPlan[]>(`/revision/plans?student_id=${encodeURIComponent(studentId)}`);
    } catch {
      return [];
    }
  }

  public async getTopicPerformance(studentId: string, topicId?: string): Promise<TopicPerformance[]> {
    try {
      const query = topicId ? `?student_id=${studentId}&topic_id=${topicId}` : `?student_id=${studentId}`;
      return await api.get<TopicPerformance[]>(`/performance/topics${query}`);
    } catch {
      return [];
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
}

export const adaptiveService = new AdaptiveService();
