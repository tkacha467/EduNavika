// Student View Renderers for EduNavika

import { icon } from '../../utils/icons';
import { sparkline, barChart, donut } from '../../utils/charts';
import {
  statBlock,
  progressBar,
  riskBadge,
  statusBadge,
  aiInsight,
  pageHead,
  openModal,
  closeOverlay,
  openDrawer,
  toast,
} from '../../components/common';
import { SUBJECTS } from '../../services/curriculumService';
import { STUDENT, getCurrentUser } from '../../services/authService';
import { UI } from '../../services/uiState';
import {
  REVISION_QUEUE,
  FORGETTING_TIMELINE,
  UPCOMING_ASSESSMENTS,
  COMPLETED_ASSESSMENTS,
  NOTIFICATIONS,
  TIMETABLE,
  CLASS_WEAK_TOPICS,
} from './studentData';

declare const window: any;

/* ---------- Dashboard ---------- */
export function studentDashboard(): string {
  const sub = SUBJECTS;
  const user = getCurrentUser();
  const firstName = user.full_name?.split(' ')[0] || user.name?.split(' ')[0] || 'Student';
  const isNew = (user.todayGoal || 0) === 0;

  const todayFocus = [
    { kind: 'continue', label: 'Core Learning', subject: 'Mathematics', topic: 'Real Numbers & Polynomials', meta: 'Standard 10 · Chapter 1', pct: (user.todayGoal || 0) > 0 ? 100 : 0, go: "startQuiz('Real Numbers & Polynomials')", action: (user.todayGoal || 0) > 0 ? 'Completed ✓' : 'Start Practice' },
    { kind: 'practice', label: 'Active Practice', subject: 'Science', topic: 'Chemical Reactions & Equations', meta: 'Standard 10 · Core Chapter', pct: 0, go: "startQuiz('Chemical Reactions & Equations')", action: 'Start Quiz' },
    { kind: 'revision', label: 'Concept Check', subject: 'Physics', topic: 'Electricity & Circuits', meta: 'Diagnostic assessment', pct: 0, go: "startQuiz('Electricity & Circuits')", action: 'Take Quiz' }
  ];

  return `
  <div class="page with-rail">
    <!-- Welcome -->
    <div class="welcome">
      <div class="welcome-c">
        <div class="welcome-l">
          <div class="hi">Welcome, ${firstName} 👋</div>
          <h1>${isNew ? "Here's your learning workspace." : "Here's what needs your attention today."}</h1>
          <p>${isNew ? "Welcome to EduNavika! You are registered in <b>Standard 10 (GSEB)</b>. Complete a practice quiz below to begin tracking your live knowledge retention and learning progress." : "Keep up the momentum! Review today's topics and continue your adaptive practice."}</p>
        </div>
        <div class="welcome-r">
          <div class="wstat"><div class="l">Curriculum</div><div class="v">Std 10</div><div class="d">GSEB Science</div></div>
          <div class="wstat"><div class="l">Today</div><div class="v">${user.todayGoal || 0}<small>/ 3</small></div><div class="d">Tasks assigned</div></div>
          <div class="wstat"><div class="l">Weekly</div><div class="v">${user.weeklyGoal || 0}<small>%</small></div><div class="d">School mandate</div></div>
          <div class="wstat"><div class="l">Status</div><div class="v">Active</div><div class="d">Term 1 (2026)</div></div>
        </div>
      </div>
    </div>

    <!-- Today's Focus -->
    <div class="sec-head">
      <div><h2>${icon('target')} Today's Focus</h2><p>Recommended curriculum topics for Standard 10. Start practice to establish your learning profile.</p></div>
      <div class="right"><button class="btn btn-sm" data-go="student/learning">View all</button></div>
    </div>
    <div class="focus-grid mb-6">
      ${todayFocus.map(f => `
        <div class="focus-card ${f.kind}" onclick="${f.go}">
          <div class="ftag">${f.kind === 'continue' ? icon('play', 'ic-xs') : f.kind === 'revision' ? icon('refresh', 'ic-xs') : icon('zap', 'ic-xs')} ${f.label}</div>
          <div class="fsub">${f.subject}</div>
          <h4>${f.topic}</h4>
          <div class="fmeta">${f.meta}</div>
          ${f.pct > 0 ? `<div class="fbar">${progressBar(f.pct, 'indigo')}<b>${f.pct}%</b></div>` : ''}
          <button class="btn btn-sm btn-primary" style="width:100%">${f.action}</button>
        </div>`).join('')}
    </div>

    <!-- Knowledge Health + AI Insight -->
    <div class="grid g-3-1 mb-6">
      <div class="card">
        <div class="card-h">
          <div><h3>Knowledge Health</h3><div class="sub">Live model-derived estimate of how stable your learning is</div></div>
          <div class="right"><span class="badge teal">${icon('sparkles')} EduSense AI</span></div>
        </div>
        <div class="card-b">
          ${isNew ? `
            <div class="kh-hero" style="padding:28px 20px;text-align:center;">
              <div style="font-size:36px;margin-bottom:8px;">🎯</div>
              <h3 style="font-size:18px;font-weight:700;color:var(--text);margin-bottom:6px;">Ready for Initial Diagnostic Check</h3>
              <p style="color:var(--text-3);max-width:520px;margin:0 auto 18px auto;font-size:13.5px;line-height:1.5;">
                Welcome <b>${firstName}</b>! You have a fresh new account. Complete your first practice set in <b>Mathematics</b> or <b>Science</b> to compute your baseline knowledge health and stability curve.
              </p>
              <button class="btn btn-primary" onclick="startQuiz('Real Numbers & Polynomials')">
                ${icon('play', 'ic-xs')} Begin First Practice Quiz
              </button>
            </div>
          ` : `
            <div class="kh-hero" style="padding:0;border:0">
              <div class="kh-top">
                <div class="kh-score">
                  <div class="big">${Math.min(100, 70 + (user.todayGoal || 1) * 10)}<small>%</small></div>
                  <div class="cap"><b>Active Knowledge Health</b>Based on your latest practice session</div>
                </div>
                <div class="kh-dist">
                  <div class="kh-bar">
                    <div class="kh-seg" style="width:60%;background:var(--green)"></div>
                    <div class="kh-seg" style="width:25%;background:var(--teal)"></div>
                    <div class="kh-seg" style="width:15%;background:var(--amber)"></div>
                  </div>
                  <div class="kh-legend">
                    <span class="item"><span class="sw" style="background:var(--green)"></span>Strong <b>60%</b></span>
                    <span class="item"><span class="sw" style="background:var(--teal)"></span>Stable <b>25%</b></span>
                    <span class="item"><span class="sw" style="background:var(--amber)"></span>Needs review <b>15%</b></span>
                  </div>
                </div>
              </div>
            </div>
          `}
        </div>
      </div>
      <div class="flex-c">
        ${aiInsight('Diagnostic Baseline',
          `Welcome to EduNavika, <b>${firstName}</b>! Complete a quick 5-question check on <b>Real Numbers</b> or <b>Chemical Reactions</b> to establish your initial knowledge stability profile.`,
          'Start first quiz', `startQuiz('Real Numbers & Polynomials')`)}
        ${aiInsight('Study Strategy',
          `As a new student, aiming for <b>3 short practice sets daily</b> builds strong memory retention and prepares you for GSEB Standard 10 board exams.`,
          'Explore syllabus', `navigate('student/subjects')`)}
      </div>
    </div>

    <!-- Forgetting Timeline + Upcoming Assessments -->
    <div class="grid g-2-1 mb-6">
      <div class="card">
        <div class="card-h">
          <div><h3>Your Forgetting Timeline</h3><div class="sub">Estimated forgetting risk across your topics</div></div>
          <div class="right"><button class="btn btn-sm" data-go="student/knowledge">Details</button></div>
        </div>
        <div class="card-b">
          ${FORGETTING_TIMELINE.length === 0 ? `
            <div style="padding:28px 20px;text-align:center;color:var(--text-3)">
              <div style="font-size:28px;margin-bottom:6px">📈</div>
              <div style="font-weight:600;color:var(--text);font-size:13.5px">No memory decay detected</div>
              <p style="font-size:12px;max-width:380px;margin:4px auto 0 auto">Take quizzes or practice sessions to allow EduSense AI to model your memory retention curve.</p>
            </div>
          ` : `
          <div class="timeline">
            ${FORGETTING_TIMELINE.slice(0, 5).map(t => `
              <div class="tl-item risk-${t.risk}">
                <div class="tl-when">${t.when}</div>
                <div class="tl-title">${t.subject} — ${t.topic}</div>
                <div class="tl-meta">${t.note} · Knowledge health ${t.kh}%</div>
                <div class="flex gap-2">
                  ${riskBadge(t.risk)}
                  ${t.risk === 'high' ? `<button class="btn btn-sm btn-primary" data-go="student/revision">Review now</button>` : `<button class="btn btn-sm">View topic</button>`}
                </div>
              </div>`).join('')}
          </div>
          `}
          <p class="tiny" style="margin-top:14px;padding-top:14px;border-top:1px solid var(--border-2);display:flex;gap:6px;align-items:flex-start">
            ${icon('bulb', 'ic-xs')}
            <span>Estimates are model-derived from accuracy, response time and revision history. They are not absolute predictions — a single low score never means "forgotten".</span>
          </p>
        </div>
      </div>

      <div class="card">
        <div class="card-h">
          <div><h3>Upcoming Assessments</h3><div class="sub">${UPCOMING_ASSESSMENTS.length} scheduled</div></div>
          <div class="right"><button class="btn btn-sm" data-go="student/assessments">All</button></div>
        </div>
        <div class="card-b">
          <div class="flex-c">
            ${UPCOMING_ASSESSMENTS.map(a => `
              <div style="padding:14px;border:1px solid var(--border);border-radius:var(--r-md);background:var(--surface-2)">
                <div class="flex-b mb-2">
                  <span class="badge ${a.daysLeft <= 3 ? 'coral' : a.daysLeft <= 7 ? 'amber' : 'indigo'}">${a.daysLeft} days left</span>
                  <span class="tiny">${a.date}</span>
                </div>
                <div style="font-size:13.5px;font-weight:700;margin-bottom:3px">${a.subject} — ${a.topic}</div>
                <div class="tiny mb-2">${a.time} · ${a.questions} questions · ${a.duration}</div>
                <div class="flex gap-2" style="font-size:11.5px;color:var(--text-3)">
                  <span>Preparation</span>
                  <div class="prog thin" style="flex:1"><i class="fill-${a.prep >= 70 ? 'green' : a.prep >= 50 ? 'amber' : 'coral'}" style="width:${a.prep}%"></i></div>
                  <b style="color:var(--text)">${a.prep === 0 ? 'Not started' : a.prep + '%'}</b>
                </div>
              </div>`).join('')}
          </div>
        </div>
      </div>
    </div>

    <!-- Weekly Progress + Subject Performance -->
    <div class="grid g-3-1 mb-6">
      <div class="card">
        <div class="card-h">
          <div><h3>Learning This Week</h3><div class="sub">Current weekly activity</div></div>
          <div class="right"><span class="badge grey">Baseline</span></div>
        </div>
        <div class="card-b">
          <div class="grid g-4 mb-5">
            ${statBlock('Study Time', isNew ? '0m' : '15m', isNew ? '0m' : '+15m', 'clock', 'up')}
            ${statBlock('Questions Solved', isNew ? '0' : '5', isNew ? '0' : '+5', 'target', 'up')}
            ${statBlock('Avg. Accuracy', isNew ? '--' : '100%', isNew ? '0%' : '+100%', 'chart', 'up')}
            ${statBlock('Curriculum Pace', isNew ? 'On Track' : 'Active', 'Standard 10', 'book', 'up')}
          </div>
          <div class="grid g-2">
            <div>
              <div class="tiny mb-2" style="font-weight:600;color:var(--text-2);text-transform:uppercase;letter-spacing:.04em">Study time · daily</div>
              ${barChart(isNew ? [0, 0, 0, 0, 0, 0, 0] : [0, 0, 0, 0, 0, 15, 0], ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'], 400, 130, '#243B6B')}
            </div>
            <div>
              <div class="tiny mb-2" style="font-weight:600;color:var(--text-2);text-transform:uppercase;letter-spacing:.04em">Accuracy trend</div>
              ${sparkline(isNew ? [0, 0, 0, 0, 0, 0, 0] : [0, 0, 0, 0, 0, 100, 100], 400, 130, '#2E9B68')}
            </div>
          </div>
        </div>
      </div>

      <div class="card">
        <div class="card-h">
          <div><h3>Weak Areas</h3><div class="sub">Priority topics</div></div>
          <div class="right"><button class="btn btn-sm" data-go="student/weak">View all</button></div>
        </div>
        <div class="card-b">
          ${CLASS_WEAK_TOPICS.length === 0 ? `
            <div style="padding:24px 12px;text-align:center;color:var(--text-3)">
              <div style="font-size:24px;margin-bottom:6px">🎯</div>
              <div style="font-weight:600;color:var(--text);font-size:13px">No weak areas identified</div>
              <p style="font-size:11.5px;margin-top:4px">Weak concepts will automatically surface here after you attempt quizzes.</p>
            </div>
          ` : CLASS_WEAK_TOPICS.slice(0, 3).map(t => `
            <div style="padding:11px 0;border-bottom:1px solid var(--border-2)">
              <div class="flex-b mb-2">
                <span style="font-size:12.5px;font-weight:600">${t.topic}</span>
                <span class="badge ${t.severity === 'high' ? 'coral' : 'amber'}">${t.mastery}%</span>
              </div>
              ${progressBar(t.mastery, t.severity === 'high' ? 'coral' : 'amber')}
              <div class="tiny" style="margin-top:5px">${t.subject} · ${t.students} students</div>
            </div>`).join('')}
        </div>
      </div>
    </div>

    <!-- Subject Performance -->
    <div class="sec-head">
      <div><h2>${icon('grid')} Subject Performance</h2><p>Mastery and knowledge health across your subjects</p></div>
      <div class="right"><button class="btn btn-sm" data-go="student/subjects">See subjects</button></div>
    </div>
    <div class="grid g-3">
      ${sub.map(s => `
        <div class="subj-card" onclick="openSubject('${s.id}')">
          <div class="sc-h">
            <div class="subj-ic" style="background:${s.bg};color:${s.color}">${s.code}</div>
            <div style="flex:1;min-width:0">
              <h4>${s.name}</h4>
              <span>${s.done} of ${s.topics} topics complete</span>
            </div>
            ${s.done === 0 ? '<span class="badge grey">Unassessed</span>' : riskBadge(s.risk)}
          </div>
          <div class="subj-metrics">
            <div class="m"><div class="l">Mastery</div><div class="v">${s.mastery}%</div>${progressBar(s.mastery, s.mastery >= 80 ? 'green' : s.mastery >= 60 ? 'indigo' : 'amber')}</div>
            <div class="m"><div class="l">Knowledge Health</div><div class="v" style="color:${s.kh >= 70 ? 'var(--green)' : s.kh >= 55 ? 'var(--amber)' : 'var(--text-3)'}">${s.kh === 0 ? '--' : s.kh + '%'}</div>${progressBar(s.kh, s.kh >= 70 ? 'green' : s.kh >= 55 ? 'amber' : 'coral')}</div>
          </div>
        </div>`).join('')}
    </div>

    <!-- Notices -->
    <div class="sec-head mt-6">
      <div><h2>${icon('bell')} Recent Notices</h2><p>From your school and teachers</p></div>
      <div class="right"><button class="btn btn-sm" data-go="student/notifications">Notification center</button></div>
    </div>
    <div class="card">
      <div class="card-b">
        <div class="notice">
          <span class="n-dot urgent"></span>
          <div class="n-body"><b>Physics assessment in 3 days</b><p>Electricity & Circuits test is scheduled for September 18 at 10:00 AM. Recommended preparation: revise today's queue.</p><div class="n-time">${icon('clock', 'ic-xs')} 3 hours ago · Assessment</div></div>
        </div>
        <div class="notice">
          <span class="n-dot teal"></span>
          <div class="n-body"><b>New study material for Grade 10</b><p>"Forgetting curves and revision planning" has been added to your Science resources.</p><div class="n-time">${icon('clock', 'ic-xs')} 5 hours ago · Content</div></div>
        </div>
        <div class="notice">
          <span class="n-dot"></span>
          <div class="n-body"><b>Timetable update — Friday</b><p>Physics practical moved to Lab 2 at 2:30 PM.</p><div class="n-time">${icon('clock', 'ic-xs')} Yesterday · Academic</div></div>
        </div>
      </div>
    </div>
  </div>

  <aside class="rail">
    <div class="rail-inner">
      <div class="ai-card">
        <div class="ai-head"><div class="ai-mark">${icon('sparkles')}</div><b>EduSense AI</b></div>
        <div class="ai-body">Welcome <b>${firstName}</b>! Take a 5-minute practice quiz in Mathematics or Science to establish your knowledge health baseline.</div>
        <div class="ai-actions"><button class="btn btn-sm btn-teal" onclick="startQuiz('Real Numbers & Polynomials')">Start first quiz</button></div>
      </div>

      <div class="card">
        <div class="card-h" style="padding-bottom:12px"><h3 style="font-size:13.5px">Quick Actions</h3></div>
        <div class="card-b" style="padding-top:0;display:flex;flex-direction:column;gap:8px">
          <button class="qa-tile" onclick="navigate('student/assessments')">
            <div class="qi">${icon('clipboard')}</div>
            <div><b>Start MCQ practice</b><span>Pick a topic and begin</span></div>
          </button>
          <button class="qa-tile" onclick="navigate('student/subjects')">
            <div class="qi" style="background:var(--indigo-50);color:var(--indigo)">${icon('book')}</div>
            <div><b>Explore GSEB syllabus</b><span>Standard 10 chapters</span></div>
          </button>
          <button class="qa-tile" onclick="navigate('student/materials')">
            <div class="qi" style="background:var(--teal-50);color:var(--teal-600)">${icon('folder')}</div>
            <div><b>Study materials</b><span>Textbooks, notes, PDFs</span></div>
          </button>
        </div>
      </div>

      <div class="card">
        <div class="card-h" style="padding-bottom:12px"><h3 style="font-size:13.5px">Next Assessment</h3></div>
        <div class="card-b" style="padding-top:0">
          <div class="flex-b mb-2">
            <span class="badge teal">Upcoming</span>
            <span class="tiny">Standard 10</span>
          </div>
          <div style="font-size:14px;font-weight:700;margin-bottom:2px">Diagnostic Mastery Check</div>
          <div class="small mb-3">Mathematics & Science · 15 min</div>
          <div class="flex gap-2 mb-3" style="font-size:11.5px;color:var(--text-3)">
            <span>Readiness</span>
            <div class="prog thin" style="flex:1"><i class="fill-indigo" style="width:${(user.todayGoal || 0) > 0 ? 100 : 0}%"></i></div>
            <b style="color:var(--text)">${(user.todayGoal || 0) > 0 ? '100%' : '0%'}</b>
          </div>
          <button class="btn btn-primary btn-sm" style="width:100%" onclick="startQuiz('Real Numbers & Polynomials')">Take Diagnostic Test</button>
        </div>
      </div>
    </div>
  </aside>`;
}

