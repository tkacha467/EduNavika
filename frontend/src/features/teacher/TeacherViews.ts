// Teacher View Renderers for EduNavika

import { icon } from '../../utils/icons';
import { sparkline } from '../../utils/charts';
import {
  statBlock,
  progressBar,
  statusBadge,
  aiInsight,
  pageHead,
  closeOverlay,
  openDrawer,
  toast,
} from '../../components/common';
import { getCurrentUser } from '../../services/authService';
import { CLASS_WEAK_TOPICS } from '../student/studentData';
import {
  TEACHER_CLASSES,
  TEACHER_STUDENTS,
  CLASS_FORGETTING,
  TEACHER_ASSESSMENTS,
  TEACHER_CONTENT,
} from './teacherData';

declare const window: any;

/* ---------- Teacher Dashboard ---------- */
export function teacherDashboard(): string {
  return `
  <div class="page with-rail">
    <div class="welcome">
      <div class="welcome-c">
        <div class="welcome-l">
          <div class="hi">Good morning, Ms. Nair 👋</div>
          <h1>Here's what your classes need today.</h1>
          <p>5 students need attention, 4 high-priority forgetting events detected, and one assessment pending your approval.</p>
        </div>
        <div class="welcome-r">
          <div class="wstat"><div class="l">Classes</div><div class="v">4<small>· 161 students</small></div><div class="d">Grade 10 · A–D</div></div>
          <div class="wstat"><div class="l">Class avg</div><div class="v">76<small>%</small></div><div class="d">+4% vs last week</div></div>
          <div class="wstat"><div class="l">At risk</div><div class="v">5<small>students</small></div><div class="d">Requires intervention</div></div>
          <div class="wstat"><div class="l">Events</div><div class="v">4<small>detected</small></div><div class="d">High-priority forgetting</div></div>
        </div>
      </div>
    </div>

    <div class="grid g-4 mb-6">
      ${statBlock('Total students', '161', 'Across 4 sections', 'users')}
      ${statBlock('Class average', '76%', '+4% vs last week', 'chart', 'up')}
      ${statBlock('Assessment completion', '93%', 'Across published exams', 'check', 'up')}
      ${statBlock('Revision compliance', '78%', 'Students completing revision', 'refresh')}
    </div>

    <div class="grid g-3-1 mb-6">
      <div class="card">
        <div class="card-h"><div><h3>Students needing attention</h3><div class="sub">Based on knowledge health, trend and forgetting events</div></div><div class="right"><button class="btn btn-sm" data-go="teacher/students">All students</button></div></div>
        <table class="tbl">
          <thead><tr><th>Student</th><th>Avg</th><th>Trend</th><th>Weak topic</th><th>Events</th><th></th></tr></thead>
          <tbody>
            ${TEACHER_STUDENTS.filter(s => s.status !== 'ok').map(s => `
              <tr>
                <td><div class="flex gap-2"><div class="av sm av-i1">${s.initials}</div><span class="nm">${s.name}</span></div></td>
                <td><b>${s.avg}%</b></td>
                <td class="${s.trend >= 0 ? '' : 'coral'}" style="font-weight:700;color:${s.trend >= 0 ? 'var(--green)' : 'var(--coral)'}">${s.trend >= 0 ? '+' : ''}${s.trend}%</td>
                <td class="muted">${s.weak}</td>
                <td>${s.events ? `<span class="badge ${s.events > 1 ? 'coral' : 'amber'}">${s.events}</span>` : '—'}</td>
                <td class="right"><button class="btn btn-sm" onclick="openStudent('${s.id}')">Review</button></td>
              </tr>`).join('')}
          </tbody>
        </table>
      </div>

      <div class="flex-c">
        ${aiInsight('Class priority', '<b>Light — Reflection & Refraction</b> dropped to 44% class mastery (was 66%). 11 students affected. Consider a re-teach session this week.', 'Assign revision', `toast('Revision assigned to 11 students','','good')`)}
        ${aiInsight('Assessment ready', 'Your <b>Electricity & Circuits</b> MCQ set is ready for review. 25 questions generated and validated.', 'Review exam', `toast('Opening assessment builder…','','teal')`)}
      </div>
    </div>

    <div class="grid g-2 mb-6">
      <div class="card">
        <div class="card-h"><h3>Topics showing decline</h3><div class="right"><span class="badge amber">Class-wide</span></div></div>
        <div class="card-b">
          ${CLASS_WEAK_TOPICS.map(t => `
            <div style="padding:12px 0;border-bottom:1px solid var(--border-2)">
              <div class="flex-b mb-2">
                <div><div style="font-size:13.5px;font-weight:600">${t.topic}</div><div class="tiny">${t.subject} · ${t.students} students</div></div>
                <span class="badge ${t.severity === 'high' ? 'coral' : 'amber'}">${t.trend}%</span>
              </div>
              <div class="flex gap-2">${progressBar(t.mastery, t.mastery >= 70 ? 'green' : t.mastery >= 55 ? 'amber' : 'coral')}<b style="font-size:12px">${t.mastery}%</b></div>
            </div>`).join('')}
        </div>
      </div>
      <div class="card">
        <div class="card-h"><h3>Forgetting events</h3><div class="right"><span class="badge coral">${CLASS_FORGETTING.length} detected</span></div></div>
        <div class="card-b">
          ${CLASS_FORGETTING.map(f => `
            <div style="padding:12px 0;border-bottom:1px solid var(--border-2)">
              <div class="flex-b mb-2">
                <div><b style="font-size:13.5px">${f.student}</b><div class="tiny">${f.topic}</div></div>
                <span class="badge ${f.severity === 'high' ? 'coral' : 'amber'}">${f.gap}</span>
              </div>
              <div class="flex-b" style="font-size:11.5px;color:var(--text-3)">
                <span>KH dropped to <b style="color:var(--coral)">${f.kh}%</b></span>
                <button class="btn btn-sm" onclick="toast('Revision recommended','to ${f.student}','good')">Recommend</button>
              </div>
            </div>`).join('')}
        </div>
      </div>
    </div>

    <div class="card">
      <div class="card-h"><h3>Class performance overview</h3><div class="right"><button class="btn btn-sm" data-go="teacher/analytics">Full analytics</button></div></div>
      <div class="card-b">
        <table class="tbl">
          <thead><tr><th>Class</th><th>Students</th><th>Subject</th><th>Average</th><th>Trend</th><th>At risk</th><th>Knowledge Health</th><th></th></tr></thead>
          <tbody>
            ${TEACHER_CLASSES.map(c => `
              <tr>
                <td class="nm">${c.name}</td>
                <td>${c.students}</td>
                <td class="muted">${c.subject}</td>
                <td><b>${c.avg}%</b></td>
                <td style="color:var(--green);font-weight:700">+${c.trend}%</td>
                <td><span class="badge ${c.atRisk > 5 ? 'coral' : c.atRisk > 2 ? 'amber' : 'green'}">${c.atRisk}</span></td>
                <td style="width:160px"><div class="flex gap-2">${progressBar(c.kh, c.kh >= 70 ? 'green' : c.kh >= 55 ? 'amber' : 'coral')}<b style="font-size:12px">${c.kh}%</b></div></td>
                <td class="right"><button class="btn btn-sm" onclick="navigate('teacher/classes')">Open</button></td>
              </tr>`).join('')}
          </tbody>
        </table>
      </div>
    </div>
  </div>

  <aside class="rail">
    <div class="rail-inner">
      <div class="ai-card">
        <div class="ai-head"><div class="ai-mark">${icon('sparkles')}</div><b>EduSense AI</b></div>
        <div class="ai-body"><b>Class 10A</b> shows a 22% drop on <b>Light & Refraction</b> mastery since last week. A 30-minute re-teach session is likely to have the highest impact.</div>
        <div class="ai-actions"><button class="btn btn-sm btn-teal" onclick="toast('Re-teach session added to schedule','','good')">Schedule re-teach</button></div>
      </div>

      <div class="card">
        <div class="card-h" style="padding-bottom:12px"><h3 style="font-size:13.5px">Quick Actions</h3></div>
        <div class="card-b" style="padding-top:0;display:flex;flex-direction:column;gap:8px">
          <button class="qa-tile" onclick="openBuilder()"><div class="qi">${icon('plus')}</div><div><b>Create MCQ exam</b><span>Real-time generation</span></div></button>
          <button class="qa-tile" onclick="navigate('teacher/students')"><div class="qi" style="background:var(--coral-50);color:var(--coral)">${icon('alert')}</div><div><b>Review at-risk students</b><span>5 flagged</span></div></button>
          <button class="qa-tile" onclick="navigate('teacher/content')"><div class="qi" style="background:var(--teal-50);color:var(--teal-600)">${icon('folder')}</div><div><b>Manage content</b><span>Upload materials</span></div></button>
        </div>
      </div>
    </div>
  </aside>`;
}

