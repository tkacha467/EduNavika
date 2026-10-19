import { ExamSelection, getSelectedExam } from './examService';

export interface UIState {
  subjectId: string | null;
  topicId: string | null;
  notifFilter: string;
  builderStep: number;
  builderTopic: string;
  examSelection: ExamSelection;
}

export const UI: UIState = {
  subjectId: null,
  topicId: null,
  notifFilter: 'all',
  builderStep: 0,
  builderTopic: '',
  examSelection: typeof localStorage !== 'undefined' ? getSelectedExam() : 'GENERAL',
};

// Also expose on window for inline event strings in templates
if (typeof window !== 'undefined') {
  (window as any).UI = UI;
}