/* ---------- My Learning ---------- */
export function studentLearning(): string {
  if (UI.subjectId) return subjectDetailPage();
  const user = getCurrentUser();
  const hasActivity = (user.todayGoal || 0) > 0 || COMPLETED_ASSESSMENTS.length > 0;

  return `
  <div class="page">
    ${pageHead('My Learning', 'Continue your learning journey', 'Everything you are studying right now — continue, review or explore new topics.', `<button class="btn btn-primary" onclick="navigate('student/assessments')">${icon('play')} Take a practice check</button>`)}

    <!-- Continue learning -->
    <div class="sec-head"><div><h2>${icon('play')} Core GSEB Curriculum</h2><p>Recommended starting topics for Standard 10</p></div></div>
    <div class="grid g-3 mb-6">
      ${[
        { subject: 'Mathematics', topic: 'Real Numbers & Polynomials', pct: (user.todayGoal || 0) > 0 ? 100 : 0, time: (user.todayGoal || 0) > 0 ? 'Completed ✓' : 'Not started', color: '#243B6B', bg: '#E8EDF7', icon: 'MTH', id: 'math' },
        { subject: 'Physics', topic: 'Electricity & Circuits', pct: 0, time: 'Not started', color: '#18A6A6', bg: '#E3F5F5', icon: 'PHY', id: 'phy' },
        { subject: 'Chemistry', topic: 'Chemical Reactions & Equations', pct: 0, time: 'Not started', color: '#2E9B68', bg: '#E7F5EE', icon: 'CHM', id: 'chem' }
      ].map(c => `
        <div class="card hoverable pad" style="cursor:pointer" onclick="openSubject('${c.id}')">
          <div class="flex gap-3 mb-4">
            <div class="subj-ic" style="background:${c.bg};color:${c.color};width:44px;height:44px;font-size:12px">${c.icon}</div>
            <div style="flex:1;min-width:0">
              <div class="tiny" style="font-weight:600;text-transform:uppercase;letter-spacing:.04em;color:${c.color}">${c.subject}</div>
              <div style="font-size:14px;font-weight:700;margin-top:2px;line-height:1.3">${c.topic}</div>
            </div>
          </div>
          <div class="flex gap-2 mb-3">
            ${progressBar(c.pct, c.pct >= 70 ? 'green' : 'indigo')}
            <b style="font-size:12.5px">${c.pct}%</b>
          </div>
          <div class="flex-b">
            <span class="tiny">${c.time}</span>
            <span class="btn btn-sm btn-primary">Open ${icon('arrowR', 'ic-xs')}</span>
          </div>
        </div>`).join('')}
    </div>

    <!-- Subjects -->
    <div class="sec-head"><div><h2>${icon('grid')} Your Subjects</h2><p>6 subjects enrolled this term</p></div><div class="right"><button class="btn btn-sm" data-go="student/subjects">Manage</button></div></div>
    <div class="grid g-3 mb-6">
      ${SUBJECTS.map(s => `
        <div class="subj-card" onclick="openSubject('${s.id}')">
          <div class="sc-h">
            <div class="subj-ic" style="background:${s.bg};color:${s.color}">${s.code}</div>
            <div style="flex:1;min-width:0">
              <h4>${s.name}</h4>
              <span>${s.done} of ${s.topics} topics complete</span>
            </div>
            ${s.done === 0 ? '<span class="badge grey">Unassessed</span>' : riskBadge(s.risk)}
          </div>
          <div class="subj-metrics">
            <div class="m"><div class="l">Mastery</div><div class="v">${s.mastery}%</div>${progressBar(s.mastery, s.mastery >= 80 ? 'green' : 'indigo')}</div>
            <div class="m"><div class="l">Knowledge Health</div><div class="v" style="color:${s.kh >= 70 ? 'var(--green)' : s.kh >= 55 ? 'var(--amber)' : 'var(--text-3)'}">${s.kh === 0 ? '--' : s.kh + '%'}</div>${progressBar(s.kh, s.kh >= 70 ? 'green' : s.kh >= 55 ? 'amber' : 'coral')}</div>
          </div>
        </div>`).join('')}
    </div>

    <!-- Recommended + Recent Activity -->
    <div class="grid g-2-1">
      <div class="card">
        <div class="card-h"><div><h3>Recommended for you</h3><div class="sub">Curriculum guidance from EduSense AI</div></div></div>
        <div class="card-b">
          <div class="flex-c">
            ${aiInsight('Diagnostic Practice', `Welcome to Standard 10! Complete a quick 5-question baseline practice set in Mathematics or Science to calibrate your knowledge curve.`, 'Start practice', `startQuiz('Real Numbers & Polynomials')`)}
            ${aiInsight('Structured Revision', `EduSense AI continuously schedules revision sessions to reinforce retention before concepts fade.`, 'View revision plan', `navigate('student/revision')`)}
          </div>
        </div>
      </div>
      <div class="card">
        <div class="card-h"><h3>Recent activity</h3></div>
        <div class="card-b" style="padding-top:8px">
          ${!hasActivity ? `
            <div style="padding:28px 16px;text-align:center;color:var(--text-3)">
              <div style="font-size:24px;margin-bottom:6px">📋</div>
              <div style="font-weight:600;color:var(--text);font-size:13px">No activity recorded yet</div>
              <p style="font-size:12px;margin-top:4px">Your study sessions, reading history, and quiz submissions will appear here.</p>
            </div>
          ` : COMPLETED_ASSESSMENTS.slice(0, 4).map(c => `
            <div class="notice"><span class="n-dot teal"></span><div class="n-body"><b>Completed ${c.topic} check</b><p>${c.accuracy}% accuracy · ${c.time} duration</p><div class="n-time">${icon('clock', 'ic-xs')} ${c.date}</div></div></div>
          `).join('')}
        </div>
      </div>
    </div>
  </div>`;
}

