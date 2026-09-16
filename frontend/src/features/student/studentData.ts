// Authoritative Reference Data from Final Design/final desgin.html

export const REVISION_QUEUE = [
  { subject: 'Physics', topic: 'Electricity & Circuits', kh: 42, risk: 'High', when: 'Today', reason: 'Recent accuracy dropped from 72% to 48%, last revised 9 days ago.' },
  { subject: 'Physics', topic: 'Light — Reflection & Refraction', kh: 58, risk: 'High', when: 'Today', reason: 'Knowledge health has declined over 3 consecutive practice sessions.' },
  { subject: 'Chemistry', topic: 'Organic Chemistry', kh: 35, risk: 'High', when: 'Today', reason: 'Lowest knowledge health in the subject; strong risk of forgetting.' },
  { subject: 'Mathematics', topic: 'Probability', kh: 44, risk: 'High', when: 'Today', reason: 'Not revised for 9 days; accuracy dropped 14% since last check.' },
  { subject: 'Mathematics', topic: 'Coordinate Geometry', kh: 58, risk: 'Medium', when: 'Sep 15', reason: 'Last revised 16 days ago; knowledge health is declining slowly.' },
  { subject: 'Social Studies', topic: 'Nationalism in India', kh: 58, risk: 'Medium', when: 'Sep 17', reason: 'Assigned revision this week based on your accuracy trend.' },
  { subject: 'English', topic: 'Grammar — Tenses', kh: 72, risk: 'Medium', when: 'Sep 19', reason: 'Stable but not yet strong; scheduled for routine revision.' },
  { subject: 'Chemistry', topic: 'Acids, Bases & Salts', kh: 82, risk: 'Low', when: 'Sep 21', reason: 'Solid mastery — routine reinforcement only.' },
];

export const FORGETTING_TIMELINE = [
  { when: 'Today', subject: 'Physics', topic: 'Electricity & Circuits', note: 'Revision recommended', risk: 'high', kh: 42, reason: 'Accuracy down 24% over the last 5 sessions' },
  { when: 'Today', subject: 'Chemistry', topic: 'Organic Chemistry', note: 'Revision recommended', risk: 'high', kh: 35, reason: 'Knowledge health unstable for 11 days' },
  { when: 'In 3 days', subject: 'Mathematics', topic: 'Quadratic Equations', note: 'Stable', risk: 'low', kh: 88, reason: 'Last revised 3 days ago; strong retention' },
  { when: 'In 6 days', subject: 'Mathematics', topic: 'Probability', note: 'Review soon', risk: 'medium', kh: 44, reason: 'First weak signal detected 9 days ago' },
  { when: 'In 9 days', subject: 'Physics', topic: 'Light — Reflection & Refraction', note: 'Review soon', risk: 'medium', kh: 58, reason: 'Repeated forgetting events over 2 weeks' },
  { when: 'In 14 days', subject: 'Biology', topic: 'Photosynthesis', note: 'Stable', risk: 'low', kh: 93, reason: 'Mastered and consistently reinforced' },
];

export const UPCOMING_ASSESSMENTS = [
  { subject: 'Physics', topic: 'Electricity & Circuits', date: 'Sep 18, 2026', time: '10:00 AM', daysLeft: 3, prep: 72, duration: '45 min', questions: 25, difficulty: 'Medium', color: '#18A6A6' },
  { subject: 'Mathematics', topic: 'Quadratic Equations', date: 'Sep 21, 2026', time: '9:30 AM', daysLeft: 6, prep: 85, duration: '60 min', questions: 30, difficulty: 'Medium', color: '#243B6B' },
  { subject: 'Chemistry', topic: 'Chemical Reactions', date: 'Sep 25, 2026', time: '11:00 AM', daysLeft: 10, prep: 64, duration: '40 min', questions: 20, difficulty: 'Easy', color: '#2E9B68' },
];

export const COMPLETED_ASSESSMENTS = [
  { subject: 'Mathematics', topic: 'Trigonometry — Set 3', date: 'Sep 10, 2026', score: 78, accuracy: 78, time: '22 min', strong: ['Trig ratios', 'Standard angles'], weak: ['Identities'], kh: +6 },
  { subject: 'Science', topic: 'Chemical Reactions', date: 'Sep 05, 2026', score: 84, accuracy: 84, time: '28 min', strong: ['Balancing equations', 'Types of reactions'], weak: ['Displacement examples'], kh: +4 },
  { subject: 'Mathematics', topic: 'Coordinate Geometry', date: 'Aug 28, 2026', score: 52, accuracy: 52, time: '18 min', strong: ['Distance formula'], weak: ['Section formula', 'Midpoint'], kh: -11 },
];

