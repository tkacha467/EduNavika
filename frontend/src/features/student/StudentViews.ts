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
import {
  SUBJECTS,
  curriculumService,
  CurriculumHierarchyResponse,
} from '../../services/curriculumService';
import { STUDENT, getCurrentUser } from '../../services/authService';
import { adaptiveService } from '../../services/adaptiveService';
import { explanationService } from '../../services/explanationService';
import { UI } from '../../services/uiState';
import { StudentProgressResponse, RevisionPlanResponse, RevisionPlanItem, GamificationResponse } from '../../types';
import { t, getLanguage } from '../../utils/i18n';
import {
  FORGETTING_TIMELINE,
  UPCOMING_ASSESSMENTS,
  COMPLETED_ASSESSMENTS,
  NOTIFICATIONS,
  TIMETABLE,
  CLASS_WEAK_TOPICS,
} from './studentData';

declare const window: any;

/* ---------- Dashboard ---------- */
let dashboardHeroState: {
  recommendation?: any;
  loading: boolean;
} = {
  loading: false,
};

export async function loadDashboardRecommendation(): Promise<void> {
  if (dashboardHeroState.loading) return;
  const user = getCurrentUser();
  const studentId = user.id || 'e09699dd-0c64-44cc-82ef-ab41a832e072';
  dashboardHeroState.loading = true;
  try {
    const rec = await adaptiveService.getNextPracticeRecommendation(studentId);
    dashboardHeroState.recommendation = rec;
  } catch (err) {
    console.debug('Dashboard recommendation fetch note:', err);
  } finally {
    dashboardHeroState.loading = false;
  }
}

/* ---------- Gamification MVP State (Phase 17) ---------- */
let gamificationState: {
  data?: GamificationResponse;
  loading: boolean;
  studentId?: string;
  language?: string;
} = {
  loading: false,
};

export async function loadStudentGamification(force: boolean = false): Promise<void> {
  const user = getCurrentUser();
  const studentId = user.id || 'e09699dd-0c64-44cc-82ef-ab41a832e072';
  const lang = getLanguage();
  if (gamificationState.loading) return;
  if (gamificationState.data && gamificationState.studentId === studentId && gamificationState.language === lang && !force) return;
  gamificationState.loading = true;
  gamificationState.studentId = studentId;
  gamificationState.language = lang;
  try {
    const data = await adaptiveService.getGamification(studentId, lang);
    if (data) {
      gamificationState.data = data;
    }
  } catch (err) {
    console.debug('Failed loading gamification data:', err);
  } finally {
    gamificationState.loading = false;
  }
}

function renderGamificationSection(g?: GamificationResponse): string {
  if (!g) {
    return `
    <div class="card pad-lg mb-6" style="border-radius:14px;border:1px solid var(--border);background:var(--surface)">
      <div class="flex-b items-center mb-3">
        <div style="font-size:12px;font-weight:700;color:var(--indigo);text-transform:uppercase;display:flex;align-items:center;gap:6px">
          <span>🏆</span> ${t('gamification.title')}
        </div>
        <span class="badge grey">Loading achievements...</span>
      </div>
    </div>`;
  }

  const xpPercent = Math.min(100, Math.max(0, g.level_progress_percentage || 0));
  const goalPercent = Math.min(100, Math.max(0, Math.round(g.daily_goal.percentage || ((g.daily_goal.completed / Math.max(1, g.daily_goal.target)) * 100))));
  const allBadges = [...(g.unlocked_badges || []), ...(g.locked_badges || [])];

  return `
  <!-- LEARNING ACHIEVEMENTS & DAILY GOALS (PHASE 17 GAMIFICATION MVP) -->
  <div class="card pad-lg mb-6" style="border-radius:16px;border:1px solid var(--border);background:var(--surface);box-shadow:0 2px 8px rgba(0,0,0,0.04)">
    <div class="flex-b items-center mb-4" style="flex-wrap:wrap;gap:8px">
      <div>
        <div style="font-size:11px;font-weight:800;letter-spacing:.06em;color:var(--indigo);text-transform:uppercase;display:flex;align-items:center;gap:6px">
          <span style="font-size:14px">🏆</span> ${t('gamification.title')}
        </div>
        <p style="font-size:12px;color:var(--text-3);margin:2px 0 0 0">${t('gamification.subtitle')}</p>
      </div>
      <div class="flex items-center gap-2">
        <span class="badge indigo" style="font-size:11.5px;padding:4px 10px;font-weight:700">
          ${t('gamification.level')} ${g.level} · ${g.level_title}
        </span>
      </div>
    </div>

    <!-- 3 Stat Blocks: Level & XP, Learning Streak, Daily Goal -->
    <div class="grid g-3 mb-5" style="gap:16px">
      <!-- 1. Level & XP -->
      <div style="background:var(--surface-2);border:1px solid var(--border-2);border-radius:12px;padding:14px 16px;display:flex;flex-direction:column;justify-content:space-between">
        <div>
          <div class="flex-b items-center mb-1">
            <span style="font-size:11px;font-weight:700;color:var(--text-3);text-transform:uppercase">${t('gamification.level')} ${g.level}</span>
            <span style="font-size:11.5px;font-weight:800;color:var(--indigo)">${g.total_xp} XP</span>
          </div>
          <div style="font-size:15px;font-weight:800;color:var(--text);margin-bottom:8px">${g.level_title}</div>
        </div>
        <div>
          <div class="flex-b items-center tiny mb-1" style="color:var(--text-3)">
            <span>${g.xp_towards_next_level} / ${g.xp_required_for_next_level} XP</span>
            <span>${xpPercent}%</span>
          </div>
          ${progressBar(xpPercent, 'indigo')}
          <div class="tiny mt-1" style="color:var(--text-3);font-size:11px">
            ${g.level >= 5 ? 'Max Level Reached' : `${Math.max(0, g.xp_required_for_next_level - g.xp_towards_next_level)} XP to Level ${g.level + 1}`}
          </div>
        </div>
      </div>

      <!-- 2. Active Learning Streak -->
      <div style="background:var(--surface-2);border:1px solid var(--border-2);border-radius:12px;padding:14px 16px;display:flex;flex-direction:column;justify-content:space-between">
        <div>
          <div class="flex-b items-center mb-1">
            <span style="font-size:11px;font-weight:700;color:var(--text-3);text-transform:uppercase">${t('gamification.streak')}</span>
            <span style="font-size:16px">${g.current_streak > 0 ? '🔥' : '🌱'}</span>
          </div>
          <div style="font-size:22px;font-weight:800;color:var(--text);line-height:1.2">
            ${g.current_streak} <span style="font-size:13px;font-weight:600;color:var(--text-2)">${t('gamification.days')}</span>
          </div>
        </div>
        <div style="padding-top:10px;border-top:1px solid var(--border-2);margin-top:8px">
          <div class="flex-b items-center tiny" style="color:var(--text-3)">
            <span>${t('gamification.longestStreak')}</span>
            <b style="color:var(--text)">${g.longest_streak} ${t('gamification.days')}</b>
          </div>
        </div>
      </div>

      <!-- 3. Daily Learning Goal -->
      <div style="background:var(--surface-2);border:1px solid var(--border-2);border-radius:12px;padding:14px 16px;display:flex;flex-direction:column;justify-content:space-between">
        <div>
          <div class="flex-b items-center mb-1">
            <span style="font-size:11px;font-weight:700;color:var(--text-3);text-transform:uppercase">${t('gamification.dailyGoal')}</span>
            ${g.daily_goal.is_completed ? `<span class="badge green" style="font-size:10.5px">✓ +25 XP</span>` : `<span class="badge amber" style="font-size:10.5px">${Math.max(0, g.daily_goal.target - g.daily_goal.completed)} left</span>`}
          </div>
          <div style="font-size:22px;font-weight:800;color:var(--text);line-height:1.2">
            ${g.daily_goal.completed} / ${g.daily_goal.target} <span style="font-size:12px;font-weight:600;color:var(--text-2)">activities</span>
          </div>
        </div>
        <div>
          <div class="flex-b items-center tiny mb-1" style="color:var(--text-3)">
            <span>${t('gamification.dailyGoalSub')}</span>
            <span>${goalPercent}%</span>
          </div>
          ${progressBar(goalPercent, g.daily_goal.is_completed ? 'green' : 'amber')}
        </div>
      </div>
    </div>

    <!-- Badges Shelf -->
    <div>
      <div class="flex-b items-center mb-3">
        <span style="font-size:12px;font-weight:700;color:var(--text-2);text-transform:uppercase;letter-spacing:.04em">
          ${t('gamification.badges')} (${g.unlocked_badges.length} / ${allBadges.length} ${t('gamification.unlocked')})
        </span>
      </div>
      <div style="display:grid;grid-template-columns:repeat(auto-fit, minmax(140px, 1fr));gap:10px">
        ${allBadges.map(b => {
          const isU = b.is_unlocked;
          return `
          <div class="badge-card" style="padding:10px;border-radius:10px;display:flex;flex-direction:column;align-items:center;text-align:center;gap:6px;transition:transform .15s ease;${isU ? 'background:var(--surface);border:1.5px solid var(--indigo);box-shadow:0 2px 6px rgba(79,70,229,.1);' : 'background:var(--surface-2);border:1px dashed var(--border-2);opacity:.65;'}" title="${b.description}">
            <div style="font-size:24px;filter:${isU ? 'none' : 'grayscale(100%)'};line-height:1">${b.icon}</div>
            <div style="font-size:11.5px;font-weight:700;color:var(--text);line-height:1.2;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;width:100%" title="${b.name}">${b.name}</div>
            <div style="font-size:10px;color:var(--text-3);line-height:1.2;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden">${b.description}</div>
            <span class="badge ${isU ? 'green' : 'grey'}" style="font-size:9.5px;padding:1px 6px;margin-top:auto">
              ${isU ? '✓ ' + t('gamification.unlocked') : t('gamification.locked')}
            </span>
          </div>`;
        }).join('')}
      </div>
    </div>
  </div>`;
}

function renderTodayRevisionSection(rev?: RevisionPlanResponse): string {
  const items: RevisionPlanItem[] = rev?.revisions || [];
  const dueItems = items.filter((i: RevisionPlanItem) => i.is_due_today || i.is_overdue);

  if (dueItems.length === 0) {
    return `
    <!-- TODAY'S REVISION: ALL CAUGHT UP EMPTY STATE -->
    <div class="card pad-lg mb-6" style="border-radius:14px;border:1px solid var(--border);background:var(--surface)">
      <div class="flex-b items-center mb-3">
        <div style="font-size:11px;font-weight:800;letter-spacing:.06em;color:var(--teal);text-transform:uppercase;display:flex;align-items:center;gap:6px">
          <span style="font-size:14px">🔄</span> TODAY'S REVISION
        </div>
        <span class="badge green">✓ All Caught Up</span>
      </div>
      <div style="display:flex;align-items:center;gap:16px;padding:8px 0;flex-wrap:wrap">
        <div style="font-size:32px">✨</div>
        <div style="flex:1;min-width:240px">
          <h4 style="font-size:15px;font-weight:700;color:var(--text);margin-bottom:3px">You're all caught up!</h4>
          <p style="font-size:13px;color:var(--text-3);margin:0;line-height:1.5">
            Your next revision will appear here when needed. EduNavika monitors your forgetting curve and schedules review before concepts fade.
          </p>
        </div>
        <button class="btn btn-sm btn-outline" data-go="student/revision">Full Revision Plan →</button>
      </div>
    </div>`;
  }

  return `
  <!-- TODAY'S REVISION: DUE ITEMS -->
  <div class="card pad-lg mb-6" style="border-radius:14px;border:1px solid var(--border);background:var(--surface)">
    <div class="flex-b items-center mb-4" style="flex-wrap:wrap;gap:8px">
      <div>
        <div style="font-size:11px;font-weight:800;letter-spacing:.06em;color:var(--teal);text-transform:uppercase;display:flex;align-items:center;gap:6px">
          <span style="font-size:14px">🔄</span> TODAY'S REVISION
        </div>
        <p style="font-size:12px;color:var(--text-3);margin:2px 0 0 0">Scheduled reviews based on your on-device decay curve</p>
      </div>
      <div class="flex items-center gap-2">
        <span class="badge ${dueItems.some((i: RevisionPlanItem) => i.is_overdue) ? 'coral' : 'amber'}" style="font-weight:700">
          ${dueItems.length} Due Today
        </span>
        <button class="btn btn-sm btn-outline" data-go="student/revision">View All →</button>
      </div>
    </div>

    <div class="grid g-3" style="gap:14px">
      ${dueItems.slice(0, 3).map((item: RevisionPlanItem) => `
        <div style="background:var(--surface-2);border:1px solid var(--border-2);border-radius:12px;padding:16px;display:flex;flex-direction:column;justify-content:space-between">
          <div>
            <div class="flex-b items-center mb-2">
              <span class="badge ${item.is_overdue ? 'coral' : 'amber'}" style="font-size:10px;font-weight:700">
                ${item.is_overdue ? 'OVERDUE' : 'DUE TODAY'}
              </span>
              <span class="tiny" style="color:var(--text-3)">Priority: ${item.priority}</span>
            </div>
            <h4 style="font-size:14.5px;font-weight:700;color:var(--text);margin-bottom:4px;line-height:1.3">${item.topic_title}</h4>
            <div class="tiny" style="color:var(--text-3);margin-bottom:10px">
              Mastery: <b>${item.mastery_level}</b> · Risk: <b>${item.retention_risk}</b>
            </div>
            <p style="font-size:12px;color:var(--text-2);line-height:1.45;margin-bottom:12px">${item.reason}</p>
          </div>
          <button class="btn btn-sm btn-primary" style="width:100%" onclick="loadAdaptivePractice('${item.topic_id}')">
            ${icon('refresh')} Revise Now
          </button>
        </div>
      `).join('')}
    </div>
  </div>`;
}

