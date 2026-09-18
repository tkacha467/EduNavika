// Student View Renderers for EduNavika

import { icon } from '../../utils/icons';
import { sparkline, barChart, donut, heatmap } from '../../utils/charts';
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
  CAL_EVENTS,
  calKey,
} from './studentData';

declare const window: any;

/* ---------- Dashboard ---------- */
export function studentDashboard(): string {
  const sub = SUBJECTS;
  const revCount = REVISION_QUEUE.filter(r => r.when === 'Today').length;
  const todayFocus = [
    { kind: 'continue', label: 'Continue Learning', subject: 'Mathematics', topic: 'Trigonometry — Lesson 5', meta: 'Estimated 25 min remaining', pct: 62, go: "openSubject('math')", action: 'Resume' },
    { kind: 'revision', label: 'Revision Due', subject: 'Physics', topic: 'Electricity & Circuits', meta: 'Knowledge health: 42% · Review recommended today', pct: 42, go: "navigate('student/revision')", action: 'Review now' },
    { kind: 'practice', label: 'Quick Practice', subject: 'Chemistry', topic: 'Balancing Equations', meta: '10 questions · Estimated 12 min', pct: 0, go: "startQuiz('Chemistry')", action: 'Start' }
  ];

  return `
  <div class="page with-rail">
    <!-- Welcome -->
    <div class="welcome">
      <div class="welcome-c">
        <div class="welcome-l">
          <div class="hi">Good morning, Aarav 👋</div>
          <h1>Here's what needs your attention today.</h1>
          <p>You have ${revCount} revisions due and ${UPCOMING_ASSESSMENTS[0].daysLeft} days until your next assessment. Focus on Physics — Electricity first.</p>
        </div>
        <div class="welcome-r">
          <div class="wstat"><div class="l">Streak</div><div class="v">${STUDENT.streak}<small>days</small></div><div class="d">🔥 Personal best: 12</div></div>
          <div class="wstat"><div class="l">Today</div><div class="v">1<small>/ 3</small></div><div class="d">Goal progress</div></div>
          <div class="wstat"><div class="l">Weekly</div><div class="v">${STUDENT.weeklyGoal}<small>%</small></div><div class="d">Completion</div></div>
          <div class="wstat"><div class="l">Next test</div><div class="v">${UPCOMING_ASSESSMENTS[0].daysLeft}<small>days</small></div><div class="d">${UPCOMING_ASSESSMENTS[0].subject}</div></div>
        </div>
      </div>
    </div>

    <!-- Today's Focus -->
    <div class="sec-head">
      <div><h2>${icon('target')} Today's Focus</h2><p>Three things to complete today. Stay focused, then take a break.</p></div>
      <div class="right"><button class="btn btn-sm" data-go="student/learning">View all</button></div>
    </div>
    <div class="focus-grid mb-6">
      ${todayFocus.map(f => `
        <div class="focus-card ${f.kind}" onclick="${f.go}">
          <div class="ftag">${f.kind === 'continue' ? icon('play', 'ic-xs') : f.kind === 'revision' ? icon('refresh', 'ic-xs') : icon('zap', 'ic-xs')} ${f.label}</div>
          <div class="fsub">${f.subject}</div>
          <h4>${f.topic}</h4>
          <div class="fmeta">${f.meta}</div>
          ${f.pct > 0 ? `<div class="fbar">${progressBar(f.pct, f.kind === 'revision' ? 'amber' : 'indigo')}<b>${f.pct}%</b></div>` : ''}
          <button class="btn btn-sm btn-primary" style="width:100%">${f.action}</button>
        </div>`).join('')}
    </div>

    <!-- Knowledge Health + AI Insight -->
    <div class="grid g-3-1 mb-6">
      <div class="card">
        <div class="card-h">
          <div><h3>Knowledge Health</h3><div class="sub">Model-derived estimate of how stable your learning is</div></div>
          <div class="right"><span class="badge teal">${icon('sparkles')} EduSense AI</span></div>
        </div>
        <div class="card-b">
          <div class="kh-hero" style="padding:0;border:0">
            <div class="kh-top">
              <div class="kh-score">
                <div class="big">73<small>%</small></div>
                <div class="cap"><b>Overall Knowledge Health</b>Across 6 subjects · Updated 2 hours ago</div>
              </div>
              <div class="kh-dist">
                <div class="kh-bar">
                  <div class="kh-seg" style="width:38%;background:var(--green)"></div>
                  <div class="kh-seg" style="width:24%;background:var(--teal)"></div>
                  <div class="kh-seg" style="width:22%;background:var(--amber)"></div>
                  <div class="kh-seg" style="width:16%;background:var(--coral)"></div>
                </div>
                <div class="kh-legend">
                  <span class="item"><span class="sw" style="background:var(--green)"></span>Strong <b>38%</b></span>
                  <span class="item"><span class="sw" style="background:var(--teal)"></span>Stable <b>24%</b></span>
                  <span class="item"><span class="sw" style="background:var(--amber)"></span>Needs revision <b>22%</b></span>
                  <span class="item"><span class="sw" style="background:var(--coral)"></span>At risk <b>16%</b></span>
                </div>
              </div>
            </div>
            <div class="kh-lists">
              <div class="kh-list">
                <h4><span class="dot" style="background:var(--green)"></span> Strong</h4>
                <ul>
                  <li><b>Algebra</b><span class="pct" style="color:var(--green)">91%</span></li>
                  <li><b>Statistics</b><span class="pct" style="color:var(--green)">87%</span></li>
                  <li><b>Photosynthesis</b><span class="pct" style="color:var(--green)">90%</span></li>
                </ul>
              </div>
              <div class="kh-list">
                <h4><span class="dot" style="background:var(--amber)"></span> Needs Attention</h4>
                <ul>
                  <li><b>Electricity</b><span class="pct" style="color:var(--amber)">42%</span></li>
                  <li><b>Probability</b><span class="pct" style="color:var(--amber)">44%</span></li>
                  <li><b>Coordinate Geometry</b><span class="pct" style="color:var(--amber)">58%</span></li>
                </ul>
              </div>
              <div class="kh-list">
                <h4><span class="dot" style="background:var(--coral)"></span> At Risk</h4>
                <ul>
                  <li><b>Organic Chemistry</b><span class="pct" style="color:var(--coral)">35%</span></li>
                  <li><b>Light & Refraction</b><span class="pct" style="color:var(--coral)">58%</span></li>
                </ul>
              </div>
            </div>
            <div style="margin-top:16px;font-size:11.5px;color:var(--text-4);display:flex;align-items:center;gap:7px">
              ${icon('bulb', 'ic-xs')} Based on your recent practice, accuracy, response time and revision history.
            </div>
          </div>
        </div>
      </div>
      <div class="flex-c">
        ${aiInsight('EduSense Insight',
          `Your <b>Physics knowledge</b> has become less stable over the last 5 practice sessions. Accuracy dropped from <b>72%</b> to <b>48%</b> — concentrated on circuit analysis.`,
          'Review Physics now', `navigate('student/revision')`)}
        ${aiInsight('Weekly pattern',
          `You study best between <b>4 PM and 7 PM</b>. Your revision completion is <b>23% higher</b> on days when you start before 5 PM.`,
          'See analytics', `navigate('student/analytics')`)}
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
                  <b style="color:var(--text)">${a.prep}%</b>
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
          <div><h3>Learning This Week</h3><div class="sub">Sep 9 – Sep 15 · compared to previous week</div></div>
          <div class="right"><span class="badge green">${icon('arrowUp', 'ic-xs')} +12% activity</span></div>
        </div>
        <div class="card-b">
          <div class="grid g-4 mb-5">
            ${statBlock('Study Time', '2h 40m', '+22m', 'clock', 'up')}
            ${statBlock('Questions Solved', '126', '+18', 'target', 'up')}
            ${statBlock('Avg. Accuracy', '84%', '+6%', 'chart', 'up')}
            ${statBlock('Learning Streak', '7 days', '+2', 'flame', 'up')}
          </div>
          <div class="grid g-2">
            <div>
              <div class="tiny mb-2" style="font-weight:600;color:var(--text-2);text-transform:uppercase;letter-spacing:.04em">Study time · daily</div>
              ${barChart([35, 52, 48, 68, 45, 72, 55], ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'], 400, 130, '#243B6B')}
            </div>
            <div>
              <div class="tiny mb-2" style="font-weight:600;color:var(--text-2);text-transform:uppercase;letter-spacing:.04em">Accuracy trend</div>
              ${sparkline([62, 68, 71, 74, 78, 82, 84], 400, 130, '#2E9B68')}
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
          ${CLASS_WEAK_TOPICS.slice(0, 3).map(t => `
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
            ${riskBadge(s.risk)}
          </div>
          <div class="subj-metrics">
            <div class="m"><div class="l">Mastery</div><div class="v">${s.mastery}%</div>${progressBar(s.mastery, s.mastery >= 80 ? 'green' : s.mastery >= 60 ? 'indigo' : 'amber')}</div>
            <div class="m"><div class="l">Knowledge Health</div><div class="v" style="color:${s.kh >= 70 ? 'var(--green)' : s.kh >= 55 ? 'var(--amber)' : 'var(--coral)'}">${s.kh}%</div>${progressBar(s.kh, s.kh >= 70 ? 'green' : s.kh >= 55 ? 'amber' : 'coral')}</div>
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
        <div class="ai-body">You're most productive in the <b>4–7 PM</b> window. I've scheduled your revision for today at 5:00 PM.</div>
        <div class="ai-actions"><button class="btn btn-sm btn-teal" onclick="navigate('student/revision')">Open plan</button></div>
      </div>

      <div class="card">
        <div class="card-h" style="padding-bottom:12px"><h3 style="font-size:13.5px">Quick Actions</h3></div>
        <div class="card-b" style="padding-top:0;display:flex;flex-direction:column;gap:8px">
          <button class="qa-tile" onclick="navigate('student/assessments')">
            <div class="qi">${icon('clipboard')}</div>
            <div><b>Start MCQ practice</b><span>Pick a topic and begin</span></div>
          </button>
          <button class="qa-tile" onclick="navigate('student/revision')">
            <div class="qi" style="background:var(--amber-50);color:#B4731A">${icon('refresh')}</div>
            <div><b>Review today's queue</b><span>4 topics awaiting</span></div>
          </button>
          <button class="qa-tile" onclick="navigate('student/materials')">
            <div class="qi" style="background:var(--teal-50);color:var(--teal-600)">${icon('folder')}</div>
            <div><b>Study materials</b><span>Notes, videos, PDFs</span></div>
          </button>
        </div>
      </div>

      <div class="card">
        <div class="card-h" style="padding-bottom:12px"><h3 style="font-size:13.5px">Next Test</h3></div>
        <div class="card-b" style="padding-top:0">
          <div class="flex-b mb-2">
            <span class="badge coral">${UPCOMING_ASSESSMENTS[0].daysLeft} days left</span>
            <span class="tiny">${UPCOMING_ASSESSMENTS[0].date}</span>
          </div>
          <div style="font-size:14px;font-weight:700;margin-bottom:2px">${UPCOMING_ASSESSMENTS[0].topic}</div>
          <div class="small mb-3">${UPCOMING_ASSESSMENTS[0].subject} · ${UPCOMING_ASSESSMENTS[0].duration}</div>
          <div class="flex gap-2 mb-3" style="font-size:11.5px;color:var(--text-3)">
            <span>Preparation</span>
            <div class="prog thin" style="flex:1"><i class="fill-amber" style="width:${UPCOMING_ASSESSMENTS[0].prep}%"></i></div>
            <b style="color:var(--text)">${UPCOMING_ASSESSMENTS[0].prep}%</b>
          </div>
          <button class="btn btn-primary btn-sm" style="width:100%" onclick="navigate('student/revision')">Revise for this test</button>
        </div>
      </div>

      <div class="card">
        <div class="card-h" style="padding-bottom:12px"><h3 style="font-size:13.5px">Study Consistency</h3></div>
        <div class="card-b" style="padding-top:0">
          <div class="tiny mb-2">Last 20 weeks · darker = more activity</div>
          ${heatmap(20)}
          <div class="flex-b mt-3 tiny">
            <span>Less</span>
            <div class="flex gap-2">
              <span class="hm-c" style="width:10px;height:10px"></span>
              <span class="hm-c l1" style="width:10px;height:10px"></span>
              <span class="hm-c l2" style="width:10px;height:10px"></span>
              <span class="hm-c l3" style="width:10px;height:10px"></span>
              <span class="hm-c l4" style="width:10px;height:10px"></span>
            </div>
            <span>More</span>
          </div>
        </div>
      </div>
    </div>
  </aside>`;
}

/* ---------- My Learning ---------- */
export function studentLearning(): string {
  if (UI.subjectId) return subjectDetailPage();
  return `
  <div class="page">
    ${pageHead('My Learning', 'Continue your learning journey', 'Everything you are studying right now — continue, review or explore new topics.', `<button class="btn btn-primary" onclick="navigate('student/assessments')">${icon('play')} Take a practice check</button>`)}

    <!-- Continue learning -->
    <div class="sec-head"><div><h2>${icon('play')} Continue Learning</h2><p>Pick up where you left off</p></div></div>
    <div class="grid g-3 mb-6">
      ${[
        { subject: 'Mathematics', topic: 'Trigonometry — Lesson 5', pct: 62, time: '25 min remaining', color: '#243B6B', bg: '#E8EDF7', icon: 'MTH' },
        { subject: 'Physics', topic: 'Electricity & Circuits — Lesson 3', pct: 34, time: '38 min remaining', color: '#18A6A6', bg: '#E3F5F5', icon: 'PHY' },
        { subject: 'Chemistry', topic: 'Chemical Reactions — Practice', pct: 78, time: '12 min remaining', color: '#2E9B68', bg: '#E7F5EE', icon: 'CHM' }
      ].map(c => `
        <div class="card hoverable pad" style="cursor:pointer" onclick="openSubject('${c.subject === 'Mathematics' ? 'math' : c.subject === 'Physics' ? 'phy' : 'chem'}')">
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
            <span class="btn btn-sm btn-primary">Continue ${icon('arrowR', 'ic-xs')}</span>
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
          </div>
          <div class="subj-metrics">
            <div class="m"><div class="l">Mastery</div><div class="v">${s.mastery}%</div>${progressBar(s.mastery, s.mastery >= 80 ? 'green' : 'indigo')}</div>
            <div class="m"><div class="l">Knowledge Health</div><div class="v" style="color:${s.kh >= 70 ? 'var(--green)' : s.kh >= 55 ? 'var(--amber)' : 'var(--coral)'}">${s.kh}%</div>${progressBar(s.kh, s.kh >= 70 ? 'green' : s.kh >= 55 ? 'amber' : 'coral')}</div>
          </div>
        </div>`).join('')}
    </div>

    <!-- Recommended + Recent Activity -->
    <div class="grid g-2-1">
      <div class="card">
        <div class="card-h"><div><h3>Recommended for you</h3><div class="sub">Based on weak areas and forgetting signals</div></div></div>
        <div class="card-b">
          <div class="flex-c">
            ${aiInsight('Focus on Physics — Electricity', `Accuracy has dropped 24% over the last 5 sessions. A 20-minute revision now will help stabilise your knowledge health (currently 42%).`, 'Start revision', `navigate('student/revision')`)}
            ${aiInsight('Reinforce Organic Chemistry basics', `This topic has been at 35% knowledge health for 11 days. Revisit the core concepts before they fully decay.`, 'Open topic', `openSubject('chem')`)}
          </div>
        </div>
      </div>
      <div class="card">
        <div class="card-h"><h3>Recent activity</h3></div>
        <div class="card-b" style="padding-top:8px">
          <div class="notice"><span class="n-dot teal"></span><div class="n-body"><b>Completed Trigonometry practice</b><p>18 / 20 correct · 92% accuracy</p><div class="n-time">${icon('clock', 'ic-xs')} 2 hours ago</div></div></div>
          <div class="notice"><span class="n-dot"></span><div class="n-body"><b>Read "Electricity — Chapter 4"</b><p>25 minutes · completed</p><div class="n-time">${icon('clock', 'ic-xs')} Yesterday</div></div></div>
          <div class="notice"><span class="n-dot"></span><div class="n-body"><b>Submitted Chemistry assignment</b><p>Balancing equations — 15 questions</p><div class="n-time">${icon('clock', 'ic-xs')} 2 days ago</div></div></div>
          <div class="notice"><span class="n-dot"></span><div class="n-body"><b>Retook Light — MCQ check</b><p>Score: 58% · improved by 6%</p><div class="n-time">${icon('clock', 'ic-xs')} 3 days ago</div></div></div>
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
          ${statBlock('Mastery', s.mastery + '%', '+4% this month', 'award', 'up')}
          ${statBlock('Knowledge Health', s.kh + '%', s.kh >= 70 ? 'Stable' : 'Declining', 'brain', s.kh >= 70 ? 'up' : 'down')}
          ${statBlock('Topics', s.done + ' / ' + s.topics, s.topics - s.done + ' remaining', 'book2')}
          ${statBlock('Practice', '124 Q', '86% avg accuracy', 'target', 'up')}
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
            ${riskBadge(s.risk)}
          </div>
          <div class="grid g-2 mb-4">
            <div><div class="tiny mb-2">Mastery</div><div style="font-size:18px;font-weight:800;font-family:Manrope">${s.mastery}%</div></div>
            <div><div class="tiny mb-2">Knowledge Health</div><div style="font-size:18px;font-weight:800;font-family:Manrope;color:${s.kh >= 70 ? 'var(--green)' : s.kh >= 55 ? 'var(--amber)' : 'var(--coral)'}">${s.kh}%</div></div>
          </div>
          ${progressBar(s.mastery, 'indigo')}
          <div class="flex-b mt-3"><span class="tiny">Updated 2h ago</span><span class="btn btn-sm">Open ${icon('arrowR', 'ic-xs')}</span></div>
        </div>`).join('')}
    </div>
  </div>`;
}

