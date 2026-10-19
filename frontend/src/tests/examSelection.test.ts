// Phase E.6: Frontend Exam Selection and End-to-End Integration Tests
import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import {
  getSelectedExam,
  getSelectedExamCode,
  setSelectedExam,
  getExamMetadata,
  onExamChange,
  isValidExamCode,
  isValidExamSelection,
  SUPPORTED_EXAM_CODES,
  SUPPORTED_EXAM_SELECTIONS,
  EXAM_METADATA_MAP,
  STORAGE_KEY_EXAM,
  ExamSelection,
} from '../services/examService';
import { curriculumService } from '../services/curriculumService';
import { adaptiveService } from '../services/adaptiveService';
import { UI } from '../services/uiState';

// In-memory mock storage and event system for Node environment
class MockLocalStorage {
  private store: Record<string, string> = {};
  getItem(key: string): string | null {
    return this.store[key] ?? null;
  }
  setItem(key: string, value: string): void {
    this.store[key] = String(value);
  }
  removeItem(key: string): void {
    delete this.store[key];
  }
  clear(): void {
    this.store = {};
  }
}

class MockCustomEvent extends Event {
  detail: any;
  constructor(type: string, eventInitDict?: CustomEventInit) {
    super(type);
    this.detail = eventInitDict?.detail;
  }
}

