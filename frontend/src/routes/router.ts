// Centralized Role-Aware Router & Application Controller

import {
  renderLogin,
  bindLoginEvents,
  renderResetPasswordPage,
  bindResetPasswordEvents,
} from '../features/auth/Login';
import { renderAppShell } from '../layouts/AppShell';
import { getCurrentUser, isAuthenticated, getRole, authService } from '../services/authService';
import {
  studentDashboard,
  studentLearning,
  studentSubjects,
  studentRevision,
  studentKnowledge,
  studentSkills,
  studentAnalytics,
  studentWeak,
  studentAssessments,
  studentMaterials,
  studentNotes,
  studentAssignments,
  studentExams,
  studentTimetable,
  studentNotifications,
  studentProfile,
  studentSettings,
  studentHelp,
  openAIPanel,
} from '../features/student/StudentViews';
import {
  teacherDashboard,
  teacherClasses,
  teacherStudents,
  teacherSubjects,
  teacherAssessments,
  teacherAssignments,
  teacherAttendance,
  teacherContent,
  teacherAnalytics,
  teacherRevision,
  teacherNotifications,
  teacherProfile,
} from '../features/teacher/TeacherViews';
import { startQuiz } from '../features/interactive/QuizRunner';
import { openBuilder } from '../features/interactive/AssessmentBuilder';

declare const window: any;

export type ViewRenderer = () => string;

export const ROUTES: Record<string, ViewRenderer> = {
  'student/dashboard': studentDashboard,
  'student/learning': studentLearning,
  'student/subjects': studentSubjects,
  'student/revision': studentRevision,
  'student/knowledge': studentKnowledge,
  'student/skills': studentSkills,
  'student/analytics': studentAnalytics,
  'student/weak': studentWeak,
  'student/assessments': studentAssessments,
  'student/materials': studentMaterials,
  'student/notes': studentNotes,
  'student/assignments': studentAssignments,
  'student/exams': studentExams,
  'student/timetable': studentTimetable,
  'student/notifications': studentNotifications,
  'student/profile': studentProfile,
  'student/settings': studentSettings,
  'student/help': studentHelp,
  'teacher/dashboard': teacherDashboard,
  'teacher/classes': teacherClasses,
  'teacher/students': teacherStudents,
  'teacher/subjects': teacherSubjects,
  'teacher/assessments': teacherAssessments,
  'teacher/assignments': teacherAssignments,
  'teacher/attendance': teacherAttendance,
  'teacher/content': teacherContent,
  'teacher/analytics': teacherAnalytics,
  'teacher/revision': teacherRevision,
  'teacher/notifications': teacherNotifications,
  'teacher/profile': teacherProfile,
};

let currentRoute = 'student/dashboard';

export function getCurrentRoute(): string {
  return currentRoute;
}

export function navigate(route: string): void {
  // Clean hash prefix if provided
  let target = route.replace(/^#\/?/, '');
  if (!target) {
    const role = getRole();
    target = `${role}/dashboard`;
  }

  // Handle Reset Password route
  if (target.startsWith('reset-password')) {
    currentRoute = target;
    window.location.hash = `#/${target}`;
    renderCurrentRoute();
    return;
  }

  // Handle Login route
  if (target === 'login') {
    currentRoute = 'login';
    window.location.hash = '#/login';
    renderCurrentRoute();
    return;
  }

  // Check auth
  if (!isAuthenticated()) {
    currentRoute = 'login';
    window.location.hash = '#/login';
    renderCurrentRoute();
    return;
  }

  const role = getRole();

  // Role protection
  if (role === 'student' && target.startsWith('teacher/')) {
    target = 'student/dashboard';
  } else if (role === 'teacher' && target.startsWith('student/')) {
    target = 'teacher/dashboard';
  }

  const cleanTarget = target.split('?')[0];
  if (!ROUTES[cleanTarget]) {
    target = `${role}/dashboard`;
  }

  currentRoute = target;
  window.location.hash = `#/${target}`;
  renderCurrentRoute();
}

export function renderCurrentRoute(): void {
  const root = document.getElementById('appRoot');
  if (!root) return;

  // Handle Reset Password View
  if (currentRoute.startsWith('reset-password')) {
    const queryString = window.location.hash.includes('?') ? window.location.hash.split('?')[1] : '';
    const params = new URLSearchParams(queryString);
    const email = params.get('email') || '';
    const token = params.get('token') || '';
    root.innerHTML = renderResetPasswordPage(email, token);
    bindResetPasswordEvents();
    return;
  }

  // Handle Login View
  if (currentRoute === 'login' || !isAuthenticated()) {
    root.innerHTML = renderLogin(getRole());
    bindLoginEvents();
    return;
  }

  const user = getCurrentUser();
  const cleanRoute = currentRoute.split('?')[0];
  const renderer = ROUTES[cleanRoute] || (user.role === 'teacher' ? teacherDashboard : studentDashboard);
  const pageHtml = renderer();
  root.innerHTML = renderAppShell(user, cleanRoute, pageHtml);

  // Re-bind dynamic layout interactions
  bindShellInteractions();
}

function bindShellInteractions(): void {
  // Sidebar collapse toggle
  const btnToggle = document.getElementById('btnToggleSidebar');
  const sidebar = document.getElementById('sidebar');
  if (btnToggle && sidebar) {
    btnToggle.onclick = () => {
      sidebar.classList.toggle('collapsed');
    };
  }

  // Mobile burger toggle
  const btnBurger = document.getElementById('btnBurger');
  if (btnBurger && sidebar) {
    btnBurger.onclick = () => {
      sidebar.classList.toggle('open');
    };
  }

  // Sign out button
  const btnLogout = document.getElementById('btnAppLogout');
  if (btnLogout) {
    btnLogout.onclick = () => {
      authService.logout();
      navigate('login');
    };
  }

  // AI Assistant pulse button in topbar
  const btnAI = document.getElementById('btnAIPulse');
  if (btnAI) {
    btnAI.onclick = () => {
      openAIPanel();
    };
  }
}

// Global click event delegation for [data-go] links
if (typeof document !== 'undefined') {
  document.addEventListener('click', (e: MouseEvent) => {
    const target = (e.target as HTMLElement).closest('[data-go]') as HTMLElement | null;
    if (target) {
      const route = target.getAttribute('data-go');
      if (route) {
        e.preventDefault();
        navigate(route);
      }
    }
  });
}

// Window hashchange listener
if (typeof window !== 'undefined') {
  window.addEventListener('hashchange', () => {
    const hash = window.location.hash.replace(/^#\/?/, '');
    if (hash && hash !== currentRoute) {
      navigate(hash);
    }
  });
}

// Expose navigation globals for HTML templates
if (typeof window !== 'undefined') {
  window.navigate = navigate;
  window.startQuiz = startQuiz;
  window.openBuilder = openBuilder;
  window.openAIPanel = openAIPanel;
}