/* ---------- My Classes ---------- */
export function teacherClasses(): string {
  return `
  <div class="page">
    ${pageHead('My Classes', 'Your classes', '4 sections · 161 students · Grade 10 Science stream.')}
    <div class="grid g-4 mb-6">
      ${statBlock('Total classes', '4', 'Grade 10 · A–D', 'graduation')}
      ${statBlock('Total students', '161', 'Across all sections', 'users')}
      ${statBlock('Avg. attendance', '94%', 'This term', 'check', 'up')}
      ${statBlock('At-risk students', '15', 'Need intervention', 'alert', 'down')}
    </div>
    <div class="grid g-2">
      ${TEACHER_CLASSES.map(c => `
        <div class="card hoverable pad-lg" style="cursor:pointer">
          <div class="flex-b mb-4">
            <div>
              <h3 class="h3 mb-1">${c.name}</h3>
              <div class="small">${c.subject} · ${c.students} students</div>
            </div>
            <span class="badge indigo">${c.students} students</span>
          </div>
          <div class="grid g-3 mb-4">
            <div><div class="tiny">Class average</div><div style="font-size:20px;font-weight:800;font-family:Manrope">${c.avg}%</div></div>
            <div><div class="tiny">Trend</div><div style="font-size:20px;font-weight:800;font-family:Manrope;color:var(--green)">+${c.trend}%</div></div>
            <div><div class="tiny">At risk</div><div style="font-size:20px;font-weight:800;font-family:Manrope;color:var(--coral)">${c.atRisk}</div></div>
          </div>
          <div class="flex gap-2 mb-2"><span class="tiny" style="width:100px">Knowledge health</span>${progressBar(c.kh, c.kh >= 70 ? 'green' : 'amber')}<b style="font-size:12px">${c.kh}%</b></div>
          <div class="flex gap-2 mt-3">
            <button class="btn btn-sm btn-primary" style="flex:1" onclick="toast('Opened ${c.name}','','good')">Open class</button>
            <button class="btn btn-sm" onclick="navigate('teacher/analytics')">Analytics</button>
          </div>
        </div>`).join('')}
    </div>
  </div>`;
}

