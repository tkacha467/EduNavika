// Authoritative Student Reference Data for EduNavika

export const REVISION_QUEUE: Array<{
  subject: string;
  topic: string;
  kh: number;
  risk: string;
  when: string;
  reason: string;
}> = [];

export const FORGETTING_TIMELINE: Array<{
  when: string;
  subject: string;
  topic: string;
  note: string;
  risk: string;
  kh: number;
  reason: string;
}> = [];

export const UPCOMING_ASSESSMENTS: Array<{
  subject: string;
  topic: string;
  date: string;
  time: string;
  daysLeft: number;
  prep: number;
  duration: string;
  questions: number;
  difficulty: string;
  color: string;
}> = [];

export const COMPLETED_ASSESSMENTS: Array<{
  subject: string;
  topic: string;
  date: string;
  score: number;
  accuracy: number;
  time: string;
  strong: string[];
  weak: string[];
  kh: number;
}> = [];

export const NOTIFICATIONS = [
  { id: 1, cat: 'system', title: 'Welcome to EduNavika', body: 'Your learning workspace is active. Take your first practice quiz or diagnostic assessment to calibrate your knowledge health.', time: 'Just now', unread: false },
  { id: 2, cat: 'academic', title: 'Curriculum assigned for Grade 10', body: 'All 6 core subjects (Math, Physics, Chemistry, Biology, English, SST) are ready in your portal.', time: '1 hour ago', unread: false },
  { id: 3, cat: 'assessment', title: 'Diagnostic assessment scheduled', body: 'Physics & Mathematics baseline diagnostic checks are ready.', time: 'Today', unread: false, urgent: false },
];

export const TIMETABLE = {
  days: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri'],
  periods: [
    { time: '08:00', rows: [['Mathematics', 'Quadratic Equations', '#243B6B'], ['Physics', 'Motion & Force', '#18A6A6'], ['Mathematics', 'Trigonometry', '#243B6B'], ['Biology', 'Life Processes', '#E9A23B'], ['Mathematics', 'Probability', '#243B6B']] },
    { time: '09:00', rows: [['English', 'Reading Comp.', '#7C5CD6'], ['Chemistry', 'Chemical Reactions', '#2E9B68'], ['Physics', 'Light', '#18A6A6'], ['English', 'Grammar — Tenses', '#7C5CD6'], ['Chemistry', 'Acids & Bases', '#2E9B68']] },
    { time: '10:00', rows: [['—', 'Break', '#E4E8EF'], ['—', 'Break', '#E4E8EF'], ['—', 'Break', '#E4E8EF'], ['—', 'Break', '#E4E8EF'], ['—', 'Break', '#E4E8EF']] },
    { time: '10:30', rows: [['Physics', 'Electricity', '#18A6A6'], ['Mathematics', 'Coordinate Geometry', '#243B6B'], ['Chemistry', 'Organic Chemistry', '#2E9B68'], ['Social Studies', 'Nationalism', '#E56B6F'], ['Biology', 'Heredity', '#E9A23B']] },
    { time: '11:30', rows: [['Biology', 'Photosynthesis', '#E9A23B'], ['English', 'Letter Writing', '#7C5CD6'], ['Social Studies', 'Federalism', '#E56B6F'], ['Physics', 'Work & Energy', '#18A6A6'], ['Physical Ed.', '—', '#7C5CD6']] },
    { time: '12:30', rows: [['—', 'Lunch', '#E4E8EF'], ['—', 'Lunch', '#E4E8EF'], ['—', 'Lunch', '#E4E8EF'], ['—', 'Lunch', '#E4E8EF'], ['—', 'Lunch', '#E4E8EF']] },
    { time: '01:30', rows: [['Social Studies', 'Resources', '#E56B6F'], ['Biology', 'Life Processes', '#E9A23B'], ['Physics', 'Practical', '#18A6A6'], ['Mathematics', 'Statistics', '#243B6B'], ['Chemistry', 'Practical', '#2E9B68']] },
    { time: '02:30', rows: [['Chemistry', 'Periodic Table', '#2E9B68'], ['Social Studies', 'Nationalism', '#E56B6F'], ['English', 'Comprehension', '#7C5CD6'], ['Physics', 'Electricity', '#18A6A6'], ['Mathematics', 'Quadratic Eq.', '#243B6B']] },
  ],
};

export const CLASS_WEAK_TOPICS: Array<{
  topic: string;
  subject: string;
  mastery: number;
  students: number;
  trend: number;
  severity: string;
}> = [];