/* ---------- Revision Plan ---------- */
export function studentRevision(): string {
  const dueToday = REVISION_QUEUE.filter(r => r.when === 'Today');
  const dueWeek = REVISION_QUEUE.filter(r => r.when !== 'Today' && r.risk === 'High');
  const upcoming = REVISION_QUEUE.filter(r => r.when !== 'Today' && r.risk !== 'High');
  return `
  <div class="page">
    ${pageHead('Revision Plan', 'Your personalised revision plan', 'EduSense AI schedules revision at the moment it will have the greatest impact — based on your knowledge health, accuracy and last revision date.')}

    <div class="grid g-4 mb-6">
      ${statBlock('Due today', dueToday.length, 'High priority', 'alert', 'down')}
      ${statBlock('This week', dueWeek.length, 'Scheduled for you', 'calendar')}
      ${statBlock('Completed', '9', 'Last 30 days', 'check', 'up')}
      ${statBlock('Revision accuracy', '+12%', 'On revised topics', 'trendUp', 'up')}
    </div>

    ${aiInsight('This week\'s priority',
      `Your <b>Physics knowledge has become less stable</b> over the last 5 practice sessions. Focus on <b>Electricity & Circuits</b> first — accuracy has dropped 24% and the last revision was 9 days ago.`,
      'Start with Physics', `startQuiz('Electricity')`)}

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

    <!-- Completed -->
    <div class="sec-head"><div><h2>${icon('check')} Recently Completed</h2><p>Last 7 days</p></div></div>
    <div class="card">
      <div class="card-b">
        ${[
          { s: 'Mathematics', t: 'Quadratic Equations', d: '3 days ago', r: '+4% KH' },
          { s: 'Chemistry', t: 'Acids, Bases & Salts', d: '2 days ago', r: '+6% KH' },
          { s: 'English', t: 'Reading Comprehension', d: '2 days ago', r: '+2% KH' },
          { s: 'Biology', t: 'Photosynthesis', d: '1 day ago', r: '+3% KH' },
        ].map(c => `
          <div class="flex-b" style="padding:12px 0;border-bottom:1px solid var(--border-2)">
            <div class="flex gap-3">
              <div class="ri" style="background:var(--green-50);color:var(--green);width:30px;height:30px;border-radius:8px;display:grid;place-items:center">${icon('check', 'ic-sm')}</div>
              <div><div style="font-size:13px;font-weight:600">${c.s} — ${c.t}</div><div class="tiny">Completed ${c.d}</div></div>
            </div>
            <span class="badge green">${c.r}</span>
          </div>`).join('')}
      </div>
    </div>
  </div>`;
}