/* ---------- Subject detail ---------- */
export function subjectDetailPage(): string {
  const s = SUBJECTS.find(x => x.id === UI.subjectId);
  if (!s) return `<div class="page"><div class="empty"><b>Subject not found</b></div></div>`;
  return `
  <div class="page">
    <button class="btn btn-ghost btn-sm mb-3" onclick="UI.subjectId=null;navigate('student/learning')">${icon('chevL')} Back to My Learning</button>

    <div class="card mb-5">
      <div class="card-b" style="padding:24px">
        <div class="flex gap-4 wrap">
          <div class="subj-ic" style="background:${s.bg};color:${s.color};width:64px;height:64px;font-size:18px;border-radius:16px">${s.code}</div>
          <div style="flex:1;min-width:220px">
            <div class="flex gap-2 mb-2">${riskBadge(s.risk)}<span class="badge grey">Grade 10 · Science</span></div>
            <h1 class="h1 mb-2">${s.name}</h1>
            <p class="body">${s.topics} topics · ${s.done} completed · Average mastery ${s.mastery}%</p>
          </div>
          <div class="flex gap-2" style="align-self:flex-start">
            <button class="btn" onclick="navigate('student/revision')">${icon('refresh')} Revision plan</button>
            <button class="btn btn-primary" onclick="startQuiz('${s.name}')">${icon('play')} Practice</button>
          </div>
        </div>
        <div class="grid g-4 mt-5" style="padding-top:20px;border-top:1px solid var(--border-2)">
          ${statBlock('Mastery', s.mastery + '%', s.mastery === 0 ? 'Baseline' : '+4% this month', 'award', 'up')}
          ${statBlock('Knowledge Health', s.kh === 0 ? '--' : s.kh + '%', s.kh === 0 ? 'Unassessed' : s.kh >= 70 ? 'Stable' : 'Needs practice', 'brain', s.kh >= 70 ? 'up' : 'down')}
          ${statBlock('Topics', s.done + ' / ' + s.topics, s.topics - s.done + ' remaining', 'book2')}
          ${statBlock('Practice', s.done === 0 ? '0 Q' : `${s.done * 10} Q`, s.done === 0 ? 'Not started' : 'In progress', 'target', 'up')}
        </div>
      </div>
    </div>

    <div class="card">
      <div class="tabs">
        <button class="tab on" onclick="switchTab(this,'sd-overview')">Overview</button>
        <button class="tab" onclick="switchTab(this,'sd-topics')">Topics</button>
        <button class="tab" onclick="switchTab(this,'sd-practice')">Practice</button>
        <button class="tab" onclick="switchTab(this,'sd-rev')">Revision</button>
        <button class="tab" onclick="switchTab(this,'sd-analytics')">Analytics</button>
        <button class="tab" onclick="switchTab(this,'sd-materials')">Materials</button>
      </div>
      <div class="card-b">
        <div id="sd-overview" class="tabpane">
          <div class="grid g-2-1 mb-5">
            <div class="card pad" style="border:1px solid var(--border-2)">
              <div class="h4 mb-3">Mastery distribution</div>
              ${s.topicList.map(t => `
                <div class="progress-row flex gap-3 mb-3">
                  <span style="flex:0 0 180px;font-size:12.5px;font-weight:600">${t.name}</span>
                  ${progressBar(t.mastery, t.mastery >= 80 ? 'green' : t.mastery >= 60 ? 'indigo' : t.mastery >= 45 ? 'amber' : 'coral')}
                  <b style="width:40px;text-align:right;font-size:12.5px">${t.mastery}%</b>
                </div>`).join('')}
            </div>
            <div class="card pad" style="border:1px solid var(--border-2);text-align:center">
              <div class="h4 mb-3">Knowledge health</div>
              ${donut(s.kh, 140, 12, s.color)}
              <p class="tiny mt-3">Across ${s.topicList.length} active topics</p>
            </div>
          </div>
          <div class="ai-card">
            <div class="ai-head"><div class="ai-mark">${icon('sparkles')}</div><b>EduSense AI — ${s.name}</b></div>
            <div class="ai-body">${s.risk === 'high'
              ? `<b>${s.name}</b> needs attention this week. ${s.topicList.filter(t => t.risk === 'high').length} topics are at risk of forgetting. Focus on <b>${s.topicList.find(t => t.risk === 'high')?.name || 'core topics'}</b> first.`
              : `<b>${s.name}</b> is progressing steadily. Your strongest area is <b>${s.topicList[0]?.name || 'this subject'}</b>. Continue your current revision pattern.`}</div>
          </div>
        </div>

        <div id="sd-topics" class="tabpane hide">
          ${s.topicList.map(t => `
            <div class="card pad mb-3" style="border:1px solid var(--border-2)">
              <div class="flex-b mb-3">
                <div>
                  <div style="font-size:14.5px;font-weight:700">${t.name}</div>
                  <div class="tiny">Last reviewed ${t.last} · Next revision ${t.next}</div>
                </div>
                <div class="flex gap-2">
                  ${riskBadge(t.risk)}
                  <button class="btn btn-sm">Open</button>
                </div>
              </div>
              <div class="grid g-3">
                <div><div class="tiny mb-2">Mastery</div><div class="flex gap-2">${progressBar(t.mastery, 'indigo')}<b style="font-size:12.5px">${t.mastery}%</b></div></div>
                <div><div class="tiny mb-2">Knowledge Health</div><div class="flex gap-2">${progressBar(t.kh, t.kh >= 70 ? 'green' : t.kh >= 55 ? 'amber' : 'coral')}<b style="font-size:12.5px">${t.kh}%</b></div></div>
                <div><div class="tiny mb-2">Status</div>${statusBadge(t.status)}</div>
              </div>
            </div>`).join('')}
        </div>

        <div id="sd-practice" class="tabpane hide">
          <div class="grid g-3">
            ${[
              { n: 'Quick practice set', q: 10, d: 'Mixed difficulty', time: '12 min', tone: 'teal' },
              { n: 'Chapter-wise practice', q: 20, d: 'Standard difficulty', time: '25 min', tone: 'indigo' },
              { n: 'Exam-style questions', q: 15, d: 'Hard · timed', time: '30 min', tone: 'amber' }
            ].map(p => `
              <div class="card pad">
                <div class="h4 mb-2">${p.n}</div>
                <div class="tiny mb-3">${p.q} questions · ${p.d}</div>
                <div class="flex-b"><span class="badge ${p.tone}">${p.time}</span><button class="btn btn-sm btn-primary" onclick="startQuiz('${s.name}')">${icon('play')} Start</button></div>
              </div>`).join('')}
          </div>
        </div>

        <div id="sd-rev" class="tabpane hide">
          <table class="tbl">
            <thead><tr><th>Topic</th><th>Knowledge Health</th><th>Risk</th><th>Recommended</th><th></th></tr></thead>
            <tbody>
              ${s.topicList.map(t => `
                <tr>
                  <td class="nm">${t.name}</td>
                  <td><div class="flex gap-2" style="width:140px">${progressBar(t.kh, t.kh >= 70 ? 'green' : t.kh >= 55 ? 'amber' : 'coral')}<b style="font-size:12px">${t.kh}%</b></div></td>
                  <td>${riskBadge(t.risk)}</td>
                  <td class="muted">${t.next}</td>
                  <td class="right"><button class="btn btn-sm" onclick="startQuiz('${t.name}')">Review</button></td>
                </tr>`).join('')}
            </tbody>
          </table>
        </div>

        <div id="sd-analytics" class="tabpane hide">
          <div class="grid g-2">
            <div class="card pad" style="border:1px solid var(--border-2)">
              <div class="h4 mb-3">Accuracy trend · last 8 sessions</div>
              ${sparkline([58, 62, 68, 71, 74, 72, 78, 82], 420, 140, s.color)}
            </div>
            <div class="card pad" style="border:1px solid var(--border-2)">
              <div class="h4 mb-3">Response time · seconds/question</div>
              ${barChart([42, 38, 35, 33, 31, 30, 29, 27], ['S1', 'S2', 'S3', 'S4', 'S5', 'S6', 'S7', 'S8'], 420, 140, s.color)}
            </div>
          </div>
        </div>

        <div id="sd-materials" class="tabpane hide">
          <div class="grid g-3">
            ${[
              { n: 'Chapter notes — complete', t: 'PDF', s: '2.4 MB' },
              { n: 'Concept video walkthrough', t: 'Video', s: '22 min' },
              { n: 'Practice question bank', t: 'Practice', s: '60 questions' },
              { n: 'Quick revision sheet', t: 'PDF', s: '680 KB' }
            ].map(m => `
              <div class="card pad">
                <div class="flex gap-3 mb-3">
                  <div class="qa-tile" style="padding:8px;width:38px;height:38px;justify-content:center"><div class="qi" style="width:30px;height:30px;background:${s.bg};color:${s.color}">${icon('file')}</div></div>
                  <div style="flex:1;min-width:0"><div class="h4" style="font-size:13.5px">${m.n}</div><div class="tiny">${m.s}</div></div>
                </div>
                <div class="flex-b"><span class="badge grey">${m.t}</span><button class="btn btn-sm">${icon('download')} Open</button></div>
              </div>`).join('')}
          </div>
        </div>
      </div>
    </div>
  </div>`;
}