/* ---------- Students ---------- */
export function teacherStudents(): string {
  return `
  <div class="page">
    ${pageHead('Students', 'All students', 'Complete overview of every student across your classes.',
      `<button class="btn" onclick="toast('Student roster exported','CSV generated','good')">${icon('download')} Export list</button>`)}

    <div class="grid g-4 mb-6">
      ${statBlock('Total students', '161', 'Grade 10 · A–D', 'users')}
      ${statBlock('Above 75%', '86', 'Consistently strong', 'award', 'up')}
      ${statBlock('50–75%', '60', 'Steady progress', 'chart')}
      ${statBlock('Below 50%', '15', 'Requires intervention', 'alert', 'down')}
    </div>

    <div class="card">
      <div class="card-h">
        <h3>All students</h3>
        <div class="right"><span class="badge grey">Showing ${TEACHER_STUDENTS.length} of 161</span></div>
      </div>
      <table class="tbl">
        <thead><tr><th>Student</th><th>Average</th><th>Trend</th><th>Knowledge Health</th><th>Weak topic</th><th>Events</th><th>Last active</th><th>Status</th><th></th></tr></thead>
        <tbody>
          ${TEACHER_STUDENTS.map(s => `
            <tr>
              <td><div class="flex gap-2"><div class="av sm av-i1">${s.initials}</div><span class="nm">${s.name}</span></div></td>
              <td><b>${s.avg}%</b></td>
              <td style="font-weight:700;color:${s.trend >= 0 ? 'var(--green)' : 'var(--coral)'}">${s.trend >= 0 ? '+' : ''}${s.trend}%</td>
              <td><div class="flex gap-2" style="width:130px">${progressBar(s.kh, s.kh >= 70 ? 'green' : s.kh >= 55 ? 'amber' : 'coral')}<b style="font-size:12px">${s.kh}%</b></div></td>
              <td class="muted">${s.weak}</td>
              <td>${s.events ? `<span class="badge ${s.events > 1 ? 'coral' : 'amber'}">${s.events}</span>` : '—'}</td>
              <td class="muted">${s.last}</td>
              <td>${s.status === 'risk' ? '<span class="badge coral dot">At risk</span>' : s.status === 'watch' ? '<span class="badge amber dot">Watch</span>' : '<span class="badge green dot">On track</span>'}</td>
              <td class="right"><button class="btn btn-sm" onclick="openStudent('${s.id}')">Open</button></td>
            </tr>`).join('')}
        </tbody>
      </table>
    </div>
  </div>`;
}

