// Login Page Feature for EduNavika

import { Role } from '../../types';

export function renderLogin(currentRole: Role = 'student'): string {
  return `
<div id="login" class="login">
  <div class="login-left">
    <div class="login-brand">
      <div class="login-mark">E</div>
      <div><b>EduNavika</b><span>INTELLIGENT LEARNING PLATFORM</span></div>
    </div>
    <div class="login-hero">
      <h1>The learning portal that<br>understands <em>how you learn.</em></h1>
      <p>Personalised revision, knowledge health tracking, forgetting prediction and continuous assessment — designed for real schools and real students.</p>
      <div class="login-feats">
        <div class="login-feat">
          <div class="fic"><svg class="ic" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 12h-4l-3 9L9 3l-3 9H2"/></svg></div>
          <div><b>Knowledge Health</b><span>Live model-derived estimate of how stable your learning is.</span></div>
        </div>
        <div class="login-feat">
          <div class="fic"><svg class="ic" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="9"/><path d="M12 7v5l3.5 2"/></svg></div>
          <div><b>Forgetting Timeline</b><span>See what needs revision before you forget it.</span></div>
        </div>
        <div class="login-feat">
          <div class="fic"><svg class="ic" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 3l1.8 4.7L18.5 9.5 13.8 11.3 12 16l-1.8-4.7L5.5 9.5l4.7-1.8z"/><path d="M18.5 15.5l.8 2.1 2.1.8-2.1.8-.8 2.1-.8-2.1-2.1-.8 2.1-.8z"/></svg></div>
          <div><b>EduNavika AI</b><span>Adaptive practice and revision grounded in your syllabus.</span></div>
        </div>
      </div>
    </div>
    <div class="login-foot">© 2026 EduNavika · A modern learning platform for schools</div>
  </div>

  <div class="login-right">
    <form class="login-form" id="loginForm">
      <h2>Welcome back</h2>
      <p>Sign in to continue to your EduNavika portal.</p>

      <div class="role-toggle">
        <button type="button" class="role-btn ${currentRole === 'student' ? 'on' : ''}" id="roleStudentBtn">
          <div class="ric"><svg class="ic" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 6.5C10.5 5 8.5 4.5 5 4.5v13c3.5 0 5.5.5 7 2 1.5-1.5 3.5-2 7-2v-13c-3.5 0-5.5.5-7 2z"/><path d="M12 6.5v13"/></svg></div>
          <b>Student</b><span>Learn and revise</span>
        </button>
        <button type="button" class="role-btn ${currentRole === 'teacher' ? 'on' : ''}" id="roleTeacherBtn">
          <div class="ric"><svg class="ic" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M16 20v-1.5a4 4 0 0 0-4-4H7a4 4 0 0 0-4 4V20"/><circle cx="9.5" cy="7" r="3.5"/><path d="M21 20v-1.5a4 4 0 0 0-3-3.87"/><path d="M16.5 3.6a4 4 0 0 1 0 7.75"/></svg></div>
          <b>Teacher</b><span>Manage your class</span>
        </button>
      </div>

      <div class="field">
        <label>School ID / Email</label>
        <input class="input" type="text" id="loginEmail" placeholder="${currentRole === 'student' ? 'a.sharma@dps.edu.in' : 'p.nair@dps.edu.in'}" value="${currentRole === 'student' ? 'a.sharma@dps.edu.in' : 'p.nair@dps.edu.in'}">
      </div>
      <div class="field">
        <label>Password</label>
        <input class="input" type="password" id="loginPassword" placeholder="••••••••" value="demo1234">
      </div>

      <div class="login-row">
        <label class="check"><input type="checkbox" checked> Remember me</label>
        <a href="javascript:void(0)">Forgot password?</a>
      </div>

      <button type="submit" class="btn-login" id="btnSubmitLogin">Sign in to EduNavika</button>

      <p class="login-alt">Trouble signing in? <a href="javascript:void(0)">Contact your school administrator</a></p>
    </form>
  </div>
</div>`;
}