/* ---------- Subjects (grid page) ---------- */
export function studentSubjects(): string {
  return `
  <div class="page">
    ${pageHead('Subjects', 'Your subjects', '6 subjects enrolled for Grade 10 · Science stream.', '<button class="btn btn-primary" onclick="navigate(\'student/learning\')">' + icon('book') + ' My Learning</button>')}
    <div class="grid g-3">
      ${SUBJECTS.map(s => `
        <div class="card hoverable pad-lg" style="cursor:pointer" onclick="openSubject('${s.id}')">
          <div class="flex gap-3 mb-4">
            <div class="subj-ic" style="background:${s.bg};color:${s.color};width:52px;height:52px;font-size:15px;border-radius:14px">${s.code}</div>
            <div style="flex:1;min-width:0">
              <h3 class="h4">${s.name}</h3>
              <div class="tiny">${s.topics} topics · ${s.done} completed</div>
            </div>
            ${s.done === 0 ? '<span class="badge grey">Unassessed</span>' : riskBadge(s.risk)}
          </div>
          <div class="grid g-2 mb-4">
            <div><div class="tiny mb-2">Mastery</div><div style="font-size:18px;font-weight:800;font-family:Manrope">${s.mastery}%</div></div>
            <div><div class="tiny mb-2">Knowledge Health</div><div style="font-size:18px;font-weight:800;font-family:Manrope;color:${s.kh >= 70 ? 'var(--green)' : s.kh >= 55 ? 'var(--amber)' : 'var(--text-3)'}">${s.kh === 0 ? '--' : s.kh + '%'}</div></div>
          </div>
          ${progressBar(s.mastery, 'indigo')}
          <div class="flex-b mt-3"><span class="tiny">${s.done === 0 ? 'Not started' : 'Active'}</span><span class="btn btn-sm">Open ${icon('arrowR', 'ic-xs')}</span></div>
        </div>`).join('')}
    </div>
  </div>`;
}

/* ---------- Revision Plan ---------- */
export function studentRevision(): string {
  const dueToday = REVISION_QUEUE.filter(r => r.when === 'Today');
  const dueWeek = REVISION_QUEUE.filter(r => r.when !== 'Today' && r.risk === 'High');
  const upcoming = REVISION_QUEUE.filter(r => r.when !== 'Today' && r.risk !== 'High');
  const hasCompletedRev = COMPLETED_ASSESSMENTS.filter(a => a.kh > 0);

  return `
  <div class="page">
    ${pageHead('Revision Plan', 'Your personalised revision plan', 'EduSense AI schedules revision at the moment it will have the greatest impact — based on your knowledge health, accuracy and last revision date.')}

    <div class="grid g-4 mb-6">
      ${statBlock('Due today', dueToday.length, dueToday.length ? 'High priority' : 'None due', 'alert', dueToday.length ? 'down' : 'up')}
      ${statBlock('This week', dueWeek.length, dueWeek.length ? 'Scheduled for you' : 'None scheduled', 'calendar')}
      ${statBlock('Completed', `${hasCompletedRev.length}`, 'Last 30 days', 'check', 'up')}
      ${statBlock('Revision accuracy', hasCompletedRev.length ? '+8%' : '--', 'On revised topics', 'trendUp', 'up')}
    </div>

    ${REVISION_QUEUE.length === 0 ? `
      <div class="card pad-lg mb-6" style="padding:48px 24px;text-align:center">
        <div style="font-size:36px;margin-bottom:8px">🎉</div>
        <h3 class="h3 mb-2">No revisions currently due</h3>
        <p style="color:var(--text-3);max-width:520px;margin:0 auto 20px auto;font-size:13.5px;line-height:1.5">
          Your revision queue is clear. As you complete lessons and quizzes across your 6 subjects, EduSense AI will track memory decay and schedule spaced revision here when it's most effective.
        </p>
        <button class="btn btn-primary" onclick="navigate('student/learning')">${icon('play')} Practice Standard 10 Syllabus</button>
      </div>
    ` : `
    ${aiInsight('This week\'s priority',
      `Your <b>Physics knowledge has become less stable</b> over recent sessions. Focus on <b>Electricity & Circuits</b> first to reverse forgetting.`,
      'Start with Physics', `startQuiz('Electricity & Circuits')`)}

    <!-- Due Today -->
    <div class="sec-head mt-6"><div><h2>${icon('alert')} Due Today</h2><p>${dueToday.length} high-priority topics · recommended before 7 PM</p></div></div>
    <div class="card mb-6">
      ${dueToday.map(r => `
        <div class="rev-row">
          <div class="ri" style="background:var(--coral-50);color:var(--coral)">${icon('refresh')}</div>
          <div class="rmain">
            <b>${r.subject} — ${r.topic}</b>
            <span>${r.reason}</span>
          </div>
          <div class="rkh">
            <div class="tiny">KH</div>
            <div class="flex gap-2">${progressBar(r.kh, 'coral')}<b style="font-size:12px;color:var(--coral)">${r.kh}%</b></div>
          </div>
          ${riskBadge(r.risk.toLowerCase())}
          <div class="rdate">~20 min</div>
          <button class="btn btn-primary btn-sm" onclick="startQuiz('${r.topic}')">${icon('play')} Start</button>
        </div>`).join('')}
    </div>

    <!-- This week -->
    <div class="sec-head"><div><h2>${icon('calendar')} Due This Week</h2><p>Scheduled for the right moment</p></div></div>
    <div class="card mb-6">
      ${dueWeek.length ? dueWeek.map(r => `
        <div class="rev-row">
          <div class="ri" style="background:var(--amber-50);color:#B4731A">${icon('refresh')}</div>
          <div class="rmain"><b>${r.subject} — ${r.topic}</b><span>${r.reason}</span></div>
          <div class="rkh"><div class="tiny">KH</div><div class="flex gap-2">${progressBar(r.kh, 'amber')}<b style="font-size:12px">${r.kh}%</b></div></div>
          ${riskBadge(r.risk.toLowerCase())}
          <div class="rdate">${r.when}</div>
          <button class="btn btn-sm" onclick="startQuiz('${r.topic}')">Review</button>
        </div>`).join('') : '<div class="empty">Nothing else this week 🎉</div>'}
    </div>

    <!-- Upcoming -->
    <div class="sec-head"><div><h2>${icon('clock')} Upcoming</h2><p>Routine reinforcement</p></div></div>
    <div class="card mb-6">
      ${upcoming.map(r => `
        <div class="rev-row">
          <div class="ri" style="background:var(--teal-50);color:var(--teal-600)">${icon('clock')}</div>
          <div class="rmain"><b>${r.subject} — ${r.topic}</b><span>${r.reason}</span></div>
          <div class="rkh"><div class="tiny">KH</div><div class="flex gap-2">${progressBar(r.kh, 'green')}<b style="font-size:12px">${r.kh}%</b></div></div>
          ${riskBadge(r.risk.toLowerCase())}
          <div class="rdate">${r.when}</div>
          <button class="btn btn-sm">View</button>
        </div>`).join('')}
    </div>
    `}

    <!-- Completed -->
    <div class="sec-head"><div><h2>${icon('check')} Recently Completed</h2><p>Last 7 days</p></div></div>
    <div class="card">
      <div class="card-b">
        ${hasCompletedRev.length === 0 ? `
          <div style="padding:24px;text-align:center;color:var(--text-3)">
            <div style="font-size:24px;margin-bottom:4px">📚</div>
            <div style="font-weight:600;color:var(--text);font-size:13px">No revisions completed yet</div>
            <p style="font-size:12px;margin-top:4px">Topics you revise will appear here along with their measured knowledge health recovery.</p>
          </div>
        ` : hasCompletedRev.map(c => `
          <div class="flex-b" style="padding:12px 0;border-bottom:1px solid var(--border-2)">
            <div class="flex gap-3">
              <div class="ri" style="background:var(--green-50);color:var(--green);width:30px;height:30px;border-radius:8px;display:grid;place-items:center">${icon('check', 'ic-sm')}</div>
              <div><div style="font-size:13px;font-weight:600">${c.subject} — ${c.topic}</div><div class="tiny">Completed ${c.date}</div></div>
            </div>
            <span class="badge green">+${c.kh}% KH</span>
          </div>`).join('')}
      </div>
    </div>
  </div>`;
}

/* ---------- Knowledge Health ---------- */
export function studentKnowledge(): string {
  const allTopics = SUBJECTS.flatMap(s => s.topicList);
  const assessedTopics = allTopics.filter(t => (t.done || 0) > 0 || (t.mastery || 0) > 0);
  const overallKh = assessedTopics.length > 0 ? Math.round(assessedTopics.reduce((a, b) => a + (b.kh || 0), 0) / assessedTopics.length) : 0;
  const isZero = assessedTopics.length === 0;

  const strongTopics = allTopics.filter(t => (t.done || 0) > 0 && (t.kh || 0) >= 75);
  const attentionTopics = allTopics.filter(t => (t.done || 0) > 0 && (t.kh || 0) >= 45 && (t.kh || 0) < 75);
  const atRiskTopics = allTopics.filter(t => (t.done || 0) > 0 && (t.kh || 0) < 45);

  return `
  <div class="page">
    ${pageHead('Knowledge Health', 'How stable is your learning?', 'A model-derived estimate combining your accuracy, response time, revision history and time since last practice.')}

    <div class="card mb-6">
      <div class="card-b" style="padding:24px">
        <div class="flex gap-5 wrap" style="align-items:center">
          <div style="text-align:center">${donut(overallKh, 160, 14, isZero ? '#A0AEC0' : '#243B6B')}<div class="small mt-2">${isZero ? 'Unassessed Baseline' : 'Overall Knowledge Health'}</div></div>
          <div style="flex:1;min-width:280px">
            <div class="h3 mb-3">${isZero ? 'No topics assessed yet' : `Across 6 subjects and ${assessedTopics.length} active topics`}</div>
            <div class="kh-bar mb-3" style="height:14px">
              ${isZero ? `
                <div class="kh-seg" style="width:100%;background:var(--border-2)"></div>
              ` : `
                <div class="kh-seg" style="width:${Math.round((strongTopics.length / assessedTopics.length) * 100)}%;background:var(--green)"></div>
                <div class="kh-seg" style="width:${Math.round((attentionTopics.length / assessedTopics.length) * 100)}%;background:var(--amber)"></div>
                <div class="kh-seg" style="width:${Math.round((atRiskTopics.length / assessedTopics.length) * 100)}%;background:var(--coral)"></div>
              `}
            </div>
            <div class="kh-legend">
              ${isZero ? `
                <span class="item"><span class="sw" style="background:var(--border-2)"></span>Unassessed <b>100%</b></span>
              ` : `
                <span class="item"><span class="sw" style="background:var(--green)"></span>Strong <b>${strongTopics.length}</b></span>
                <span class="item"><span class="sw" style="background:var(--amber)"></span>Needs revision <b>${attentionTopics.length}</b></span>
                <span class="item"><span class="sw" style="background:var(--coral)"></span>At risk <b>${atRiskTopics.length}</b></span>
              `}
            </div>
            <p class="tiny mt-4">${icon('bulb', 'ic-xs')} Knowledge Health is calibrated through diagnostic practice and tests.</p>
          </div>
        </div>
      </div>
    </div>

    ${isZero ? `
      ${aiInsight('Diagnostic Baseline Ready',
        `You have not completed any quizzes yet. Complete your first practice set in <b>Mathematics</b> or <b>Science</b> to compute your initial knowledge health and stability curve.`,
        'Start Diagnostic Practice', `startQuiz('Real Numbers & Polynomials')`)}
    ` : `
      ${aiInsight('EduSense Insight',
        `Your retention models are active. Spaced revision will trigger automatically when topics approach the forgetting threshold.`,
        'View revision plan', `navigate('student/revision')`)}
    `}

    <div class="sec-head mt-6"><div><h2>${icon('grid')} By Subject</h2><p>Knowledge health and trend across your subjects</p></div></div>
    <div class="grid g-2 mb-6">
      ${SUBJECTS.map(s => `
        <div class="card pad">
          <div class="flex-b mb-3">
            <div class="flex gap-3">
              <div class="subj-ic" style="background:${s.bg};color:${s.color};width:40px;height:40px;font-size:12px">${s.code}</div>
              <div><div class="h4">${s.name}</div><div class="tiny">${s.topics} topics · ${s.done} complete</div></div>
            </div>
            <div style="font-size:24px;font-weight:800;font-family:Manrope;color:${s.kh >= 70 ? 'var(--green)' : s.kh >= 55 ? 'var(--amber)' : 'var(--text-3)'}">${s.kh === 0 ? '--' : s.kh + '%'}</div>
          </div>
          ${progressBar(s.kh, s.kh >= 70 ? 'green' : s.kh >= 55 ? 'amber' : 'coral')}
          <div class="flex-b mt-3">
            <span class="tiny">Mastery ${s.mastery}%</span>
            ${s.done === 0 ? '<span class="badge grey">Unassessed</span>' : riskBadge(s.risk)}
          </div>
        </div>`).join('')}
    </div>

    <div class="sec-head"><div><h2>${icon('brain')} Topic-level breakdown</h2><p>Subjects ranked by knowledge health</p></div></div>
    ${isZero ? `
      <div class="card pad-lg text-center" style="padding:40px 20px;text-align:center;color:var(--text-3)">
        <div style="font-size:32px;margin-bottom:8px">🎯</div>
        <h3 class="h3 mb-2">No Topic Scores Yet</h3>
        <p style="font-size:13px;max-width:440px;margin:0 auto">As you take quizzes, topics will automatically be grouped into Strong, Needs Attention, and At Risk.</p>
      </div>
    ` : `
    <div class="grid g-3">
      <div class="card">
        <div class="card-h" style="padding-bottom:12px"><h3 style="font-size:14px"><span style="display:inline-block;width:8px;height:8px;border-radius:50%;background:var(--green);margin-right:7px"></span>Strong (${strongTopics.length})</h3></div>
        <div class="card-b" style="padding-top:0">
          <ul style="list-style:none">
            ${strongTopics.length === 0 ? '<li class="tiny p-3 text-center text-muted">None yet</li>' : strongTopics.map(t => `
              <li class="flex-b" style="padding:9px 0;border-bottom:1px solid var(--border-2);font-size:13px"><b>${t.name}</b><span style="color:var(--green);font-weight:700">${t.kh}%</span></li>`).join('')}
          </ul>
        </div>
      </div>
      <div class="card">
        <div class="card-h" style="padding-bottom:12px"><h3 style="font-size:14px"><span style="display:inline-block;width:8px;height:8px;border-radius:50%;background:var(--amber);margin-right:7px"></span>Needs Attention (${attentionTopics.length})</h3></div>
        <div class="card-b" style="padding-top:0">
          <ul style="list-style:none">
            ${attentionTopics.length === 0 ? '<li class="tiny p-3 text-center text-muted">None yet</li>' : attentionTopics.map(t => `
              <li class="flex-b" style="padding:9px 0;border-bottom:1px solid var(--border-2);font-size:13px"><b>${t.name}</b><span style="color:var(--amber);font-weight:700">${t.kh}%</span></li>`).join('')}
          </ul>
        </div>
      </div>
      <div class="card">
        <div class="card-h" style="padding-bottom:12px"><h3 style="font-size:14px"><span style="display:inline-block;width:8px;height:8px;border-radius:50%;background:var(--coral);margin-right:7px"></span>At Risk (${atRiskTopics.length})</h3></div>
        <div class="card-b" style="padding-top:0">
          <ul style="list-style:none">
            ${atRiskTopics.length === 0 ? '<li class="tiny p-3 text-center text-muted">None yet</li>' : atRiskTopics.map(t => `
              <li class="flex-b" style="padding:9px 0;border-bottom:1px solid var(--border-2);font-size:13px"><b>${t.name}</b><span style="color:var(--coral);font-weight:700">${t.kh}%</span></li>`).join('')}
          </ul>
        </div>
      </div>
    </div>
    `}
  </div>`;
}