/* ---------- Student Drawer View ---------- */
export function openStudent(id: string): void {
  const s = TEACHER_STUDENTS.find(x => x.id === id);
  if (!s) return;
  openDrawer(`
    <div class="modal-h" style="border-radius:0">
      <div class="av md av-i1">${s.initials}</div>
      <div style="flex:1"><h3>${s.name}</h3><div class="sub">Grade 10 · Section A · ${s.status === 'risk' ? 'At risk' : s.status === 'watch' ? 'Needs watching' : 'On track'}</div></div>
      <button class="btn btn-sm btn-icon" onclick="closeOverlay()">${icon('x')}</button>
    </div>
    <div class="modal-b">
      <div class="grid g-3 mb-4">
        <div class="card pad-sm center"><div class="tiny">Average</div><div style="font-size:20px;font-weight:800;font-family:Manrope">${s.avg}%</div></div>
        <div class="card pad-sm center"><div class="tiny">Trend</div><div style="font-size:20px;font-weight:800;font-family:Manrope;color:${s.trend >= 0 ? 'var(--green)' : 'var(--coral)'}">${s.trend >= 0 ? '+' : ''}${s.trend}%</div></div>
        <div class="card pad-sm center"><div class="tiny">Events</div><div style="font-size:20px;font-weight:800;font-family:Manrope">${s.events}</div></div>
      </div>

      <div class="card pad-sm mb-4">
        <div class="h4 mb-3">Knowledge health by subject</div>
        ${[['Mathematics', Math.min(96, s.avg + 12)], ['Physics', Math.max(22, s.avg - 18)], ['Chemistry', Math.min(95, s.avg + 4)], ['Biology', Math.min(96, s.avg + 8)]].map(([n, v]) => `
          <div class="flex gap-2 mb-3" style="font-size:12.5px">
            <span style="flex:0 0 100px">${n}</span>
            ${progressBar(v as number, (v as number) >= 70 ? 'green' : (v as number) >= 55 ? 'amber' : 'coral')}
            <b style="width:36px;text-align:right">${v}%</b>
          </div>`).join('')}
      </div>

      <div class="card pad-sm mb-4">
        <div class="h4 mb-3">Recent MCQ history</div>
        <table class="tbl">
          <thead><tr><th>Topic</th><th>Score</th><th>Date</th></tr></thead>
          <tbody>
            ${[
              ['Trigonometry — Set 3', 78, 'Sep 10'],
              ['Chemical Reactions', 84, 'Sep 05'],
              ['Light — MCQ', 58, 'Aug 28'],
              ['Coordinate Geometry', 52, 'Aug 21']
            ].map(([t, sc, d]) => `<tr><td class="nm">${t}</td><td><span class="badge ${(sc as number) >= 75 ? 'green' : (sc as number) >= 55 ? 'amber' : 'coral'}">${sc}%</span></td><td class="muted">${d}</td></tr>`).join('')}
          </tbody>
        </table>
      </div>

      <div class="ai-card mb-4">
        <div class="ai-head"><div class="ai-mark">${icon('sparkles')}</div><b>EduSense Insight</b></div>
        <div class="ai-body">This student's <b>Physics knowledge health</b> has declined 22% over 9 days. Recommended: assign a 20-minute Electricity revision and follow up within 3 days.</div>
      </div>

      <div class="card pad-sm">
        <div class="h4 mb-3">Intervention actions</div>
        <div class="flex wrap gap-2">
          <button class="btn btn-sm" onclick="toast('Topic review assigned','to ${s.name}','good')">${icon('book')} Assign topic review</button>
          <button class="btn btn-sm" onclick="toast('Revision recommended','to ${s.name}','good')">${icon('refresh')} Recommend revision</button>
          <button class="btn btn-sm" onclick="toast('Follow-up scheduled','','good')">${icon('check')} Schedule follow-up</button>
        </div>
        <textarea class="input textarea mt-3" placeholder="Add a note about this student…"></textarea>
        <button class="btn btn-primary btn-sm mt-3" onclick="toast('Note saved','','good')">${icon('check')} Save note</button>
      </div>
    </div>`);
}

/* ---------- Subjects ---------- */
export function teacherSubjects(): string {
  return `
  <div class="page">
    ${pageHead('Subjects', 'Subjects you teach', 'Mathematics and Physics · Grade 10 · 4 sections.')}
    <div class="grid g-2">
      ${[
        { n: 'Mathematics', c: 'MTH', color: '#243B6B', bg: '#E8EDF7', topics: 12, classes: 4, avg: 76, kh: 74, weak: 'Coordinate Geometry, Probability' },
        { n: 'Physics', c: 'PHY', color: '#18A6A6', bg: '#E3F5F5', topics: 10, classes: 4, avg: 71, kh: 68, weak: 'Light & Refraction, Electricity' },
      ].map(s => `
        <div class="card pad-lg">
          <div class="flex gap-3 mb-4">
            <div class="subj-ic" style="background:${s.bg};color:${s.color};width:52px;height:52px;font-size:15px;border-radius:14px">${s.c}</div>
            <div style="flex:1"><h3 class="h3">${s.n}</h3><div class="small">${s.topics} topics · ${s.classes} classes</div></div>
          </div>
          <div class="grid g-3 mb-4">
            <div><div class="tiny">Class avg</div><div style="font-size:20px;font-weight:800;font-family:Manrope">${s.avg}%</div></div>
            <div><div class="tiny">Knowledge health</div><div style="font-size:20px;font-weight:800;font-family:Manrope">${s.kh}%</div></div>
            <div><div class="tiny">Topics</div><div style="font-size:20px;font-weight:800;font-family:Manrope">${s.topics}</div></div>
          </div>
          <div class="card pad-sm" style="background:var(--amber-50);border-color:rgba(233,162,59,.25)">
            <div class="tiny" style="font-weight:700;color:#B4731A;text-transform:uppercase;letter-spacing:.04em;margin-bottom:4px">Weak topics</div>
            <div style="font-size:13px;color:var(--text-2)">${s.weak}</div>
          </div>
          <div class="flex gap-2 mt-4">
            <button class="btn btn-primary btn-sm" style="flex:1" onclick="navigate('teacher/analytics')">Open subject</button>
            <button class="btn btn-sm" onclick="navigate('teacher/analytics')">Analytics</button>
          </div>
        </div>`).join('')}
    </div>
  </div>`;
}

