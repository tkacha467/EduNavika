// Shared UI interaction state for EduNavika portals

export interface UIState {
  subjectId: string | null;
  topicId: string | null;
  notifFilter: string;
  builderStep: number;
  builderTopic: string;
}

export const UI: UIState = {
  subjectId: null,
  topicId: null,
  notifFilter: 'all',
  builderStep: 0,
  builderTopic: '',
};

// Also expose on window for inline event strings in templates
if (typeof window !== 'undefined') {
  (window as any).UI = UI;
}