function renderProgressSection(p?: StudentProgressResponse, firstName: string = 'Student', isNew: boolean = false, topicId: string = '5a321a44-bc06-4db4-a50f-5e53f913b612'): string {
  const totalAttempts = p?.overall.total_attempts ?? 0;

  if (isNew || totalAttempts === 0) {
    return `
    <!-- YOUR PROGRESS: FRESH STUDENT EMPTY STATE -->
    <div class="card pad-lg mb-6" style="border-radius:14px;border:1px solid var(--border);background:var(--surface);text-align:center;padding:36px 20px">
      <div style="font-size:36px;margin-bottom:8px">🎯</div>
      <h3 style="font-size:17px;font-weight:700;color:var(--text);margin-bottom:6px">Start your first practice to build your learning profile</h3>
      <p style="color:var(--text-3);font-size:13px;max-width:540px;margin:0 auto 18px auto;line-height:1.5">
        Welcome, <b>${firstName}</b>! Complete your first adaptive practice set in Science or Mathematics to compute your baseline knowledge health, accuracy, and forgetting stability curve on this device.
      </p>
      <button class="btn btn-primary" onclick="loadAdaptivePractice('${topicId}')">
        ${icon('play')} Begin Diagnostic Practice
      </button>
    </div>`;
  }

  const correctAttempts = p?.overall.correct_attempts ?? 0;
  const accuracy = p?.overall.overall_accuracy ?? 0;
  const topicsStudied = p?.overall.topics_studied ?? 0;
  const totalTopics = p?.overall.total_topics_available ?? 1;
  const trend = p?.overall.overall_trend ?? 'STABLE';
  const m = p?.overall.mastery_distribution ?? { unassessed: 0, novice: 0, developing: 0, proficient: 0, mastered: 0 };
  const totalForBar = Math.max(totalTopics, 1);
  const pMastered = Math.round((m.mastered / totalForBar) * 100);
  const pProficient = Math.round((m.proficient / totalForBar) * 100);
  const pDeveloping = Math.round((m.developing / totalForBar) * 100);
  const pNovice = Math.round((m.novice / totalForBar) * 100);

  return `
  <!-- YOUR PROGRESS: LIVE TELEMETRY & MASTERY BREAKDOWN -->
  <div class="card pad-lg mb-6" style="border-radius:14px;border:1px solid var(--border);background:var(--surface)">
    <div class="flex-b items-center mb-4" style="flex-wrap:wrap;gap:8px">
      <div>
        <div style="font-size:11px;font-weight:800;letter-spacing:.06em;color:var(--indigo);text-transform:uppercase;display:flex;align-items:center;gap:6px">
          <span>📊</span> YOUR PROGRESS & KNOWLEDGE HEALTH
        </div>
        <p style="font-size:12px;color:var(--text-3);margin:2px 0 0 0">Standard 10 syllabus mastery computed locally from verified learning events</p>
      </div>
      <button class="btn btn-sm btn-outline" data-go="student/analytics">Detailed Learning Journey →</button>
    </div>

    <div class="grid g-4 mb-4">
      ${statBlock('Questions Solved', `${totalAttempts}`, `${correctAttempts} correct`, 'target', 'up')}
      ${statBlock('Overall Accuracy', `${accuracy.toFixed(1)}%`, accuracy >= 70 ? 'Strong baseline' : 'Building accuracy', 'chart', accuracy >= 70 ? 'up' : 'down')}
      ${statBlock('Topics Studied', `${topicsStudied}`, `of ${totalTopics} available`, 'book', 'up')}
      ${statBlock('Retention Trend', trend, 'Local stability estimate', 'brain', trend === 'IMPROVING' ? 'up' : 'neutral')}
    </div>

    <div>
      <div class="flex-b items-center tiny mb-2" style="color:var(--text-2);font-weight:600">
        <span>Mastery Breakdown across ${totalTopics} Topics</span>
        <div class="flex gap-3">
          <span style="color:var(--green)">● Mastered ${pMastered}%</span>
          <span style="color:var(--teal)">● Proficient ${pProficient}%</span>
          <span style="color:var(--amber)">● Developing ${pDeveloping}%</span>
          <span style="color:var(--coral)">● Novice ${pNovice}%</span>
        </div>
      </div>
      <div style="height:10px;border-radius:99px;background:var(--border-2);display:flex;overflow:hidden">
        <div style="width:${pMastered}%;background:var(--green)" title="Mastered: ${m.mastered}"></div>
        <div style="width:${pProficient}%;background:var(--teal)" title="Proficient: ${m.proficient}"></div>
        <div style="width:${pDeveloping}%;background:var(--amber)" title="Developing: ${m.developing}"></div>
        <div style="width:${pNovice}%;background:var(--coral)" title="Novice: ${m.novice}"></div>
      </div>
    </div>
  </div>`;
}