/* ---------- Assessments ---------- */
export function teacherAssessments(): string {
  return `
  <div class="page">
    ${pageHead('Assessments', 'Your assessments', 'Generate fresh MCQ exams in real time, review and publish, then act on results.',
      `<button class="btn btn-primary" onclick="openBuilder()">${icon('plus')} Create MCQ exam</button>`)}

    <div class="grid g-4 mb-6">
      ${statBlock('Total assessments', '13', 'This term', 'clipboard')}
      ${statBlock('Avg. class score', '68%', '+4% this month', 'chart', 'up')}
      ${statBlock('Pending review', '1', 'Draft awaiting approval', 'alert', 'warn')}
      ${statBlock('Questions generated', '1,240', 'All curriculum-grounded', 'sparkles', 'up')}
    </div>

    <div class="card mb-6">
      <div class="card-h"><h3>Your assessments</h3></div>
      <table class="tbl">
        <thead><tr><th>Title</th><th>Subject</th><th>Questions</th><th>Submissions</th><th>Average</th><th>Status</th><th>Date</th><th></th></tr></thead>
        <tbody>
          ${TEACHER_ASSESSMENTS.map(a => `
            <tr>
              <td class="nm">${a.title}</td>
              <td class="muted">${a.subject}</td>
              <td>${a.questions}</td>
              <td>${a.taken || '—'}</td>
              <td>${a.avg ? `<b>${a.avg}%</b>` : '<span class="muted">—</span>'}</td>
              <td>${statusBadge(a.status)}</td>
              <td class="muted">${a.date}</td>
              <td class="right">
                ${a.status === 'completed' ? `<button class="btn btn-sm" onclick="toast('Viewing results for ${a.title}','','good')">Results</button>` : a.status === 'draft' ? `<button class="btn btn-sm btn-primary" onclick="openBuilder()">Review</button>` : `<button class="btn btn-sm" onclick="toast('Viewing assessment ${a.title}','','good')">View</button>`}
              </td>
            </tr>`).join('')}
        </tbody>
      </table>
    </div>

    <div class="grid g-2">
      <div class="card pad">
        <div class="h4 mb-3">${icon('sparkles', 'ic-sm')} How generation works</div>
        <div class="flex-c" style="gap:10px">
          ${[
            { l: 'Teacher selects a topic', done: true },
            { l: 'Relevant curriculum content is retrieved', done: true },
            { l: 'Fresh MCQs are generated from that content', done: true },
            { l: 'Validation & duplicate check', done: true },
            { l: 'Teacher reviews and approves', done: false },
            { l: 'Exam is published to students', done: false },
          ].map((s, i) => `
            <div class="flex gap-3" style="font-size:13px">
              <div style="width:22px;height:22px;border-radius:50%;display:grid;place-items:center;flex:0 0 auto;background:${s.done ? 'var(--green-50)' : 'var(--bg)'};color:${s.done ? 'var(--green)' : 'var(--text-3)'}">${s.done ? icon('check', 'ic-xs') : `<span style="font-size:11px;font-weight:700">${i + 1}</span>`}</div>
              <span style="color:${s.done ? 'var(--text)' : 'var(--text-3)'}">${s.l}</span>
            </div>`).join('')}
        </div>
      </div>

      <div class="card pad">
        <div class="h4 mb-3">${icon('bulb', 'ic-sm')} Quality rules</div>
        <ul style="list-style:none;font-size:13px;color:var(--text-2);line-height:1.7">
          <li>• Every question is grounded in approved curriculum material.</li>
          <li>• Retrieval and teacher approval are required safeguards.</li>
          <li>• Each new exam attempts fresh questions, checked against history.</li>
          <li>• Exactly one correct answer per question.</li>
          <li>• No unsupported facts or off-syllabus content.</li>
        </ul>
      </div>
    </div>
  </div>`;
}

/* ---------- Assignments ---------- */
export function teacherAssignments(): string {
  return `
  <div class="page">
    ${pageHead('Assignments', 'Manage assignments', 'Create, assign and grade work across your classes.', '<button class="btn btn-primary" onclick="toast(\'Create assignment wizard ready\',\'\',\'good\')">' + icon('plus') + ' New assignment</button>')}
    <div class="grid g-4 mb-6">
      ${statBlock('Active', 5, 'Currently assigned', 'edit')}
      ${statBlock('Submitted', 38, 'This week', 'check', 'up')}
      ${statBlock('Pending', 22, 'Awaiting students', 'clock', 'warn')}
      ${statBlock('Avg. score', '79%', 'Across graded work', 'award', 'up')}
    </div>
    <div class="card">
      <div class="card-h"><h3>All assignments</h3></div>
      <table class="tbl">
        <thead><tr><th>Assignment</th><th>Subject</th><th>Class</th><th>Due date</th><th>Submitted</th><th>Avg. score</th><th></th></tr></thead>
        <tbody>
          ${[
            ['Balancing chemical equations', 'Chemistry', '10A', 'Sep 17', '32/42', '84%'],
            ['Physics numericals — Electricity', 'Physics', '10B', 'Sep 19', '28/40', '—'],
            ['Essay: Nationalism in India', 'Social Studies', '10A', 'Sep 22', '12/42', '—'],
            ['Trigonometry worksheet', 'Mathematics', '10A', 'Sep 12', '40/42', '82%'],
            ['Grammar worksheet — Tenses', 'English', '10C', 'Sep 08', '38/38', '88%'],
          ].map(([a, b, c, d, e, f]) => `
            <tr>
              <td class="nm">${a}</td>
              <td class="muted">${b}</td>
              <td><span class="badge indigo">${c}</span></td>
              <td class="muted">${d}</td>
              <td>${e}</td>
              <td>${f === '—' ? '<span class="muted">—</span>' : `<b>${f}</b>`}</td>
              <td class="right"><button class="btn btn-sm" onclick="toast('Assignment details loaded','','good')">Open</button></td>
            </tr>`).join('')}
        </tbody>
      </table>
    </div>
  </div>`;
}