/* ---------- Skill Mastery ---------- */
export function studentSkills(): string {
  const completedCount = COMPLETED_ASSESSMENTS.length;
  // Dynamic skill modeling based on real assessments
  const skills: Array<{ name: string; level: number; cat: string; trend: number }> = [];
  if (completedCount > 0) {
    skills.push({ name: 'Curriculum Comprehension', level: COMPLETED_ASSESSMENTS[0].score, cat: COMPLETED_ASSESSMENTS[0].subject, trend: +2 });
  }
  const strong = skills.filter(s => s.level >= 75);
  const mid = skills.filter(s => s.level >= 50 && s.level < 75);
  const weak = skills.filter(s => s.level < 50);

  return `
  <div class="page">
    ${pageHead('Skill Mastery', 'Your developing skills', 'A breakdown of the specific skills assessed across your practice and MCQ checks.')}

    <div class="grid g-3 mb-6">
      ${statBlock('Strong skills', strong.length, 'Above 75%', 'award', 'up')}
      ${statBlock('Developing', mid.length, '50 – 75%', 'target')}
      ${statBlock('Needs work', weak.length, 'Below 50%', 'alert', 'down')}
    </div>

    <div class="card">
      <div class="card-h"><h3>All skills</h3><div class="right"><span class="badge grey">${skills.length} assessed</span></div></div>
      <div class="card-b">
        ${skills.length === 0 ? `
          <div style="padding:48px 24px;text-align:center;color:var(--text-3)">
            <div style="font-size:32px;margin-bottom:8px">🎯</div>
            <h3 class="h3 mb-2">No Skill Data Recorded</h3>
            <p style="font-size:13px;max-width:440px;margin:0 auto 16px auto">
              Cognitive skills like reasoning, equation solving, and comprehension will calibrate here once you submit topic practice checks.
            </p>
            <button class="btn btn-primary" onclick="navigate('student/learning')">${icon('play')} Start Topic Practice</button>
          </div>
        ` : skills.map(s => `
          <div style="padding:13px 0;border-bottom:1px solid var(--border-2)">
            <div class="flex-b mb-2">
              <div>
                <div style="font-size:13.5px;font-weight:600">${s.name}</div>
                <div class="tiny">${s.cat}</div>
              </div>
              <div class="flex gap-3">
                <span class="badge ${s.trend > 0 ? 'green' : 'coral'}">${s.trend > 0 ? '+' : ''}${s.trend}%</span>
                <b style="font-family:Manrope;font-size:14px;width:46px;text-align:right">${s.level}%</b>
              </div>
            </div>
            ${progressBar(s.level, s.level >= 75 ? 'green' : s.level >= 50 ? 'indigo' : 'coral')}
          </div>`).join('')}
      </div>
    </div>
  </div>`;
}

/* ---------- Learning Analytics ---------- */
export function studentAnalytics(): string {
  const user = getCurrentUser();
  const count = COMPLETED_ASSESSMENTS.length;
  const isZero = count === 0 && (user.todayGoal || 0) === 0;
  const avgAcc = count > 0 ? Math.round(COMPLETED_ASSESSMENTS.reduce((a, b) => a + b.accuracy, 0) / count) : null;

  return `
  <div class="page">
    ${pageHead('Learning Analytics', 'How you are learning', 'Weekly and long-term patterns across study time, accuracy, revision effectiveness and consistency.', '<button class="btn" onclick="toast(\'Analytics exported\',\'PDF ready\',\'good\')">' + icon('download') + ' Export</button>')}

    <div class="grid g-4 mb-6">
      ${statBlock('Study time', isZero ? '0m' : '20m', isZero ? 'Baseline' : '+20m this week', 'clock', 'up')}
      ${statBlock('Questions solved', `${count * 5}`, isZero ? '0' : `+${count * 5} this week`, 'target', 'up')}
      ${statBlock('Avg. accuracy', avgAcc !== null ? `${avgAcc}%` : '--', isZero ? 'Not assessed' : 'Active', 'chart', 'up')}
      ${statBlock('Curriculum Pace', isZero ? 'On Track' : 'Active', 'Term 1 · Std 10', 'book', 'up')}
    </div>

    <div class="grid g-2 mb-6">
      <div class="card">
        <div class="card-h"><h3>Weekly activity</h3><div class="right"><span class="badge grey">Last 7 days</span></div></div>
        <div class="card-b">${barChart(isZero ? [0, 0, 0, 0, 0, 0, 0] : [0, 0, 0, 0, 0, 20, 0], ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'], 600, 180, '#243B6B')}</div>
      </div>
      <div class="card">
        <div class="card-h"><h3>Accuracy trend</h3><div class="right"><span class="badge ${avgAcc ? 'green' : 'grey'}">${avgAcc ? icon('arrowUp', 'ic-xs') + ' Active' : 'Baseline'}</span></div></div>
        <div class="card-b">${sparkline(isZero ? [0, 0, 0, 0, 0, 0, 0] : [0, 0, 0, 0, 0, avgAcc || 100, avgAcc || 100], 600, 180, '#2E9B68')}</div>
      </div>
    </div>

    <div class="grid g-3 mb-6">
      <div class="card pad">
        <div class="h4 mb-3">Revision effectiveness</div>
        <div class="tiny mb-3">Knowledge health improvement after each revision session</div>
        ${sparkline(isZero ? [0, 0, 0, 0, 0, 0, 0] : [0, 0, 0, 0, 0, 6, 6], 400, 120, '#18A6A6')}
        <div class="flex-b mt-3"><span class="tiny">${isZero ? 'No sessions yet' : 'Positive retention'}</span><span class="badge ${isZero ? 'grey' : 'teal'}">${isZero ? 'Baseline' : 'Active'}</span></div>
      </div>
      <div class="card pad">
        <div class="h4 mb-3">Study session frequency</div>
        <div class="tiny mb-3">Sessions per day this week</div>
        ${barChart(isZero ? [0, 0, 0, 0, 0, 0, 0] : [0, 0, 0, 0, 0, 1, 0], ['M', 'T', 'W', 'T', 'F', 'S', 'S'], 400, 120, '#7C5CD6')}
        <div class="flex-b mt-3"><span class="tiny">${isZero ? '0 avg/day' : '1 session today'}</span><span class="badge ${isZero ? 'grey' : 'violet'}">${isZero ? 'Starting' : 'On track'}</span></div>
      </div>
      <div class="card pad">
        <div class="h4 mb-3">Time distribution</div>
        <div class="tiny mb-3">Where your study time goes</div>
        ${[
          ['Practice questions', isZero ? 0 : 70, 'indigo'],
          ['Revision', isZero ? 0 : 20, 'amber'],
          ['Reading materials', isZero ? 0 : 10, 'teal'],
          ['Assessments', 0, 'violet'],
        ].map(([n, v, c]) => `
          <div class="flex gap-3 mb-3" style="font-size:12.5px">
            <span style="flex:0 0 130px">${n}</span>
            ${progressBar(v as number, c as string)}
            <b style="width:36px;text-align:right">${v}%</b>
          </div>`).join('')}
      </div>
  </div>`;
}

/* ---------- Weak Areas ---------- */
export function studentWeak(): string {
  const allTopics = SUBJECTS.flatMap(s => s.topicList);
  const weakTopics = allTopics.filter(t => (t.done || 0) > 0 && (t.mastery || 0) < 60);

  return `
  <div class="page">
    ${pageHead('Weak Areas', 'Topics that need your attention', 'Ranked by knowledge health, forgetting risk and recent accuracy.')}

    ${weakTopics.length === 0 ? `
      <div class="card pad-lg mb-6" style="padding:48px 24px;text-align:center;color:var(--text-3)">
        <div style="font-size:36px;margin-bottom:8px">✨</div>
        <h3 class="h3 mb-2">No Weak Areas Identified</h3>
        <p style="font-size:13.5px;max-width:480px;margin:0 auto 18px auto;line-height:1.5">
          You have a clean slate with no detected weak areas. Take topic quizzes and practice tests — if your accuracy on any topic falls below the target threshold, it will automatically appear here for remediation.
        </p>
        <button class="btn btn-primary" onclick="navigate('student/learning')">${icon('play')} Start Topic Practice</button>
      </div>
    ` : `
    ${aiInsight('Priority focus this week', 'EduSense AI has flagged topics requiring attention based on your latest practice sessions.', 'Open revision plan', `navigate('student/revision')`)}

    <div class="card mt-5">
      <div class="card-h"><h3>Ranked by urgency</h3></div>
      <table class="tbl">
        <thead><tr><th>Topic</th><th>Subject</th><th>Knowledge Health</th><th>Risk</th><th>Last revised</th><th></th></tr></thead>
        <tbody>
          ${weakTopics.map(t => `
            <tr>
              <td class="nm">${t.name}</td>
              <td class="muted">Standard 10</td>
              <td><div class="flex gap-2" style="width:130px">${progressBar(t.kh, t.kh >= 70 ? 'green' : t.kh >= 55 ? 'amber' : 'coral')}<b style="font-size:12px">${t.kh}%</b></div></td>
              <td>${riskBadge(t.risk)}</td>
              <td class="muted">${t.last}</td>
              <td class="right"><button class="btn btn-sm btn-primary" onclick="startQuiz('${t.name}')">Review</button></td>
            </tr>`).join('')}
        </tbody>
      </table>
    </div>
    `}
  </div>`;
}


