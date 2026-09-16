// Content Service: Topic Reading & Study Telemetry Integration

import { api } from './api';
import { LearningContent } from '../types';

export class ContentService {
  public async getContentByTopic(topicId: string): Promise<LearningContent[]> {
    try {
      return await api.get<LearningContent[]>(`/content/by-topic/${encodeURIComponent(topicId)}`);
    } catch {
      return [];
    }
  }

  public async recordStudySession(contentId: string, studentId: string, durationSeconds = 120): Promise<boolean> {
    try {
      await api.post(`/content/${contentId}/study`, {
        student_id: studentId,
        duration_seconds: durationSeconds,
      });
      return true;
    } catch {
      return false;
    }
  }
}

export const contentService = new ContentService();
