// Centralized Competitive Examination Scope Management Service for EduNavika
// Manages JEE Main, JEE Advanced, NEET UG, and General School Study Modes

export type ExamCode = 'JEE_MAIN' | 'JEE_ADVANCED' | 'NEET_UG';
export type ExamSelection = ExamCode | 'GENERAL';

export const SUPPORTED_EXAM_CODES: ExamCode[] = ['JEE_MAIN', 'JEE_ADVANCED', 'NEET_UG'];
export const SUPPORTED_EXAM_SELECTIONS: ExamSelection[] = ['GENERAL', 'JEE_MAIN', 'JEE_ADVANCED', 'NEET_UG'];

export const STORAGE_KEY_EXAM = 'edunavika_selected_exam';

export interface ExamMetadata {
  code: ExamSelection;
  label: string;
  shortLabel: string;
  conductingBody: string;
  badgeIcon: string;
  badgeClass: string;
  description: string;
  subjects: string[];
  totalTopics: number;
}

export const EXAM_METADATA_MAP: Record<ExamSelection, ExamMetadata> = {
  GENERAL: {
    code: 'GENERAL',
    label: 'General School Study',
    shortLabel: 'General Study',
    conductingBody: 'GSEB / NCERT',
    badgeIcon: '📚',
    badgeClass: 'badge-general',
    description: 'Complete Standards 10–12 Science Curriculum (Unfiltered school syllabus)',
    subjects: ['Physics', 'Chemistry', 'Mathematics', 'Biology'],
    totalTopics: 626,
  },
  JEE_MAIN: {
    code: 'JEE_MAIN',
    label: 'JEE Main (NTA)',
    shortLabel: 'JEE Main',
    conductingBody: 'National Testing Agency (NTA)',
    badgeIcon: '🎯',
    badgeClass: 'badge-jee-main',
    description: 'Engineering Entrance Syllabus (Physics, Chemistry, Mathematics; 436 verified topics)',
    subjects: ['Physics', 'Chemistry', 'Mathematics'],
    totalTopics: 436,
  },
  JEE_ADVANCED: {
    code: 'JEE_ADVANCED',
    label: 'JEE Advanced (IIT)',
    shortLabel: 'JEE Advanced',
    conductingBody: 'IIT Joint Admission Board (JAB)',
    badgeIcon: '🚀',
    badgeClass: 'badge-jee-adv',
    description: 'Advanced Engineering Syllabus (Retains 8 classical analytical topics; 444 verified topics)',
    subjects: ['Physics', 'Chemistry', 'Mathematics'],
    totalTopics: 444,
  },
  NEET_UG: {
    code: 'NEET_UG',
    label: 'NEET UG (NMC)',
    shortLabel: 'NEET UG',
    conductingBody: 'National Medical Commission (NMC)',
    badgeIcon: '🩺',
    badgeClass: 'badge-neet',
    description: 'Medical Entrance Syllabus (Physics, Chemistry, Biology; 497 verified topics)',
    subjects: ['Physics', 'Chemistry', 'Biology'],
    totalTopics: 497,
  },
};

/**
 * Validates if the string is a valid competitive examination code.
 */
export function isValidExamCode(code: unknown): code is ExamCode {
  return typeof code === 'string' && SUPPORTED_EXAM_CODES.includes(code as ExamCode);
}

/**
 * Validates if the string is a valid examination selection (including 'GENERAL').
 */
export function isValidExamSelection(selection: unknown): selection is ExamSelection {
  return typeof selection === 'string' && SUPPORTED_EXAM_SELECTIONS.includes(selection as ExamSelection);
}

/**
 * Retrieves the currently selected examination mode from storage.
 * Defaults to 'GENERAL' if unselected.
 * Throws an explicit error if the stored value is invalid, preventing silent corruption.
 */
export function getSelectedExam(): ExamSelection {
  if (typeof localStorage === 'undefined') return 'GENERAL';
  const stored = localStorage.getItem(STORAGE_KEY_EXAM);
  if (!stored) return 'GENERAL';

  if (!isValidExamSelection(stored)) {
    console.error(`Invalid examination code '${stored}' found in storage.`);
    throw new Error(`Invalid stored examination selection: '${stored}'. Supported values: ${SUPPORTED_EXAM_SELECTIONS.join(', ')}`);
  }

  return stored as ExamSelection;
}

/**
 * Returns the active competitive exam code string (for API queries),
 * or null if in 'GENERAL' school study mode.
 */
export function getSelectedExamCode(): ExamCode | null {
  const current = getSelectedExam();
  return current === 'GENERAL' ? null : (current as ExamCode);
}

/**
 * Sets the active examination mode.
 * Strictly validates against supported examination codes.
 * Persists to localStorage and dispatches a reactive custom event.
 */
export function setSelectedExam(exam: unknown): void {
  if (!isValidExamSelection(exam)) {
    throw new Error(`Invalid exam selection: '${exam}'. Must be one of: ${SUPPORTED_EXAM_SELECTIONS.join(', ')}`);
  }

  if (typeof localStorage !== 'undefined') {
    localStorage.setItem(STORAGE_KEY_EXAM, exam);
  }

  // Dispatch reactive event across window
  if (typeof window !== 'undefined') {
    window.dispatchEvent(
      new CustomEvent('edunavika:examChange', {
        detail: {
          exam,
          metadata: EXAM_METADATA_MAP[exam],
        },
      })
    );
  }
}

/**
 * Returns rich UI metadata for the given or currently selected examination mode.
 */
export function getExamMetadata(exam?: ExamSelection): ExamMetadata {
  const code = exam || getSelectedExam();
  return EXAM_METADATA_MAP[code] || EXAM_METADATA_MAP.GENERAL;
}

/**
 * Subscribes a callback to examination mode changes. Returns an unsubscribe function.
 */
export function onExamChange(callback: (exam: ExamSelection, meta: ExamMetadata) => void): () => void {
  if (typeof window === 'undefined') return () => {};

  const handler = (e: Event) => {
    const custom = e as CustomEvent<{ exam: ExamSelection; metadata: ExamMetadata }>;
    if (custom.detail) {
      callback(custom.detail.exam, custom.detail.metadata);
    }
  };

  window.addEventListener('edunavika:examChange', handler);
  return () => {
    window.removeEventListener('edunavika:examChange', handler);
  };
}
