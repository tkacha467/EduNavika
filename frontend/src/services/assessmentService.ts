// Assessment Service: Real Telemetry Recording for Questions and Attempts

import { api } from './api';
import { MCQQuestion, StudentAttempt } from '../types';

export const SAMPLE_QUESTIONS: Record<string, MCQQuestion[]> = {
  // Curriculum-grounded questions for Standard 10 GSEB
  '5a321a44-bc06-4db4-a50f-5e53f913b612': [
    {
      id: 'chem-ch1-f01',
      topic_id: '5a321a44-bc06-4db4-a50f-5e53f913b612',
      question_text: 'Why must chemical equations be balanced in accordance with the Law of Conservation of Mass?',
      options: {
        A: 'Total mass of elements in products must equal total mass in reactants',
        B: 'To accelerate the reaction speed without altering mass',
        C: 'To change the chemical formulae of reactants into simpler states',
        D: 'To equalize the volume of gases participating in the reaction',
      },
      correct_option: 'A',
      explanation: 'Mass can neither be created nor destroyed in a chemical reaction. Total mass in products must equal reactants (Textbook Page 16).',
    },
    {
      id: 'chem-ch1-g01',
      topic_id: '5a321a44-bc06-4db4-a50f-5e53f913b612',
      question_text: 'In the reaction 2Mg(s) + O2(g) -> 2MgO(s), what type of chemical reaction is taking place?',
      options: {
        A: 'Combination reaction',
        B: 'Decomposition reaction',
        C: 'Double displacement reaction',
        D: 'Neutralisation reaction',
      },
      correct_option: 'A',
      explanation: 'When two or more substances combine to form a single product, it is called a combination reaction (Textbook Page 19).',
    },
  ],
};

export class AssessmentService {
  public async getQuestionsForTopic(topicId: string): Promise<MCQQuestion[]> {
    try {
      const questions = await api.get<MCQQuestion[]>(`/mcqs/by-topic/${encodeURIComponent(topicId)}`);
      if (questions && questions.length > 0) return questions;
    } catch {
      // Endpoint fallback
    }
    return SAMPLE_QUESTIONS[topicId] || [];
  }

  public async recordAttempt(payload: {
    student_id: string;
    mcq_id: string;
    topic_id: string;
    selected_option: string;
    is_correct: boolean;
    score: number;
    response_time_ms: number;
    hint_requested?: boolean;
  }): Promise<StudentAttempt | null> {
    const postPayload = {
      ...payload,
      hint_requested: payload.hint_requested || false,
    };

    for (let attempt = 0; attempt < 2; attempt++) {
      try {
        return await api.post<StudentAttempt>('/attempts', postPayload);
      } catch (err) {
        if (attempt === 0) {
          await new Promise((resolve) => setTimeout(resolve, 150));
          continue;
        }
        console.warn('Backend attempt telemetry recording offline or failed:', err);
        return null;
      }
    }
    return null;
  }
}

export const assessmentService = new AssessmentService();
