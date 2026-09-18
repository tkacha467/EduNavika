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
      { id: 'm1', chapter_id: 'ch_math_1', title: 'Quadratic Equations', name: 'Quadratic Equations', order_index: 1, mastery: 0, kh: 0, risk: 'ok', last: 'Not started', next: 'Ready', status: 'ok' },
      { id: 'm2', chapter_id: 'ch_math_1', title: 'Trigonometry', name: 'Trigonometry', order_index: 2, mastery: 0, kh: 0, risk: 'ok', last: 'Not started', next: 'Ready', status: 'ok' },
      { id: 'm3', chapter_id: 'ch_math_2', title: 'Coordinate Geometry', name: 'Coordinate Geometry', order_index: 3, mastery: 0, kh: 0, risk: 'ok', last: 'Not started', next: 'Ready', status: 'ok' },
      { id: 'm4', chapter_id: 'ch_math_2', title: 'Probability', name: 'Probability', order_index: 4, mastery: 0, kh: 0, risk: 'ok', last: 'Not started', next: 'Ready', status: 'ok' },
      { id: 'm5', chapter_id: 'ch_math_3', title: 'Statistics', name: 'Statistics', order_index: 5, mastery: 0, kh: 0, risk: 'ok', last: 'Not started', next: 'Ready', status: 'ok' },
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
      { id: 'p1', chapter_id: 'ch_phy_1', title: 'Electricity & Circuits', name: 'Electricity & Circuits', order_index: 1, mastery: 0, kh: 0, risk: 'ok', last: 'Not started', next: 'Ready', status: 'ok' },
      { id: 'p2', chapter_id: 'ch_phy_1', title: 'Light — Reflection & Refraction', name: 'Light — Reflection & Refraction', order_index: 2, mastery: 0, kh: 0, risk: 'ok', last: 'Not started', next: 'Ready', status: 'ok' },
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
      { id: 'c1', chapter_id: 'ch_chm_1', title: 'Chemical Reactions', name: 'Chemical Reactions', order_index: 1, mastery: 0, kh: 0, risk: 'ok', last: 'Not started', next: 'Ready', status: 'ok' },
      { id: 'c2', chapter_id: 'ch_chm_1', title: 'Acids, Bases & Salts', name: 'Acids, Bases & Salts', order_index: 2, mastery: 0, kh: 0, risk: 'ok', last: 'Not started', next: 'Ready', status: 'ok' },
      { id: 'c3', chapter_id: 'ch_chm_2', title: 'Organic Chemistry', name: 'Organic Chemistry', order_index: 3, mastery: 0, kh: 0, risk: 'ok', last: 'Not started', next: 'Ready', status: 'ok' },
      { id: 'c4', chapter_id: 'ch_chm_2', title: 'Periodic Table', name: 'Periodic Table', order_index: 4, mastery: 0, kh: 0, risk: 'ok', last: 'Not started', next: 'Ready', status: 'ok' },
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
      { id: 'b1', chapter_id: 'ch_bio_1', title: 'Photosynthesis', name: 'Photosynthesis', order_index: 1, mastery: 0, kh: 0, risk: 'ok', last: 'Not started', next: 'Ready', status: 'ok' },
      { id: 'b2', chapter_id: 'ch_bio_1', title: 'Life Processes', name: 'Life Processes', order_index: 2, mastery: 0, kh: 0, risk: 'ok', last: 'Not started', next: 'Ready', status: 'ok' },
      { id: 'b3', chapter_id: 'ch_bio_2', title: 'Heredity & Evolution', name: 'Heredity & Evolution', order_index: 3, mastery: 0, kh: 0, risk: 'ok', last: 'Not started', next: 'Ready', status: 'ok' },
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
      { id: 'e1', chapter_id: 'ch_eng_1', title: 'Reading Comprehension', name: 'Reading Comprehension', order_index: 1, mastery: 0, kh: 0, risk: 'ok', last: 'Not started', next: 'Ready', status: 'ok' },
      { id: 'e2', chapter_id: 'ch_eng_1', title: 'Grammar — Tenses', name: 'Grammar — Tenses', order_index: 2, mastery: 0, kh: 0, risk: 'ok', last: 'Not started', next: 'Ready', status: 'ok' },
      { id: 'e3', chapter_id: 'ch_eng_2', title: 'Letter Writing', name: 'Letter Writing', order_index: 3, mastery: 0, kh: 0, risk: 'ok', last: 'Not started', next: 'Ready', status: 'ok' },
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