/* ---------- Knowledge Health ---------- */
export function studentKnowledge(): string {
  return `
  <div class="page">
    ${pageHead('Knowledge Health', 'How stable is your learning?', 'A model-derived estimate combining your accuracy, response time, revision history and time since last practice.')}

    <div class="card mb-6">
      <div class="card-b" style="padding:24px">
        <div class="flex gap-5 wrap" style="align-items:center">
          <div style="text-align:center">${donut(73, 160, 14, '#243B6B')}<div class="small mt-2">Overall Knowledge Health</div></div>
          <div style="flex:1;min-width:280px">
            <div class="h3 mb-3">Across 6 subjects and 42 active topics</div>
            <div class="kh-bar mb-3" style="height:14px">
              <div class="kh-seg" style="width:38%;background:var(--green)"></div>
              <div class="kh-seg" style="width:24%;background:var(--teal)"></div>
              <div class="kh-seg" style="width:22%;background:var(--amber)"></div>
              <div class="kh-seg" style="width:16%;background:var(--coral)"></div>
            </div>
            <div class="kh-legend">
              <span class="item"><span class="sw" style="background:var(--green)"></span>Strong <b>38%</b></span>
              <span class="item"><span class="sw" style="background:var(--teal)"></span>Stable <b>24%</b></span>
              <span class="item"><span class="sw" style="background:var(--amber)"></span>Needs revision <b>22%</b></span>
              <span class="item"><span class="sw" style="background:var(--coral)"></span>At risk <b>16%</b></span>
            </div>
            <p class="tiny mt-4">${icon('bulb', 'ic-xs')} Knowledge Health is an estimate, not a fixed truth. It changes as you practice and revise.</p>
          </div>
        </div>
      </div>
    </div>

    ${aiInsight('EduSense Insight',
      `You have <b>2 high-priority forgetting risks</b> this week. If you revise <b>Electricity & Circuits</b> today, your knowledge health could recover to an estimated <b>62–68%</b> by Friday.`,
      'Schedule revision', `navigate('student/revision')`)}

    <div class="sec-head mt-6"><div><h2>${icon('grid')} By Subject</h2><p>Knowledge health and trend across your subjects</p></div></div>
    <div class="grid g-2 mb-6">
      ${SUBJECTS.map(s => `
        <div class="card pad">
          <div class="flex-b mb-3">
            <div class="flex gap-3">
              <div class="subj-ic" style="background:${s.bg};color:${s.color};width:40px;height:40px;font-size:12px">${s.code}</div>
              <div><div class="h4">${s.name}</div><div class="tiny">${s.topics} topics · ${s.done} complete</div></div>
            </div>
            <div style="font-size:24px;font-weight:800;font-family:Manrope;color:${s.kh >= 70 ? 'var(--green)' : s.kh >= 55 ? 'var(--amber)' : 'var(--coral)'}">${s.kh}%</div>
          </div>
          ${progressBar(s.kh, s.kh >= 70 ? 'green' : s.kh >= 55 ? 'amber' : 'coral')}
          <div class="flex-b mt-3">
            <span class="tiny">Mastery ${s.mastery}%</span>
            ${riskBadge(s.risk)}
          </div>
        </div>`).join('')}
    </div>

    <div class="sec-head"><div><h2>${icon('brain')} Topic-level breakdown</h2><p>Subjects ranked by knowledge health</p></div></div>
    <div class="grid g-3">
      <div class="card">
        <div class="card-h" style="padding-bottom:12px"><h3 style="font-size:14px"><span style="display:inline-block;width:8px;height:8px;border-radius:50%;background:var(--green);margin-right:7px"></span>Strong</h3></div>
        <div class="card-b" style="padding-top:0">
          <ul style="list-style:none">
            ${[['Algebra', '91%'], ['Statistics', '87%'], ['Photosynthesis', '90%'], ['Motion & Force', '78%'], ['Chemical Reactions', '80%']].map(([n, v]) => `
              <li class="flex-b" style="padding:9px 0;border-bottom:1px solid var(--border-2);font-size:13px"><b>${n}</b><span style="color:var(--green);font-weight:700">${v}</span></li>`).join('')}
          </ul>
        </div>
      </div>
      <div class="card">
        <div class="card-h" style="padding-bottom:12px"><h3 style="font-size:14px"><span style="display:inline-block;width:8px;height:8px;border-radius:50%;background:var(--amber);margin-right:7px"></span>Needs Attention</h3></div>
        <div class="card-b" style="padding-top:0">
          <ul style="list-style:none">
            ${[['Electricity', '42%'], ['Probability', '44%'], ['Coordinate Geometry', '58%'], ['Light & Refraction', '58%'], ['Nationalism in India', '58%']].map(([n, v]) => `
              <li class="flex-b" style="padding:9px 0;border-bottom:1px solid var(--border-2);font-size:13px"><b>${n}</b><span style="color:var(--amber);font-weight:700">${v}</span></li>`).join('')}
          </ul>
        </div>
      </div>
      <div class="card">
        <div class="card-h" style="padding-bottom:12px"><h3 style="font-size:14px"><span style="display:inline-block;width:8px;height:8px;border-radius:50%;background:var(--coral);margin-right:7px"></span>At Risk</h3></div>
        <div class="card-b" style="padding-top:0">
          <ul style="list-style:none">
            ${[['Organic Chemistry', '35%'], ['Work & Energy', '48%']].map(([n, v]) => `
              <li class="flex-b" style="padding:9px 0;border-bottom:1px solid var(--border-2);font-size:13px"><b>${n}</b><span style="color:var(--coral);font-weight:700">${v}</span></li>`).join('')}
          </ul>
        </div>
      </div>
    </div>
  </div>`;
}