/* ---------- Attendance ---------- */
export function teacherAttendance(): string {
  return `
  <div class="page">
    ${pageHead('Attendance', 'Daily attendance', 'Mark and review attendance for today across your classes.', '<button class="btn btn-primary" onclick="toast(\'Today attendance marked\',\'Saved to database\',\'good\')">' + icon('check') + ' Mark today\'s attendance</button>')}
    <div class="grid g-4 mb-6">
      ${statBlock('Present today', '152', 'of 161 students', 'check', 'up')}
      ${statBlock('Absent', '9', 'Marked absent', 'alert', 'down')}
      ${statBlock('Attendance rate', '94%', 'This term', 'chart', 'up')}
      ${statBlock('Low attendance', '3', 'Below 75%', 'alert', 'warn')}
    </div>
    <div class="card mb-6">
      <div class="card-h"><h3>Today · Sep 15, 2026</h3></div>
      <table class="tbl">
        <thead><tr><th>Class</th><th>Present</th><th>Absent</th><th>Rate</th><th>Marked by</th><th></th></tr></thead>
        <tbody>
          ${[
            ['Grade 10 · A', 40, 2, '95%', 'Ms. Nair'],
            ['Grade 10 · B', 36, 4, '90%', 'Ms. Nair'],
            ['Grade 10 · C', 38, 0, '100%', 'Mr. Kumar'],
            ['Grade 10 · D', 38, 3, '93%', 'Ms. Rao'],
          ].map(([a, b, c, d, e]) => `<tr><td class="nm">${a}</td><td>${b}</td><td>${c}</td><td><b>${d}</b></td><td class="muted">${e}</td><td class="right"><button class="btn btn-sm" onclick="toast('Editing attendance for ${a}','','good')">Edit</button></td></tr>`).join('')}
        </tbody>
      </table>
    </div>
    <div class="card">
      <div class="card-h"><h3>Attendance trend — last 30 days</h3></div>
      <div class="card-b">${sparkline([88, 90, 92, 91, 93, 89, 94, 92, 95, 93, 94, 92, 93, 94, 95, 93, 94, 92, 94, 95], 600, 160, '#2E9B68')}</div>
    </div>
  </div>`;
}

/* ---------- Content ---------- */
export function teacherContent(): string {
  return `
  <div class="page">
    ${pageHead('Content', 'Content management', 'Upload, organise and publish learning materials for your subjects.', '<button class="btn btn-primary" onclick="toast(\'Upload dialog opened\',\'\',\'good\')">' + icon('plus') + ' Upload material</button>')}
    <div class="grid g-4 mb-6">
      ${statBlock('Total files', '127', 'Across all subjects', 'folder')}
      ${statBlock('Published', '114', 'Visible to students', 'check', 'up')}
      ${statBlock('Drafts', '13', 'Pending review', 'edit', 'warn')}
      ${statBlock('Downloads', '2,340', 'This month', 'download', 'up')}
    </div>
    <div class="grid g-3">
      ${TEACHER_CONTENT.map(c => `
        <div class="card hoverable pad" style="cursor:pointer" onclick="toast('Selected ${c.title}','','good')">
          <div class="flex gap-3 mb-4">
            <div class="qa-tile" style="padding:0;border:0;background:var(--indigo-50);width:44px;height:44px;justify-content:center;border-radius:11px">
              <span style="color:var(--indigo);display:grid;place-items:center">${icon(c.type === 'Video' ? 'video' : c.type === 'Presentation' ? 'layers' : c.type === 'Practice' ? 'target' : 'file')}</span>
            </div>
            <div style="flex:1;min-width:0"><div class="h4" style="font-size:13.5px;line-height:1.35">${c.title}</div><div class="tiny mt-1">${c.subject}</div></div>
          </div>
          <div class="flex-b"><span class="badge indigo">${c.type}</span><span class="tiny">${c.size} · ${c.updated}</span></div>
        </div>`).join('')}
    </div>
  </div>`;
}

