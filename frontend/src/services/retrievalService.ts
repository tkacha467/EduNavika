import { api } from './api';
import { RetrievalSearchRequest, RetrievalSearchResponse } from '../types';

export class RetrievalService {
  /**
   * Search grounded curriculum learning materials by topic and query.
   */
  public async searchCurriculum(request: RetrievalSearchRequest): Promise<RetrievalSearchResponse | null> {
    try {
      return await api.post<RetrievalSearchResponse>('/retrieval/search', request);
    } catch (err) {
      console.warn('Failed to retrieve curriculum content:', err);
      return null;
    }
  }
}

export const retrievalService = new RetrievalService();