export function studentDashboard(): string {
  const sub = SUBJECTS;
  const user = getCurrentUser();
  const firstName = user.full_name?.split(' ')[0] || user.name?.split(' ')[0] || 'Student';
  const rec = dashboardHeroState.recommendation;
  const g = gamificationState.data;
  const rev = revisionPlanState.data;
  const prog = progressState.data;

  const totalAttempts = prog?.overall.total_attempts ?? (COMPLETED_ASSESSMENTS.length > 0 ? 5 : 0);
  const isNew = totalAttempts === 0 && (user.todayGoal || 0) === 0;

  const refreshDashboard = () => {
    if (typeof window !== 'undefined' && window.location.hash.includes('student/dashboard')) {
      const root = document.getElementById('main');
      if (root) {
        root.innerHTML = studentDashboard();
      }
    }
  };

  // Proactively trigger async loads for live data
  if (!rec && !dashboardHeroState.loading) {
    loadDashboardRecommendation().then(refreshDashboard);
  }
  if (!g && !gamificationState.loading) {
    loadStudentGamification().then(refreshDashboard);
  }
  if (!rev && !revisionPlanState.loading) {
    loadRevisionPlan().then(refreshDashboard);
  }
  if (!prog && !progressState.loading) {
    loadStudentProgress().then(refreshDashboard);
  }

  // Time-aware greeting
  const hour = new Date().getHours();
  const timeGreeting = hour < 12 ? 'Good morning' : hour < 17 ? 'Good afternoon' : 'Good evening';

  const topicTitle = rec ? rec.topic_title : 'Chemical Reactions and Equations';
  const topicId = rec ? rec.topic_id : '5a321a44-bc06-4db4-a50f-5e53f913b612';
  const mastery = rec ? rec.mastery_level : (isNew ? 'UNASSESSED' : 'NOVICE');
  const accuracy = rec ? `${rec.accuracy.toFixed(1)}%` : (isNew ? '0.0%' : '0.0%');
  const recentAccuracy = rec?.recent_accuracy != null ? `${rec.recent_accuracy.toFixed(1)}%` : accuracy;
  const retentionRisk = rec ? rec.retention_risk : (isNew ? 'UNASSESSED' : 'MODERATE');
  const trend = rec ? rec.trend : (isNew ? 'INSUFFICIENT_DATA' : 'STABLE');
  const diff = rec ? rec.recommended_difficulty : 'FOUNDATIONAL';
  const actionLabel = rec?.recommended_action?.replace(/_/g, ' ') || 'DIAGNOSTIC PRACTICE';
  const reasonText = rec?.reason || (isNew ? 'Begin with a diagnostic practice set to establish your baseline curriculum knowledge profile.' : 'Adaptive practice tailored to your current knowledge profile.');

  return `
  <div class="page with-rail">
    <!-- Welcome Header with Team Varja Attribution -->
    <div class="welcome" style="margin-bottom:24px">
      <div class="welcome-c">
        <div class="welcome-l">
          <div class="hi" style="display:flex;align-items:center;gap:8px">
            <span>${timeGreeting}, ${firstName} 👋</span>
            <span class="badge" style="background:rgba(255,255,255,.18);color:#fff;font-size:10px;padding:2px 8px;border-radius:10px">Std 10 · GSEB Science & Mathematics</span>
          </div>
          <h1 style="margin-top:6px">On-Device Personalized Learning Assistant</h1>
          <p>Continuous adaptive practice, verified curriculum grounding, and retention-aware study paths — completely private on this device.</p>
        </div>
        <div class="welcome-r">
          <div class="wstat"><div class="l">Engine</div><div class="v">Local SLM</div><div class="d">Qwen2.5-0.5B</div></div>
          <div class="wstat"><div class="l">Inference</div><div class="v">CPU</div><div class="d">100% Offline</div></div>
          <div class="wstat"><div class="l">Curriculum</div><div class="v">GSEB 10</div><div class="d">NCERT-aligned</div></div>
          <div class="wstat"><div class="l">Status</div><div class="v">Active</div><div class="d">Private on-device</div></div>
        </div>
      </div>
    </div>

    <!-- 1. YOUR LEARNING TODAY (LIVE GAMIFICATION DATA) -->
    ${renderGamificationSection(gamificationState.data)}

    <!-- 2. RECOMMENDED FOR YOU (PERSONALIZED LEARNING PATH) -->
    <div class="card pad-lg mb-6" style="background:linear-gradient(135deg, #1E293B, #0F172A);color:#fff;border-radius:16px;border:1px solid rgba(255,255,255,.1);box-shadow:0 8px 30px rgba(15,23,42,.35)">
      <div class="flex-b items-center mb-3">
        <div style="font-size:11px;font-weight:800;letter-spacing:.08em;color:#38BDF8;text-transform:uppercase;display:flex;align-items:center;gap:6px">
          <span style="display:inline-block;width:8px;height:8px;border-radius:50%;background:#38BDF8;box-shadow:0 0 8px #38BDF8"></span>
          RECOMMENDED FOR YOU
        </div>
        <span class="badge" style="background:rgba(56,189,248,.15);color:#38BDF8;border:1px solid rgba(56,189,248,.3);font-size:11px;font-weight:700">
          ${actionLabel}
        </span>
      </div>

      <div class="grid g-3-1 items-center" style="gap:24px">
        <div>
          <h2 style="font-size:24px;font-weight:800;line-height:1.3;margin-bottom:8px;color:#F8FAFC">
            ${topicTitle}
          </h2>
          <div style="font-size:13.5px;color:#94A3B8;line-height:1.55;margin-bottom:18px">
            <b style="color:#CBD5E1">Why this topic?</b> ${reasonText}
          </div>

          <!-- 4 Pillars Knowledge Grid -->
          <div class="grid g-4" style="background:rgba(255,255,255,.05);padding:14px 18px;border-radius:12px;border:1px solid rgba(255,255,255,.08);margin-bottom:20px">
            <div>
              <div style="font-size:11px;color:#94A3B8;text-transform:uppercase;font-weight:600;letter-spacing:.03em">Mastery</div>
              <div style="font-size:16px;font-weight:800;color:#38BDF8;margin-top:2px">${mastery}</div>
            </div>
            <div>
              <div style="font-size:11px;color:#94A3B8;text-transform:uppercase;font-weight:600;letter-spacing:.03em">Recent Accuracy</div>
              <div style="font-size:16px;font-weight:800;color:#4ADE80;margin-top:2px">${recentAccuracy}</div>
            </div>
            <div>
              <div style="font-size:11px;color:#94A3B8;text-transform:uppercase;font-weight:600;letter-spacing:.03em">Retention Risk</div>
              <div style="font-size:16px;font-weight:800;color:#FBBF24;margin-top:2px">${retentionRisk}</div>
            </div>
            <div>
              <div style="font-size:11px;color:#94A3B8;text-transform:uppercase;font-weight:600;letter-spacing:.03em">Trend</div>
              <div style="font-size:16px;font-weight:800;color:#A78BFA;margin-top:2px">${trend}</div>
            </div>
          </div>

          <div class="flex gap-3 wrap">
            <button class="btn btn-primary btn-lg" style="background:#2563EB;border-color:#2563EB;padding:12px 24px;font-size:14px;font-weight:700;display:flex;align-items:center;gap:8px" onclick="loadAdaptivePractice('${topicId}')">
              ${icon('play')} Practice Now
            </button>
            <button class="btn btn-lg" style="background:rgba(255,255,255,.1);color:#fff;border:1px solid rgba(255,255,255,.2);padding:12px 22px;font-size:14px;font-weight:600;display:flex;align-items:center;gap:8px" onclick="openAIPanel()">
              ${icon('sparkles')} Ask EduNavika AI
            </button>
          </div>
        </div>

        <!-- Provenance and On-Device Assurance Card -->
        <div style="background:rgba(255,255,255,.03);border:1px solid rgba(255,255,255,.07);border-radius:12px;padding:18px;display:flex;flex-direction:column;gap:12px">
          <div style="font-size:12px;font-weight:700;color:#38BDF8;text-transform:uppercase;letter-spacing:.04em">
            ⚡ On-Device Intelligence
          </div>
          <div style="font-size:12px;color:#94A3B8;line-height:1.5">
            Your knowledge profile and recommendations are computed entirely on-device without cloud analytics.
          </div>
          <div style="padding-top:10px;border-top:1px solid rgba(255,255,255,.08);font-size:11.5px;color:#CBD5E1">
            <b>Textbook Provenance:</b><br>
            Standard 10 Verified Curriculum
          </div>
          <div style="font-size:11px;color:#64748B">
            Target Tier: <b>${diff}</b>
          </div>
        </div>
      </div>
    </div>

    <!-- 3. TODAY'S REVISION (LIVE REVISION PLAN DATA) -->
    ${renderTodayRevisionSection(revisionPlanState.data)}

    <!-- 4. YOUR PROGRESS & KNOWLEDGE HEALTH (LIVE TELEMETRY) -->
    ${renderProgressSection(progressState.data, firstName, isNew, topicId)}

    <!-- 5. Active Practice & Curriculum Focus -->
    <div class="sec-head">
      <div><h2>${icon('target')} Curriculum Focus</h2><p>Topics aligned with your Standard 10 GSEB syllabus.</p></div>
      <div class="right"><button class="btn btn-sm" data-go="student/practice">Adaptive Practice →</button></div>
    </div>
    <div class="focus-grid mb-6">
      <div class="focus-card practice" onclick="loadAdaptivePractice()" style="border:1.5px solid var(--indigo)">
        <div class="ftag" style="background:var(--indigo-50);color:var(--indigo)">${icon('zap', 'ic-xs')} Active Recommendation</div>
        <div class="fsub">Science · Chapter 1</div>
        <h4>Chemical Reactions & Equations</h4>
        <div class="fmeta">Accuracy: ${accuracy} · ${mastery}</div>
        <button class="btn btn-sm btn-primary" style="width:100%">Practice Recommended Tier</button>
      </div>

      <div class="focus-card continue" onclick="startQuiz('Electricity & Circuits')">
        <div class="ftag">${icon('play', 'ic-xs')} Diagnostic Check</div>
        <div class="fsub">Science · Chapter 11</div>
        <h4>Electricity</h4>
        <div class="fmeta">Standard 10 Core Physics</div>
        <button class="btn btn-sm" style="width:100%">Start Quiz</button>
      </div>

      <div class="focus-card revision" onclick="startQuiz('Real Numbers & Polynomials')">
        <div class="ftag">${icon('refresh', 'ic-xs')} Math Concept Check</div>
        <div class="fsub">Mathematics · Chapter 1</div>
        <h4>Real Numbers & Polynomials</h4>
        <div class="fmeta">Foundational Algebra</div>
        <button class="btn btn-sm" style="width:100%">Take Quiz</button>
      </div>
    </div>


    <!-- Knowledge Health + AI Insight -->
    <div class="grid g-3-1 mb-6">
      <div class="card">
        <div class="card-h">
          <div><h3>Knowledge Health</h3><div class="sub">Live model-derived estimate of how stable your learning is</div></div>
          <div class="right"><span class="badge teal">${icon('sparkles')} EduNavika AI</span></div>
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
              <p style="font-size:12px;max-width:380px;margin:4px auto 0 auto">Take quizzes or practice sessions to allow EduNavika AI to model your memory retention curve.</p>
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
      <div><h2>${icon('grid')} Subject Performance & Knowledge Health</h2><p>Mastery, stability estimates, and priority topics across your subjects</p></div>
      <div class="right"><button class="btn btn-sm" data-go="student/subjects">See all subjects →</button></div>
    </div>
    <div class="grid g-3">
      ${sub.map(s => {
        const isAssessed = s.done > 0 || s.mastery > 0 || (s.id === 'chem' && rec);
        const subjMastery = (s.id === 'chem' && rec) ? (rec.accuracy ? Math.round(rec.accuracy) : 44) : s.mastery;
        const subjKhLabel = (s.id === 'chem' && rec) ? (rec.retention_risk === 'HIGH' ? 'Needs attention' : rec.retention_risk === 'MODERATE' ? 'Moderate' : 'Stable') : (s.kh >= 70 ? 'Stable' : s.kh >= 50 ? 'Needs attention' : 'Unassessed');
        const priorityTopic = (s.id === 'chem' && rec) ? rec.topic_title : (s.topicList[0]?.name || 'Core concept');
        const nextAction = (s.id === 'chem' && rec) ? actionLabel : (isAssessed ? 'Review topic' : 'Diagnostic check');

        return `
        <div class="subj-card" onclick="openSubject('${s.id}')" style="display:flex;flex-direction:column;justify-content:space-between">
          <div>
            <div class="sc-h mb-3">
              <div class="subj-ic" style="background:${s.bg};color:${s.color}">${s.code}</div>
              <div style="flex:1;min-width:0">
                <h4 style="font-size:15px;font-weight:700">${s.name}</h4>
                <span class="tiny" style="color:var(--text-3)">Priority: <b>${priorityTopic}</b></span>
              </div>
              <span class="badge ${subjKhLabel === 'Needs attention' ? 'amber' : subjKhLabel === 'Stable' ? 'green' : 'grey'}">${subjKhLabel}</span>
            </div>
            <div class="subj-metrics mb-3">
              <div class="m"><div class="l">Mastery</div><div class="v">${isAssessed ? `${subjMastery}%` : 'Baseline'}</div>${progressBar(subjMastery, subjMastery >= 75 ? 'green' : subjMastery >= 50 ? 'indigo' : 'amber')}</div>
              <div class="m"><div class="l">Knowledge Health</div><div class="v" style="color:${subjKhLabel === 'Stable' ? 'var(--green)' : subjKhLabel === 'Needs attention' ? 'var(--amber)' : 'var(--text-3)'}">${subjKhLabel}</div>${progressBar(s.kh || (isAssessed ? 55 : 0), subjKhLabel === 'Stable' ? 'green' : subjKhLabel === 'Needs attention' ? 'amber' : 'coral')}</div>
            </div>
          </div>
          <div style="padding-top:10px;border-top:1px solid var(--border-2);display:flex;align-items:center;justify-content:space-between">
            <span class="tiny" style="color:var(--text-2);font-weight:600">Action: ${nextAction}</span>
            <span class="btn btn-sm btn-ghost" style="padding:2px 8px;font-size:11px">Open →</span>
          </div>
        </div>`;
      }).join('')}
    </div>

    <!-- Learning Reminders & Curriculum Alerts -->
    <div class="sec-head mt-6">
      <div><h2>${icon('bell')} Learning Updates & Reminders</h2><p>Curriculum milestones and spaced revision alerts</p></div>
      <div class="right"><button class="btn btn-sm" data-go="student/notifications">Notification center</button></div>
    </div>
    <div class="card">
      <div class="card-b">
        <div class="notice">
          <span class="n-dot urgent"></span>
          <div class="n-body"><b>Spaced Revision Scheduled</b><p>Electricity & Circuits practice is scheduled for memory stabilization. Recommended preparation: complete today's revision queue.</p><div class="n-time">${icon('clock', 'ic-xs')} Today · Adaptive Scheduler</div></div>
        </div>
        <div class="notice">
          <span class="n-dot teal"></span>
          <div class="n-body"><b>Standard 10 Science Syllabus Active</b><p>Chemical Reactions and Equations & Acids, Bases and Salts verified learning materials are available locally on this device.</p><div class="n-time">${icon('clock', 'ic-xs')} Active · On-Device Curriculum</div></div>
        </div>
        <div class="notice">
          <span class="n-dot"></span>
          <div class="n-body"><b>Daily Learning Goal</b><p>Complete 5 meaningful learning activities today to maintain your learning streak and earn +25 bonus XP.</p><div class="n-time">${icon('clock', 'ic-xs')} Daily · Milestones</div></div>
        </div>
      </div>
    </div>
  </div>

  <aside class="rail">
    <div class="rail-inner">
      <div class="ai-card">
        <div class="ai-head"><div class="ai-mark">${icon('sparkles')}</div><b>EduNavika AI</b></div>
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
        <div class="card-h"><div><h3>Recommended for you</h3><div class="sub">Curriculum guidance from EduNavika AI</div></div></div>
        <div class="card-b">
          <div class="flex-c">
            ${aiInsight('Diagnostic Practice', `Welcome to Standard 10! Complete a quick 5-question baseline practice set in Mathematics or Science to calibrate your knowledge curve.`, 'Start practice', `startQuiz('Real Numbers & Polynomials')`)}
            ${aiInsight('Structured Revision', `EduNavika AI continuously schedules revision sessions to reinforce retention before concepts fade.`, 'View revision plan', `navigate('student/revision')`)}
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
            <div class="ai-head"><div class="ai-mark">${icon('sparkles')}</div><b>EduNavika AI — ${s.name}</b></div>
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

/* ---------- Personalized Revision Plan State (Phase 16) ---------- */
let revisionPlanState: {
  data?: RevisionPlanResponse;
  loading: boolean;
  studentId?: string;
  language?: string;
} = {
  loading: false,
};

export async function loadRevisionPlan(force: boolean = false): Promise<void> {
  const user = getCurrentUser();
  const studentId = user.id || 'e09699dd-0c64-44cc-82ef-ab41a832e072';
  const lang = getLanguage();
  if (revisionPlanState.loading) return;
  if (revisionPlanState.data && revisionPlanState.studentId === studentId && revisionPlanState.language === lang && !force) return;
  revisionPlanState.loading = true;
  revisionPlanState.studentId = studentId;
  revisionPlanState.language = lang;
  try {
    const data = await adaptiveService.getRevisionPlan(studentId, undefined, lang);
    if (data) {
      revisionPlanState.data = data;
    }
  } catch (err) {
    console.debug('Failed loading revision plan from backend:', err);
  } finally {
    revisionPlanState.loading = false;
  }
}

export async function loadRevisionPlansFromBackend(): Promise<void> {
  await loadRevisionPlan(true);
}

if (typeof window !== 'undefined') {
  (window as any).refreshRevisionQueue = loadRevisionPlansFromBackend;
  (window as any).loadRevisionPlan = loadRevisionPlan;
}

/* ---------- Revision Plan ---------- */
export function studentRevision(): string {
  if (!revisionPlanState.data && !revisionPlanState.loading) {
    loadRevisionPlan().then(() => {
      if (typeof window !== 'undefined' && window.location.hash.includes('student/revision')) {
        const root = document.getElementById('main');
        if (root) {
          root.innerHTML = studentRevision();
        }
      }
    });
  }

  const p = revisionPlanState.data;
  const revisions = p?.revisions ?? [];
  const dueToday = revisions.filter(r => r.urgency_tier === 'TODAY' || r.is_due_today);
  const dueWeek = revisions.filter(r => r.urgency_tier === 'THIS_WEEK' && !r.is_due_today);
  const upcoming = revisions.filter(r => r.urgency_tier === 'UPCOMING');
  const isZero = revisions.length === 0;

  const renderRevRow = (r: RevisionPlanItem, isUrgent = false) => {
    const pBadge = r.priority === 'URGENT'
      ? `<span class="badge coral">${t('revision.priority.URGENT')}</span>`
      : r.priority === 'HIGH'
      ? `<span class="badge amber">${t('revision.priority.HIGH')}</span>`
      : r.priority === 'MEDIUM'
      ? `<span class="badge indigo">${t('revision.priority.MEDIUM')}</span>`
      : `<span class="badge teal">${t('revision.priority.LOW')}</span>`;

    const riskB = r.retention_risk === 'HIGH'
      ? riskBadge('high')
      : r.retention_risk === 'MODERATE'
      ? riskBadge('medium')
      : riskBadge('low');

    const dueBadge = r.is_due_today
      ? `<span class="badge coral">${t('revision.todayBadge')}</span>`
      : r.days_until_due === 1
      ? `<span class="badge amber">${t('revision.dueTomorrow')}</span>`
      : `<span class="badge grey">${t('revision.dueInDays').replace('{n}', String(r.days_until_due))}</span>`;

    const iconBg = isUrgent ? 'var(--coral-50)' : r.priority === 'HIGH' ? 'var(--amber-50)' : 'var(--teal-50)';
    const iconColor = isUrgent ? 'var(--coral)' : r.priority === 'HIGH' ? '#B4731A' : 'var(--teal-600)';

    return `
      <div class="rev-row" style="align-items:flex-start;padding:16px 20px;border-bottom:1px solid var(--border-2)">
        <div class="ri" style="background:${iconBg};color:${iconColor};margin-top:2px">${icon('refresh')}</div>
        <div class="rmain" style="flex:1;min-width:200px">
          <div class="flex gap-2 items-center wrap mb-1">
            <b style="font-size:14px">${r.subject_name} — ${r.topic_title}</b>
            ${pBadge}
            ${dueBadge}
          </div>
          <p style="font-size:12.5px;color:var(--text);margin:0 0 6px 0;line-height:1.45">${r.reason}</p>
          <div class="flex gap-4 wrap" style="font-size:11.5px;color:var(--text-3)">
            <span>${t('progress.col.mastery')}: <b>${t('mastery.' + r.mastery_level) || r.mastery_level}</b></span>
            <span>${t('progress.col.accuracy')}: <b>${r.accuracy.toFixed(1)}%</b></span>
            ${r.recent_accuracy != null ? `<span>Recent: <b>${r.recent_accuracy.toFixed(1)}%</b></span>` : ''}
            <span>${t('progress.col.risk')}: <b>${t('risk.' + r.retention_risk) || r.retention_risk}</b></span>
            ${r.source_document ? `<span>📖 <b>${t('revision.source')}:</b> ${r.source_page ? `Page ${r.source_page}` : r.source_document}</span>` : ''}
          </div>
        </div>
        <div style="display:flex;flex-direction:column;align-items:flex-end;gap:8px;margin-left:12px">
          ${riskB}
          <button class="btn btn-primary btn-sm" onclick="loadAdaptivePractice('${r.topic_id}')">${icon('play')} ${t('revision.btnStart')}</button>
        </div>
      </div>
    `;
  };

  return `
  <div class="page">
    ${pageHead(
      t('revision.title'),
      t('revision.sub'),
      t('revision.desc'),
      '<button class="btn btn-sm btn-outline" onclick="loadRevisionPlan(true).then(() => { const r = document.getElementById(\'main\'); if(r) r.innerHTML = studentRevision(); toast(\'Revision Refreshed\',\'Spaced intervals recalculated\',\'good\'); })">' + icon('refresh') + ' ' + t('btn.refresh') + '</button>'
    )}

    <div class="grid g-4 mb-6">
      ${statBlock(t('revision.dueToday'), dueToday.length, dueToday.length ? `${p?.urgent_count ?? 0} Urgent` : 'None due', 'alert', dueToday.length ? 'down' : 'up')}
      ${statBlock(t('revision.dueThisWeek'), dueWeek.length, dueWeek.length ? 'Scheduled' : 'None scheduled', 'calendar')}
      ${statBlock(t('revision.upcoming'), upcoming.length, 'Spaced Maintenance', 'clock', 'up')}
      ${statBlock('Total Active', revisions.length, `${p?.urgent_count ?? 0} Urgent · ${p?.high_count ?? 0} High`, 'target', 'up')}
    </div>

    ${isZero ? `
      <div class="card pad-lg mb-6" style="padding:48px 24px;text-align:center">
        <div style="font-size:36px;margin-bottom:8px">🎉</div>
        <h3 class="h3 mb-2">${t('revision.empty')}</h3>
        <p style="color:var(--text-3);max-width:520px;margin:0 auto 20px auto;font-size:13.5px;line-height:1.5">
          ${t('revision.emptyDesc')}
        </p>
        <button class="btn btn-primary" onclick="navigate('student/learning')">${icon('play')} Practice Standard 10 Syllabus</button>
      </div>
    ` : `
    <!-- Due Today -->
    <div class="sec-head mt-4"><div><h2>${icon('alert')} ${t('revision.dueToday')}</h2><p>${t('revision.dueTodaySub')} (${dueToday.length})</p></div></div>
    <div class="card mb-6">
      ${dueToday.length ? dueToday.map(r => renderRevRow(r, true)).join('') : `<div class="empty" style="padding:24px;text-align:center;color:var(--text-3)">No items due today 🎉</div>`}
    </div>

    <!-- This week -->
    <div class="sec-head"><div><h2>${icon('calendar')} ${t('revision.dueThisWeek')}</h2><p>${t('revision.dueThisWeekSub')} (${dueWeek.length})</p></div></div>
    <div class="card mb-6">
      ${dueWeek.length ? dueWeek.map(r => renderRevRow(r, false)).join('') : `<div class="empty" style="padding:24px;text-align:center;color:var(--text-3)">Nothing else this week 🎉</div>`}
    </div>

    <!-- Upcoming -->
    <div class="sec-head"><div><h2>${icon('clock')} ${t('revision.upcoming')}</h2><p>${t('revision.upcomingSub')} (${upcoming.length})</p></div></div>
    <div class="card mb-6">
      ${upcoming.length ? upcoming.map(r => renderRevRow(r, false)).join('') : `<div class="empty" style="padding:24px;text-align:center;color:var(--text-3)">No upcoming maintenance scheduled</div>`}
    </div>
    `}
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
      ${aiInsight('EduNavika Insight',
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

/* ---------- Progress & Learning Journey State ---------- */
let progressState: {
  data?: StudentProgressResponse;
  loading: boolean;
  studentId?: string;
} = {
  loading: false,
};

export async function loadStudentProgress(force: boolean = false): Promise<void> {
  const user = getCurrentUser();
  const studentId = user.id || 'e09699dd-0c64-44cc-82ef-ab41a832e072';
  if (progressState.loading) return;
  if (progressState.data && progressState.studentId === studentId && !force) return;
  progressState.loading = true;
  progressState.studentId = studentId;
  try {
    const data = await adaptiveService.getProgress(studentId);
    if (data) {
      progressState.data = data;
    }
  } catch (err) {
    console.debug('Failed to load student progress:', err);
  } finally {
    progressState.loading = false;
  }
}

/* ---------- Learning Analytics & Progress Tracking ---------- */
export function studentAnalytics(): string {
  if (!progressState.data && !progressState.loading) {
    loadStudentProgress().then(() => {
      if (typeof window !== 'undefined' && window.location.hash.includes('student/analytics')) {
        const root = document.getElementById('main');
        if (root) {
          root.innerHTML = studentAnalytics();
        }
      }
    });
  }

  const p = progressState.data;
  const isZero = !p || p.overall.total_attempts === 0;

  const totalAttempts = p?.overall.total_attempts ?? 0;
  const correctAttempts = p?.overall.correct_attempts ?? 0;
  const accuracy = p?.overall.overall_accuracy ?? 0;
  const topicsStudied = p?.overall.topics_studied ?? 0;
  const totalTopics = p?.overall.total_topics_available ?? 1;
  const overallTrend = p?.overall.overall_trend ?? 'INSUFFICIENT_DATA';
  const masteryDist = p?.overall.mastery_distribution ?? { unassessed: 1, novice: 0, developing: 0, proficient: 0, mastered: 0 };
  const sw = p?.strengths_weaknesses ?? { strengths: [], weaknesses: [], developing: [], unassessed_count: 1 };
  const journey = p?.learning_journey ?? [];
  const topics = p?.topics ?? [];

  const trendBadge = overallTrend === 'IMPROVING'
    ? '<span class="badge green">↑ Improving</span>'
    : overallTrend === 'DECLINING'
    ? '<span class="badge coral">↓ Declining</span>'
    : overallTrend === 'STABLE'
    ? '<span class="badge teal">→ Stable</span>'
    : '<span class="badge grey">Baseline</span>';

  // Calculate percentage segments for mastery bar
  const totalForBar = Math.max(totalTopics, 1);
  const pMastered = Math.round((masteryDist.mastered / totalForBar) * 100);
  const pProficient = Math.round((masteryDist.proficient / totalForBar) * 100);
  const pDeveloping = Math.round((masteryDist.developing / totalForBar) * 100);
  const pNovice = Math.round((masteryDist.novice / totalForBar) * 100);
  const pUnassessed = Math.max(0, 100 - (pMastered + pProficient + pDeveloping + pNovice));

  return `
  <div class="page">
    ${pageHead(
      'Learning Progress & Journey',
      'Continuous on-device progress tracking',
      `Empirical telemetry, syllabus mastery distribution, and real-time learning history for GSEB Standard 10 (${p?.overall.subject_name || 'Science & Technology'}).`,
      '<button class="btn btn-sm btn-outline" onclick="loadStudentProgress(true).then(() => { const r = document.getElementById(\'main\'); if(r) r.innerHTML = studentAnalytics(); toast(\'Progress Refreshed\',\'Empirical telemetry updated\',\'good\'); })">' + icon('refresh') + ' Refresh</button>'
    )}

    <!-- OVERALL METRICS -->
    <div class="grid g-4 mb-6">
      ${statBlock('Questions Solved', `${totalAttempts}`, isZero ? 'No attempts yet' : `${correctAttempts} correct`, 'target', totalAttempts > 0 ? 'up' : 'down')}
      ${statBlock('Overall Accuracy', isZero ? '--' : `${accuracy.toFixed(1)}%`, isZero ? 'Unassessed' : `${correctAttempts} of ${totalAttempts} answered correctly`, 'chart', accuracy >= 70 ? 'up' : 'down')}
      ${statBlock('Syllabus Coverage', `${topicsStudied} / ${totalTopics}`, isZero ? `0 of ${totalTopics} topics studied` : `${topicsStudied} of ${totalTopics} supported topics studied (${Math.round((topicsStudied / totalTopics) * 100)}%)`, 'book', 'up')}
      <div class="stat-card">
        <div class="stat-l">Learning Trend</div>
        <div class="stat-v" style="display:flex;align-items:center;gap:8px;font-size:18px;margin-top:6px">
          ${trendBadge}
        </div>
        <div class="stat-s tiny muted" style="margin-top:4px">
          ${p?.overall.recent_activity_at ? `Last active: ${new Date(p.overall.recent_activity_at).toLocaleDateString()}` : (p?.overall.subject_name || 'GSEB Std 10 Science')}
        </div>
      </div>
    </div>

    <!-- MASTERY DISTRIBUTION -->
    <div class="card pad mb-6">
      <div class="flex-b mb-2" style="align-items:center">
        <div>
          <h3 style="font-size:15px;font-weight:700;margin:0">Syllabus Mastery Distribution</h3>
          <p class="tiny muted" style="margin-top:2px">4-tier empirical mastery model for ${p?.overall.subject_name || 'Science & Technology'} (GSEB Standard 10)</p>
        </div>
        <span class="badge grey">${p?.overall.subject_name ? `${p.overall.subject_name}: ` : ''}${totalTopics} Supported Topics</span>
      </div>

      <!-- Segmented Bar -->
      <div style="height:16px;border-radius:8px;overflow:hidden;background:#E2E8F0;display:flex;margin:14px 0 10px 0;box-shadow:inset 0 1px 2px rgba(0,0,0,.08)">
        ${pMastered > 0 ? `<div style="width:${pMastered}%;background:#2E9B68;title:'Mastered: ${masteryDist.mastered}'"></div>` : ''}
        ${pProficient > 0 ? `<div style="width:${pProficient}%;background:#18A6A6;title:'Proficient: ${masteryDist.proficient}'"></div>` : ''}
        ${pDeveloping > 0 ? `<div style="width:${pDeveloping}%;background:#4F46E5;title:'Developing: ${masteryDist.developing}'"></div>` : ''}
        ${pNovice > 0 ? `<div style="width:${pNovice}%;background:#D97706;title:'Novice: ${masteryDist.novice}'"></div>` : ''}
        ${pUnassessed > 0 ? `<div style="width:${pUnassessed}%;background:#94A3B8;title:'Unassessed: ${masteryDist.unassessed}'"></div>` : ''}
      </div>

      <!-- Legend -->
      <div class="flex gap-4 wrap" style="font-size:12px;margin-top:8px">
        <span style="display:flex;align-items:center;gap:6px"><span style="width:10px;height:10px;border-radius:2px;background:#2E9B68"></span>Mastered: <b>${masteryDist.mastered}</b></span>
        <span style="display:flex;align-items:center;gap:6px"><span style="width:10px;height:10px;border-radius:2px;background:#18A6A6"></span>Proficient: <b>${masteryDist.proficient}</b></span>
        <span style="display:flex;align-items:center;gap:6px"><span style="width:10px;height:10px;border-radius:2px;background:#4F46E5"></span>Developing: <b>${masteryDist.developing}</b></span>
        <span style="display:flex;align-items:center;gap:6px"><span style="width:10px;height:10px;border-radius:2px;background:#D97706"></span>Novice: <b>${masteryDist.novice}</b></span>
        <span style="display:flex;align-items:center;gap:6px"><span style="width:10px;height:10px;border-radius:2px;background:#94A3B8"></span>Unassessed: <b>${masteryDist.unassessed}</b></span>
      </div>
    </div>

    <!-- STRENGTHS & WEAKNESSES -->
    <div class="grid g-3 mb-6">
      <!-- Strengths -->
      <div class="card pad">
        <div class="card-h mb-3" style="padding:0;border:none">
          <h3 style="font-size:14px;color:var(--green);display:flex;align-items:center;gap:6px">
            ${icon('check', 'ic-sm')} Strengths (${sw.strengths.length})
          </h3>
        </div>
        ${sw.strengths.length === 0 ? `
          <div class="tiny muted" style="padding:14px 0">
            ${isZero ? 'No topics assessed yet. Complete practice sessions to discover your strengths.' : 'Achieve ≥ 70% accuracy on active topics to promote them into Strengths.'}
          </div>
        ` : `
          <ul style="list-style:none;padding:0;margin:0">
            ${sw.strengths.map(t => `
              <li class="flex-b items-center" style="padding:8px 0;border-bottom:1px solid var(--border-2);font-size:12.5px">
                <div>
                  <b>${t.topic_title}</b>
                  <div class="tiny muted">${t.subject_name} · ${t.correct_attempts}/${t.total_attempts} correct</div>
                </div>
                <span class="badge green">${t.accuracy.toFixed(0)}%</span>
              </li>
            `).join('')}
          </ul>
        `}
      </div>

      <!-- Developing -->
      <div class="card pad">
        <div class="card-h mb-3" style="padding:0;border:none">
          <h3 style="font-size:14px;color:var(--indigo, #4F46E5);display:flex;align-items:center;gap:6px">
            ${icon('clock', 'ic-sm')} Developing (${sw.developing.length})
          </h3>
        </div>
        ${sw.developing.length === 0 ? `
          <div class="tiny muted" style="padding:14px 0">
            ${isZero ? 'Baseline stage. Practicing topics will move them into the developing tier.' : 'No topics currently in developing tier.'}
          </div>
        ` : `
          <ul style="list-style:none;padding:0;margin:0">
            ${sw.developing.map(t => `
              <li class="flex-b items-center" style="padding:8px 0;border-bottom:1px solid var(--border-2);font-size:12.5px">
                <div>
                  <b>${t.topic_title}</b>
                  <div class="tiny muted">${t.subject_name} · ${t.accuracy.toFixed(0)}% acc</div>
                </div>
                <button class="btn btn-xs btn-outline" onclick="loadAdaptivePractice('${t.topic_id}')">Practice</button>
              </li>
            `).join('')}
          </ul>
        `}
      </div>

      <!-- Weaknesses -->
      <div class="card pad">
        <div class="card-h mb-3" style="padding:0;border:none">
          <h3 style="font-size:14px;color:var(--coral);display:flex;align-items:center;gap:6px">
            ${icon('alert', 'ic-sm')} Weak Areas (${sw.weaknesses.length})
          </h3>
        </div>
        ${sw.weaknesses.length === 0 ? `
          <div class="tiny muted" style="padding:14px 0">
            ${isZero ? 'Clean slate. Topics with accuracy < 50% or high forgetting risk will appear here.' : '✨ No weak areas detected! Keep up the consistent work.'}
          </div>
        ` : `
          <ul style="list-style:none;padding:0;margin:0">
            ${sw.weaknesses.map(t => `
              <li class="flex-b items-center" style="padding:8px 0;border-bottom:1px solid var(--border-2);font-size:12.5px">
                <div>
                  <b style="color:var(--coral)">${t.topic_title}</b>
                  <div class="tiny muted">${t.accuracy.toFixed(0)}% acc · ${t.retention_risk} risk</div>
                </div>
                <button class="btn btn-xs btn-primary" onclick="loadAdaptivePractice('${t.topic_id}')">Remediate</button>
              </li>
            `).join('')}
          </ul>
        `}
      </div>
    </div>

    <!-- TOPIC-WISE BREAKDOWN TABLE -->
    <div class="card mb-6">
      <div class="card-h flex-b items-center">
        <div>
          <h3>Curriculum Topic Performance</h3>
          <p class="tiny muted">GSEB Standard 10 curriculum breakdown with adaptive recommendations</p>
        </div>
        <span class="badge grey">${topics.length} Curriculum Units</span>
      </div>
      <div style="overflow-x:auto">
        <table class="tbl" style="width:100%">
          <thead>
            <tr>
              <th>Topic</th>
              <th>Attempts</th>
              <th style="min-width:140px">Accuracy</th>
              <th>Mastery</th>
              <th>Trend</th>
              <th>Risk</th>
              <th>Recommended Next</th>
              <th>Action</th>
            </tr>
          </thead>
          <tbody>
            ${topics.length === 0 ? `
              <tr><td colspan="8" class="text-center muted py-4">No curriculum topics registered.</td></tr>
            ` : topics.map(t => {
              const accColor = t.total_attempts === 0 ? 'grey' : t.accuracy >= 70 ? 'green' : t.accuracy >= 50 ? 'indigo' : 'coral';
              const masteryBadge = t.mastery_level === 'MASTERED'
                ? '<span class="badge green">Mastered</span>'
                : t.mastery_level === 'PROFICIENT'
                ? '<span class="badge teal">Proficient</span>'
                : t.mastery_level === 'DEVELOPING'
                ? '<span class="badge indigo">Developing</span>'
                : t.mastery_level === 'NOVICE'
                ? '<span class="badge amber">Novice</span>'
                : '<span class="badge grey">Unassessed</span>';

              const riskBadge = t.retention_risk === 'HIGH'
                ? '<span class="badge coral">High</span>'
                : t.retention_risk === 'MODERATE'
                ? '<span class="badge amber">Moderate</span>'
                : t.retention_risk === 'LOW'
                ? '<span class="badge green">Low</span>'
                : '<span class="badge grey">--</span>';

              const trendIcon = t.trend === 'IMPROVING'
                ? '<span style="color:var(--green)">↑ Improving</span>'
                : t.trend === 'DECLINING'
                ? '<span style="color:var(--coral)">↓ Declining</span>'
                : t.trend === 'STABLE'
                ? '<span style="color:var(--teal)">→ Stable</span>'
                : '<span class="muted">--</span>';

              return `
                <tr>
                  <td>
                    <div style="font-weight:600;font-size:13px">${t.topic_title}</div>
                    <div class="tiny muted">${t.subject_name}</div>
                  </td>
                  <td style="font-size:12.5px">${t.total_attempts > 0 ? `${t.correct_attempts} / ${t.total_attempts}` : '<span class="muted">0</span>'}</td>
                  <td>
                    <div class="flex gap-2 items-center" style="width:130px">
                      ${progressBar(t.total_attempts > 0 ? t.accuracy : 0, accColor)}
                      <b style="font-size:11.5px">${t.total_attempts > 0 ? `${t.accuracy.toFixed(0)}%` : '--'}</b>
                    </div>
                  </td>
                  <td>${masteryBadge}</td>
                  <td style="font-size:12px">${trendIcon}</td>
                  <td>${riskBadge}</td>
                  <td>
                    <div style="font-size:11.5px;font-weight:600">${t.recommended_difficulty}</div>
                    <div class="tiny muted">${t.recommended_action.replace(/_/g, ' ')}</div>
                  </td>
                  <td>
                    <button class="btn btn-xs btn-primary" onclick="loadAdaptivePractice('${t.topic_id}')">Practice</button>
                  </td>
                </tr>
              `;
            }).join('')}
          </tbody>
        </table>
      </div>
    </div>

    <!-- LEARNING JOURNEY (CHRONOLOGICAL EVENT STREAM) -->
    <div class="card pad">
      <div class="card-h mb-3 flex-b items-center" style="padding:0;border:none">
        <div>
          <h3>Chronological Learning Journey</h3>
          <p class="tiny muted">Real-time learning event log recorded on-device</p>
        </div>
        <span class="badge teal">${journey.length} Recent Events</span>
      </div>

      ${journey.length === 0 ? `
        <div style="padding:32px 16px;text-align:center;color:var(--text-3)">
          <div style="font-size:28px;margin-bottom:6px">🧭</div>
          <div style="font-weight:600;font-size:14px;color:var(--text-2);margin-bottom:4px">No Learning Events Recorded Yet</div>
          <p class="tiny muted" style="max-width:380px;margin:0 auto 12px auto">
            As you practice and submit curriculum questions, your learning events and response times will stream here chronologically.
          </p>
          <button class="btn btn-sm btn-primary" onclick="loadAdaptivePractice()">Start Practice Check</button>
        </div>
      ` : `
        <div class="timeline" style="display:flex;flex-direction:column;gap:12px;margin-top:12px">
          ${journey.map(e => {
            const isCorrect = e.correctness === true;
            const isWrong = e.correctness === false;
            const iconBg = isCorrect ? '#E6F4EA' : isWrong ? '#FCE8E6' : '#EFF6FF';
            const iconColor = isCorrect ? '#137333' : isWrong ? '#C5221F' : '#1D4ED8';
            const iconSymbol = isCorrect ? '✓' : isWrong ? '✗' : 'ℹ';
            const timeStr = new Date(e.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) + ' · ' + new Date(e.timestamp).toLocaleDateString([], { month: 'short', day: 'numeric' });

            return `
              <div class="flex gap-3 items-center" style="padding:10px 14px;border-radius:10px;background:var(--bg-2, #F8FAFC);border:1px solid var(--border-2)">
                <div style="width:32px;height:32px;border-radius:50%;background:${iconBg};color:${iconColor};display:flex;align-items:center;justify-content:center;font-weight:800;font-size:14px;flex-shrink:0">
                  ${iconSymbol}
                </div>
                <div style="flex:1;min-width:0">
                  <div class="flex-b items-center">
                    <div style="font-weight:700;font-size:13px">${e.topic_title}</div>
                    <span class="tiny muted">${timeStr}</span>
                  </div>
                  <div class="flex gap-2 items-center wrap tiny muted" style="margin-top:2px">
                    <span class="badge ${isCorrect ? 'green' : isWrong ? 'coral' : 'grey'}" style="font-size:10px;padding:1px 6px">
                      ${isCorrect ? 'Correct' : isWrong ? 'Incorrect' : 'Interacted'}
                    </span>
                    <span>${e.event_type}</span>
                    ${e.difficulty ? `<span>· Tier: <b>${e.difficulty}</b></span>` : ''}
                    ${e.response_time_ms ? `<span>· Time: <b>${(e.response_time_ms / 1000).toFixed(1)}s</b></span>` : ''}
                  </div>
                </div>
              </div>
            `;
          }).join('')}
        </div>
      `}
    </div>

  </div>`;
}

/* ---------- Weak Areas ---------- */
export function studentWeak(): string {
  const p = progressState.data;
  if (!p && !progressState.loading) {
    loadStudentProgress().then(() => {
      if (typeof window !== 'undefined' && window.location.hash.includes('student/weak')) {
        const root = document.getElementById('main');
        if (root) root.innerHTML = studentWeak();
      }
    });
  }

  const weakTopics = p?.strengths_weaknesses.weaknesses ?? [];

  return `
  <div class="page">
    ${pageHead('Weak Areas & Remediation', 'Topics flagged for active reinforcement', 'Ranked by empirical accuracy, forgetting risk and conceptual difficulty.')}

    ${weakTopics.length === 0 ? `
      <div class="card pad-lg mb-6" style="padding:48px 24px;text-align:center;color:var(--text-3)">
        <div style="font-size:36px;margin-bottom:8px">✨</div>
        <h3 class="h3 mb-2">No Weak Areas Identified</h3>
        <p style="font-size:13.5px;max-width:480px;margin:0 auto 18px auto;line-height:1.5">
          You have a clean slate with no detected weak areas. As you complete adaptive practice, any topic falling below 50% accuracy or showing high forgetting risk will be queued here for structured remediation.
        </p>
        <button class="btn btn-primary" onclick="loadAdaptivePractice()">${icon('play')} Start Practice Session</button>
      </div>
    ` : `
    ${aiInsight('Priority Remediation Focus', 'EduNavika on-device AI has flagged topics requiring conceptual strengthening based on your latest practice attempts.', 'Start Targeted Practice', `loadAdaptivePractice('${weakTopics[0].topic_id}')`)}

    <div class="card mt-5">
      <div class="card-h"><h3>Topics Requiring Remediation (${weakTopics.length})</h3></div>
      <table class="tbl">
        <thead><tr><th>Topic</th><th>Subject</th><th>Accuracy</th><th>Risk</th><th>Recommended Difficulty</th><th></th></tr></thead>
        <tbody>
          ${weakTopics.map(t => `
            <tr>
              <td class="nm"><b>${t.topic_title}</b></td>
              <td class="muted">${t.subject_name}</td>
              <td><div class="flex gap-2" style="width:130px">${progressBar(t.accuracy, 'coral')}<b style="font-size:12px">${t.accuracy.toFixed(0)}%</b></div></td>
              <td><span class="badge coral">${t.retention_risk}</span></td>
              <td class="muted">${t.recommended_difficulty}</td>
              <td class="right"><button class="btn btn-sm btn-primary" onclick="loadAdaptivePractice('${t.topic_id}')">Remediate</button></td>
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

    <div class="sec-head"><div><h2>${icon('calendar')} Upcoming Checkpoints</h2><p>Adaptive milestones & practice goals</p></div></div>
    <div class="grid g-3 mb-6">
      ${UPCOMING_ASSESSMENTS.length === 0 ? `
        <div class="card pad-lg" style="grid-column:1/-1;text-align:center;color:var(--text-3);padding:36px 24px">
          No upcoming milestones scheduled. Use Practice to test your knowledge anytime.
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
        <div class="ai-head"><div class="ai-mark">${icon('sparkles')}</div><b>EduNavika Insight</b></div>
        <div class="ai-body">Your accuracy on <b>applied questions</b> is 32% lower than on conceptual ones. Recommended: 15 practice questions in this format before your next assessment.</div>
      </div>
    </div>
    <div class="modal-f">
      <button class="btn" onclick="closeOverlay()">Close</button>
      <button class="btn btn-primary" onclick="closeOverlay();navigate('student/revision')">${icon('refresh')} Add to revision plan</button>
    </div>`, { width: 'wide' });
}

/* ---------- Curriculum Hierarchy & Study Materials State ---------- */
let hierarchyState: {
  data?: CurriculumHierarchyResponse;
  loading: boolean;
  selectedSubjectId?: string;
} = {
  loading: false,
};

export async function loadCurriculumHierarchy(force: boolean = false): Promise<void> {
  if (hierarchyState.loading) return;
  if (hierarchyState.data && !force) return;
  hierarchyState.loading = true;
  try {
    const data = await curriculumService.getHierarchy(10);
    if (data) {
      hierarchyState.data = data;
      if (!hierarchyState.selectedSubjectId && data.subjects.length > 0) {
        const sci = data.subjects.find(s => s.name.toLowerCase().includes('science'));
        hierarchyState.selectedSubjectId = sci ? sci.id : data.subjects[0].id;
      }
    }
  } catch (err) {
    console.debug('Failed to load curriculum hierarchy:', err);
  } finally {
    hierarchyState.loading = false;
  }
}

export function selectCurriculumSubject(subjectId: string): void {
  hierarchyState.selectedSubjectId = subjectId;
  const root = document.getElementById('main');
  if (root) {
    root.innerHTML = studentMaterials();
  }
}

export async function openTopicContentReader(topicId: string, topicTitle: string, subjectName: string): Promise<void> {
  openModal(`
    <div style="padding:24px;text-align:center">
      <div style="font-size:28px;margin-bottom:8px">📖</div>
      <div style="font-weight:700;font-size:15px">Loading Local Textbook Passages...</div>
      <div class="tiny" style="color:var(--text-3);margin-top:4px">Retrieving verified content chunks from on-device store</div>
    </div>
  `, { width: 'wide' });

  try {
    const chunks = await curriculumService.getTopicContent(topicId);
    if (!chunks || chunks.length === 0) {
      openModal(`
        <div style="padding:12px">
          <div class="flex-b items-center mb-3">
            <span class="badge grey">${subjectName}</span>
            <span class="badge amber">Offline Queue</span>
          </div>
          <h3 style="font-size:18px;font-weight:800;color:var(--text);margin-bottom:8px">${topicTitle}</h3>
          <div style="background:var(--surface-2);border:1px dashed var(--border-2);border-radius:12px;padding:24px;text-align:center;margin:16px 0">
            <div style="font-size:32px;margin-bottom:8px">📚</div>
            <div style="font-weight:700;color:var(--text);font-size:14px;margin-bottom:4px">Not Included in Local Textbook Index</div>
            <p style="font-size:12.5px;color:var(--text-3);max-width:440px;margin:0 auto;line-height:1.5">
              This topic is not currently included in the verified offline curriculum available on this device.
            </p>
          </div>
          <div class="flex-b items-center pt-3" style="border-top:1px solid var(--border-2)">
            <button class="btn btn-outline" onclick="closeOverlay()">Close</button>
            <button class="btn btn-primary" onclick="closeOverlay();loadAdaptivePractice('${topicId}')">Try Diagnostic Practice</button>
          </div>
        </div>
      `, { width: 'wide' });
      return;
    }

    const firstChunk = chunks[0];
    const sourceDoc = firstChunk.source_document || 'NCERT Standard 10';
    const sourcePage = firstChunk.source_page || '—';

    openModal(`
      <div style="padding:12px">
        <div class="flex-b items-center mb-2">
          <div class="flex items-center gap-2">
            <span class="badge indigo">${subjectName}</span>
            <span class="badge green">✓ Verified & Available Locally</span>
          </div>
          <span class="tiny" style="color:var(--text-3)">${chunks.length} Passages Indexed</span>
        </div>
        <h3 style="font-size:18px;font-weight:800;color:var(--text);margin-bottom:4px">${topicTitle}</h3>
        <div class="tiny mb-3" style="color:var(--text-3)">
          📖 <b>Source:</b> ${sourceDoc} · <b>Page:</b> ${sourcePage} · <b>Framework:</b> GSEB / NCERT
        </div>

        <div style="max-height:420px;overflow-y:auto;padding-right:8px;display:flex;flex-direction:column;gap:12px">
          ${chunks.map((c: any, idx: number) => `
            <div style="background:var(--surface-2);border:1px solid var(--border-2);border-radius:10px;padding:14px">
              <div class="flex-b items-center mb-2">
                <span style="font-size:11px;font-weight:700;color:var(--indigo);text-transform:uppercase">Passage ${idx + 1}: ${c.title || 'Curriculum Content'}</span>
                ${c.source_page ? `<span class="tiny" style="color:var(--text-3)">Page ${c.source_page}</span>` : ''}
              </div>
              <div style="font-size:13px;line-height:1.65;color:var(--text);white-space:pre-wrap;font-family:var(--font-sans,inherit)">${c.content_text}</div>
            </div>
          `).join('')}
        </div>

        <div class="flex-b items-center pt-3 mt-3" style="border-top:1px solid var(--border-2)">
          <button class="btn btn-outline" onclick="closeOverlay()">Close</button>
          <div class="flex gap-2">
            <button class="btn btn-teal" onclick="closeOverlay();openAIPanel();">${icon('sparkles')} Ask AI About This</button>
            <button class="btn btn-primary" onclick="closeOverlay();loadAdaptivePractice('${topicId}')">${icon('play')} Practice Now</button>
          </div>
        </div>
      </div>
    `, { width: 'wide' });
  } catch (err) {
    console.debug('Error opening topic content:', err);
    closeOverlay();
    toast('Error loading content', 'Could not retrieve local textbook passage', 'bad');
  }
}

/* ---------- Study Materials & Curriculum Explorer ---------- */
export function studentMaterials(): string {
  if (!hierarchyState.data && !hierarchyState.loading) {
    loadCurriculumHierarchy().then(() => {
      if (typeof window !== 'undefined' && window.location.hash.includes('student/materials')) {
        const root = document.getElementById('main');
        if (root) {
          root.innerHTML = studentMaterials();
        }
      }
    });
  }

  const hier = hierarchyState.data;
  const subjects = (hier?.subjects || []).filter(s =>
    s.name.includes('Science') || s.name.includes('Mathematics')
  );

  const activeSubjId = hierarchyState.selectedSubjectId || subjects[0]?.id;
  const activeSubj = subjects.find(s => s.id === activeSubjId) || subjects[0];

  return `
  <div class="page">
    ${pageHead(
      'Your Learning Resources',
      'Standard 10 Curriculum & Local Resources',
      'Standard 10 curriculum and verified learning materials are available directly on this device without constant internet connectivity.',
      '<button class="btn btn-primary" onclick="loadAdaptivePractice()">' + icon('play') + ' Adaptive Practice</button>'
    )}

    <!-- ON-DEVICE PROVISIONING NOTICE -->
    <div class="card pad-lg mb-6" style="background:linear-gradient(135deg, #1E293B, #0F172A);color:#fff;border-radius:16px;border:1px solid rgba(255,255,255,.1);box-shadow:0 8px 30px rgba(15,23,42,.35)">
      <div class="flex-b items-center mb-2">
        <span style="font-size:11px;font-weight:800;color:#38BDF8;text-transform:uppercase;letter-spacing:.06em">⚡ On-Device Knowledge Store</span>
        <span class="badge" style="background:rgba(74,222,128,.15);color:#4ADE80;border:1px solid rgba(74,222,128,.3)">100% Offline Accessible</span>
      </div>
      <h3 style="font-size:18px;font-weight:800;color:#F8FAFC;margin-bottom:6px">Standard 10 GSEB / NCERT Curriculum</h3>
      <p style="font-size:13px;color:#94A3B8;line-height:1.5;margin:0">
        All textbook source passages, BM25 semantic indices, and verified canonical question banks are pre-loaded locally on this device.
        No school uploads, external LMS accounts, or internet connections required.
      </p>
    </div>

    <!-- SUBJECT SELECTOR TABS -->
    <div class="flex gap-3 mb-5 wrap">
      ${subjects.map(s => `
        <button class="btn ${s.id === activeSubj?.id ? 'btn-primary' : 'btn-outline'}" style="padding:10px 18px;font-size:13.5px;font-weight:700" onclick="selectCurriculumSubject('${s.id}')">
          ${s.name.includes('Science') ? '🔬' : '📐'} ${s.name} (${s.total_chapters} Chapters)
        </button>
      `).join('')}
    </div>

    ${!activeSubj ? `
      <div class="card pad-lg" style="text-align:center;color:var(--text-3)">
        <div style="font-size:32px;margin-bottom:8px">📚</div>
        <b>Loading Standard 10 curriculum hierarchy...</b>
      </div>
    ` : `
      <div class="sec-head">
        <div>
          <h2>${activeSubj.name.includes('Science') ? '🔬' : '📐'} ${activeSubj.name} (${activeSubj.total_chapters} Chapters)</h2>
          <p>Verified syllabus structure for GSEB Standard 10.</p>
        </div>
      </div>

      <div style="display:flex;flex-direction:column;gap:16px" class="mb-6">
        ${activeSubj.chapters.map(ch => `
          <div class="card" style="border-radius:14px;border:1px solid var(--border)">
            <div class="card-h" style="background:var(--surface-2);border-bottom:1px solid var(--border-2);padding:14px 20px">
              <div class="flex items-center gap-3">
                <span class="badge indigo" style="font-size:12px;font-weight:800">Chapter ${ch.chapter_number}</span>
                <h3 style="font-size:15px;font-weight:700;margin:0">${ch.title}</h3>
              </div>
              <span class="tiny" style="color:var(--text-3)">${ch.topics.length} Topics</span>
            </div>

            <div class="card-b" style="padding:16px 20px;display:flex;flex-direction:column;gap:12px">
              ${ch.topics.map(tp => `
                <div style="background:var(--surface);border:1px solid var(--border-2);border-radius:10px;padding:14px;display:flex;align-items:center;justify-content:space-between;gap:16px;flex-wrap:wrap">
                  <div style="flex:1;min-width:240px">
                    <div class="flex items-center gap-2 mb-1">
                      <span style="font-size:14px;font-weight:700;color:var(--text)">${tp.title}</span>
                      ${tp.content_available
                        ? '<span class="badge green" style="font-size:10px">✓ Verified & Available Locally</span>'
                        : '<span class="badge grey" style="font-size:10px">Offline Queue</span>'}
                    </div>
                    ${tp.content_available ? `
                      <div class="tiny" style="color:var(--text-3)">
                        📖 <b>Source:</b> ${tp.source_document || 'NCERT Standard 10'} · <b>Page:</b> ${tp.source_page || '—'} · <b>Chunks:</b> ${tp.content_count}
                      </div>
                    ` : `
                      <div class="tiny" style="color:var(--text-3)">
                        This topic is not currently included in the verified offline curriculum available on this device.
                      </div>
                    `}
                  </div>

                  <div class="flex gap-2 items-center">
                    ${tp.content_available ? `
                      <button class="btn btn-sm btn-outline" onclick="openTopicContentReader('${tp.id}', '${tp.title.replace(/'/g, "\\'")}', '${activeSubj.name.replace(/'/g, "\\'")}')">
                        📖 Read Passage
                      </button>
                    ` : ''}
                    <button class="btn btn-sm btn-primary" onclick="loadAdaptivePractice('${tp.id}')">
                      ${icon('play')} Practice Now
                    </button>
                  </div>
                </div>
              `).join('')}
            </div>
          </div>
        `).join('')}
      </div>
    `}
  </div>`;
}

/* ---------- Achievements & Badges View (Phase 17/18A) ---------- */
export function studentAchievements(): string {
  if (!gamificationState.data && !gamificationState.loading) {
    loadStudentGamification().then(() => {
      if (typeof window !== 'undefined' && window.location.hash.includes('student/achievements')) {
        const root = document.getElementById('main');
        if (root) {
          root.innerHTML = studentAchievements();
        }
      }
    });
  }

  const g = gamificationState.data;
  const level = g?.level ?? 1;
  const levelTitle = g?.level_title ?? 'Novice Explorer';
  const totalXp = g?.total_xp ?? 0;
  const xpTowardsNext = g?.xp_towards_next_level ?? 0;
  const xpRequired = g?.xp_required_for_next_level ?? 100;
  const xpPercent = Math.min(100, Math.max(0, g?.level_progress_percentage ?? 0));
  const currentStreak = g?.current_streak ?? 0;
  const longestStreak = g?.longest_streak ?? 0;
  const dailyCompleted = g?.daily_goal?.completed ?? 0;
  const dailyTarget = g?.daily_goal?.target ?? 3;
  const dailyGoalDone = g?.daily_goal?.is_completed ?? false;
  const dailyPercent = Math.min(100, Math.round(((dailyCompleted / Math.max(1, dailyTarget)) * 100)));
  const allBadges = [...(g?.unlocked_badges || []), ...(g?.locked_badges || [])];

  return `
  <div class="page">
    ${pageHead(
      'Achievements & Learning Badges',
      'Deterministic on-device learning gamification',
      'Earn XP and badges exclusively from genuine learning activities, practice completion, and retention revisions — 100% private on this device.',
      '<button class="btn btn-primary" onclick="loadAdaptivePractice()">' + icon('play') + ' Practice to Earn XP</button>'
    )}

    <!-- STATS ROW: LEVEL & XP, STREAK, DAILY GOAL -->
    <div class="grid g-3 mb-6" style="gap:16px">
      <!-- Level & XP -->
      <div class="card pad" style="background:var(--surface);border:1px solid var(--border);border-radius:14px;display:flex;flex-direction:column;justify-content:space-between">
        <div>
          <div class="flex-b items-center mb-2">
            <span style="font-size:11px;font-weight:700;color:var(--text-3);text-transform:uppercase">Level & Experience</span>
            <span class="badge indigo" style="font-weight:800;font-size:12px">${totalXp} XP</span>
          </div>
          <div style="font-size:20px;font-weight:800;color:var(--text);margin-bottom:6px">
            Level ${level}: ${levelTitle}
          </div>
          <p style="font-size:12px;color:var(--text-3);margin:0 0 12px 0">
            ${level >= 5 ? 'Master level achieved!' : `${Math.max(0, xpRequired - xpTowardsNext)} XP needed to reach Level ${level + 1}`}
          </p>
        </div>
        <div>
          <div class="flex-b items-center tiny mb-1" style="color:var(--text-3)">
            <span>${xpTowardsNext} / ${xpRequired} XP to next level</span>
            <b style="color:var(--indigo)">${xpPercent}%</b>
          </div>
          ${progressBar(xpPercent, 'indigo')}
        </div>
      </div>

      <!-- Streak -->
      <div class="card pad" style="background:var(--surface);border:1px solid var(--border);border-radius:14px;display:flex;flex-direction:column;justify-content:space-between">
        <div>
          <div class="flex-b items-center mb-2">
            <span style="font-size:11px;font-weight:700;color:var(--text-3);text-transform:uppercase">Learning Habit Streak</span>
            <span style="font-size:18px">${currentStreak > 0 ? '🔥' : '🌱'}</span>
          </div>
          <div style="font-size:24px;font-weight:800;color:var(--text);line-height:1.2;margin-bottom:4px">
            ${currentStreak} <span style="font-size:14px;font-weight:600;color:var(--text-2)">days streak</span>
          </div>
          <p style="font-size:12px;color:var(--text-3);margin:0">
            Consecutive calendar days with at least one completed learning event.
          </p>
        </div>
        <div style="padding-top:12px;border-top:1px solid var(--border-2);margin-top:12px" class="flex-b items-center tiny">
          <span style="color:var(--text-3)">Longest Streak Record:</span>
          <b style="color:var(--text);font-size:13px">${longestStreak} days</b>
        </div>
      </div>

      <!-- Daily Goal -->
      <div class="card pad" style="background:var(--surface);border:1px solid var(--border);border-radius:14px;display:flex;flex-direction:column;justify-content:space-between">
        <div>
          <div class="flex-b items-center mb-2">
            <span style="font-size:11px;font-weight:700;color:var(--text-3);text-transform:uppercase">Daily Learning Goal</span>
            ${dailyGoalDone ? '<span class="badge green">✓ Complete (+25 XP)</span>' : '<span class="badge amber">In Progress</span>'}
          </div>
          <div style="font-size:24px;font-weight:800;color:var(--text);line-height:1.2;margin-bottom:4px">
            ${dailyCompleted} / ${dailyTarget} <span style="font-size:14px;font-weight:600;color:var(--text-2)">learning events</span>
          </div>
          <p style="font-size:12px;color:var(--text-3);margin:0">
            ${dailyGoalDone ? 'Daily learning objective achieved for today!' : `Complete ${dailyTarget - dailyCompleted} more learning activities today to earn bonus XP.`}
          </p>
        </div>
        <div>
          <div class="flex-b items-center tiny mb-1" style="color:var(--text-3)">
            <span>Today's Completion</span>
            <b style="color:${dailyGoalDone ? 'var(--green)' : 'var(--amber)'}">${dailyPercent}%</b>
          </div>
          ${progressBar(dailyPercent, dailyGoalDone ? 'green' : 'amber')}
        </div>
      </div>
    </div>

    <!-- BADGES SHOWCASE -->
    <div class="sec-head">
      <div>
        <h2>${icon('award')} Learning Badges</h2>
        <p>Curriculum milestones and mastery achievements unlocked through continuous study.</p>
      </div>
      <div class="right">
        <span class="badge grey">${g?.unlocked_badges?.length || 0} of ${allBadges.length} Unlocked</span>
      </div>
    </div>

    <div class="grid g-3 mb-6" style="gap:16px">
      ${allBadges.map(b => {
        const isU = b.is_unlocked;
        return `
        <div class="card pad" style="border-radius:14px;transition:transform .15s ease;display:flex;flex-direction:column;justify-content:space-between;${isU ? 'background:var(--surface);border:1.5px solid var(--indigo);box-shadow:0 4px 12px rgba(79,70,229,.08);' : 'background:var(--surface-2);border:1px dashed var(--border-2);opacity:.75;'}">
          <div>
            <div class="flex-b items-center mb-3">
              <span style="font-size:32px;line-height:1;filter:${isU ? 'none' : 'grayscale(100%)'}">${b.icon}</span>
              <span class="badge ${isU ? 'green' : 'grey'}" style="font-size:10.5px">
                ${isU ? '✓ Unlocked' : '🔒 Locked'}
              </span>
            </div>
            <h4 style="font-size:15px;font-weight:700;color:var(--text);margin-bottom:6px">${b.name}</h4>
            <p style="font-size:12.5px;color:var(--text-2);line-height:1.45;margin:0 0 12px 0">${b.description}</p>
          </div>
          <div style="padding-top:10px;border-top:1px solid var(--border-2);font-size:11.5px;color:var(--text-3)">
            ${isU ? '<b style="color:var(--green)">Earned through on-device learning</b>' : 'Complete learning actions to unlock'}
          </div>
        </div>`;
      }).join('')}
    </div>

    <!-- DETERMINISTIC XP ALLOCATION RULEBOOK -->
    <div class="card mb-6" style="border-radius:14px;overflow:hidden">
      <div class="card-h">
        <div>
          <h3>Deterministic XP Rewards Rulebook</h3>
          <div class="sub">XP is awarded exclusively for real educational effort and retention actions</div>
        </div>
        <div class="right"><span class="badge teal">100% Offline Integrity</span></div>
      </div>
      <table class="tbl">
        <thead>
          <tr>
            <th>Learning Action</th>
            <th>Trigger Condition</th>
            <th>XP Reward</th>
            <th>Pedagogical Purpose</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td><b>Complete Practice Set</b></td>
            <td>Submitting an adaptive practice attempt</td>
            <td><span class="badge indigo">+10 XP</span></td>
            <td>Rewards proactive learning engagement</td>
          </tr>
          <tr>
            <td><b>Correct Answer</b></td>
            <td>Selecting the correct response on an assessment</td>
            <td><span class="badge green">+5 XP</span></td>
            <td>Encourages accuracy and concept mastery</td>
          </tr>
          <tr>
            <td><b>Complete Scheduled Revision</b></td>
            <td>Reviewing a concept on or before its due date</td>
            <td><span class="badge teal">+15 XP</span></td>
            <td>Incentivizes combating the forgetting curve</td>
          </tr>
          <tr>
            <td><b>Improve a Weak Topic</b></td>
            <td>Transitioning a topic from Weak/Novice to higher tier</td>
            <td><span class="badge amber">+20 XP</span></td>
            <td>Celebrates perseverance and concept remediation</td>
          </tr>
          <tr>
            <td><b>Daily Learning Goal</b></td>
            <td>Completing 3 learning activities in a calendar day</td>
            <td><span class="badge coral">+25 XP</span></td>
            <td>Builds consistent daily study habit</td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- ON-DEVICE PRIVACY GUARANTEE -->
    <div class="card pad" style="background:var(--surface-2);border:1px solid var(--border-2);border-radius:14px">
      <div class="flex gap-3 items-center">
        <div style="font-size:28px">🛡️</div>
        <div style="flex:1">
          <h4 style="font-size:14px;font-weight:700;margin-bottom:2px;color:var(--text)">Private On-Device Gamification</h4>
          <p style="font-size:12.5px;color:var(--text-3);margin:0">
            All XP computations, badge evaluations, and streak dates are determined strictly by local SQLite learning events on this device.
            No cloud leaderboards, no vanity metrics, and no competitive surveillance — designed solely for student motivation and self-paced mastery.
          </p>
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
            All Standard 10 practice tasks and revision modules are self-paced and managed directly on-device in Personalized Practice and Revision Plan.
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
          No scheduled exam sessions. Offline milestones and adaptive practice checks can be started anytime.
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
    ${pageHead('Notifications', 'Your notification center', 'Everything that needs your attention — learning, revision, assessments and milestone alerts.', '<button class="btn" onclick="toast(\'All marked as read\',\'You are up to date\',\'good\')">' + icon('check') + ' Mark all read</button>')}

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
            ['Stream', 'Science & Mathematics'],
            ['Device mode', 'Offline-First On-Device'],
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
            ['Weekly goal', 'Self-paced Mastery'],
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
    ${pageHead('Settings', 'Your preferences', 'Control how EduNavika works for you.')}

    <div class="grid g-2">
      <div class="card">
        <div class="card-h"><h3>Notifications</h3></div>
        <div class="card-b">
          ${[
            ['Revision reminders', true],
            ['Assessment reminders', true],
            ['Weekly progress summary', true],
            ['New content alerts', false],
            ['Revision milestones', true],
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
          <div class="field"><label>${t('settings.language', 'Language / ભાષા / भाषा')}</label>
            <select class="input select" onchange="window.setLanguage ? window.setLanguage(this.value) : null; toast('Language updated / ભાષા બદલાઈ / भाषा अपडेट की गई','','good')">
              <option value="en" ${getLanguage() === 'en' ? 'selected' : ''}>🇬🇧 English</option>
              <option value="gu" ${getLanguage() === 'gu' ? 'selected' : ''}>🇮🇳 ગુજરાતી (Gujarati)</option>
              <option value="hi" ${getLanguage() === 'hi' ? 'selected' : ''}>🇮🇳 हिन्दी (Hindi)</option>
            </select>
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
    { q: 'What is a forgetting event?', a: 'When your performance on a topic drops meaningfully after a gap in practice — usually 15–20 days — EduNavika records a potential forgetting event and adds it to your revision plan.' },
    { q: 'How is my revision scheduled?', a: 'EduNavika AI schedules revision at the moment it will have the greatest impact — balancing knowledge health, time since last revision, and upcoming assessments.' },
    { q: 'How accurate are these predictions?', a: 'They are estimates based on evidence, not certainties. A single low score never means you have forgotten something. Multiple consistent signals over time are required.' },
    { q: 'Can I reset my progress?', a: 'Progress is stored locally on this device as your learning journey grows.' },
  ];
  return `
  <div class="page">
    ${pageHead('Help & Support', 'How can we help?', 'Answers to common questions, plus ways to reach the EduNavika team.')}

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
    <div class="modal-h" style="border-radius:0;border-bottom:1px solid var(--border)">
      <div class="ai-mark" style="width:34px;height:34px;border-radius:10px;background:var(--indigo-50);color:var(--indigo);display:grid;place-items:center">${icon('sparkles')}</div>
      <div style="flex:1">
        <div style="display:flex;align-items:center;gap:8px">
          <h3 style="font-size:15px;margin:0">EduNavika AI</h3>
          <span class="badge" style="background:var(--green-50,#E6F4EA);color:var(--green-700,#137333);font-size:10.5px;font-weight:700">● On-Device Ready</span>
        </div>
        <div class="sub" style="font-size:11.5px;color:var(--text-3);margin-top:2px">Private On-Device Assistant · Grounded in Standard 10 GSEB Syllabus</div>
      </div>
      <button class="btn btn-sm btn-icon" onclick="closeOverlay()">${icon('x')}</button>
    </div>
    <div style="flex:1;padding:20px 22px;display:flex;flex-direction:column;gap:16px;overflow-y:auto" id="aiChat">
      <div class="msg" style="display:flex;gap:10px">
        <div class="ai-mark" style="width:28px;height:28px;border-radius:8px;background:var(--teal-50);color:var(--teal-600);display:grid;place-items:center;flex:0 0 auto">${icon('sparkles', 'ic-sm')}</div>
        <div class="bubble" style="background:var(--teal-50);border:1px solid rgba(24,166,166,.2);padding:11px 14px;border-radius:12px;font-size:13px;line-height:1.55">
          Hello ${getCurrentUser().full_name?.split(' ')[0] || 'Student'} 👋 I am your <b>on-device learning assistant</b>. I run locally on this machine to explain concepts step-by-step using your official <b>GSEB Standard 10 textbooks</b>. What concept would you like to explore?
        </div>
      </div>
      <div style="font-size:11.5px;color:var(--text-3);text-transform:uppercase;letter-spacing:.05em;font-weight:700;margin-top:4px">Demo Prompts</div>
      <div style="display:flex;flex-direction:column;gap:8px">
        ${[
          'I don\'t understand how to balance chemical equations',
          'Explain why mass must be conserved in reactions',
          'What are the 4 indicators that a chemical reaction took place?',
          'What should I practice next based on my knowledge model?'
        ].map(q => `
          <button class="qa-tile" onclick="sendAI('${q.replace(/'/g, "\\'")}')">
            <div class="qi" style="width:28px;height:28px;background:var(--teal-50);color:var(--teal-600);display:grid;place-items:center">${icon('sparkles', 'ic-sm')}</div>
            <div><b style="font-size:12.5px">${q}</b></div>
          </button>`).join('')}
      </div>
    </div>
    <div style="padding:16px 22px;border-top:1px solid var(--border);display:flex;gap:10px">
      <input class="input" id="aiInput" placeholder="Ask EduNavika AI anything from your syllabus…" onkeydown="if(event.key==='Enter')sendAI()">
      <button class="btn btn-primary btn-icon" onclick="sendAI()">${icon('send')}</button>
    </div>`);
}

export async function sendAI(q?: string): Promise<void> {
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
  typing.innerHTML = `<div style="display:flex;gap:10px"><div class="ai-mark" style="width:28px;height:28px;flex:0 0 auto">${icon('sparkles', 'ic-sm')}</div><div style="background:var(--bg);padding:11px 14px;border-radius:12px;font-size:13px">Thinking locally…</div></div>`;
  chat.appendChild(typing);
  chat.scrollTop = chat.scrollHeight;

  try {
    const user = getCurrentUser();
    const studentId = user.id || 'e09699dd-0c64-44cc-82ef-ab41a832e072';
    // Request explanation from local on-device explanation service
    const expRes = await explanationService.getExplanation({
      student_id: studentId,
      topic_id: '5a321a44-bc06-4db4-a50f-5e53f913b612', // Chemical Reactions and Equations
      query: msg,
      top_k: 3,
    });

    typing.remove();

    if (expRes) {
      const isLocalLLM = expRes.generation_mode === 'LOCAL_LLM';
      const badgeHtml = isLocalLLM
        ? `<div style="display:flex;align-items:center;gap:6px;margin-bottom:8px">
             <span class="badge" style="background:#0F172A;color:#38BDF8;font-size:11px;font-weight:700;padding:3px 8px;border-radius:6px;border:1px solid #1E293B">⚡ ON-DEVICE AI</span>
             <span class="badge" style="background:var(--green-50,#E6F4EA);color:var(--green-700,#137333);font-size:11px;font-weight:700">${expRes.model_name || 'Qwen2.5-0.5B-Instruct'}${expRes.inference_time_ms ? ` · ${expRes.inference_time_ms}ms` : ''}</span>
           </div>`
        : `<div style="display:flex;align-items:center;gap:6px;margin-bottom:8px">
             <span class="badge" style="background:var(--amber-50,#FEF7E0);color:var(--amber-800,#B06000);font-size:11px;font-weight:700">🔒 OFFLINE FALLBACK</span>
             <span class="badge" style="background:var(--bg,#F1F5F9);color:var(--text-2);font-size:11px;font-weight:600">Curriculum Grounding Engine</span>
           </div>`;

      const sourcesList = expRes.sources && expRes.sources.length > 0
        ? expRes.sources.map(s => `STD-10 Science (Page ${s.source_page || 'N/A'})`).join(' · ')
        : 'STD-10 Science Chapter 1';

      const sourcesHtml = `
        <div style="margin-top:10px;padding-top:10px;border-top:1px dashed rgba(24,166,166,.3);font-size:11.5px;color:var(--text-3);display:flex;align-items:center;gap:6px">
          <span style="font-weight:700;color:var(--teal-700,#007B83)">📖 Curriculum Grounding:</span>
          <span>${sourcesList}</span>
        </div>`;

      const struct = expRes.structured_explanation;
      const bodyHtml = struct
        ? `<div style="font-size:14px;font-weight:800;color:var(--text);margin-bottom:6px">${struct.title}</div>
           <div style="font-size:12px;color:var(--indigo-700,#3B5998);margin-bottom:8px;font-weight:600"><b>Why this explanation?</b> ${struct.why_this_matters || 'Targeted to your current knowledge profile'}</div>
           <div style="font-size:13px;line-height:1.55;margin-bottom:8px"><b>Core Concept:</b> ${struct.core_concept}</div>
           ${struct.step_by_step && struct.step_by_step.length ? `<div style="font-size:12.5px;font-weight:600;margin-bottom:2px">Step-by-Step Understanding:</div><ul style="margin:2px 0 8px 18px;padding:0;font-size:12.5px;line-height:1.5">${struct.step_by_step.map(s => `<li>${s}</li>`).join('')}</ul>` : ''}
           ${struct.common_mistake ? `<div style="font-size:12px;color:var(--coral-700,#C5221F);margin-bottom:6px;background:rgba(235,94,85,.08);padding:6px 10px;border-radius:6px"><b>Misconception to avoid:</b> ${struct.common_mistake}</div>` : ''}
           ${struct.quick_check ? `<div style="font-size:12px;color:var(--teal-700,#007B83);background:rgba(24,166,166,.08);padding:6px 10px;border-radius:6px"><b>Quick Concept Check:</b> ${struct.quick_check.question}</div>` : ''}`
        : `<div style="font-size:13px;line-height:1.6">${expRes.explanation}</div>`;

      chat.insertAdjacentHTML('beforeend', `
        <div style="display:flex;gap:10px">
          <div class="ai-mark" style="width:28px;height:28px;border-radius:8px;background:var(--teal-50);color:var(--teal-600);display:grid;place-items:center;flex:0 0 auto">${icon('sparkles', 'ic-sm')}</div>
          <div style="background:var(--teal-50);border:1px solid rgba(24,166,166,.2);padding:14px 16px;border-radius:12px;max-width:90%">
            ${badgeHtml}
            ${bodyHtml}
            ${sourcesHtml}
          </div>
        </div>`);
    } else {
      chat.insertAdjacentHTML('beforeend', `
        <div style="display:flex;gap:10px">
          <div class="ai-mark" style="width:28px;height:28px;flex:0 0 auto">${icon('sparkles', 'ic-sm')}</div>
          <div style="background:var(--teal-50);border:1px solid rgba(24,166,166,.2);padding:11px 14px;border-radius:12px;font-size:13px;line-height:1.6;max-width:86%">
            <span class="badge grey mb-2">Offline Fallback</span>
            ${aiReply(msg)}
          </div>
        </div>`);
    }
  } catch (err) {
    typing.remove();
    chat.insertAdjacentHTML('beforeend', `
      <div style="display:flex;gap:10px">
        <div class="ai-mark" style="width:28px;height:28px;flex:0 0 auto">${icon('sparkles', 'ic-sm')}</div>
        <div style="background:var(--teal-50);border:1px solid rgba(24,166,166,.2);padding:11px 14px;border-radius:12px;font-size:13px;line-height:1.6;max-width:86%">
          ${aiReply(msg)}
        </div>
      </div>`);
  }
  chat.scrollTop = chat.scrollHeight;
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

/* ---------- Adaptive Practice View (Phase 7) ---------- */
let practiceState: {
  topicId: string;
  topicTitle: string;
  loading: boolean;
  questions: any[];
  currentIndex: number;
  generationMode?: string;
  targetDifficulty?: string;
  selectedOption?: string;
  submitted: boolean;
  lastResponse?: any;
  recommendation?: any;
} = {
  topicId: '5a321a44-bc06-4db4-a50f-5e53f913b612',
  topicTitle: 'Chemical Reactions and Equations',
  loading: false,
  questions: [],
  currentIndex: 0,
  submitted: false,
};

export function studentPractice(): string {
  if (practiceState.questions.length === 0 && !practiceState.loading) {
    loadAdaptivePractice();
    return `
      <div class="page">
        <div class="card pad" style="text-align:center;padding:48px 24px">
          <div style="font-size:28px;margin-bottom:12px">⚡</div>
          <h3>Loading Adaptive Practice…</h3>
          <p class="sub" style="margin-top:6px">Analyzing your empirical mastery and generating curriculum-grounded questions.</p>
        </div>
      </div>`;
  }

  if (practiceState.loading) {
    return `
      <div class="page">
        <div class="card pad" style="text-align:center;padding:48px 24px">
          <div style="font-size:28px;margin-bottom:12px">⚙️</div>
          <h3>Generating Practice Set…</h3>
          <p class="sub" style="margin-top:6px">Evaluating curriculum concepts for ${practiceState.topicTitle}…</p>
        </div>
      </div>`;
  }

  const q = practiceState.questions[practiceState.currentIndex];
  if (!q) {
    return `
      <div class="page">
        <div class="card pad" style="text-align:center;padding:40px 20px">
          <h3>Practice Set Complete 🎉</h3>
          <p class="sub mt-2 mb-4">You have completed all questions in this adaptive set.</p>
          <button class="btn btn-primary" onclick="restartAdaptivePractice()">Start New Set</button>
        </div>
      </div>`;
  }

  const isLocalLLM = practiceState.generationMode === 'LOCAL_LLM';
  const badgeHtml = isLocalLLM
    ? `<span class="badge" style="background:var(--green-50, #E6F4EA);color:var(--green-700, #137333);font-size:11px;font-weight:700">⚡ On-Device AI</span>`
    : `<span class="badge" style="background:var(--amber-50, #FEF7E0);color:var(--amber-800, #B06000);font-size:11px;font-weight:700">🔒 Offline Fallback</span>`;

  const diffBadge = `<span class="badge indigo">${q.difficulty}</span>`;
  const rec = practiceState.recommendation;

  return `
    <div class="page">
      <div class="flex-b mb-4">
        <div>
          <div class="flex gap-2 items-center mb-1">
            <h1 class="h1">Personalized Practice</h1>
            ${badgeHtml}
            ${diffBadge}
          </div>
          <p class="sub">Topic: <b>${practiceState.topicTitle}</b> · Question ${practiceState.currentIndex + 1} of ${practiceState.questions.length}</p>
        </div>
        <div class="flex gap-2">
          <button class="btn btn-sm" onclick="loadAdaptivePractice()">${icon('refresh')} New Questions</button>
        </div>
      </div>

      <!-- Adaptive Context Card: Why this practice? -->
      <div class="card pad mb-4" style="background:linear-gradient(135deg, rgba(36,59,107,.05), rgba(78,140,255,.07));border:1.5px solid rgba(36,59,107,.15);border-radius:12px">
        <div class="flex-b items-center mb-2">
          <div style="font-weight:700;font-size:13px;color:var(--indigo);display:flex;align-items:center;gap:6px">
            <span>✦ Personalized for you</span>
          </div>
          <span class="badge indigo" style="font-size:10.5px">Recommended: ${rec?.recommended_difficulty || q.difficulty}</span>
        </div>
        <div style="font-size:14.5px;font-weight:700;margin-bottom:6px">${practiceState.topicTitle}</div>
        <div class="flex gap-4 wrap mb-2" style="font-size:12px;color:var(--text-2)">
          <span>Accuracy: <b>${rec ? rec.accuracy.toFixed(1) : '38.5'}%</b></span>
          <span>Mastery: <b>${rec ? rec.mastery_level : 'NOVICE'}</b></span>
          <span>Retention Risk: <b>${rec ? rec.retention_risk : 'MODERATE'}</b></span>
          <span>Trend: <b>${rec ? rec.trend : 'STABLE'}</b></span>
        </div>
        <p style="font-size:12px;line-height:1.45;color:var(--text);margin:0">
          ${rec?.reason || q.personalization_reason || 'Recent performance indicates foundational practice is optimal before increasing difficulty.'}
        </p>
      </div>

      <div class="card pad mb-5" style="border:1px solid var(--border-2)">
        <div class="tiny text-muted mb-2" style="font-weight:600;text-transform:uppercase;letter-spacing:.04em">
          Personalization Strategy: ${q.personalization_reason || 'Targeted practice'}
        </div>
        <h3 style="font-size:16px;line-height:1.5;margin-bottom:16px">${q.question}</h3>

        <div class="grid g-1 mb-4" id="practiceOptions" style="display:flex;flex-direction:column;gap:10px">
          ${q.options.map((opt: string) => {
            const isSel = practiceState.selectedOption === opt;
            const isSubmitted = practiceState.submitted;
            const resp = practiceState.lastResponse;
            let optStyle = "padding:12px 16px;border:1px solid var(--border);border-radius:10px;cursor:pointer;display:flex;align-items:center;gap:10px;background:var(--card-bg, #fff);font-size:13.5px;transition:all .15s";
            if (isSel && !isSubmitted) {
              optStyle = "padding:12px 16px;border:2px solid var(--indigo);border-radius:10px;cursor:pointer;display:flex;align-items:center;gap:10px;background:var(--indigo-50, #EEF2FF);font-size:13.5px;font-weight:600";
            } else if (isSubmitted) {
              if (opt === resp?.correct_answer) {
                optStyle = "padding:12px 16px;border:2px solid var(--green);border-radius:10px;display:flex;align-items:center;gap:10px;background:var(--green-50, #E6F4EA);font-size:13.5px;font-weight:600;color:var(--green-800)";
              } else if (isSel && !resp?.correct) {
                optStyle = "padding:12px 16px;border:2px solid var(--coral);border-radius:10px;display:flex;align-items:center;gap:10px;background:var(--coral-50, #FCE8E6);font-size:13.5px;font-weight:600;color:var(--coral-800)";
              }
            }
            return `
              <div style="${optStyle}" onclick="selectPracticeOption('${opt.replace(/'/g, "\\'")}')">
                <input type="radio" name="practice_opt" ${isSel ? 'checked' : ''} ${isSubmitted ? 'disabled' : ''}>
                <span>${opt}</span>
              </div>`;
          }).join('')}
        </div>

        ${!practiceState.submitted ? `
          <button class="btn btn-primary" onclick="submitPracticeAnswer()" ${!practiceState.selectedOption ? 'disabled' : ''}>
            Submit Answer
          </button>
        ` : ''}

        ${practiceState.submitted && practiceState.lastResponse ? `
          <div style="margin-top:20px;padding:18px;border-radius:12px;background:${practiceState.lastResponse.correct ? 'var(--green-50, #E6F4EA)' : 'var(--coral-50, #FCE8E6)'};border:1.5px solid ${practiceState.lastResponse.correct ? 'rgba(46,155,104,.4)' : 'rgba(235,94,85,.4)'}">
            <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:8px">
              <span style="font-weight:800;font-size:15px;color:${practiceState.lastResponse.correct ? 'var(--green-800, #137333)' : 'var(--coral-800, #C5221F)'}">
                ${practiceState.lastResponse.correct ? '✓ Correct Concept Applied' : '✗ Misconception Detected'}
              </span>
              <span class="badge ${practiceState.lastResponse.correct ? 'green' : 'coral'}" style="font-size:11px;font-weight:700">
                ${practiceState.lastResponse.correct ? 'Accuracy Gained' : 'Learning Path Updated'}
              </span>
            </div>
            
            <p style="font-size:13.5px;line-height:1.55;margin-bottom:10px;color:var(--text)">${practiceState.lastResponse.feedback}</p>
            
            <div style="display:flex;align-items:center;gap:6px;font-size:12px;color:var(--text-2);margin-bottom:12px;background:rgba(255,255,255,.6);padding:6px 12px;border-radius:8px">
              <span style="font-weight:700;color:var(--indigo)">📖 Verified Provenance:</span>
              <span>${practiceState.lastResponse.source_document || 'STD-10 Science'} (Textbook Page ${practiceState.lastResponse.source_page || 14})</span>
            </div>

            <!-- Visible Adaptive Causal Chain -->
            <div style="background:#fff;padding:12px 14px;border-radius:10px;border:1px solid rgba(0,0,0,.08);margin-bottom:14px">
              <div style="font-size:11.5px;font-weight:700;color:var(--indigo);text-transform:uppercase;letter-spacing:.03em;margin-bottom:4px">
                ⚡ Knowledge Model Adaptation
              </div>
              <div style="font-size:12px;color:var(--text);line-height:1.5">
                ${practiceState.lastResponse.correct
                  ? `<b>Success recorded!</b> Your rolling accuracy for this concept increased. The recommendation engine is advancing your mastery curve.`
                  : `<b>Weakness flagged:</b> Learning event recorded in local memory. Difficulty adjusted to <b>FOUNDATIONAL</b>. The system targets this exact concept for remediation.`}
              </div>
              <div style="margin-top:6px;font-size:11.5px;color:var(--text-3)">
                <b>Next Action:</b> ${practiceState.lastResponse.next_recommended_action}
              </div>
            </div>

            <div class="flex gap-2 items-center wrap">
              <button class="btn btn-primary" onclick="nextPracticeQuestion()">
                ${practiceState.currentIndex < practiceState.questions.length - 1 ? 'Next Adaptive Question →' : 'Finish Practice Set'}
              </button>
              <button class="btn" style="background:#fff" onclick="openAIPanel()">
                ${icon('sparkles')} Ask EduNavika AI to explain this
              </button>
            </div>
          </div>
        ` : ''}
      </div>
    </div>`;
}

export async function loadAdaptivePractice(topicId?: string): Promise<void> {
  if (topicId) {
    practiceState.topicId = topicId;
  }
  practiceState.loading = true;
  practiceState.submitted = false;
  practiceState.selectedOption = undefined;
  practiceState.lastResponse = undefined;

  const user = getCurrentUser();
  const studentId = user.id || 'e09699dd-0c64-44cc-82ef-ab41a832e072';

  // Concurrently fetch recommendation and questions
  const [rec, res] = await Promise.all([
    adaptiveService.getNextPracticeRecommendation(studentId, practiceState.topicId),
    adaptiveService.getPracticeQuestions(studentId, practiceState.topicId, 3),
  ]);

  practiceState.loading = false;
  practiceState.recommendation = rec;
  if (res && res.questions) {
    practiceState.questions = res.questions;
    practiceState.currentIndex = 0;
    practiceState.generationMode = res.generation_mode;
    practiceState.targetDifficulty = res.target_difficulty;
  }
  if (typeof window !== 'undefined' && window.navigate) {
    window.navigate('student/practice');
  }
}


export function selectPracticeOption(opt: string): void {
  if (practiceState.submitted) return;
  practiceState.selectedOption = opt;
  if (typeof window !== 'undefined' && window.navigate) {
    window.navigate('student/practice');
  }
}

export async function submitPracticeAnswer(): Promise<void> {
  if (!practiceState.selectedOption || practiceState.submitted) return;
  const q = practiceState.questions[practiceState.currentIndex];
  if (!q) return;

  const user = getCurrentUser();
  const studentId = user.id || 'e09699dd-0c64-44cc-82ef-ab41a832e072';

  const res = await adaptiveService.submitPracticeAnswer({
    student_id: studentId,
    question_id: q.id,
    topic_id: q.topic_id,
    selected_answer: practiceState.selectedOption,
    response_time_ms: 6000,
  });

  practiceState.submitted = true;
  practiceState.lastResponse = res;
  loadStudentProgress(true);
  loadStudentGamification(true);
  if (typeof window !== 'undefined' && window.navigate) {
    window.navigate('student/practice');
  }
}

export function nextPracticeQuestion(): void {
  practiceState.currentIndex += 1;
  practiceState.submitted = false;
  practiceState.selectedOption = undefined;
  practiceState.lastResponse = undefined;
  if (typeof window !== 'undefined' && window.navigate) {
    window.navigate('student/practice');
  }
}

export function restartAdaptivePractice(): void {
  practiceState.questions = [];
  loadAdaptivePractice();
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

  window.loadAdaptivePractice = loadAdaptivePractice;
  window.selectPracticeOption = selectPracticeOption;
  window.submitPracticeAnswer = submitPracticeAnswer;
  window.nextPracticeQuestion = nextPracticeQuestion;
  window.restartAdaptivePractice = restartAdaptivePractice;
  window.loadStudentProgress = loadStudentProgress;
  window.loadStudentGamification = loadStudentGamification;
  window.studentAchievements = studentAchievements;
  window.studentMaterials = studentMaterials;
  window.selectCurriculumSubject = selectCurriculumSubject;
  window.openTopicContentReader = openTopicContentReader;
  window.loadCurriculumHierarchy = loadCurriculumHierarchy;
}