/* ---------- Skill Mastery ---------- */
export function studentSkills(): string {
  const skills = [
    { name: 'Algebraic reasoning', level: 88, cat: 'Mathematics', trend: +4 },
    { name: 'Geometric problem solving', level: 64, cat: 'Mathematics', trend: -3 },
    { name: 'Circuit analysis', level: 48, cat: 'Physics', trend: -9 },
    { name: 'Optical reasoning', level: 58, cat: 'Physics', trend: -5 },
    { name: 'Chemical equation balancing', level: 84, cat: 'Chemistry', trend: +2 },
    { name: 'Organic structure recognition', level: 38, cat: 'Chemistry', trend: -6 },
    { name: 'Biological process understanding', level: 92, cat: 'Biology', trend: +3 },
    { name: 'Reading & interpretation', level: 88, cat: 'English', trend: +2 },
    { name: 'Grammar application', level: 74, cat: 'English', trend: +1 },
    { name: 'Historical analysis', level: 62, cat: 'Social Studies', trend: -2 },
  ];
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
      <div class="card-h"><h3>All skills</h3><div class="right"><span class="badge grey">${skills.length} skills</span></div></div>
      <div class="card-b">
        ${skills.map(s => `
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
  return `
  <div class="page">
    ${pageHead('Learning Analytics', 'How you are learning', 'Weekly and long-term patterns across study time, accuracy, revision effectiveness and consistency.', '<button class="btn" onclick="toast(\'Analytics exported\',\'PDF ready\',\'good\')">' + icon('download') + ' Export</button>')}

    <div class="grid g-4 mb-6">
      ${statBlock('Study time', '2h 40m', '+22m vs last week', 'clock', 'up')}
      ${statBlock('Questions solved', '126', '+18 this week', 'target', 'up')}
      ${statBlock('Avg. accuracy', '84%', '+6% this week', 'chart', 'up')}
      ${statBlock('Consistency', '86%', '+4% this month', 'flame', 'up')}
    </div>

    <div class="grid g-2 mb-6">
      <div class="card">
        <div class="card-h"><h3>Weekly activity</h3><div class="right"><span class="badge grey">Last 7 days</span></div></div>
        <div class="card-b">${barChart([35, 52, 48, 68, 45, 72, 55], ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'], 600, 180, '#243B6B')}</div>
      </div>
      <div class="card">
        <div class="card-h"><h3>Accuracy trend</h3><div class="right"><span class="badge green">${icon('arrowUp', 'ic-xs')} Improving</span></div></div>
        <div class="card-b">${sparkline([62, 68, 71, 74, 72, 78, 82, 84], 600, 180, '#2E9B68')}</div>
      </div>
    </div>

    <div class="grid g-3 mb-6">
      <div class="card pad">
        <div class="h4 mb-3">Revision effectiveness</div>
        <div class="tiny mb-3">Knowledge health improvement after each revision session</div>
        ${sparkline([4, 6, 5, 8, 7, 11, 9, 12], 400, 120, '#18A6A6')}
        <div class="flex-b mt-3"><span class="tiny">Avg. +8.4% per session</span><span class="badge teal">Strong</span></div>
      </div>
      <div class="card pad">
        <div class="h4 mb-3">Study session frequency</div>
        <div class="tiny mb-3">Sessions per day this week</div>
        ${barChart([2, 3, 2, 4, 3, 5, 3], ['M', 'T', 'W', 'T', 'F', 'S', 'S'], 400, 120, '#7C5CD6')}
        <div class="flex-b mt-3"><span class="tiny">3.1 avg/day</span><span class="badge violet">Above target</span></div>
      </div>
      <div class="card pad">
        <div class="h4 mb-3">Time distribution</div>
        <div class="tiny mb-3">Where your study time goes</div>
        ${[
          ['Practice questions', 42, 'indigo'],
          ['Revision', 28, 'amber'],
          ['Reading materials', 18, 'teal'],
          ['Assessments', 12, 'violet'],
        ].map(([n, v, c]) => `
          <div class="flex gap-3 mb-3" style="font-size:12.5px">
            <span style="flex:0 0 130px">${n}</span>
            ${progressBar(v as number, c as string)}
            <b style="width:36px;text-align:right">${v}%</b>
          </div>`).join('')}
      </div>
    </div>

    <div class="card">
      <div class="card-h"><h3>Learning consistency — last 20 weeks</h3><div class="right"><span class="badge green">${icon('flame', 'ic-xs')} 7-day streak</span></div></div>
      <div class="card-b">${heatmap(20)}</div>
    </div>
  </div>`;
}

/* ---------- Weak Areas ---------- */
export function studentWeak(): string {
  return `
  <div class="page">
    ${pageHead('Weak Areas', 'Topics that need your attention', 'Ranked by knowledge health, forgetting risk and recent accuracy.')}

    ${aiInsight('Priority focus this week', 'Your <b>Physics knowledge is declining fastest</b> — 2 of your top 3 weak topics are from Physics. Set aside <b>40 minutes today</b> to reverse the trend.', 'Open revision plan', `navigate('student/revision')`)}

    <div class="card mt-5">
      <div class="card-h"><h3>Ranked by urgency</h3></div>
      <table class="tbl">
        <thead><tr><th>Topic</th><th>Subject</th><th>Knowledge Health</th><th>Risk</th><th>Last revised</th><th></th></tr></thead>
        <tbody>
          ${[
            ['Organic Chemistry', 'Chemistry', 35, 'high', '11 days ago'],
            ['Electricity & Circuits', 'Physics', 42, 'high', '9 days ago'],
            ['Probability', 'Mathematics', 44, 'high', '9 days ago'],
            ['Work, Energy & Power', 'Physics', 48, 'high', '6 days ago'],
            ['Light — Reflection', 'Physics', 58, 'medium', '12 days ago'],
            ['Coordinate Geometry', 'Mathematics', 58, 'medium', '16 days ago'],
            ['Nationalism in India', 'Social Studies', 58, 'medium', '17 days ago'],
            ['Grammar — Tenses', 'English', 72, 'medium', '4 days ago'],
          ].map(([t, s, kh, r, last]) => `
            <tr>
              <td class="nm">${t}</td>
              <td class="muted">${s}</td>
              <td><div class="flex gap-2" style="width:130px">${progressBar(kh as number, (kh as number) >= 70 ? 'green' : (kh as number) >= 55 ? 'amber' : 'coral')}<b style="font-size:12px">${kh}%</b></div></td>
              <td>${riskBadge(r as string)}</td>
              <td class="muted">${last}</td>
              <td class="right"><button class="btn btn-sm btn-primary" onclick="startQuiz('${t}')">Review</button></td>
            </tr>`).join('')}
        </tbody>
      </table>
    </div>
  </div>`;
}

/* ---------- Calendar ---------- */
export function studentCalendar(): string {
  const c = UI.calCursor, y = c.getFullYear(), m = c.getMonth();
  const first = new Date(y, m, 1).getDay();
  const days = new Date(y, m + 1, 0).getDate();
  const prev = new Date(y, m, 0).getDate();
  const today = new Date();
  const monthName = c.toLocaleString('en-US', { month: 'long', year: 'numeric' });
  let cells = '';
  for (let i = first - 1; i >= 0; i--) cells += `<div class="cal-day out"><div class="d">${prev - i}</div></div>`;
  for (let d = 1; d <= days; d++) {
    const date = new Date(y, m, d);
    const isToday = date.toDateString() === today.toDateString();
    const evs = CAL_EVENTS[calKey(date)] || [];
    cells += `<div class="cal-day ${isToday ? 'today' : ''}" style="background:var(--surface);border:1px solid ${isToday ? 'var(--indigo)' : 'var(--border)'};border-radius:var(--r);padding:8px;min-height:100px;display:flex;flex-direction:column;gap:4px;transition:.15s">
      <div style="font-size:12px;font-weight:700;color:${isToday ? 'var(--indigo)' : 'var(--text)'}">${d}</div>
      ${evs.slice(0, 3).map(e => {
        const clr = { revision: 'amber', exam: 'coral', class: 'indigo', done: 'green', holiday: 'violet', ai: 'teal' }[e.t] || 'grey';
        return `<div style="font-size:10px;padding:2px 6px;border-radius:5px;background:var(--${clr}-50);color:var(--${clr}-600);font-weight:600;overflow:hidden;text-overflow:ellipsis;white-space:nowrap">${e.title}</div>`;
      }).join('')}
    </div>`;
  }
  const tail = (7 - ((first + days) % 7)) % 7;
  for (let i = 1; i <= tail; i++) cells += `<div class="cal-day out"><div class="d">${i}</div></div>`;

  return `
  <div class="page">
    ${pageHead('Calendar', monthName, 'All your classes, revisions, exams and school events in one place.',
      `<div class="flex gap-2">
        <button class="btn btn-sm" onclick="setCalView('month')" style="${UI.calView === 'month' ? 'background:var(--indigo);color:#fff;border-color:var(--indigo)' : ''}">Month</button>
        <button class="btn btn-sm" onclick="setCalView('week')" style="${UI.calView === 'week' ? 'background:var(--indigo);color:#fff;border-color:var(--indigo)' : ''}">Week</button>
        <button class="btn btn-sm" onclick="setCalView('day')" style="${UI.calView === 'day' ? 'background:var(--indigo);color:#fff;border-color:var(--indigo)' : ''}">Day</button>
      </div>`)}

    <div class="grid g-3-1">
      <div class="card">
        <div class="card-h">
          <button class="btn btn-sm btn-icon" onclick="calMove(-1)">${icon('chevL')}</button>
          <h3 style="min-width:180px;text-align:center">${monthName}</h3>
          <button class="btn btn-sm btn-icon" onclick="calMove(1)">${icon('chevR')}</button>
          <div class="right"><button class="btn btn-sm" onclick="calToday()">Today</button></div>
        </div>
        <div class="card-b">
          <div style="display:grid;grid-template-columns:repeat(7,1fr);gap:6px;margin-bottom:6px">
            ${['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'].map(d => `<div class="tiny" style="text-align:center;font-weight:700;padding:6px 0">${d}</div>`).join('')}
          </div>
          <div style="display:grid;grid-template-columns:repeat(7,1fr);gap:6px">${cells}</div>
        </div>
        <div class="card-f">
          <div class="flex wrap gap-4 tiny">
            <span class="flex gap-2"><span style="width:9px;height:9px;border-radius:3px;background:var(--indigo-50);border:1px solid var(--indigo-500)"></span>Class</span>
            <span class="flex gap-2"><span style="width:9px;height:9px;border-radius:3px;background:var(--amber-50);border:1px solid var(--amber)"></span>Revision</span>
            <span class="flex gap-2"><span style="width:9px;height:9px;border-radius:3px;background:var(--coral-50);border:1px solid var(--coral)"></span>Exam</span>
            <span class="flex gap-2"><span style="width:9px;height:9px;border-radius:3px;background:var(--teal-50);border:1px solid var(--teal)"></span>AI recommended</span>
            <span class="flex gap-2"><span style="width:9px;height:9px;border-radius:3px;background:var(--green-50);border:1px solid var(--green)"></span>Completed</span>
            <span class="flex gap-2"><span style="width:9px;height:9px;border-radius:3px;background:var(--violet-50);border:1px solid var(--violet)"></span>Holiday</span>
          </div>
        </div>
      </div>

      <div class="flex-c">
        <div class="card">
          <div class="card-h" style="padding-bottom:12px"><h3 style="font-size:13.5px">Today · Sep 15</h3></div>
          <div class="card-b" style="padding-top:0">
            ${[
              { t: '08:00', n: 'Mathematics — Quadratic Equations', c: 'indigo' },
              { t: '10:30', n: 'Physics — Electricity', c: 'teal' },
              { t: '13:30', n: 'Social Studies — Resources', c: 'coral' },
              { t: '17:00', n: 'EduSense AI — Physics revision', c: 'amber', ai: true },
            ].map(e => `
              <div class="flex gap-3" style="padding:11px 0;border-bottom:1px solid var(--border-2)">
                <div class="tiny mono" style="width:44px;color:var(--text-3);padding-top:2px">${e.t}</div>
                <div style="flex:1;min-width:0;border-left:3px solid var(--${e.c});padding-left:10px">
                  <div style="font-size:12.5px;font-weight:600">${e.n}</div>
                  ${e.ai ? `<div class="tiny" style="color:var(--teal-600);margin-top:2px;display:flex;gap:4px;align-items:center">${icon('sparkles', 'ic-xs')} AI recommended</div>` : ''}
                </div>
              </div>`).join('')}
          </div>
        </div>

        <div class="card">
          <div class="card-h" style="padding-bottom:12px"><h3 style="font-size:13.5px">Upcoming · This week</h3></div>
          <div class="card-b" style="padding-top:0">
            ${[
              { d: 'Sep 18', n: 'Physics assessment', c: 'coral' },
              { d: 'Sep 19', n: 'English revision due', c: 'amber' },
              { d: 'Sep 21', n: 'Mathematics assessment', c: 'coral' },
              { d: 'Sep 25', n: 'Chemistry assessment', c: 'coral' },
            ].map(e => `
              <div class="flex-b" style="padding:9px 0;border-bottom:1px solid var(--border-2)">
                <div class="flex gap-3"><span class="tiny mono" style="color:var(--text-3);width:52px">${e.d}</span><span style="font-size:12.5px;font-weight:600">${e.n}</span></div>
                <span style="width:8px;height:8px;border-radius:50%;background:var(--${e.c})"></span>
              </div>`).join('')}
          </div>
        </div>
      </div>
    </div>
  </div>`;
}

export function calMove(n: number): void {
  UI.calCursor = new Date(UI.calCursor.getFullYear(), UI.calCursor.getMonth() + n, 1);
  window.navigate('student/calendar');
}

export function calToday(): void {
  UI.calCursor = new Date();
  window.navigate('student/calendar');
}

export function setCalView(v: 'month' | 'week' | 'day'): void {
  UI.calView = v;
  window.navigate('student/calendar');
}

/* ---------- Assessments ---------- */
export function studentAssessments(): string {
  return `
  <div class="page">
    ${pageHead('Assessments', 'Your assessments', 'Scheduled tests, completed attempts and detailed performance breakdowns.',
      `<button class="btn btn-primary" onclick="startQuiz('Mixed practice')">${icon('play')} Quick practice</button>`)}

    <div class="grid g-4 mb-6">
      ${statBlock('Upcoming', UPCOMING_ASSESSMENTS.length, 'Next in 3 days', 'calendar')}
      ${statBlock('Completed', COMPLETED_ASSESSMENTS.length, 'This month', 'check', 'up')}
      ${statBlock('Avg. score', '71%', '+6% vs last month', 'chart', 'up')}
      ${statBlock('Best subject', 'Biology', '88% avg accuracy', 'award', 'up')}
    </div>

    <div class="sec-head"><div><h2>${icon('calendar')} Upcoming Tests</h2><p>Scheduled by your teacher</p></div></div>
    <div class="grid g-3 mb-6">
      ${UPCOMING_ASSESSMENTS.map(a => `
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
            <span>Preparation</span><b style="color:var(--text)">${a.prep}%</b>
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
          ${[
            { n: 'Forgetting Curves & Revision Planning', s: 'Study Skills', t: 'PDF', m: '2.4 MB', c: 'indigo' },
            { n: 'Quadratic Equations — Complete Notes', s: 'Mathematics', t: 'PDF', m: '1.8 MB', c: 'indigo' },
            { n: 'Electricity — Video Lecture 1', s: 'Physics', t: 'Video', m: '48 min', c: 'teal' },
            { n: 'Chemical Reactions — Practice Set', s: 'Chemistry', t: 'Practice', m: '30 Q', c: 'green' },
            { n: 'Life Processes — Presentation', s: 'Biology', t: 'Presentation', m: '8.2 MB', c: 'amber' },
            { n: 'Trigonometry Quick Revision Sheet', s: 'Mathematics', t: 'PDF', m: '680 KB', c: 'indigo' },
            { n: 'Light & Refraction — Notes', s: 'Physics', t: 'Notes', m: '1.2 MB', c: 'teal' },
            { n: 'Grammar — Tenses Worksheet', s: 'English', t: 'PDF', m: '420 KB', c: 'violet' },
            { n: 'Nationalism in India — Summary', s: 'Social Studies', t: 'Notes', m: '780 KB', c: 'coral' },
          ].map(m => `
            <div class="card hoverable pad" style="cursor:pointer">
              <div class="flex gap-3 mb-4">
                <div class="qa-tile" style="padding:0;border:0;background:var(--${m.c}-50);width:42px;height:42px;justify-content:center;border-radius:11px">
                  <span style="color:var(--${m.c});display:grid;place-items:center">${icon(m.t === 'Video' ? 'video' : m.t === 'Presentation' ? 'layers' : m.t === 'Practice' ? 'target' : 'file')}</span>
                </div>
                <div style="flex:1;min-width:0">
                  <div class="h4" style="font-size:13.5px;line-height:1.35">${m.n}</div>
                  <div class="tiny mt-1">${m.s}</div>
                </div>
              </div>
              <div class="flex-b">
                <span class="badge ${m.c}">${m.t}</span>
                <span class="tiny">${m.m}</span>
              </div>
            </div>`).join('')}
        </div>
      </div>

      <div class="flex-c">
        <div class="ai-card">
          <div class="ai-head"><div class="ai-mark">${icon('sparkles')}</div><b>Recommended for you</b></div>
          <div class="ai-body">Since you're revising <b>Electricity</b>, these resources will help:</div>
          <div class="flex-c mt-3" style="gap:8px">
            <button class="qa-tile" style="padding:10px">
              <div class="qi" style="background:var(--teal-50);color:var(--teal-600);width:28px;height:28px">${icon('video')}</div>
              <div><b style="font-size:12px">Video Lecture 1</b><span style="font-size:11px">48 min</span></div>
            </button>
            <button class="qa-tile" style="padding:10px">
              <div class="qi" style="background:var(--indigo-50);color:var(--indigo);width:28px;height:28px">${icon('file')}</div>
              <div><b style="font-size:12px">Chapter notes</b><span style="font-size:11px">1.8 MB PDF</span></div>
            </button>
          </div>
        </div>

        <div class="card">
          <div class="card-h" style="padding-bottom:12px"><h3 style="font-size:13.5px">Recently opened</h3></div>
          <div class="card-b" style="padding-top:0">
            ${['Quadratic Equations Notes', 'Electricity Video', 'Chemical Reactions Set'].map(n => `
              <div class="flex gap-3" style="padding:10px 0;border-bottom:1px solid var(--border-2);font-size:12.5px">
                ${icon('clock', 'ic-xs')}<span>${n}</span>
              </div>`).join('')}
          </div>
        </div>
      </div>
    </div>
  </div>`;
}

/* ---------- Notes ---------- */
export function studentNotes(): string {
  const notes = [
    { title: 'Quadratic Equations — key formulas', subject: 'Mathematics', updated: '3 days ago', words: 420 },
    { title: 'Electricity — circuit analysis steps', subject: 'Physics', updated: '5 days ago', words: 680 },
    { title: 'Chemical Reactions — balancing rules', subject: 'Chemistry', updated: '1 week ago', words: 340 },
    { title: 'Photosynthesis — diagram notes', subject: 'Biology', updated: '2 days ago', words: 520 },
    { title: 'Grammar — Tenses cheat sheet', subject: 'English', updated: '1 week ago', words: 280 },
    { title: 'Nationalism in India — timeline', subject: 'Social Studies', updated: '2 weeks ago', words: 610 },
  ];
  return `
  <div class="page">
    ${pageHead('Notes', 'Your personal notes', 'Everything you have written or saved while studying.', '<button class="btn btn-primary">' + icon('plus') + ' New note</button>')}
    <div class="grid g-3">
      ${notes.map(n => `
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
  const items = [
    { title: 'Balancing chemical equations', subject: 'Chemistry', due: 'Sep 17, 2026', status: 'pending', progress: 0 },
    { title: 'Physics numericals — Electricity', subject: 'Physics', due: 'Sep 19, 2026', status: 'pending', progress: 45 },
    { title: 'Essay: Nationalism in India', subject: 'Social Studies', due: 'Sep 22, 2026', status: 'in-progress', progress: 20 },
    { title: 'Trigonometry worksheet', subject: 'Mathematics', due: 'Sep 12, 2026', status: 'submitted', progress: 100 },
    { title: 'Grammar worksheet — Tenses', subject: 'English', due: 'Sep 08, 2026', status: 'graded', progress: 100, score: 88 },
  ];
  return `
  <div class="page">
    ${pageHead('Assignments', 'Your assignments', 'Track pending work, in-progress tasks and graded submissions.')}
    <div class="grid g-4 mb-6">
      ${statBlock('Pending', items.filter(i => i.status === 'pending').length, 'Due this week', 'alert', 'down')}
      ${statBlock('In progress', items.filter(i => i.status === 'in-progress').length, 'Submitted soon', 'edit')}
      ${statBlock('Submitted', items.filter(i => i.status === 'submitted' || i.status === 'graded').length, 'This month', 'check', 'up')}
      ${statBlock('Avg. score', '86%', 'On graded work', 'award', 'up')}
    </div>
    <div class="card">
      <div class="card-h"><h3>All assignments</h3></div>
      <div class="card-b">
        ${items.map(i => `
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
  return `
  <div class="page">
    ${pageHead('Exams', 'Your exam schedule', 'Board exams, internal assessments and unit tests this term.')}
    <div class="grid g-3 mb-6">
      ${[
        { t: 'Unit Test 2 — Mathematics', d: 'Sep 21, 2026 · 9:30 AM', w: '6 days', c: 'indigo' },
        { t: 'Unit Test 2 — Physics', d: 'Sep 18, 2026 · 10:00 AM', w: '3 days', c: 'teal' },
        { t: 'Unit Test 2 — Chemistry', d: 'Sep 25, 2026 · 11:00 AM', w: '10 days', c: 'green' },
        { t: 'Mid-term Examination', d: 'Oct 12, 2026 · 9:00 AM', w: '27 days', c: 'amber' },
      ].map(e => `
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
          ${[
            ['Unit Test 2 — Physics', 'Sep 18, 2026', '45 min', '25 MCQ', 'Electricity'],
            ['Unit Test 2 — Mathematics', 'Sep 21, 2026', '60 min', '30 MCQ', 'Quadratic, Trig'],
            ['Unit Test 2 — Chemistry', 'Sep 25, 2026', '40 min', '20 MCQ', 'Reactions'],
            ['Mid-term — All subjects', 'Oct 12-20, 2026', '2 hours', 'Written + MCQ', 'Full syllabus'],
          ].map(([a, b, c, d, e]) => `<tr><td class="nm">${a}</td><td class="muted">${b}</td><td>${c}</td><td>${d}</td><td class="muted">${e}</td></tr>`).join('')}
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
              <span class="badge green">${icon('flame', 'ic-xs')} ${u.streak}-day streak</span>
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
            ['Date of birth', '14 Mar 2010'],
            ['Phone', '+91 ••••• 43210'],
            ['Address', 'Bangalore, Karnataka'],
            ['Guardian', 'Mr. Rajesh Sharma'],
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
            ['Class teacher', 'Ms. Priya Nair'],
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
            ${statBlock('Overall mastery', '73%', '+8% this term', 'award', 'up')}
            ${statBlock('Knowledge health', '73%', 'Stable', 'brain')}
            ${statBlock('Current streak', u.streak + ' days', 'Personal best 12', 'flame')}
            ${statBlock('Topics mastered', '23', 'of 42', 'book2')}
          </div>
        </div>
      </div>

      <div class="card">
        <div class="card-h"><h3>Study preferences</h3></div>
        <div class="card-b">
          ${[
            ['Preferred study time', '4:00 PM – 7:00 PM'],
            ['Session length', '25 minutes'],
            ['Revision reminders', 'Enabled · push + email'],
            ['Weekly goal', '5 sessions / week'],
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
            ['Study streak reminders', true],
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
          Hi Aarav 👋 I can help you understand topics, plan revision, or prepare for your assessments. What would you like to work on?
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
  window.calMove = calMove;
  window.calToday = calToday;
  window.setCalView = setCalView;
  window.openResult = openResult;
  window.openAIPanel = openAIPanel;
  window.sendAI = sendAI;
  window.closeOverlay = closeOverlay;
  window.toast = toast;
}