export const NOTIFICATIONS = [
  { id: 1, cat: 'revision', title: 'Physics revision due today', body: 'Electricity & Circuits has dropped to 42% knowledge health. Schedule a 20-minute revision session.', time: '12 min ago', unread: true, urgent: true },
  { id: 2, cat: 'learning', title: 'Your Mathematics accuracy improved by 8%', body: 'You are now averaging 82% accuracy across Mathematics topics.', time: '1 hour ago', unread: true },
  { id: 3, cat: 'assessment', title: 'Physics assessment in 3 days', body: 'Electricity & Circuits test scheduled for Sep 18 at 10:00 AM.', time: '3 hours ago', unread: true, urgent: true },
  { id: 4, cat: 'learning', title: 'New study material available', body: '"Forgetting curves and revision planning" notes have been added for Grade 10.', time: '5 hours ago', unread: false },
  { id: 5, cat: 'academic', title: 'Timetable update', body: 'Friday Physics practical has been moved to Lab 2 at 2:30 PM.', time: 'Yesterday', unread: false },
  { id: 6, cat: 'system', title: 'EduNavika AI weekly summary is ready', body: 'View your personalized weekly learning report.', time: 'Yesterday', unread: false },
  { id: 7, cat: 'assessment', title: 'Assessment result published', body: 'Trigonometry — Set 3: 78% (Grade A-). View detailed breakdown.', time: '2 days ago', unread: false },
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

export const CLASS_WEAK_TOPICS = [
  { topic: 'Light — Reflection & Refraction', subject: 'Physics', mastery: 44, students: 11, trend: -22, severity: 'high' },
  { topic: 'Coordinate Geometry', subject: 'Mathematics', mastery: 51, students: 9, trend: -16, severity: 'high' },
  { topic: 'Organic Chemistry', subject: 'Chemistry', mastery: 38, students: 8, trend: -19, severity: 'high' },
  { topic: 'Nationalism in India', subject: 'Social Studies', mastery: 58, students: 7, trend: -11, severity: 'medium' },
  { topic: 'Probability', subject: 'Mathematics', mastery: 54, students: 6, trend: -8, severity: 'medium' },
];

export const CAL_EVENTS: Record<string, Array<{ t: string; title: string }>> = {};
(function seed() {
  const t = new Date();
  const k = (d: Date) => `${d.getFullYear()}-${d.getMonth()}-${d.getDate()}`;
  const add = (off: number, items: Array<{ t: string; title: string }>) => {
    const d = new Date(t);
    d.setDate(t.getDate() + off);
    CAL_EVENTS[k(d)] = items;
  };
  add(0, [{ t: 'revision', title: 'Physics — Electricity revision' }, { t: 'class', title: 'Mathematics · Quadratic Eq.' }, { t: 'ai', title: 'EduNavika AI recommends Chemistry revision' }]);
  add(1, [{ t: 'class', title: 'Physics · Light' }, { t: 'revision', title: 'Chemistry — Organic revision' }]);
  add(2, [{ t: 'revision', title: 'Mathematics — Probability' }]);
  add(3, [{ t: 'exam', title: 'Physics assessment — Electricity' }, { t: 'class', title: 'Chemistry · Periodic Table' }]);
  add(6, [{ t: 'exam', title: 'Mathematics assessment — Quadratic' }]);
  add(10, [{ t: 'exam', title: 'Chemistry assessment — Reactions' }]);
  add(14, [{ t: 'holiday', title: 'School holiday' }]);
  add(-1, [{ t: 'done', title: 'Trigonometry practice ✓' }]);
  add(-2, [{ t: 'done', title: 'Light — MCQ check ✓' }]);
  add(-4, [{ t: 'done', title: 'Reading Comprehension ✓' }]);
})();
export const calKey = (d: Date) => `${d.getFullYear()}-${d.getMonth()}-${d.getDate()}`;