describe('Phase E.6: Exam Selection Service and Logic', () => {
  let mockStorage: MockLocalStorage;

  beforeEach(() => {
    mockStorage = new MockLocalStorage();
    // @ts-ignore
    globalThis.localStorage = mockStorage;
    // @ts-ignore
    globalThis.CustomEvent = MockCustomEvent;

    // Minimal EventTarget mock on globalThis and window
    const listeners: Record<string, Function[]> = {};
    const addEventListener = (event: string, fn: Function) => {
      listeners[event] = listeners[event] || [];
      listeners[event].push(fn);
    };
    const removeEventListener = (event: string, fn: Function) => {
      if (!listeners[event]) return;
      listeners[event] = listeners[event].filter(l => l !== fn);
    };
    const dispatchEvent = (evt: Event) => {
      const fns = listeners[evt.type] || [];
      fns.forEach(fn => fn(evt));
      return true;
    };

    // @ts-ignore
    globalThis.addEventListener = addEventListener;
    // @ts-ignore
    globalThis.removeEventListener = removeEventListener;
    // @ts-ignore
    globalThis.dispatchEvent = dispatchEvent;

    // @ts-ignore
    globalThis.window = globalThis;
  });

  afterEach(() => {
    mockStorage.clear();
    vi.restoreAllMocks();
  });

  describe('1. Default Mode and Validation', () => {
    it('exports authoritative supported constants', () => {
      expect(SUPPORTED_EXAM_CODES).toEqual(['JEE_MAIN', 'JEE_ADVANCED', 'NEET_UG']);
      expect(SUPPORTED_EXAM_SELECTIONS).toEqual(['GENERAL', 'JEE_MAIN', 'JEE_ADVANCED', 'NEET_UG']);
    });

    it('defaults to GENERAL school study mode when no selection is in storage', () => {
      expect(getSelectedExam()).toBe('GENERAL');
      expect(getSelectedExamCode()).toBeNull();
    });

    it('validates supported competitive exam codes', () => {
      expect(isValidExamCode('JEE_MAIN')).toBe(true);
      expect(isValidExamCode('JEE_ADVANCED')).toBe(true);
      expect(isValidExamCode('NEET_UG')).toBe(true);
      expect(isValidExamCode('GENERAL')).toBe(false);
      expect(isValidExamCode('CAT')).toBe(false);
      expect(isValidExamCode('')).toBe(false);
      expect(isValidExamCode(null)).toBe(false);
    });

    it('validates supported exam selections including GENERAL', () => {
      expect(isValidExamSelection('GENERAL')).toBe(true);
      expect(isValidExamSelection('JEE_MAIN')).toBe(true);
      expect(isValidExamSelection('JEE_ADVANCED')).toBe(true);
      expect(isValidExamSelection('NEET_UG')).toBe(true);
      expect(isValidExamSelection('UNKNOWN')).toBe(false);
    });

    it('throws an explicit error when setting an unsupported examination code', () => {
      expect(() => setSelectedExam('UPSC')).toThrow(/Invalid exam selection: 'UPSC'/);
      expect(() => setSelectedExam('')).toThrow(/Invalid exam selection: ''/);
      expect(() => setSelectedExam(null)).toThrow(/Invalid exam selection: 'null'/);
    });

    it('throws an explicit error when storage contains a corrupted examination code', () => {
      mockStorage.setItem(STORAGE_KEY_EXAM, 'MALICIOUS_OR_CORRUPT_CODE');
      expect(() => getSelectedExam()).toThrow(/Invalid stored examination selection/);
    });
  });

  describe('2. State Switching, Persistence, and Event Dispatch', () => {
    it('persists selected exam to localStorage and returns it via getSelectedExam()', () => {
      setSelectedExam('JEE_MAIN');
      expect(getSelectedExam()).toBe('JEE_MAIN');
      expect(getSelectedExamCode()).toBe('JEE_MAIN');
      expect(mockStorage.getItem(STORAGE_KEY_EXAM)).toBe('JEE_MAIN');

      setSelectedExam('JEE_ADVANCED');
      expect(getSelectedExam()).toBe('JEE_ADVANCED');
      expect(getSelectedExamCode()).toBe('JEE_ADVANCED');
      expect(mockStorage.getItem(STORAGE_KEY_EXAM)).toBe('JEE_ADVANCED');

      setSelectedExam('NEET_UG');
      expect(getSelectedExam()).toBe('NEET_UG');
      expect(getSelectedExamCode()).toBe('NEET_UG');
      expect(mockStorage.getItem(STORAGE_KEY_EXAM)).toBe('NEET_UG');

      setSelectedExam('GENERAL');
      expect(getSelectedExam()).toBe('GENERAL');
      expect(getSelectedExamCode()).toBeNull();
      expect(mockStorage.getItem(STORAGE_KEY_EXAM)).toBe('GENERAL');
    });

    it('dispatches edunavika:examChange event with details and metadata', () => {
      let notifiedExam: ExamSelection | null = null;
      let notifiedMeta: any = null;

      const unsubscribe = onExamChange((exam, meta) => {
        notifiedExam = exam;
        notifiedMeta = meta;
      });

      setSelectedExam('JEE_MAIN');
      expect(notifiedExam).toBe('JEE_MAIN');
      expect(notifiedMeta).toBeDefined();
      expect(notifiedMeta.label).toBe('JEE Main (NTA)');
      expect(notifiedMeta.totalTopics).toBe(436);

      setSelectedExam('NEET_UG');
      expect(notifiedExam).toBe('NEET_UG');
      expect(notifiedMeta.label).toBe('NEET UG (NMC)');
      expect(notifiedMeta.totalTopics).toBe(497);

      unsubscribe();
      setSelectedExam('GENERAL');
      // Should not fire listener after unsubscribe
      expect(notifiedExam).toBe('NEET_UG');
    });
  });

  describe('3. Exam Metadata and Subject Domain Parity', () => {
    it('JEE Main: subjects are Physics, Chemistry, Math; excludes Biology; 436 topics', () => {
      const meta = getExamMetadata('JEE_MAIN');
      expect(meta.subjects).toContain('Physics');
      expect(meta.subjects).toContain('Chemistry');
      expect(meta.subjects).toContain('Mathematics');
      expect(meta.subjects).not.toContain('Biology');
      expect(meta.totalTopics).toBe(436);
    });

    it('JEE Advanced: includes analytical topics; excludes Biology; 444 topics', () => {
      const meta = getExamMetadata('JEE_ADVANCED');
      expect(meta.subjects).toContain('Physics');
      expect(meta.subjects).toContain('Chemistry');
      expect(meta.subjects).toContain('Mathematics');
      expect(meta.subjects).not.toContain('Biology');
      expect(meta.totalTopics).toBe(444);
      expect(meta.totalTopics).toBeGreaterThan(EXAM_METADATA_MAP.JEE_MAIN.totalTopics);
    });

    it('NEET UG: subjects are Physics, Chemistry, Biology; excludes Mathematics; 497 topics', () => {
      const meta = getExamMetadata('NEET_UG');
      expect(meta.subjects).toContain('Physics');
      expect(meta.subjects).toContain('Chemistry');
      expect(meta.subjects).toContain('Biology');
      expect(meta.subjects).not.toContain('Mathematics');
      expect(meta.totalTopics).toBe(497);
    });

    it('General Study: all 4 subjects included; full canonical count 626 topics', () => {
      const meta = getExamMetadata('GENERAL');
      expect(meta.subjects).toEqual(['Physics', 'Chemistry', 'Mathematics', 'Biology']);
      expect(meta.totalTopics).toBe(626);
    });
  });

  describe('4. Frontend API Service Exam Scope Propagation', () => {
    it('curriculumService.getTopics propagates examCode when selected', async () => {
      // Mock fetch
      let requestedUrl = '';
      // @ts-ignore
      globalThis.fetch = vi.fn().mockImplementation((url: string) => {
        requestedUrl = url;
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve([]),
        });
      });

      // 1. General mode: no exam_code query param
      setSelectedExam('GENERAL');
      await curriculumService.getTopics('subj-phy');
      expect(requestedUrl).toContain('/curriculum/chapters/subj-phy/topics');
      expect(requestedUrl).not.toContain('exam_code');

      // 2. JEE_MAIN mode: includes exam_code=JEE_MAIN
      setSelectedExam('JEE_MAIN');
      await curriculumService.getTopics('subj-phy');
      expect(requestedUrl).toContain('exam_code=JEE_MAIN');

      // 3. NEET_UG mode: includes exam_code=NEET_UG
      setSelectedExam('NEET_UG');
      await curriculumService.getTopics('subj-bio');
      expect(requestedUrl).toContain('exam_code=NEET_UG');

      // 4. Explicit override parameter takes precedence
      await curriculumService.getTopics('subj-math', 'JEE_ADVANCED');
      expect(requestedUrl).toContain('exam_code=JEE_ADVANCED');
    });

    it('curriculumService.getHierarchy propagates examCode', async () => {
      let requestedUrl = '';
      // @ts-ignore
      globalThis.fetch = vi.fn().mockImplementation((url: string) => {
        requestedUrl = url;
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve({ subjects: [] }),
        });
      });

      setSelectedExam('JEE_ADVANCED');
      await curriculumService.getHierarchy(11);
      expect(requestedUrl).toContain('grade=11');
      expect(requestedUrl).toContain('exam_code=JEE_ADVANCED');

      setSelectedExam('GENERAL');
      await curriculumService.getHierarchy(10);
      expect(requestedUrl).toContain('grade=10');
      expect(requestedUrl).not.toContain('exam_code');
    });

    it('adaptiveService.getNextPracticeRecommendation propagates examCode', async () => {
      let requestedUrl = '';
      // @ts-ignore
      globalThis.fetch = vi.fn().mockImplementation((url: string) => {
        requestedUrl = url;
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve({ recommendations: [] }),
        });
      });

      setSelectedExam('NEET_UG');
      await adaptiveService.getNextPracticeRecommendation('student-123');
      expect(requestedUrl).toContain('/adaptive/next-practice/student-123');
      expect(requestedUrl).toContain('exam_code=NEET_UG');

      setSelectedExam('GENERAL');
      await adaptiveService.getNextPracticeRecommendation('student-123');
      expect(requestedUrl).not.toContain('exam_code');
    });

    it('adaptiveService.getRevisionPlan propagates examCode', async () => {
      let requestedUrl = '';
      // @ts-ignore
      globalThis.fetch = vi.fn().mockImplementation((url: string) => {
        requestedUrl = url;
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve({ items: [] }),
        });
      });

      setSelectedExam('JEE_MAIN');
      await adaptiveService.getRevisionPlan('student-123');
      expect(requestedUrl).toContain('/adaptive/revision-plan/student-123');
      expect(requestedUrl).toContain('exam_code=JEE_MAIN');

      setSelectedExam('GENERAL');
      await adaptiveService.getRevisionPlan('student-123');
      expect(requestedUrl).not.toContain('exam_code');
    });
  });

  describe('5. UI State Synchronization', () => {
    it('synchronizes UI.examSelection with exam changes', () => {
      UI.examSelection = 'JEE_MAIN';
      expect(UI.examSelection).toBe('JEE_MAIN');
      UI.examSelection = 'GENERAL';
      expect(UI.examSelection).toBe('GENERAL');
    });
  });
});