/* ---------- Analytics ---------- */
export function teacherAnalytics(): string {
  return `
  <div class="page">
    ${pageHead('Analytics', 'Class and subject analytics', 'Deep analytics across performance, knowledge health, revision effectiveness and student consistency.',
      `<button class="btn" onclick="toast('Full analytical report generated','PDF downloaded','good')">${icon('download')} Export report</button>`)}

    <div class="grid g-4 mb-6">
      ${statBlock('Class average', '76%', '+4% this term', 'chart', 'up')}
      ${statBlock('Assessment completion', '93%', 'Across all exams', 'check', 'up')}
      ${statBlock('Revision compliance', '78%', 'Students completing revision', 'refresh')}
      ${statBlock('Topics at risk', '5', 'Below 60% class mastery', 'alert', 'down')}
    </div>

    <div class="grid g-2 mb-6">
      <div class="card">
        <div class="card-h"><h3>Class performance trend</h3><div class="right"><span class="badge grey">Last 8 assessments</span></div></div>
        <div class="card-b">${sparkline([62, 66, 64, 68, 71, 70, 74, 76], 600, 180, '#243B6B')}</div>
      </div>
      <div class="card">
        <div class="card-h"><h3>Score distribution</h3></div>
        <div class="card-b">
          ${[
            ['80–100%', 34, 'green'],
            ['60–79%', 71, 'indigo'],
            ['40–59%', 41, 'amber'],
            ['0–39%', 15, 'coral'],
          ].map(([n, v, c]) => `
            <div class="flex gap-3 mb-3" style="font-size:13px">
              <span style="flex:0 0 90px">${n}</span>
              ${progressBar(((v as number) / 161) * 100, c as string)}
              <b style="width:40px;text-align:right">${v}</b>
            </div>`).join('')}
        </div>
      </div>
    </div>

    <div class="card">
      <div class="card-h"><h3>Subject summary</h3></div>
      <table class="tbl">
        <thead><tr><th>Subject</th><th>Students</th><th>Class average</th><th>Trend</th><th>Knowledge health</th><th></th></tr></thead>
        <tbody>
          ${[
            ['Mathematics', 161, 76, '+4%', 74],
            ['Physics', 161, 71, '+1%', 68],
            ['Chemistry', 161, 79, '+6%', 74],
            ['Biology', 161, 82, '+2%', 79],
            ['English', 161, 80, '+5%', 78],
            ['Social Studies', 161, 73, '-2%', 69],
          ].map(([n, st, avg, t, kh]) => `
            <tr>
              <td class="nm">${n}</td>
              <td>${st}</td>
              <td><b>${avg}%</b></td>
              <td style="font-weight:700;color:${(t as string).startsWith('+') ? 'var(--green)' : 'var(--coral)'}">${t}</td>
              <td style="width:180px"><div class="flex gap-2">${progressBar(kh as number, (kh as number) >= 70 ? 'green' : 'amber')}<b style="font-size:12px">${kh}%</b></div></td>
              <td class="right"><button class="btn btn-sm" onclick="toast('Opened ${n} summary','','good')">Open</button></td>
            </tr>`).join('')}
        </tbody>
      </table>
    </div>
  </div>`;
}

/* ---------- Revision Insights ---------- */
export function teacherRevision(): string {
  return `
  <div class="page">
    ${pageHead('Revision Insights', 'Class revision overview', 'Which topics need class-wide revision and which students need individual support.')}

    <div class="grid g-4 mb-6">
      ${statBlock('High priority', 5, 'Topics needing revision', 'alert', 'down')}
      ${statBlock('Forgetting events', 5, 'Detected this week', 'refresh', 'warn')}
      ${statBlock('Students behind', 8, 'In revision compliance', 'users')}
      ${statBlock('Avg. revision rate', '78%', 'Class-wide', 'check', 'up')}
    </div>

    <div class="card mb-6">
      <div class="card-h"><h3>Class priority topics</h3><div class="right"><button class="btn btn-sm btn-primary" onclick="toast('Re-teach sessions scheduled','','good')">Schedule re-teach</button></div></div>
      <table class="tbl">
        <thead><tr><th>Topic</th><th>Subject</th><th>Class mastery</th><th>Change</th><th>Students affected</th><th>Priority</th><th></th></tr></thead>
        <tbody>
          ${CLASS_WEAK_TOPICS.map(t => `
            <tr>
              <td class="nm">${t.topic}</td>
              <td class="muted">${t.subject}</td>
              <td style="width:160px"><div class="flex gap-2">${progressBar(t.mastery, t.mastery >= 70 ? 'green' : t.mastery >= 55 ? 'amber' : 'coral')}<b style="font-size:12px">${t.mastery}%</b></div></td>
              <td style="font-weight:700;color:var(--coral)">${t.trend}%</td>
              <td>${t.students}</td>
              <td><span class="badge ${t.severity === 'high' ? 'coral' : 'amber'}">${t.severity === 'high' ? 'High' : 'Medium'}</span></td>
              <td class="right"><button class="btn btn-sm" onclick="toast('Topic added to re-teach list','','good')">Assign</button></td>
            </tr>`).join('')}
        </tbody>
      </table>
    </div>

    <div class="card">
      <div class="card-h"><h3>Forgetting events — students needing support</h3></div>
      <table class="tbl">
        <thead><tr><th>Student</th><th>Topic</th><th>Time gap</th><th>Change</th><th>KH</th><th>Severity</th><th></th></tr></thead>
        <tbody>
          ${CLASS_FORGETTING.map(f => `
            <tr>
              <td class="nm">${f.student}</td>
              <td class="muted">${f.topic}</td>
              <td>${f.gap}</td>
              <td style="color:var(--coral);font-weight:700">${f.drop}</td>
              <td><b>${f.kh}%</b></td>
              <td><span class="badge ${f.severity === 'high' ? 'coral' : 'amber'}">${f.severity === 'high' ? 'High' : 'Medium'}</span></td>
              <td class="right">
                <button class="btn btn-sm" onclick="toast('Revision recommended','to ${f.student}','good')">${icon('refresh')} Recommend</button>
              </td>
            </tr>`).join('')}
        </tbody>
      </table>
    </div>
  </div>`;
}

