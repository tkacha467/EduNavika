// Curriculum Service: Standards, Chapters, Topics, and Subjects

import { api } from './api';
import { Standard, Chapter, Topic, Subject } from '../types';

export const APPROVED_SUBJECTS: Subject[] = [
  {
    id: 'math',
    name: 'Mathematics',
    code: 'MTH',
    color: '#243B6B',
    bg: '#E8EDF7',
    mastery: 0,
    kh: 0,
    risk: 'low',
    topics: 12,
    done: 0,
    topicList: [
      { id: 'c3dd6779-9b5b-411c-9ade-07e241713835', chapter_id: 'ch_math_1', title: 'Quadratic Equations', name: 'Quadratic Equations', order_index: 1, mastery: 0, kh: 0, risk: 'ok', last: 'Not started', next: 'Ready', status: 'ok' },
      { id: 'a5d04c19-6e6b-4a88-a23b-414f71308ba9', chapter_id: 'ch_math_1', title: 'Trigonometry', name: 'Trigonometry', order_index: 2, mastery: 0, kh: 0, risk: 'ok', last: 'Not started', next: 'Ready', status: 'ok' },
      { id: '17550e06-fb15-412d-b6a9-97d3c3848c70', chapter_id: 'ch_math_2', title: 'Coordinate Geometry', name: 'Coordinate Geometry', order_index: 3, mastery: 0, kh: 0, risk: 'ok', last: 'Not started', next: 'Ready', status: 'ok' },
      { id: 'dba2e106-7967-4de4-892b-934b06a17b2f', chapter_id: 'ch_math_2', title: 'Probability', name: 'Probability', order_index: 4, mastery: 0, kh: 0, risk: 'ok', last: 'Not started', next: 'Ready', status: 'ok' },
      { id: '20d70d12-d01a-44d7-82be-772d609eb4f5', chapter_id: 'ch_math_3', title: 'Statistics', name: 'Statistics', order_index: 5, mastery: 0, kh: 0, risk: 'ok', last: 'Not started', next: 'Ready', status: 'ok' },
      { id: 'e84e1b11-f928-4b38-93ad-738af5c0b1e5', chapter_id: 'ch_math_3', title: 'Real Numbers & Polynomials', name: 'Real Numbers & Polynomials', order_index: 6, mastery: 0, kh: 0, risk: 'ok', last: 'Not started', next: 'Ready', status: 'ok' },
      { id: '1d70ba4e-6c09-432c-b740-604677902d40', chapter_id: 'ch_math_3', title: 'Arithmetic Progressions', name: 'Arithmetic Progressions', order_index: 7, mastery: 0, kh: 0, risk: 'ok', last: 'Not started', next: 'Ready', status: 'ok' },
    ],
  },
  {
    id: 'phy',
    name: 'Physics',
    code: 'PHY',
    color: '#18A6A6',
    bg: '#E3F5F5',
    mastery: 0,
    kh: 0,
    risk: 'low',
    topics: 10,
    done: 0,
    topicList: [
      { id: 'ea3cb4fd-f34d-409b-b0f6-d69b70db05b0', chapter_id: 'ch_phy_1', title: 'Electricity & Circuits', name: 'Electricity & Circuits', order_index: 1, mastery: 0, kh: 0, risk: 'ok', last: 'Not started', next: 'Ready', status: 'ok' },
      { id: 'd8e3396b-eb3e-4bb6-9ee7-46031bcc7426', chapter_id: 'ch_phy_1', title: 'Light — Reflection & Refraction', name: 'Light — Reflection & Refraction', order_index: 2, mastery: 0, kh: 0, risk: 'ok', last: 'Not started', next: 'Ready', status: 'ok' },
      { id: 'p3', chapter_id: 'ch_phy_2', title: 'Motion & Force', name: 'Motion & Force', order_index: 3, mastery: 0, kh: 0, risk: 'ok', last: 'Not started', next: 'Ready', status: 'ok' },
      { id: 'p4', chapter_id: 'ch_phy_2', title: 'Work, Energy & Power', name: 'Work, Energy & Power', order_index: 4, mastery: 0, kh: 0, risk: 'ok', last: 'Not started', next: 'Ready', status: 'ok' },
    ],
  },
  {
    id: 'chem',
    name: 'Chemistry',
    code: 'CHM',
    color: '#2E9B68',
    bg: '#E7F5EE',
    mastery: 0,
    kh: 0,
    risk: 'low',
    topics: 9,
    done: 0,
    topicList: [
      { id: '5a321a44-bc06-4db4-a50f-5e53f913b612', chapter_id: 'ch_chm_1', title: 'Chemical Reactions', name: 'Chemical Reactions', order_index: 1, mastery: 0, kh: 0, risk: 'ok', last: 'Not started', next: 'Ready', status: 'ok' },
      { id: 'efee2da2-bd20-42bb-ad01-df2516530b1f', chapter_id: 'ch_chm_1', title: 'Acids, Bases & Salts', name: 'Acids, Bases & Salts', order_index: 2, mastery: 0, kh: 0, risk: 'ok', last: 'Not started', next: 'Ready', status: 'ok' },
      { id: '9b029f78-a6e2-4776-93a1-0af927cfea40', chapter_id: 'ch_chm_2', title: 'Organic Chemistry', name: 'Organic Chemistry', order_index: 3, mastery: 0, kh: 0, risk: 'ok', last: 'Not started', next: 'Ready', status: 'ok' },
      { id: '0a40d615-e590-4088-bbb5-3ab26de1c1e4', chapter_id: 'ch_chm_2', title: 'Periodic Table', name: 'Periodic Table', order_index: 4, mastery: 0, kh: 0, risk: 'ok', last: 'Not started', next: 'Ready', status: 'ok' },
    ],
  },
  {
    id: 'bio',
    name: 'Biology',
    code: 'BIO',
    color: '#E9A23B',
    bg: '#FDF3E3',
    mastery: 0,
    kh: 0,
    risk: 'low',
    topics: 8,
    done: 0,
    topicList: [
      { id: '203b6750-6dcf-4dfc-89fd-61ca38de5fc0', chapter_id: 'f55ff549-404e-4152-9049-a6039b70d441', title: 'Life Processes', name: 'Life Processes', order_index: 1, mastery: 0, kh: 0, risk: 'ok', last: 'Not started', next: 'Ready', status: 'ok' },
      { id: 'edd6f28b-9bad-41e8-a268-8fdbca0b338a', chapter_id: '76a14754-5105-443e-8aac-ed7847d161a7', title: 'Control and Coordination', name: 'Control and Coordination', order_index: 2, mastery: 0, kh: 0, risk: 'ok', last: 'Not started', next: 'Ready', status: 'ok' },
      { id: '712ce1df-cda6-4b11-ae3e-554ce99666cf', chapter_id: 'c2a4dffb-03b7-4a2f-a9a7-7689f7087a97', title: 'Heredity & Evolution', name: 'Heredity & Evolution', order_index: 3, mastery: 0, kh: 0, risk: 'ok', last: 'Not started', next: 'Ready', status: 'ok' },
    ],
  },
  {
    id: 'eng',
    name: 'English',
    code: 'ENG',
    color: '#7C5CD6',
    bg: '#F0EBFB',
    mastery: 0,
    kh: 0,
    risk: 'low',
    topics: 7,
    done: 0,
    topicList: [
      { id: '78c9fedc-72e2-47ff-9ea4-56854e510e43', chapter_id: 'ch_eng_1', title: 'A Letter to God', name: 'A Letter to God', order_index: 1, mastery: 0, kh: 0, risk: 'ok', last: 'Not started', next: 'Ready', status: 'ok' },
      { id: '01333c04-a84b-4171-817a-b62d8ea8f645', chapter_id: 'ch_eng_1', title: 'Nelson Mandela: Long Walk to Freedom', name: 'Nelson Mandela: Long Walk to Freedom', order_index: 2, mastery: 0, kh: 0, risk: 'ok', last: 'Not started', next: 'Ready', status: 'ok' },
      { id: 'b47e3404-0988-4738-b3f9-93bf30ea38c6', chapter_id: 'ch_eng_2', title: 'Two Stories about Flying', name: 'Two Stories about Flying', order_index: 3, mastery: 0, kh: 0, risk: 'ok', last: 'Not started', next: 'Ready', status: 'ok' },
    ],
  },
  {
    id: 'sst',
    name: 'Social Studies',
    code: 'SST',
    color: '#E56B6F',
    bg: '#FCEAEB',
    mastery: 0,
    kh: 0,
    risk: 'low',
    topics: 11,
    done: 0,
    topicList: [
      { id: 's1', chapter_id: 'ch_sst_1', title: 'Nationalism in India', name: 'Nationalism in India', order_index: 1, mastery: 0, kh: 0, risk: 'ok', last: 'Not started', next: 'Ready', status: 'ok' },
      { id: 's2', chapter_id: 'ch_sst_1', title: 'Resources & Development', name: 'Resources & Development', order_index: 2, mastery: 0, kh: 0, risk: 'ok', last: 'Not started', next: 'Ready', status: 'ok' },
      { id: 's3', chapter_id: 'ch_sst_2', title: 'Federalism', name: 'Federalism', order_index: 3, mastery: 0, kh: 0, risk: 'ok', last: 'Not started', next: 'Ready', status: 'ok' },
    ],
  },
];