/* ---------- Assessments ---------- */
export function studentAssessments(): string {
  const count = COMPLETED_ASSESSMENTS.length;
  const avgScore = count > 0 ? Math.round(COMPLETED_ASSESSMENTS.reduce((a, b) => a + b.score, 0) / count) : null;
  const bestSubj = count > 0 ? COMPLETED_ASSESSMENTS[0].subject : 'None';

  return `
  <div class="page">
    ${pageHead('Assessments', 'Your assessments', 'Scheduled tests, completed attempts and detailed performance breakdowns.',
      `<button class="btn btn-primary" onclick="startQuiz('Diagnostic Check')">${icon('play')} Quick practice</button>`)}

    <div class="grid g-4 mb-6">
      ${statBlock('Upcoming', UPCOMING_ASSESSMENTS.length, 'Scheduled', 'calendar')}
      ${statBlock('Completed', count, count === 0 ? 'None yet' : 'This month', 'check', 'up')}
      ${statBlock('Avg. score', avgScore !== null ? `${avgScore}%` : '--', count === 0 ? 'Not taken yet' : 'Active', 'chart', 'up')}
      ${statBlock('Best subject', bestSubj, count === 0 ? 'Unassessed' : 'Top performer', 'award', 'up')}
    </div>

    <div class="sec-head"><div><h2>${icon('calendar')} Upcoming Tests</h2><p>Scheduled by your teacher</p></div></div>
    <div class="grid g-3 mb-6">
      ${UPCOMING_ASSESSMENTS.length === 0 ? `
        <div class="card pad-lg" style="grid-column:1/-1;text-align:center;color:var(--text-3);padding:36px 24px">
          No upcoming tests scheduled by your teacher.
        </div>
      ` : UPCOMING_ASSESSMENTS.map(a => `
        <div class="assess-card">
          <div class="ac-h">
            <div>
              <div class="tiny" style="color:${a.color};font-weight:700;text-transform:uppercase;letter-spacing:.05em">${a.subject}</div>
              <h4>${a.topic}</h4>
              <div class="ac-sub">${a.date} · ${a.time}</div>
            </div>
            <span class="badge ${a.daysLeft <= 3 ? 'coral' : a.daysLeft <= 7 ? 'amber' : 'indigo'}">${a.daysLeft}d</span>
          </div>
          <div class="ac-meta">
            <div class="m">${icon('clock')} ${a.duration}</div>
            <div class="m">${icon('check')} ${a.questions} Q</div>
            <div class="m">${icon('target')} ${a.difficulty}</div>
          </div>
          <div class="flex-b mb-3" style="font-size:11.5px;color:var(--text-3)">
            <span>Preparation</span><b style="color:var(--text)">${a.prep === 0 ? 'Not started' : a.prep + '%'}</b>
          </div>
          ${progressBar(a.prep, a.prep >= 70 ? 'green' : a.prep >= 50 ? 'amber' : 'coral')}
          <div class="flex gap-2 mt-3">
            <button class="btn btn-primary btn-sm" style="flex:1" onclick="startQuiz('${a.topic}')">${icon('play')} Practice</button>
            <button class="btn btn-sm" onclick="navigate('student/revision')">Revise</button>
          </div>
        </div>`).join('')}
    </div>

    <div class="sec-head"><div><h2>${icon('award')} Completed Tests</h2><p>Review performance and knowledge impact</p></div></div>
    <div class="card">
      ${count === 0 ? `
        <div style="padding:48px 24px;text-align:center;color:var(--text-3)">
          <div style="font-size:36px;margin-bottom:8px">📝</div>
          <h3 class="h3 mb-2">No Completed Tests Yet</h3>
          <p style="font-size:13px;max-width:440px;margin:0 auto 16px auto">
            You haven't completed any assessments or quizzes yet. When you take a quiz or exam, your score, question accuracy, and knowledge health impact will be recorded here.
          </p>
          <button class="btn btn-primary" onclick="startQuiz('Diagnostic Check')">${icon('play')} Take Practice Check</button>
        </div>
      ` : `
      <table class="tbl">
        <thead><tr><th>Topic</th><th>Subject</th><th>Date</th><th>Score</th><th>Accuracy</th><th>Knowledge Impact</th><th></th></tr></thead>
        <tbody>
          ${COMPLETED_ASSESSMENTS.map(a => `
            <tr>
              <td class="nm">${a.topic}</td>
              <td class="muted">${a.subject}</td>
              <td class="muted">${a.date}</td>
              <td><b>${a.score}%</b></td>
              <td>${a.accuracy}%</td>
              <td><span class="badge ${a.kh > 0 ? 'green' : 'coral'}">${a.kh > 0 ? '+' : ''}${a.kh}% KH</span></td>
              <td class="right"><button class="btn btn-sm" onclick="openResult(${a.score}, '${a.topic}')">View result</button></td>
            </tr>`).join('')}
        </tbody>
      </table>
      `}
    </div>
  </div>`;
}

export function openResult(score: number, topic: string): void {
  openModal(`
    <div class="modal-h">
      <div style="flex:1"><h3>Assessment Result</h3><div class="sub">${topic}</div></div>
      <button class="btn btn-sm btn-icon" onclick="closeOverlay()">${icon('x')}</button>
    </div>
    <div class="modal-b">
      <div class="center mb-5">
        ${donut(score, 150, 13, score >= 75 ? '#2E9B68' : score >= 55 ? '#E9A23B' : '#E56B6F')}
        <div class="h3 mt-3">Score ${score}%</div>
        <p class="small">${score >= 75 ? 'Excellent — strong understanding' : score >= 55 ? 'Good attempt — a short revision will strengthen this' : 'This topic needs another revision pass'}</p>
      </div>
      <div class="grid g-3 mb-4">
        <div class="card pad-sm" style="text-align:center"><div class="tiny">Accuracy</div><div style="font-size:20px;font-weight:800;font-family:Manrope">${score}%</div></div>
        <div class="card pad-sm" style="text-align:center"><div class="tiny">Time taken</div><div style="font-size:20px;font-weight:800;font-family:Manrope">22 min</div></div>
        <div class="card pad-sm" style="text-align:center"><div class="tiny">Knowledge impact</div><div style="font-size:20px;font-weight:800;font-family:Manrope;color:var(--green)">+6%</div></div>
      </div>
      <div class="grid g-2">
        <div class="card pad-sm">
          <div class="h4 mb-2" style="color:var(--green)">Strong topics</div>
          <ul style="list-style:none;font-size:12.5px">
            <li style="padding:6px 0">✓ Core definitions</li>
            <li style="padding:6px 0">✓ Conceptual reasoning</li>
          </ul>
        </div>
        <div class="card pad-sm">
          <div class="h4 mb-2" style="color:var(--coral)">Weak topics</div>
          <ul style="list-style:none;font-size:12.5px">
            <li style="padding:6px 0">• Applied problems</li>
            <li style="padding:6px 0">• Multi-step questions</li>
          </ul>
        </div>
      </div>
      <div class="ai-card mt-4">
        <div class="ai-head"><div class="ai-mark">${icon('sparkles')}</div><b>EduSense Insight</b></div>
        <div class="ai-body">Your accuracy on <b>applied questions</b> is 32% lower than on conceptual ones. Recommended: 15 practice questions in this format before your next assessment.</div>
      </div>
    </div>
    <div class="modal-f">
      <button class="btn" onclick="closeOverlay()">Close</button>
      <button class="btn btn-primary" onclick="closeOverlay();navigate('student/revision')">${icon('refresh')} Add to revision plan</button>
    </div>`, { width: 'wide' });
}

/* ---------- Study Materials ---------- */
export function studentMaterials(): string {
  return `
  <div class="page">
    ${pageHead('Study Materials', 'Your learning resources', 'Notes, videos, presentations and practice sets — all aligned to your syllabus.')}

    <div class="grid g-3-1">
      <div>
        <div class="card mb-5">
          <div class="card-b">
            <div class="flex gap-3 wrap">
              <div class="tb-search" style="flex:1;min-width:240px;display:flex;position:relative">
                <svg class="ic ic-sm" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><circle cx="11" cy="11" r="7"/><path d="M21 21l-4.3-4.3"/></svg>
                <input placeholder="Search materials...">
              </div>
              <select class="input select" style="width:auto"><option>All subjects</option><option>Mathematics</option><option>Physics</option><option>Chemistry</option><option>Biology</option><option>English</option></select>
              <select class="input select" style="width:auto"><option>All types</option><option>PDF</option><option>Video</option><option>Notes</option><option>Presentation</option></select>
            </div>
            <div class="flex gap-2 mt-4 wrap">
              <button class="badge indigo" style="cursor:pointer">All</button>
              <button class="badge grey" style="cursor:pointer">Recent</button>
              <button class="badge grey" style="cursor:pointer">Downloaded</button>
              <button class="badge grey" style="cursor:pointer">Recommended</button>
            </div>
          </div>
        </div>

        <div class="grid g-3">
          <div class="card pad-lg" style="grid-column:1/-1;text-align:center;color:var(--text-3);padding:48px 24px">
            No study materials uploaded by your school yet. Official materials added by your teachers will appear here.
          </div>
        </div>
      </div>

      <div class="flex-c">
        <div class="ai-card">
          <div class="ai-head"><div class="ai-mark">${icon('sparkles')}</div><b>Study Guidance</b></div>
          <div class="ai-body">Curriculum syllabus is active. Select any chapter from <b>My Learning</b> to start adaptive practice.</div>
          <div class="ai-actions"><button class="btn btn-sm btn-teal" onclick="navigate('student/learning')">View Curriculum</button></div>
        </div>

        <div class="card">
          <div class="card-h" style="padding-bottom:12px"><h3 style="font-size:13.5px">Recently opened</h3></div>
          <div class="card-b" style="padding-top:0">
            <div style="color:var(--text-3);font-size:12px;padding:12px 0">No recently opened materials.</div>
          </div>
        </div>
      </div>
    </div>
  </div>`;
}

/* ---------- Notes ---------- */
export function studentNotes(): string {
  const notes: any[] = [];
  return `
  <div class="page">
    ${pageHead('Notes', 'Your personal notes', 'Everything you have written or saved while studying.', '<button class="btn btn-primary" onclick="toast(\'Note editor ready\',\'\',\'good\')">' + icon('plus') + ' New note</button>')}
    <div class="grid g-3">
      ${notes.length === 0 ? `
        <div class="card pad-lg" style="grid-column:1/-1;text-align:center;color:var(--text-3);padding:48px 24px">
          No notes created yet. Click "New note" to write your first study note.
        </div>
      ` : notes.map(n => `
        <div class="card hoverable pad" style="cursor:pointer">
          <div class="flex-b mb-3">
            <span class="badge indigo">${n.subject}</span>
            <button class="tb-icon" style="width:28px;height:28px">${icon('more', 'ic-sm')}</button>
          </div>
          <div class="h4 mb-2" style="font-size:14px;line-height:1.4">${n.title}</div>
          <p class="small mb-3" style="color:var(--text-3)">${n.words} words · updated ${n.updated}</p>
          <div class="flex gap-2">${icon('file', 'ic-sm')}<span class="tiny">Personal note</span></div>
        </div>`).join('')}
    </div>
  </div>`;
}

