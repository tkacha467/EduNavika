// App Shell: Navigation Menu, Collapsible Sidebar, and Topbar

import { icon } from '../utils/icons';
import { NavGroup, User } from '../types';
import { REVISION_QUEUE, CLASS_WEAK_TOPICS, NOTIFICATIONS } from '../features/student/studentData';
import { t, getLanguage } from '../utils/i18n';
import { getSelectedExam, getExamMetadata, ExamSelection } from '../services/examService';

export const NAV: Record<'student' | 'teacher', NavGroup[]> = {
  student: [
    {
      group: 'Competitive Preparation',
      items: [
        { id: 'student/dashboard', label: 'Dashboard', icon: 'home' },
        { id: 'student/learning', label: 'Learn by Chapter', icon: 'book' },
        { id: 'student/practice', label: 'Practice MCQs', icon: 'target' },
        { id: 'student/pyqs', label: 'Previous-Year Papers', icon: 'file' },
        { id: 'student/assessments', label: 'Mock Tests', icon: 'clipboard' },
      ],
    },
    {
      group: 'Analytics & Revision',
      items: [
        { id: 'student/analytics', label: 'Performance Analytics', icon: 'chart' },
        { id: 'student/revision', label: 'Revision Planner', icon: 'refresh' },
        { id: 'student/achievements', label: 'Achievements and Streaks', icon: 'award' },
      ],
    },
    {
      group: 'Account',
      items: [
        { id: 'student/profile', label: 'Profile', icon: 'users' },
        { id: 'student/settings', label: 'Settings', icon: 'cog' },
      ],
    },
  ],

  teacher: [
    {
      group: 'Main',
      items: [
        { id: 'teacher/dashboard', label: 'Dashboard', icon: 'home' },
        { id: 'teacher/classes', label: 'My Classes', icon: 'graduation' },
        { id: 'teacher/students', label: 'Students', icon: 'users' },
        { id: 'teacher/subjects', label: 'Subjects', icon: 'book' },
      ],
    },
    {
      group: 'Teaching',
      items: [
        { id: 'teacher/assessments', label: 'Assessments', icon: 'clipboard' },
        { id: 'teacher/assignments', label: 'Assignments', icon: 'edit' },
        { id: 'teacher/attendance', label: 'Attendance', icon: 'check' },
        { id: 'teacher/content', label: 'Content', icon: 'folder' },
      ],
    },
    {
      group: 'Insights',
      items: [
        { id: 'teacher/analytics', label: 'Analytics', icon: 'chart' },
        { id: 'teacher/revision', label: 'Revision Insights', icon: 'refresh' },
      ],
    },
    {
      group: 'Support',
      items: [
        { id: 'teacher/notifications', label: 'Notifications', icon: 'bell' },
        { id: 'teacher/profile', label: 'Profile', icon: 'users' },
      ],
    },
  ],
};

function getDynamicBadge(id: string, role: string): string | null {
  if (role === 'student') {
    if (id === 'student/revision') {
      return REVISION_QUEUE.length > 0 ? String(REVISION_QUEUE.length) : null;
    }
    if (id === 'student/weak') {
      return CLASS_WEAK_TOPICS.length > 0 ? String(CLASS_WEAK_TOPICS.length) : null;
    }
    if (id === 'student/notifications') {
      const count = NOTIFICATIONS.filter(n => n.unread).length;
      return count > 0 ? String(count) : null;
    }
  }
  return null;
}


export const CRUMBS: Record<string, string[]> = {
  'student/dashboard': ['Dashboard'],
  'student/learning': ['Learn by Chapter'],
  'student/practice': ['Practice MCQs'],
  'student/pyqs': ['Previous-Year Papers'],
  'student/assessments': ['Mock Tests'],
  'student/analytics': ['Performance Analytics'],
  'student/revision': ['Revision Planner'],
  'student/achievements': ['Achievements and Streaks'],
  'student/missions': ['Personalized Learning', 'Daily Missions'],
  'student/constellation': ['Curriculum Graph', 'Knowledge Constellation'],
  'student/boss-battle': ['Remediation Challenges', 'Misconception Battle'],
  'student/memory-guardian': ['Spaced Retrieval', 'Memory Guardian'],
  'student/timeline': ['Learning History', 'Growth Timeline'],
  'student/subjects': ['Subjects'],
  'student/knowledge': ['Insights', 'Knowledge Health'],
  'student/skills': ['Insights', 'Skill Mastery'],
  'student/weak': ['Insights', 'Weak Areas'],
  'student/materials': ['Academic', 'Study Materials'],
  'student/notes': ['Academic', 'Notes'],
  'student/assignments': ['Academic', 'Assignments'],
  'student/exams': ['Academic', 'Exams'],
  'student/timetable': ['Academic', 'Timetable'],
  'student/notifications': ['Support', 'Notifications'],
  'student/help': ['Support', 'Help & Support'],
  'student/profile': ['Support', 'Profile'],
  'student/settings': ['Support', 'Settings'],
  'teacher/dashboard': ['Dashboard'],
  'teacher/classes': ['My Classes'],
  'teacher/students': ['Students'],
  'teacher/subjects': ['Subjects'],
  'teacher/assessments': ['Assessments'],
  'teacher/assignments': ['Assignments'],
  'teacher/attendance': ['Attendance'],
  'teacher/content': ['Content'],
  'teacher/analytics': ['Analytics'],
  'teacher/revision': ['Insights', 'Revision Insights'],
  'teacher/notifications': ['Notifications'],
  'teacher/profile': ['Profile'],
};