/* ---------- Notifications ---------- */
export function teacherNotifications(): string {
  return `
  <div class="page">
    ${pageHead('Notifications', 'Notification center', 'System alerts, student activity and academic updates.', '<button class="btn" onclick="toast(\'All marked as read\',\'You are up to date\',\'good\')">' + icon('check') + ' Mark all read</button>')}
    <div class="card">
      <div class="card-b">
        ${[
          { t: '5 students flagged as at-risk this week', b: 'Based on declining performance and forgetting events across your classes.', time: '1 hour ago', urgent: true },
          { t: 'Assessment ready for review', b: 'Electricity & Circuits MCQ set (25 questions) generated and awaiting your approval.', time: '3 hours ago' },
          { t: 'Light & Refraction — class mastery dropped', b: 'Class-wide mastery for 10A dropped from 66% to 44% this week.', time: 'Yesterday', urgent: true },
          { t: 'Weekly class report available', b: 'Your class performance summary for Sep 8–14 is ready.', time: 'Yesterday' },
          { t: 'New curriculum content published', b: 'Grade 10 Science — updated material added by the department.', time: '2 days ago' },
        ].map(n => `
          <div class="notice">
            <span class="n-dot ${n.urgent ? 'urgent' : 'teal'}"></span>
            <div class="n-body"><b>${n.t}</b><p>${n.b}</p><div class="n-time">${icon('clock', 'ic-xs')} ${n.time}</div></div>
          </div>`).join('')}
      </div>
    </div>
  </div>`;
}

/* ---------- Teacher Profile ---------- */
export function teacherProfile(): string {
  const u = getCurrentUser();
  return `
  <div class="page">
    ${pageHead('Profile', 'Your profile', 'Personal and professional information.', `<button class="btn btn-primary" onclick="window.openChangePasswordModal()">${icon('lock', 'ic-xs')} Change Password</button>`)}
    <div class="card mb-6">
      <div class="card-b" style="padding:28px">
        <div class="flex gap-5 wrap">
          <div class="av xl" style="background:linear-gradient(135deg,var(--violet),var(--indigo))">${u.initials}</div>
          <div style="flex:1;min-width:220px">
            <h1 class="h1 mb-2">${u.name}</h1>
            <p class="body mb-3">${u.subjects} · Grade 10 · Science stream</p>
            <div class="flex gap-2 wrap">
              <span class="badge indigo">${u.school}</span>
              <span class="badge grey">${u.email}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
    <div class="grid g-2">
      <div class="card">
        <div class="card-h"><h3>Professional information</h3></div>
        <div class="card-b">
          ${[
            ['Full name', u.name],
            ['Email', u.email],
            ['Department', 'Science'],
            ['Subjects', 'Mathematics, Physics'],
            ['Classes', 'Grade 10 · A, B, C, D'],
            ['Experience', '8 years'],
          ].map(([k, v]) => `
            <div class="flex-b" style="padding:11px 0;border-bottom:1px solid var(--border-2);font-size:13px">
              <span class="muted">${k}</span><b>${v}</b>
            </div>`).join('')}
        </div>
      </div>
      <div class="card">
        <div class="card-h"><h3>Teaching snapshot</h3></div>
        <div class="card-b">
          <div class="grid g-2">
            ${statBlock('Students', '161', 'Across 4 sections', 'users')}
            ${statBlock('Avg. class score', '76%', '+4% this term', 'chart', 'up')}
            ${statBlock('Assessments created', '13', 'This term', 'clipboard')}
            ${statBlock('Content pieces', '127', 'Published', 'folder')}
          </div>
        </div>
      </div>
    </div>
  </div>`;
}

// Global browser window bindings
if (typeof window !== 'undefined') {
  window.openStudent = openStudent;
  window.closeOverlay = closeOverlay;
  window.toast = toast;
}
