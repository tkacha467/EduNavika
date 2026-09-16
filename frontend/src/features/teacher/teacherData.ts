// Authoritative Teacher Reference Data from Final Design/final desgin.html

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

export const TEACHER_CLASSES: TeacherClass[] = [
  { id: '10a', name: 'Grade 10 · A', students: 42, subject: 'Mathematics', avg: 76, trend: +4, atRisk: 5, kh: 72 },
  { id: '10b', name: 'Grade 10 · B', students: 40, subject: 'Physics', avg: 71, trend: +1, atRisk: 7, kh: 68 },
  { id: '10c', name: 'Grade 10 · C', students: 38, subject: 'Chemistry', avg: 79, trend: +6, atRisk: 3, kh: 74 },
  { id: '10d', name: 'Grade 10 · D', students: 41, subject: 'Biology', avg: 82, trend: +2, atRisk: 2, kh: 79 },
];

export const TEACHER_STUDENTS: TeacherStudent[] = [
  { id: 's1', name: 'Aarav Sharma', initials: 'AS', avg: 76, trend: +6, kh: 74, risk: 'low', weak: '—', events: 1, last: 'Today', status: 'ok' },
  { id: 's2', name: 'Diya Menon', initials: 'DM', avg: 88, trend: +3, kh: 84, risk: 'low', weak: '—', events: 0, last: 'Today', status: 'ok' },
  { id: 's3', name: 'Rohan Verma', initials: 'RV', avg: 54, trend: -9, kh: 48, risk: 'high', weak: 'Light & Refraction', events: 2, last: '2 days ago', status: 'risk' },
  { id: 's4', name: 'Ishita Rao', initials: 'IR', avg: 63, trend: -4, kh: 59, risk: 'medium', weak: 'Chemical Reactions', events: 1, last: 'Yesterday', status: 'watch' },
  { id: 's5', name: 'Kabir Singh', initials: 'KS', avg: 47, trend: -11, kh: 41, risk: 'high', weak: 'Trigonometry, Probability', events: 3, last: '5 days ago', status: 'risk' },
  { id: 's6', name: 'Ananya Iyer', initials: 'AI', avg: 81, trend: +2, kh: 77, risk: 'low', weak: '—', events: 0, last: 'Today', status: 'ok' },
  { id: 's7', name: 'Vikram Joshi', initials: 'VJ', avg: 59, trend: -3, kh: 55, risk: 'medium', weak: 'Nationalism in India', events: 1, last: '3 days ago', status: 'watch' },
  { id: 's8', name: 'Meera Pillai', initials: 'MP', avg: 72, trend: +5, kh: 68, risk: 'low', weak: 'Letter Writing', events: 0, last: 'Yesterday', status: 'ok' },
  { id: 's9', name: 'Arjun Reddy', initials: 'AR', avg: 66, trend: +1, kh: 62, risk: 'medium', weak: 'Acids & Bases', events: 1, last: 'Yesterday', status: 'watch' },
  { id: 's10', name: 'Sara Khan', initials: 'SK', avg: 84, trend: +4, kh: 80, risk: 'low', weak: '—', events: 0, last: 'Today', status: 'ok' },
];

export const CLASS_FORGETTING: ClassForgetting[] = [
  { student: 'Rohan Verma', topic: 'Light — Reflection & Refraction', gap: '18 days', drop: '78% → 41%', kh: 41, severity: 'high' },
  { student: 'Kabir Singh', topic: 'Trigonometry', gap: '21 days', drop: '70% → 38%', kh: 38, severity: 'high' },
  { student: 'Rohan Verma', topic: 'Electricity & Circuits', gap: '9 days', drop: '72% → 48%', kh: 48, severity: 'high' },
  { student: 'Ishita Rao', topic: 'Chemical Reactions', gap: '16 days', drop: '84% → 62%', kh: 62, severity: 'medium' },
  { student: 'Vikram Joshi', topic: 'Nationalism in India', gap: '19 days', drop: '72% → 55%', kh: 55, severity: 'medium' },
];

export const TEACHER_ASSESSMENTS: TeacherAssessmentItem[] = [
  { id: 'a1', title: 'Chemical Reactions — Set 2', subject: 'Chemistry', questions: 20, taken: 39, avg: 74, status: 'completed', date: 'Sep 12, 2026' },
  { id: 'a2', title: 'Trigonometry — Set 3', subject: 'Mathematics', questions: 20, taken: 41, avg: 68, status: 'completed', date: 'Sep 10, 2026' },
  { id: 'a3', title: 'Light — Reflection', subject: 'Physics', questions: 20, taken: 38, avg: 52, status: 'completed', date: 'Aug 28, 2026' },
  { id: 'a4', title: 'Grammar — Tenses', subject: 'English', questions: 15, taken: 0, avg: 0, status: 'draft', date: '—' },
  { id: 'a5', title: 'Electricity & Circuits', subject: 'Physics', questions: 25, taken: 0, avg: 0, status: 'scheduled', date: 'Sep 18, 2026' },
];

export const TEACHER_CONTENT: TeacherContentItem[] = [
  { title: 'Forgetting Curves & Revision Planning', type: 'PDF', subject: 'Study Skills', size: '2.4 MB', updated: '2 days ago' },
  { title: 'Quadratic Equations — Complete Notes', type: 'Notes', subject: 'Mathematics', size: '1.8 MB', updated: '5 days ago' },
  { title: 'Electricity — Video Lecture 1', type: 'Video', subject: 'Physics', size: '48 min', updated: '1 week ago' },
  { title: 'Chemical Reactions — Practice Set', type: 'Practice', subject: 'Chemistry', size: '30 questions', updated: '1 week ago' },
  { title: 'Life Processes — Presentation', type: 'Presentation', subject: 'Biology', size: '8.2 MB', updated: '2 weeks ago' },
];