export function renderAppShell(user: User, currentRoute: string, pageHtml: string): string {
  const role = user.role;
  const groups = NAV[role] || NAV.student;
  const crumbs = CRUMBS[currentRoute] || ['Dashboard'];

  const crumbHtml = crumbs.length
    ? crumbs
        .map((c, i) =>
          i === crumbs.length - 1
            ? `<b>${c}</b>`
            : `<span>${c}</span><span class="sep">›</span>`
        )
        .join('')
    : '<b>Dashboard</b>';

  const currentLang = getLanguage();
  let currentExam: ExamSelection = 'GENERAL';
  try {
    currentExam = getSelectedExam();
  } catch {
    currentExam = 'GENERAL';
  }
  const examMeta = getExamMetadata(currentExam);

  const navHtml = groups
    .map(
      g => {
        const groupKey = `nav.group.${g.group.toLowerCase().replace(/[^a-z]/g, '')}`;
        const groupTitle = t(groupKey, g.group);
        return `
    <div class="nav-group">
      <div class="nav-title">${groupTitle}</div>
      ${g.items
        .map(it => {
          const badge = getDynamicBadge(it.id, role);
          const itemKey = `nav.${it.id.split('/')[1]}`;
          const itemLabel = t(itemKey, it.label);
          return `
        <div class="nav-item ${currentRoute === it.id ? 'on' : ''}" data-go="${it.id}" title="${itemLabel}">
          ${icon(it.icon)}<span class="lbl">${itemLabel}</span>
          ${badge ? `<span class="bdg">${badge}</span>` : ''}
        </div>`;
        })
        .join('')}
    </div>`;
      }
    )
    .join('');

  const hasUnread = role === 'student' && NOTIFICATIONS.some(n => n.unread);

  return `
<div id="app" class="app">
  <aside class="sidebar" id="sidebar">
    <div class="side-head">
      <div class="side-mark">E</div>
      <div class="side-brand">
        <b>EduNavika</b>
        <span style="font-size:10px;color:var(--text-3);font-weight:600;letter-spacing:.02em">Built by Team Varja</span>
      </div>
      <button class="side-toggle" id="btnToggleSidebar" title="Collapse">
        <svg class="ic" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M15 6l-6 6 6 6"/></svg>
      </button>
    </div>
    <nav class="side-nav" id="sideNav">${navHtml}</nav>
    <div class="side-foot">
      <div class="av" id="sideAvatar">${user.initials || 'U'}</div>
      <div class="info"><b id="sideName">${user.full_name}</b><span id="sideMeta">${user.grade || 'Grade 10'} · ${role === 'student' ? examMeta.shortLabel : user.section || 'Science'}</span></div>
    </div>
  </aside>

  <div class="content">
    <header class="topbar">
      <div class="tb-left">
        <button class="tb-burger" id="btnBurger">
          <svg class="ic" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M4 7h16M4 12h16M4 17h16"/></svg>
        </button>
        <div class="crumb" id="crumb">${crumbHtml}</div>
      </div>
      <div class="tb-search" id="tbSearchWrap">
        <svg class="ic ic-sm" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><circle cx="11" cy="11" r="7"/><path d="M21 21l-4.3-4.3"/></svg>
        <input placeholder="${t('shell.search')}" id="globalSearch" autocomplete="off" spellcheck="false">
        <button id="globalSearchClear" class="search-clear-btn" style="display:none;background:none;border:none;cursor:pointer;padding:0 4px;color:var(--text-3);align-items:center;" title="Clear search">
          <svg class="ic ic-xs" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M18 6L6 18M6 6l12 12"/></svg>
        </button>
        <span class="kbd" id="globalSearchKbd">⌘K</span>
        <div id="searchResultsDropdown" class="search-dropdown hide" role="listbox"></div>
      </div>
      <div class="tb-right">
        <!-- Target Examination Selector Pill -->
        <div class="tb-exam-wrap" style="display:inline-flex;align-items:center;margin-right:4px">
          <select id="topbarExamSelect" class="input select" style="padding:4px 8px;font-size:11.5px;font-weight:700;border-radius:12px;background:var(--bg-2);border:1px solid var(--border-2);cursor:pointer;color:var(--text)" onchange="window.setExam ? window.setExam(this.value) : null" title="Target Examination / લક્ષ્ય પરીક્ષા / लक्ष्य परीक्षा">
            <option value="GENERAL" ${currentExam === 'GENERAL' ? 'selected' : ''}>📚 General School Study</option>
            <option value="JEE_MAIN" ${currentExam === 'JEE_MAIN' ? 'selected' : ''}>🎯 JEE Main (436 Topics)</option>
            <option value="JEE_ADVANCED" ${currentExam === 'JEE_ADVANCED' ? 'selected' : ''}>🚀 JEE Advanced (444 Topics)</option>
            <option value="NEET_UG" ${currentExam === 'NEET_UG' ? 'selected' : ''}>🩺 NEET UG (497 Topics)</option>
          </select>
        </div>

        <!-- Language Selector Pill -->
        <div class="tb-lang-wrap" style="display:inline-flex;align-items:center;margin-right:4px">
          <select id="topbarLangSelect" class="input select" style="padding:4px 8px;font-size:11.5px;font-weight:700;border-radius:12px;background:var(--bg-2);border:1px solid var(--border-2);cursor:pointer;color:var(--text)" onchange="window.setLanguage ? window.setLanguage(this.value) : null" title="Change Language / भाषा बदलें / ભાષા બદલો">
            <option value="en" ${currentLang === 'en' ? 'selected' : ''}>🇬🇧 English</option>
            <option value="gu" ${currentLang === 'gu' ? 'selected' : ''}>🇮🇳 ગુજરાતી</option>
            <option value="hi" ${currentLang === 'hi' ? 'selected' : ''}>🇮🇳 हिन्दी</option>
          </select>
        </div>

        <!-- On-Device Offline Status Indicator -->
        <div class="tb-offline-pill" style="display:inline-flex;align-items:center;gap:6px;padding:4px 10px;border-radius:20px;background:rgba(46,155,104,.1);border:1px solid rgba(46,155,104,.25);font-size:11.5px;font-weight:600;color:var(--green-700,#137333)" title="Core learning works offline: syllabus, practice, knowledge model, explanations, and revisions run locally on this device">
          <span style="width:7px;height:7px;border-radius:50%;background:var(--green,#2E9B68);box-shadow:0 0 6px var(--green,#2E9B68);display:inline-block"></span>
          <span>${t('shell.onDevice')}</span>
        </div>

        <button class="tb-ai" id="btnAIPulse" onclick="window.openAIPanel ? window.openAIPanel() : null">
          <span class="pulse"></span>
          <svg class="ic ic-sm" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 3l1.8 4.7L18.5 9.5 13.8 11.3 12 16l-1.8-4.7L5.5 9.5l4.7-1.8z"/></svg>
          <span>${t('shell.askAi')}</span>
        </button>
        <button class="tb-icon" data-go="${role}/notifications" title="Notifications">
          <svg class="ic" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M18 8a6 6 0 0 0-12 0c0 7-3 8-3 8h18s-3-1-3-8"/><path d="M13.7 21a2 2 0 0 1-3.4 0"/></svg>
          ${hasUnread ? '<span class="dot"></span>' : ''}
        </button>
        <button class="tb-profile" data-go="${role}/profile" title="View Profile">
          <div class="av sm" id="topAvatar">${user.initials || 'U'}</div>
          <div class="who"><b id="topName">${user.full_name}</b><span id="topMeta">${user.grade || 'Grade 10'} · ${user.section || 'Science'}</span></div>
          <svg class="ic ic-sm" style="color:var(--text-4)" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M6 9l6 6 6-6"/></svg>
        </button>
        <button class="tb-icon" id="btnAppLogout" title="Sign out / Switch account" style="color:var(--coral,#ef4444);cursor:pointer">
          <svg class="ic" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/><polyline points="16 17 21 12 16 7"/><line x1="21" y1="12" x2="9" y2="12"/></svg>
        </button>
      </div>
    </header>

    <div class="main" id="main">${pageHtml}</div>
    ${role === 'student' ? `
    <nav class="mobile-bottom-nav" aria-label="Quick mobile navigation">
      <button type="button" class="mobile-nav-item ${currentRoute === 'student/dashboard' ? 'on' : ''}" data-go="student/dashboard">
        ${icon('home')}<span>Dashboard</span>
      </button>
      <button type="button" class="mobile-nav-item ${currentRoute === 'student/missions' ? 'on' : ''}" data-go="student/missions">
        ${icon('zap')}<span>Missions</span>
      </button>
      <button type="button" class="mobile-nav-item ${currentRoute === 'student/practice' ? 'on' : ''}" data-go="student/practice">
        ${icon('target')}<span>Practice</span>
      </button>
      <button type="button" class="mobile-nav-item ${currentRoute === 'student/constellation' ? 'on' : ''}" data-go="student/constellation">
        ${icon('star')}<span>Graph</span>
      </button>
      <button type="button" class="mobile-nav-item ${currentRoute === 'student/analytics' ? 'on' : ''}" data-go="student/analytics">
        ${icon('chart')}<span>Progress</span>
      </button>
    </nav>` : ''}
  </div>
</div>`;
}
