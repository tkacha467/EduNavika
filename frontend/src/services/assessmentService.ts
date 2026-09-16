// Assessment Service: Real Telemetry Recording for Questions and Attempts

import { api } from './api';
import { MCQQuestion, StudentAttempt } from '../types';

export const SAMPLE_QUESTIONS: Record<string, MCQQuestion[]> = {
  default: [
    {
      id: 'q1',
      topic_id: 'm1',
      question_text: 'What are the roots of the quadratic equation 2x² - 7x + 3 = 0?',
      options: {
        A: 'x = 3 and x = 1/2',
        B: 'x = -3 and x = -1/2',
        C: 'x = 7 and x = 2',
        D: 'x = 1/3 and x = 2',
      },
      correct_option: 'A',
      explanation: 'Using the quadratic formula x = (-b ± √(b² - 4ac)) / (2a): b² - 4ac = 49 - 24 = 25. Thus x = (7 ± 5)/4 => x = 3 or x = 1/2.',
    },
    {
      id: 'q2',
      topic_id: 'p1',
      question_text: 'According to Ohm\'s law, if the resistance in a circuit is doubled while the voltage remains constant, the current will:',
      options: {
        A: 'Double',
        B: 'Be halved',
        C: 'Remain unchanged',
        D: 'Quadruple',
      },
      correct_option: 'B',
      explanation: 'From I = V / R, current I is inversely proportional to resistance R when voltage V is constant.',
    },
    {
      id: 'q3',
      topic_id: 'c1',
      question_text: 'Which of the following is an example of an exothermic combination reaction?',
      options: {
        A: 'Decomposition of calcium carbonate',
        B: 'Reaction of quicklime with water (CaO + H₂O → Ca(OH)₂)',
        C: 'Photosynthesis in plants',
        D: 'Electrolysis of water',
      },
      correct_option: 'B',
      explanation: 'When quicklime (CaO) reacts vigorously with water, it produces slaked lime along with a large release of heat, making it exothermic.',
    },
  ],
};

export class AssessmentService {
  public async getQuestionsForTopic(topicId: string): Promise<MCQQuestion[]> {
    try {
      const questions = await api.get<MCQQuestion[]>(`/mcqs/by-topic/${encodeURIComponent(topicId)}`);
      if (questions && questions.length > 0) return questions;
    } catch {
      // Graceful fallback to sample questions
    }
    return SAMPLE_QUESTIONS[topicId] || SAMPLE_QUESTIONS.default;
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
    try {
      // Posts to backend attempts endpoint, which triggers LearningEvent persistence with idempotency
      return await api.post<StudentAttempt>('/attempts', {
        ...payload,
        hint_requested: payload.hint_requested || false,
      });
    } catch (err) {
      console.warn('Backend attempt telemetry recording offline or failed:', err);
      return null;
    }
  }
}

export const assessmentService = new AssessmentService();