/* ---------- Assignments ---------- */
export function studentAssignments(): string {
  const items: any[] = [];
  return `
  <div class="page">
    ${pageHead('Assignments', 'Your assignments', 'Track pending work, in-progress tasks and graded submissions.')}
    <div class="grid g-4 mb-6">
      ${statBlock('Pending', 0, 'Due this week', 'alert')}
      ${statBlock('In progress', 0, 'Active tasks', 'edit')}
      ${statBlock('Submitted', 0, 'This month', 'check')}
      ${statBlock('Avg. score', '--', 'On graded work', 'award')}
    </div>
    <div class="card">
      <div class="card-h"><h3>All assignments</h3></div>
      <div class="card-b">
        ${items.length === 0 ? `
          <div style="text-align:center;padding:36px 24px;color:var(--text-3)">
            No assignments assigned yet. Work assigned by your teachers will appear here.
          </div>
        ` : items.map(i => `
          <div style="padding:16px 0;border-bottom:1px solid var(--border-2)">
            <div class="flex-b mb-2 wrap" style="gap:12px">
              <div>
                <div class="h4">${i.title}</div>
                <div class="tiny">${i.subject} · Due ${i.due}</div>
              </div>
              <div class="flex gap-2">
                ${i.status === 'pending' ? '<span class="badge coral">Pending</span>' : i.status === 'in-progress' ? '<span class="badge amber">In progress</span>' : i.status === 'graded' ? `<span class="badge green">Graded · ${i.score}%</span>` : '<span class="badge teal">Submitted</span>'}
                <button class="btn btn-sm">${i.status === 'graded' ? 'View' : 'Open'}</button>
              </div>
            </div>
            ${i.progress > 0 && i.progress < 100 ? `<div class="flex gap-2" style="font-size:11.5px;color:var(--text-3)">${progressBar(i.progress, 'amber')}<b style="color:var(--text)">${i.progress}%</b></div>` : ''}
          </div>`).join('')}
      </div>
    </div>
  </div>`;
}

/* ---------- Exams ---------- */
export function studentExams(): string {
  const exams: any[] = [];
  return `
  <div class="page">
    ${pageHead('Exams', 'Your exam schedule', 'Board exams, internal assessments and unit tests this term.')}
    <div class="grid g-3 mb-6">
      ${exams.length === 0 ? `
        <div class="card pad-lg" style="grid-column:1/-1;text-align:center;color:var(--text-3);padding:36px 24px">
          No exams scheduled yet. Official school examination schedules will appear here.
        </div>
      ` : exams.map(e => `
        <div class="card pad">
          <div class="flex-b mb-3"><span class="badge ${e.c}">${e.w} left</span>${icon('award', 'ic-sm')}</div>
          <div class="h4 mb-2" style="line-height:1.35">${e.t}</div>
          <div class="tiny">${e.d}</div>
        </div>`).join('')}
    </div>
    <div class="card">
      <div class="card-h"><h3>Full schedule</h3></div>
      <table class="tbl">
        <thead><tr><th>Exam</th><th>Date</th><th>Duration</th><th>Pattern</th><th>Syllabus</th></tr></thead>
        <tbody>
          <tr>
            <td colspan="5" style="text-align:center;padding:36px;color:var(--text-3)">
              No examination schedules published at this time.
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>`;
}

/* ---------- Timetable ---------- */
export function studentTimetable(): string {
  const tt = TIMETABLE;
  return `
  <div class="page">
    ${pageHead('Timetable', 'Weekly class schedule', 'Your regular weekly schedule for Grade 10 · Section A.')}
    <div class="card">
      <div class="card-h">
        <h3>Week of Sep 15 – Sep 19, 2026</h3>
        <div class="right"><button class="btn btn-sm">${icon('download')} Print</button></div>
      </div>
      <div class="card-b" style="overflow-x:auto">
        <div class="tt-grid" style="min-width:820px">
          <div class="tt-cell tt-head">Time</div>
          ${tt.days.map(d => `<div class="tt-cell tt-head">${d}</div>`).join('')}
          ${tt.periods.map(p => `
            <div class="tt-cell tt-time">${p.time}</div>
            ${p.rows.map(([subject, topic, color]) => `
              <div class="tt-cell">
                ${subject === '—'
                  ? `<div class="tt-item" style="color:var(--text-3);border-color:${color};background:${color}20">${topic}</div>`
                  : `<div class="tt-item" style="color:${color};border-color:${color};background:${color}10">${subject}<small>${topic}</small></div>`}
              </div>`).join('')}
          `).join('')}
        </div>
      </div>
    </div>
  </div>`;
}

/* ---------- Notifications ---------- */
export function studentNotifications(): string {
  const cats = [
    { id: 'all', label: 'All' },
    { id: 'learning', label: 'Learning' },
    { id: 'revision', label: 'Revision' },
    { id: 'assessment', label: 'Assessment' },
    { id: 'academic', label: 'Academic' },
    { id: 'system', label: 'System' }
  ];
  const filtered = UI.notifFilter === 'all' ? NOTIFICATIONS : NOTIFICATIONS.filter(n => n.cat === UI.notifFilter);
  return `
  <div class="page">
    ${pageHead('Notifications', 'Your notification center', 'Everything that needs your attention — learning, revision, assessments and school announcements.', '<button class="btn" onclick="toast(\'All marked as read\',\'You are up to date\',\'good\')">' + icon('check') + ' Mark all read</button>')}

    <div class="tabs mb-5">
      ${cats.map(c => `<button class="tab ${UI.notifFilter === c.id ? 'on' : ''}" onclick="UI.notifFilter='${c.id}';navigate('student/notifications')">${c.label}</button>`).join('')}
    </div>

    <div class="card">
      <div class="card-b">
        ${filtered.length ? filtered.map(n => `
          <div class="notice" style="${n.unread ? 'background:var(--indigo-25);margin:0 -20px;padding:14px 20px' : ''}">
            <span class="n-dot ${n.urgent ? 'urgent' : n.cat === 'learning' || n.cat === 'revision' ? 'teal' : ''}"></span>
            <div class="n-body">
              <b>${n.title} ${n.unread ? `<span class="badge indigo" style="margin-left:6px">New</span>` : ''}</b>
              <p>${n.body}</p>
              <div class="n-time">${icon('clock', 'ic-xs')} ${n.time}</div>
            </div>
          </div>`).join('') : `<div class="empty"><div class="empty-ic">${icon('bell')}</div><b>No notifications</b><span>Nothing here in this category yet.</span></div>`}
      </div>
    </div>
  </div>`;
}

/* ---------- Profile ---------- */
export function studentProfile(): string {
  const u = getCurrentUser();
  return `
  <div class="page">
    ${pageHead('Profile', 'Your profile', 'Your personal and academic information.', `<button class="btn btn-primary" onclick="window.openChangePasswordModal()">${icon('lock', 'ic-xs')} Change Password</button>`)}

    <div class="card mb-6">
      <div class="card-b" style="padding:28px">
        <div class="flex gap-5 wrap">
          <div class="av xl" style="background:linear-gradient(135deg,var(--teal),var(--indigo))">${u.initials}</div>
          <div style="flex:1;min-width:220px">
            <h1 class="h1 mb-2">${u.name}</h1>
            <p class="body mb-3">${u.grade} · ${u.section} · Roll No ${u.roll}</p>
            <div class="flex gap-2 wrap">
              <span class="badge indigo">${u.school}</span>
              <span class="badge grey">Joined ${u.joined}</span>
              <span class="badge indigo">GSEB Curriculum</span>
            </div>
          </div>
          <div class="flex gap-2" style="align-self:flex-start">
            <button class="btn">${icon('download')} Report card</button>
          </div>
        </div>
      </div>
    </div>

    <div class="grid g-2">
      <div class="card">
        <div class="card-h"><h3>Personal information</h3></div>
        <div class="card-b">
          ${[
            ['Full name', u.name],
            ['Email', u.email],
            ['Date of birth', '—'],
            ['Phone', '—'],
            ['Address', '—'],
            ['Guardian', '—'],
          ].map(([k, v]) => `
            <div class="flex-b" style="padding:11px 0;border-bottom:1px solid var(--border-2);font-size:13px">
              <span class="muted">${k}</span><b>${v}</b>
            </div>`).join('')}
        </div>
      </div>

      <div class="card">
        <div class="card-h"><h3>Academic information</h3></div>
        <div class="card-b">
          ${[
            ['Grade', u.grade],
            ['Section', u.section],
            ['Roll number', u.roll],
            ['Academic year', '2025-2026'],
            ['Stream', 'Science'],
            ['Class teacher', '—'],
          ].map(([k, v]) => `
            <div class="flex-b" style="padding:11px 0;border-bottom:1px solid var(--border-2);font-size:13px">
              <span class="muted">${k}</span><b>${v}</b>
            </div>`).join('')}
        </div>
      </div>

      <div class="card">
        <div class="card-h"><h3>Learning snapshot</h3></div>
        <div class="card-b">
          <div class="grid g-2">
            ${statBlock('Overall mastery', '--', 'Unassessed', 'award')}
            ${statBlock('Knowledge health', '--', 'Unassessed', 'brain')}
            ${statBlock('Curriculum status', 'Enrolled', 'Term 1 · 2026', 'book')}
            ${statBlock('Topics mastered', '0', 'of 42', 'book2')}
          </div>
        </div>
      </div>

      <div class="card">
        <div class="card-h"><h3>Study preferences</h3></div>
        <div class="card-b">
          ${[
            ['Preferred study time', 'Self-paced'],
            ['Session length', '25 minutes'],
            ['Revision reminders', 'Enabled · push + email'],
            ['Weekly goal', 'School Mandate'],
          ].map(([k, v]) => `
            <div class="flex-b" style="padding:11px 0;border-bottom:1px solid var(--border-2);font-size:13px">
              <span class="muted">${k}</span><b>${v}</b>
            </div>`).join('')}
        </div>
      </div>
    </div>
  </div>`;
}

