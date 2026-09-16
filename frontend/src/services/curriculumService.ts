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
    mastery: 82,
    kh: 76,
    risk: 'low',
    topics: 12,
    done: 9,
    topicList: [
      { id: 'm1', chapter_id: 'ch_math_1', title: 'Quadratic Equations', name: 'Quadratic Equations', order_index: 1, mastery: 88, kh: 81, risk: 'low', last: '3 days ago', next: 'in 12 days', status: 'strong' },
      { id: 'm2', chapter_id: 'ch_math_1', title: 'Trigonometry', name: 'Trigonometry', order_index: 2, mastery: 74, kh: 68, risk: 'medium', last: '1 day ago', next: 'in 4 days', status: 'steady' },
      { id: 'm3', chapter_id: 'ch_math_2', title: 'Coordinate Geometry', name: 'Coordinate Geometry', order_index: 3, mastery: 52, kh: 58, risk: 'medium', last: '16 days ago', next: 'today', status: 'review' },
      { id: 'm4', chapter_id: 'ch_math_2', title: 'Probability', name: 'Probability', order_index: 4, mastery: 41, kh: 44, risk: 'high', last: '9 days ago', next: 'today', status: 'risk' },
      { id: 'm5', chapter_id: 'ch_math_3', title: 'Statistics', name: 'Statistics', order_index: 5, mastery: 91, kh: 87, risk: 'low', last: '2 days ago', next: 'in 14 days', status: 'strong' },
    ],
  },
  {
    id: 'phy',
    name: 'Physics',
    code: 'PHY',
    color: '#18A6A6',
    bg: '#E3F5F5',
    mastery: 68,
    kh: 61,
    risk: 'high',
    topics: 10,
    done: 6,
    topicList: [
      { id: 'p1', chapter_id: 'ch_phy_1', title: 'Electricity & Circuits', name: 'Electricity & Circuits', order_index: 1, mastery: 48, kh: 42, risk: 'high', last: '9 days ago', next: 'today', status: 'risk' },
      { id: 'p2', chapter_id: 'ch_phy_1', title: 'Light — Reflection & Refraction', name: 'Light — Reflection & Refraction', order_index: 2, mastery: 61, kh: 58, risk: 'high', last: '12 days ago', next: 'today', status: 'risk' },
      { id: 'p3', chapter_id: 'ch_phy_2', title: 'Motion & Force', name: 'Motion & Force', order_index: 3, mastery: 82, kh: 78, risk: 'low', last: '2 days ago', next: 'in 10 days', status: 'strong' },
      { id: 'p4', chapter_id: 'ch_phy_2', title: 'Work, Energy & Power', name: 'Work, Energy & Power', order_index: 4, mastery: 71, kh: 67, risk: 'medium', last: '6 days ago', next: 'in 6 days', status: 'steady' },
    ],
  },
  {
    id: 'chem',
    name: 'Chemistry',
    code: 'CHM',
    color: '#2E9B68',
    bg: '#E7F5EE',
    mastery: 79,
    kh: 73,
    risk: 'medium',
    topics: 9,
    done: 7,
    topicList: [
      { id: 'c1', chapter_id: 'ch_chm_1', title: 'Chemical Reactions', name: 'Chemical Reactions', order_index: 1, mastery: 84, kh: 80, risk: 'low', last: '3 days ago', next: 'in 10 days', status: 'strong' },
      { id: 'c2', chapter_id: 'ch_chm_1', title: 'Acids, Bases & Salts', name: 'Acids, Bases & Salts', order_index: 2, mastery: 86, kh: 82, risk: 'low', last: '2 days ago', next: 'in 14 days', status: 'strong' },
      { id: 'c3', chapter_id: 'ch_chm_2', title: 'Organic Chemistry', name: 'Organic Chemistry', order_index: 3, mastery: 38, kh: 35, risk: 'high', last: '11 days ago', next: 'today', status: 'risk' },
      { id: 'c4', chapter_id: 'ch_chm_2', title: 'Periodic Table', name: 'Periodic Table', order_index: 4, mastery: 76, kh: 71, risk: 'medium', last: '5 days ago', next: 'in 7 days', status: 'steady' },
    ],
  },
  {
    id: 'bio',
    name: 'Biology',
    code: 'BIO',
    color: '#E9A23B',
    bg: '#FDF3E3',
    mastery: 91,
    kh: 88,
    risk: 'low',
    topics: 8,
    done: 8,
    topicList: [
      { id: 'b1', chapter_id: 'ch_bio_1', title: 'Photosynthesis', name: 'Photosynthesis', order_index: 1, mastery: 93, kh: 90, risk: 'low', last: '1 day ago', next: 'in 18 days', status: 'strong' },
      { id: 'b2', chapter_id: 'ch_bio_1', title: 'Life Processes', name: 'Life Processes', order_index: 2, mastery: 88, kh: 85, risk: 'low', last: '2 days ago', next: 'in 15 days', status: 'strong' },
      { id: 'b3', chapter_id: 'ch_bio_2', title: 'Heredity & Evolution', name: 'Heredity & Evolution', order_index: 3, mastery: 91, kh: 88, risk: 'low', last: '3 days ago', next: 'in 12 days', status: 'strong' },
    ],
  },
  {
    id: 'eng',
    name: 'English',
    code: 'ENG',
    color: '#7C5CD6',
    bg: '#F0EBFB',
    mastery: 85,
    kh: 80,
    risk: 'low',
    topics: 7,
    done: 6,
    topicList: [
      { id: 'e1', chapter_id: 'ch_eng_1', title: 'Reading Comprehension', name: 'Reading Comprehension', order_index: 1, mastery: 90, kh: 86, risk: 'low', last: '2 days ago', next: 'in 16 days', status: 'strong' },
      { id: 'e2', chapter_id: 'ch_eng_1', title: 'Grammar — Tenses', name: 'Grammar — Tenses', order_index: 2, mastery: 78, kh: 72, risk: 'medium', last: '4 days ago', next: 'in 8 days', status: 'steady' },
      { id: 'e3', chapter_id: 'ch_eng_2', title: 'Letter Writing', name: 'Letter Writing', order_index: 3, mastery: 71, kh: 66, risk: 'medium', last: '8 days ago', next: 'in 5 days', status: 'steady' },
    ],
  },
  {
    id: 'sst',
    name: 'Social Studies',
    code: 'SST',
    color: '#E56B6F',
    bg: '#FCEAEB',
    mastery: 74,
    kh: 69,
    risk: 'medium',
    topics: 11,
    done: 8,
    topicList: [
      { id: 's1', chapter_id: 'ch_sst_1', title: 'Nationalism in India', name: 'Nationalism in India', order_index: 1, mastery: 62, kh: 58, risk: 'medium', last: '17 days ago', next: 'today', status: 'review' },
      { id: 's2', chapter_id: 'ch_sst_1', title: 'Resources & Development', name: 'Resources & Development', order_index: 2, mastery: 79, kh: 74, risk: 'low', last: '4 days ago', next: 'in 11 days', status: 'strong' },
      { id: 's3', chapter_id: 'ch_sst_2', title: 'Federalism', name: 'Federalism', order_index: 3, mastery: 81, kh: 76, risk: 'low', last: '3 days ago', next: 'in 13 days', status: 'strong' },
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