export interface HierarchyTopic {
  id: string;
  title: string;
  topic_order: number;
  content_available: boolean;
  content_count: number;
  practice_available: boolean;
  source_document?: string;
  source_page?: number;
}

export interface HierarchyChapter {
  id: string;
  chapter_number: number;
  title: string;
  total_topics: number;
  topics: HierarchyTopic[];
}

export interface HierarchySubject {
  id: string;
  name: string;
  code: string;
  total_chapters: number;
  chapters: HierarchyChapter[];
}

export interface CurriculumHierarchyResponse {
  standard_grade: number;
  standard_name: string;
  total_subjects: number;
  subjects: HierarchySubject[];
}

export class CurriculumService {
  public async getStandards(): Promise<Standard[]> {
    try {
      return await api.get<Standard[]>('/curriculum/standards');
    } catch {
      return [{ id: 'std-10', grade_number: 10, curriculum_framework: 'GSEB', academic_year: '2026-2027' }];
    }
  }

  public async getChapters(standardId: string): Promise<Chapter[]> {
    try {
      return await api.get<Chapter[]>(`/curriculum/standards/${standardId}/chapters`);
    } catch {
      return [];
    }
  }

  public async getTopics(chapterId: string): Promise<Topic[]> {
    try {
      return await api.get<Topic[]>(`/curriculum/chapters/${chapterId}/topics`);
    } catch {
      return [];
    }
  }

  public async getHierarchy(grade: number = 10): Promise<CurriculumHierarchyResponse | null> {
    try {
      return await api.get<CurriculumHierarchyResponse>(`/curriculum/hierarchy?grade=${grade}`);
    } catch (err) {
      console.debug('Failed to fetch hierarchy:', err);
      return null;
    }
  }

  public async getTopicContent(topicId: string): Promise<any[]> {
    try {
      return await api.get<any[]>(`/topics/${topicId}/content`);
    } catch (err) {
      console.debug('Failed to fetch topic content:', err);
      return [];
    }
  }

  public getSubjects(): Subject[] {
    return APPROVED_SUBJECTS;
  }

  public getSubjectById(id: string): Subject | undefined {
    return APPROVED_SUBJECTS.find(s => s.id === id);
  }

  public getTopicById(topicId: string): { topic: Topic; subject: Subject } | null {
    for (const subj of APPROVED_SUBJECTS) {
      const top = subj.topicList.find(t => t.id === topicId);
      if (top) return { topic: top, subject: subj };
    }
    return null;
  }
}

export const curriculumService = new CurriculumService();
export const SUBJECTS = APPROVED_SUBJECTS;