/* ---------- Settings ---------- */
export function studentSettings(): string {
  return `
  <div class="page">
    ${pageHead('Settings', 'Your preferences', 'Control how EduSense works for you.')}

    <div class="grid g-2">
      <div class="card">
        <div class="card-h"><h3>Notifications</h3></div>
        <div class="card-b">
          ${[
            ['Revision reminders', true],
            ['Assessment reminders', true],
            ['Weekly progress summary', true],
            ['New content alerts', false],
            ['School assessment schedule', true],
          ].map(([k, v]) => `
            <div class="flex-b" style="padding:12px 0;border-bottom:1px solid var(--border-2)">
              <span style="font-size:13px">${k}</span>
              <label style="position:relative;display:inline-block;width:38px;height:22px;cursor:pointer">
                <input type="checkbox" ${v ? 'checked' : ''} style="display:none" onchange="toast('Preference saved','','good')">
                <span style="position:absolute;inset:0;background:${v ? 'var(--indigo)' : 'var(--border)'};border-radius:99px;transition:.2s"></span>
                <span style="position:absolute;top:3px;left:${v ? '19px' : '3px'};width:16px;height:16px;background:#fff;border-radius:50%;transition:.2s"></span>
              </label>
            </div>`).join('')}
        </div>
      </div>

      <div class="card">
        <div class="card-h"><h3>Study preferences</h3></div>
        <div class="card-b">
          <div class="field">
            <label>Preferred study time</label>
            <select class="input select"><option>4:00 PM – 7:00 PM</option><option>Morning (6–9 AM)</option><option>Evening (7–10 PM)</option></select>
          </div>
          <div class="field">
            <label>Session length</label>
            <select class="input select"><option>25 minutes</option><option>45 minutes</option><option>60 minutes</option></select>
          </div>
          <div class="field">
            <label>Weekly goal (sessions)</label>
            <input class="input" type="number" value="5" min="1" max="14">
          </div>
          <button class="btn btn-primary" onclick="toast('Preferences saved','','good')">Save preferences</button>
        </div>
      </div>

      <div class="card">
        <div class="card-h"><h3>Account & security</h3></div>
        <div class="card-b">
          <div class="field"><label>Email</label><input class="input" value="${STUDENT.email}" disabled></div>
          <div class="field"><label>Password</label><input class="input" type="password" value="••••••••••"></div>
          <button class="btn" onclick="toast('Password reset link sent','','good')">Change password</button>
          <button class="btn btn-ghost" onclick="toast('Signed out from all devices','','warn')">Sign out from all devices</button>
        </div>
      </div>

      <div class="card">
        <div class="card-h"><h3>Appearance</h3></div>
        <div class="card-b">
          <div class="field"><label>Theme</label>
            <select class="input select"><option>Light</option><option>System</option></select>
          </div>
          <div class="field"><label>Text size</label>
            <select class="input select"><option>Standard</option><option>Large</option></select>
          </div>
          <div class="field"><label>Language</label>
            <select class="input select"><option>English</option><option>हिन्दी</option></select>
          </div>
          <button class="btn btn-primary" onclick="toast('Settings saved','','good')">Save</button>
        </div>
      </div>
    </div>
  </div>`;
}

/* ---------- Help & Support ---------- */
export function studentHelp(): string {
  const faqs = [
    { q: 'How does Knowledge Health work?', a: 'Knowledge Health is a model-derived estimate that combines your accuracy, response time and time since last revision. It is an estimate, not a fixed truth — it updates as you learn and revise.' },
    { q: 'What is a forgetting event?', a: 'When your performance on a topic drops meaningfully after a gap in practice — usually 15–20 days — EduSense records a potential forgetting event and adds it to your revision plan.' },
    { q: 'How is my revision scheduled?', a: 'EduSense AI schedules revision at the moment it will have the greatest impact — balancing knowledge health, time since last revision, and upcoming assessments.' },
    { q: 'How accurate are these predictions?', a: 'They are estimates based on evidence, not certainties. A single low score never means you have forgotten something. Multiple consistent signals over time are required.' },
    { q: 'Can I reset my progress?', a: 'Progress cannot be reset from the student portal. Please contact your school administrator if you believe there is an error.' },
  ];
  return `
  <div class="page">
    ${pageHead('Help & Support', 'How can we help?', 'Answers to common questions, plus ways to reach the EduSense team.')}

    <div class="grid g-3 mb-6">
      <div class="card pad">
        <div class="qi" style="width:40px;height:40px;border-radius:11px;background:var(--indigo-50);color:var(--indigo);display:grid;place-items:center;margin-bottom:12px">${icon('help')}</div>
        <div class="h4 mb-2">Browse FAQs</div>
        <p class="small mb-3">Answers to the most common questions</p>
        <a class="small" style="color:var(--indigo);font-weight:600">See all FAQs →</a>
      </div>
      <div class="card pad">
        <div class="qi" style="width:40px;height:40px;border-radius:11px;background:var(--teal-50);color:var(--teal-600);display:grid;place-items:center;margin-bottom:12px">${icon('send')}</div>
        <div class="h4 mb-2">Contact support</div>
        <p class="small mb-3">Reach out for help within 1 working day</p>
        <a class="small" style="color:var(--indigo);font-weight:600">Send a message →</a>
      </div>
      <div class="card pad">
        <div class="qi" style="width:40px;height:40px;border-radius:11px;background:var(--amber-50);color:#B4731A;display:grid;place-items:center;margin-bottom:12px">${icon('alert')}</div>
        <div class="h4 mb-2">Report an issue</div>
        <p class="small mb-3">Something not working as expected?</p>
        <a class="small" style="color:var(--indigo);font-weight:600">Report a bug →</a>
      </div>
    </div>

    <div class="card">
      <div class="card-h"><h3>Frequently asked questions</h3></div>
      <div class="card-b">
        ${faqs.map(f => `
          <details style="padding:14px 0;border-bottom:1px solid var(--border-2)">
            <summary style="font-size:13.5px;font-weight:600;cursor:pointer;list-style:none;display:flex;justify-content:space-between;align-items:center">
              ${f.q}
              <span style="color:var(--text-3)">${icon('chevD', 'ic-sm')}</span>
            </summary>
            <p class="small mt-3" style="line-height:1.6">${f.a}</p>
          </details>`).join('')}
      </div>
    </div>
  </div>`;
}

/* ---------- AI Assistant Drawer ---------- */
export function openAIPanel(): void {
  openDrawer(`
    <div class="modal-h" style="border-radius:0">
      <div class="ai-mark" style="width:32px;height:32px">${icon('sparkles')}</div>
      <div style="flex:1">
        <h3 style="font-size:15px">EduSense AI</h3>
        <div class="sub">Your learning assistant — grounded in your syllabus</div>
      </div>
      <button class="btn btn-sm btn-icon" onclick="closeOverlay()">${icon('x')}</button>
    </div>
    <div style="flex:1;padding:20px 22px;display:flex;flex-direction:column;gap:16px;overflow-y:auto" id="aiChat">
      <div class="msg" style="display:flex;gap:10px">
        <div class="ai-mark" style="width:28px;height:28px;flex:0 0 auto">${icon('sparkles', 'ic-sm')}</div>
        <div class="bubble" style="background:var(--teal-50);border:1px solid rgba(24,166,166,.2);padding:11px 14px;border-radius:12px;font-size:13px;line-height:1.55">
          Hi ${getCurrentUser().full_name?.split(' ')[0] || 'there'} 👋 I can help you understand topics, plan revision, or prepare for your assessments. What would you like to work on?
        </div>
      </div>
      <div style="font-size:11.5px;color:var(--text-3);text-transform:uppercase;letter-spacing:.05em;font-weight:700;margin-top:4px">Suggested</div>
      <div style="display:flex;flex-direction:column;gap:8px">
        ${['Explain Electricity simply', 'Why is my Physics knowledge declining?', 'Make a 3-day revision plan for Physics', 'What should I study first today?'].map(q => `
          <button class="qa-tile" onclick="sendAI('${q}')">
            <div class="qi" style="width:28px;height:28px;background:var(--teal-50);color:var(--teal-600)">${icon('sparkles', 'ic-sm')}</div>
            <div><b style="font-size:12.5px">${q}</b></div>
          </button>`).join('')}
      </div>
    </div>
    <div style="padding:16px 22px;border-top:1px solid var(--border);display:flex;gap:10px">
      <input class="input" id="aiInput" placeholder="Ask anything…" onkeydown="if(event.key==='Enter')sendAI()">
      <button class="btn btn-primary btn-icon" onclick="sendAI()">${icon('send')}</button>
    </div>`);
}

export function sendAI(q?: string): void {
  const input = document.getElementById('aiInput') as HTMLInputElement | null;
  const msg = q || (input ? input.value.trim() : '');
  if (!msg) return;
  if (input) input.value = '';
  const chat = document.getElementById('aiChat');
  if (!chat) return;
  chat.insertAdjacentHTML('beforeend', `
    <div style="display:flex;gap:10px;justify-content:flex-end">
      <div style="background:var(--indigo);color:#fff;padding:11px 14px;border-radius:12px;font-size:13px;max-width:80%;line-height:1.55">${msg}</div>
    </div>`);
  chat.scrollTop = chat.scrollHeight;
  const typing = document.createElement('div');
  typing.innerHTML = `<div style="display:flex;gap:10px"><div class="ai-mark" style="width:28px;height:28px;flex:0 0 auto">${icon('sparkles', 'ic-sm')}</div><div style="background:var(--bg);padding:11px 14px;border-radius:12px;font-size:13px">Thinking…</div></div>`;
  chat.appendChild(typing);
  chat.scrollTop = chat.scrollHeight;
  setTimeout(() => {
    typing.remove();
    chat.insertAdjacentHTML('beforeend', `
      <div style="display:flex;gap:10px">
        <div class="ai-mark" style="width:28px;height:28px;flex:0 0 auto">${icon('sparkles', 'ic-sm')}</div>
        <div style="background:var(--teal-50);border:1px solid rgba(24,166,166,.2);padding:11px 14px;border-radius:12px;font-size:13px;line-height:1.6;max-width:86%">
          ${aiReply(msg)}
        </div>
      </div>`);
    chat.scrollTop = chat.scrollHeight;
  }, 750);
}

export function aiReply(q: string): string {
  const s = q.toLowerCase();
  if (s.includes('electricity')) return '<b>Electricity</b> is the flow of electric charge through a conductor.<br><br>Key ideas:<br>• Current = charge / time (I = Q/t)<br>• Ohm\'s law: V = IR<br>• Resistance depends on length, area and material<br><br>Your weakest sub-topic is <b>circuit analysis with multiple resistors</b>. I recommend 10 practice questions on series and parallel combinations.';
  if (s.includes('physics') && (s.includes('declin') || s.includes('why'))) return 'Your <b>Physics knowledge health</b> dropped from 72% to 42% over 5 sessions — but only on <b>Electricity & Circuits</b>.<br><br>What the data shows:<br>• Accuracy dropped 24% on multi-step problems<br>• You haven\'t revised this topic in 9 days<br>• Response time increased by 40%<br><br>Recommended: 20-minute revision session today, focused on circuit diagrams.';
  if (s.includes('plan') || s.includes('revision')) return 'Here\'s a 3-day Physics revision plan for your upcoming assessment:<br><br><b>Day 1 (today):</b> Electricity — read notes, then 10 practice questions<br><b>Day 2:</b> Circuit diagrams — 15 questions, timed<br><b>Day 3:</b> Full mixed check — 20 MCQ, review mistakes<br><br>I can add this directly to your Revision Plan.';
  if (s.includes('first') || s.includes('today') || s.includes('study')) return 'Your three priorities for today:<br><br>1. <b>Physics — Electricity</b> (highest forgetting risk, 42% knowledge health)<br>2. <b>Chemistry — Organic Chemistry</b> (35% knowledge health)<br>3. <b>Mathematics — Probability</b> (revision overdue)<br><br>Start with Physics — it has the highest impact on your upcoming assessment.';
  return 'Here is what I can tell you from your current Grade 10 material: this concept is covered in your syllabus and connects to topics you are already studying. Try the practice set inside <b>My Learning</b>, and if a specific part is confusing, ask me about that part directly and I will break it down step by step.';
}

export function openSubject(id: string): void {
  UI.subjectId = id;
  window.navigate('student/learning');
}

export function switchTab(btn: HTMLElement, paneId: string): void {
  const wrap = btn.closest('.card');
  if (!wrap) return;
  wrap.querySelectorAll('.tab').forEach(b => b.classList.remove('on'));
  btn.classList.add('on');
  wrap.querySelectorAll('.tabpane').forEach(p => p.classList.add('hide'));
  const pane = wrap.querySelector('#' + paneId);
  if (pane) pane.classList.remove('hide');
}

// Global browser window bindings
if (typeof window !== 'undefined') {
  window.openSubject = openSubject;
  window.switchTab = switchTab;

  window.openResult = openResult;
  window.openAIPanel = openAIPanel;
  window.sendAI = sendAI;
  window.closeOverlay = closeOverlay;
  window.toast = toast;
}
