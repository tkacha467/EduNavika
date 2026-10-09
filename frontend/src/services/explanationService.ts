import { api } from './api';
import { ExplanationRequest, ExplanationResponse } from '../types';

export class ExplanationService {
  /**
   * Request a personalized, curriculum-grounded explanation generated locally.
   */
  public async getExplanation(request: ExplanationRequest): Promise<ExplanationResponse | null> {
    try {
      return await api.post<ExplanationResponse>('/adaptive/explanation', request);
    } catch (err) {
      console.warn('Failed to retrieve personalized explanation:', err);
      return null;
    }
  }
}

export const explanationService = new ExplanationService();
