// Authoritative Teacher Reference Data for EduNavika

export interface TeacherClass {
  id: string;
  name: string;
  students: number;
  subject: string;
  avg: number;
  trend: number;
  atRisk: number;
  kh: number;
}

export interface TeacherStudent {
  id: string;
  name: string;
  initials: string;
  avg: number;
  trend: number;
  kh: number;
  risk: string;
  weak: string;
  events: number;
  last: string;
  status: 'ok' | 'watch' | 'risk';
}

export interface ClassForgetting {
  student: string;
  topic: string;
  gap: string;
  drop: string;
  kh: number;
  severity: 'high' | 'medium';
}

export interface TeacherAssessmentItem {
  id: string;
  title: string;
  subject: string;
  questions: number;
  taken: number;
  avg: number;
  status: 'completed' | 'draft' | 'scheduled';
  date: string;
}

export interface TeacherContentItem {
  title: string;
  type: 'PDF' | 'Notes' | 'Video' | 'Practice' | 'Presentation';
  subject: string;
  size: string;
  updated: string;
}

export const TEACHER_CLASSES: TeacherClass[] = [];

export const TEACHER_STUDENTS: TeacherStudent[] = [];

export const CLASS_FORGETTING: ClassForgetting[] = [];

export const TEACHER_ASSESSMENTS: TeacherAssessmentItem[] = [];

export const TEACHER_CONTENT: TeacherContentItem[] = [];

