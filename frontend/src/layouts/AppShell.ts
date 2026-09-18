// App Shell: Navigation Menu, Collapsible Sidebar, and Topbar

import { icon } from '../utils/icons';
import { NavGroup, User } from '../types';

export const NAV: Record<'student' | 'teacher', NavGroup[]> = {
  student: [
    {
      group: 'Main',
      items: [
        { id: 'student/dashboard', label: 'Dashboard', icon: 'home' },
        { id: 'student/learning', label: 'My Learning', icon: 'book' },
        { id: 'student/subjects', label: 'Subjects', icon: 'grid' },
        { id: 'student/revision', label: 'Revision Plan', icon: 'refresh', badge: '4' },
        { id: 'student/assessments', label: 'Assessments', icon: 'clipboard', badge: '3' },
        { id: 'student/calendar', label: 'Calendar', icon: 'calendar' },
      ],
    },
    {
      group: 'Insights',
      items: [
        { id: 'student/knowledge', label: 'Knowledge Health', icon: 'brain' },
        { id: 'student/skills', label: 'Skill Mastery', icon: 'target' },
        { id: 'student/analytics', label: 'Learning Analytics', icon: 'chart' },
        { id: 'student/weak', label: 'Weak Areas', icon: 'alert', badge: '3' },
      ],
    },
    {
      group: 'Academic',
      items: [
        { id: 'student/materials', label: 'Study Materials', icon: 'folder' },
        { id: 'student/notes', label: 'Notes', icon: 'file' },
        { id: 'student/assignments', label: 'Assignments', icon: 'edit', badge: '2' },
        { id: 'student/exams', label: 'Exams', icon: 'award' },
        { id: 'student/timetable', label: 'Timetable', icon: 'clock' },
      ],
    },
    {
      group: 'Support',
      items: [
        { id: 'student/notifications', label: 'Notifications', icon: 'bell', badge: '3' },
        { id: 'student/help', label: 'Help & Support', icon: 'help' },
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
        { id: 'teacher/assessments', label: 'Assessments', icon: 'clipboard', badge: '1' },
        { id: 'teacher/assignments', label: 'Assignments', icon: 'edit' },
        { id: 'teacher/attendance', label: 'Attendance', icon: 'check' },
        { id: 'teacher/content', label: 'Content', icon: 'folder' },
      ],
    },
    {
      group: 'Insights',
      items: [
        { id: 'teacher/analytics', label: 'Analytics', icon: 'chart' },
        { id: 'teacher/revision', label: 'Revision Insights', icon: 'refresh', badge: '5' },
      ],
    },
    {
      group: 'Support',
      items: [
        { id: 'teacher/notifications', label: 'Notifications', icon: 'bell', badge: '2' },
        { id: 'teacher/profile', label: 'Profile', icon: 'users' },
      ],
    },
  ],
};

export const CRUMBS: Record<string, string[]> = {
  'student/dashboard': ['Dashboard'],
  'student/learning': ['My Learning'],
  'student/subjects': ['Subjects'],
  'student/revision': ['Insights', 'Revision Plan'],
  'student/assessments': ['Assessments'],
  'student/calendar': ['Calendar'],
  'student/knowledge': ['Insights', 'Knowledge Health'],
  'student/skills': ['Insights', 'Skill Mastery'],
  'student/analytics': ['Insights', 'Learning Analytics'],
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

  const navHtml = groups
    .map(
      g => `
    <div class="nav-group">
      <div class="nav-title">${g.group}</div>
      ${g.items
        .map(
          it => `
        <div class="nav-item ${currentRoute === it.id ? 'on' : ''}" data-go="${it.id}">
          ${icon(it.icon)}<span class="lbl">${it.label}</span>
          ${it.badge ? `<span class="bdg">${it.badge}</span>` : ''}
          <span class="tip">${it.label}</span>
        </div>`
        )
        .join('')}
    </div>`
    )
    .join('');

  return `
<div id="app" class="app">
  <aside class="sidebar" id="sidebar">
    <div class="side-head">
      <div class="side-mark">E</div>
      <div class="side-brand"><b>EduNavika</b><span id="sideRoleLabel">${role === 'student' ? 'STUDENT PORTAL' : 'TEACHER PORTAL'}</span></div>
      <button class="side-toggle" id="btnToggleSidebar" title="Collapse">
        <svg class="ic" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M15 6l-6 6 6 6"/></svg>
      </button>
    </div>
    <nav class="side-nav" id="sideNav">${navHtml}</nav>
    <div class="side-foot">
      <div class="av" id="sideAvatar">${user.initials || 'U'}</div>
      <div class="info"><b id="sideName">${user.full_name}</b><span id="sideMeta">${user.grade || 'Grade 10'} · ${user.section || 'Science'}</span></div>
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
      <div class="tb-search">
        <svg class="ic ic-sm" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><circle cx="11" cy="11" r="7"/><path d="M21 21l-4.3-4.3"/></svg>
        <input placeholder="Search topics, subjects, assessments…" id="globalSearch">
        <span class="kbd">⌘K</span>
      </div>
      <div class="tb-right">
        <button class="tb-ai" id="btnAIPulse">
          <span class="pulse"></span>
          <svg class="ic ic-sm" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 3l1.8 4.7L18.5 9.5 13.8 11.3 12 16l-1.8-4.7L5.5 9.5l4.7-1.8z"/></svg>
          <span>EduNavika AI</span>
        </button>
        <button class="tb-icon" data-go="${role}/notifications">
          <svg class="ic" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M18 8a6 6 0 0 0-12 0c0 7-3 8-3 8h18s-3-1-3-8"/><path d="M13.7 21a2 2 0 0 1-3.4 0"/></svg>
          <span class="dot"></span>
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
  </div>
</div>`;
}
