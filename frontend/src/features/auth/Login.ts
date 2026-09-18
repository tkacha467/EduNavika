// Login and Password Recovery Feature for EduNavika

import { Role } from '../../types';
import { authService } from '../../services/authService';
import { navigate } from '../../routes/router';

let selectedRole: Role = 'student';

export function renderLogin(currentRole: Role = 'student'): string {
  selectedRole = currentRole;
  const isStudent = selectedRole === 'student';
  const defaultEmail = isStudent
    ? 'kachatushar108@gmail.com'
    : 'tushar.kacha141862@marwadiuniversity.ac.in';
  const defaultPass = isStudent ? 'Tushar@21' : '2120@8030';

  return `
<div id="login" class="login">
  <div class="login-left">
    <div class="login-brand">
      <div class="login-mark">E</div>
      <div><b>EduNavika</b><span>INTELLIGENT LEARNING PLATFORM</span></div>
    </div>
    <div class="login-hero">
      <h1>The learning portal that<br>understands <em>how you learn.</em></h1>
      <p>Personalised revision, knowledge health tracking, forgetting prediction and continuous assessment — designed for GSEB schools, teachers, and students.</p>
      <div class="login-feats">
        <div class="login-feat">
          <div class="fic"><svg class="ic" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 12h-4l-3 9L9 3l-3 9H2"/></svg></div>
          <div><b>Knowledge Health</b><span>Live model-derived estimate of how stable learning retention is.</span></div>
        </div>
        <div class="login-feat">
          <div class="fic"><svg class="ic" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="9"/><path d="M12 7v5l3.5 2"/></svg></div>
          <div><b>Forgetting Timeline</b><span>Predicts concept decay before memory degradation occurs.</span></div>
        </div>
        <div class="login-feat">
          <div class="fic"><svg class="ic" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 3l1.8 4.7L18.5 9.5 13.8 11.3 12 16l-1.8-4.7L5.5 9.5l4.7-1.8z"/></svg></div>
          <div><b>Teacher Analytics</b><span>Real-time class mastery, struggling student alerts and curriculum coverage.</span></div>
        </div>
      </div>
    </div>
    <div class="login-foot">© 2026 EduNavika · GSEB Adaptive Platform</div>
  </div>

  <div class="login-right">
    <form class="login-form" id="loginForm" onsubmit="return false;">
      <h2>Welcome back</h2>
      <p>Sign in to continue to your EduNavika portal.</p>

      <div id="loginAlertBox" style="display:none;margin-bottom:16px;padding:12px 14px;border-radius:10px;font-size:13px;line-height:1.4;"></div>

      <div class="role-toggle">
        <button type="button" class="role-btn ${isStudent ? 'on' : ''}" id="roleStudentBtn">
          <div class="ric"><svg class="ic" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 6.5C10.5 5 8.5 4.5 5 4.5v13c3.5 0 5.5.5 7 2 1.5-1.5 3.5-2 7-2v-13c-3.5 0-5.5.5-7 2z"/><path d="M12 6.5v13"/></svg></div>
          <b>Student</b><span>Learn & revise</span>
        </button>
        <button type="button" class="role-btn ${!isStudent ? 'on' : ''}" id="roleTeacherBtn">
          <div class="ric"><svg class="ic" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M16 20v-1.5a4 4 0 0 0-4-4H7a4 4 0 0 0-4 4V20"/><circle cx="9.5" cy="7" r="3.5"/><path d="M21 20v-1.5a4 4 0 0 0-3-3.87"/><path d="M16.5 3.6a4 4 0 0 1 0 7.75"/></svg></div>
          <b>Teacher</b><span>Manage your class</span>
        </button>
      </div>

      <div class="field">
        <label id="lblLoginEmail">Email Address</label>
        <input class="input" type="text" id="loginEmail" value="${defaultEmail}" required autocomplete="username">
      </div>
      <div class="field">
        <label>Password</label>
        <input class="input" type="password" id="loginPassword" value="${defaultPass}" required autocomplete="current-password">
      </div>

      <div class="login-row">
        <label class="check"><input type="checkbox" checked id="chkRemember"> Remember me</label>
        <a href="javascript:void(0)" id="btnForgotPassLink" style="font-weight:600;color:var(--indigo,#3b5998)">Forgot password?</a>
      </div>

      <button type="submit" class="btn-login" id="btnSubmitLogin" style="cursor:pointer">Sign in to EduNavika</button>

      <p class="login-alt" style="margin-top:16px;font-size:12.5px;color:var(--text-3)">
        Student Demo: <span style="font-family:monospace;background:rgba(0,0,0,0.05);padding:2px 4px;border-radius:4px">kachatushar108@gmail.com</span><br>
        Teacher Demo: <span style="font-family:monospace;background:rgba(0,0,0,0.05);padding:2px 4px;border-radius:4px">tushar.kacha141862@marwadiuniversity.ac.in</span>
      </p>
    </form>
  </div>
</div>

<!-- Modal Container for Password Reset -->
<div id="authModalOverlay" style="display:none;position:fixed;top:0;left:0;right:0;bottom:0;background:rgba(15,23,42,0.65);z-index:9999;backdrop-filter:blur(4px);align-items:center;justify-content:center;padding:20px;">
  <div id="authModalContent" style="background:#fff;border-radius:18px;max-width:480px;width:100%;box-shadow:0 25px 50px -12px rgba(0,0,0,0.25);overflow:hidden;animation:slideUp 0.25s ease;">
  </div>
</div>
`;
}

export function renderResetPasswordPage(email: string = '', token: string = ''): string {
  return `
<div id="login" class="login" style="align-items:center;justify-content:center;background:linear-gradient(135deg,#f8fafc 0%,#eef2ff 100%);min-height:100vh;">
  <div style="background:#fff;border-radius:20px;padding:36px;max-width:440px;width:90%;box-shadow:0 20px 25px -5px rgba(0,0,0,0.1), 0 10px 10px -5px rgba(0,0,0,0.04);border:1px solid #e2e8f0;">
    <div style="display:flex;align-items:center;gap:12px;margin-bottom:20px;">
      <div class="login-mark" style="width:40px;height:40px;border-radius:10px;background:#3b5998;color:#fff;display:flex;align-items:center;justify-content:center;font-weight:800;font-size:18px;">E</div>
      <div>
        <h2 style="margin:0;font-size:19px;font-weight:700;color:#0f172a;">Reset Password</h2>
        <span style="font-size:12px;color:#64748b;">EduNavika Account Recovery</span>
      </div>
    </div>

    <div id="resetAlertBox" style="display:none;margin-bottom:16px;padding:12px;border-radius:8px;font-size:13px;"></div>

    <form id="resetPassForm" onsubmit="return false;">
      <div class="field" style="margin-bottom:14px;">
        <label style="display:block;font-size:12.5px;font-weight:600;margin-bottom:6px;color:#334155;">Email Address</label>
        <input class="input" type="email" id="resetEmailInput" value="${email}" style="width:100%;padding:10px 12px;border:1px solid #cbd5e1;border-radius:8px;" required>
      </div>

      <div class="field" style="margin-bottom:14px;">
        <label style="display:block;font-size:12.5px;font-weight:600;margin-bottom:6px;color:#334155;">Reset Token</label>
        <input class="input" type="text" id="resetTokenInput" value="${token}" style="width:100%;padding:10px 12px;border:1px solid #cbd5e1;border-radius:8px;" required>
      </div>

      <div class="field" style="margin-bottom:14px;">
        <label style="display:block;font-size:12.5px;font-weight:600;margin-bottom:6px;color:#334155;">New Password</label>
        <input class="input" type="password" id="resetNewPassInput" placeholder="Enter new password" style="width:100%;padding:10px 12px;border:1px solid #cbd5e1;border-radius:8px;" required>
      </div>

      <div class="field" style="margin-bottom:20px;">
        <label style="display:block;font-size:12.5px;font-weight:600;margin-bottom:6px;color:#334155;">Confirm New Password</label>
        <input class="input" type="password" id="resetConfirmPassInput" placeholder="Confirm new password" style="width:100%;padding:10px 12px;border:1px solid #cbd5e1;border-radius:8px;" required>
      </div>

      <button type="submit" id="btnSubmitReset" class="btn-login" style="width:100%;padding:12px;background:#3b5998;color:#fff;border:none;border-radius:8px;font-weight:700;cursor:pointer;">Update Password</button>

      <div style="text-align:center;margin-top:16px;">
        <a href="#/login" style="font-size:13px;color:#475569;text-decoration:none;font-weight:600;">← Back to Sign In</a>
      </div>
    </form>
  </div>
</div>
`;
}

export function bindLoginEvents(): void {
  const roleStudentBtn = document.getElementById('roleStudentBtn');
  const roleTeacherBtn = document.getElementById('roleTeacherBtn');
  const loginEmail = document.getElementById('loginEmail') as HTMLInputElement | null;
  const loginPassword = document.getElementById('loginPassword') as HTMLInputElement | null;
  const loginForm = document.getElementById('loginForm');
  const btnSubmitLogin = document.getElementById('btnSubmitLogin') as HTMLButtonElement | null;
  const btnForgotPassLink = document.getElementById('btnForgotPassLink');
  const alertBox = document.getElementById('loginAlertBox');

  // Role Switch Handlers
  if (roleStudentBtn && roleTeacherBtn && loginEmail && loginPassword) {
    roleStudentBtn.onclick = () => {
      selectedRole = 'student';
      roleStudentBtn.classList.add('on');
      roleTeacherBtn.classList.remove('on');
      loginEmail.value = 'kachatushar108@gmail.com';
      loginPassword.value = 'Tushar@21';
      if (alertBox) alertBox.style.display = 'none';
    };

    roleTeacherBtn.onclick = () => {
      selectedRole = 'teacher';
      roleTeacherBtn.classList.add('on');
      roleStudentBtn.classList.remove('on');
      loginEmail.value = 'tushar.kacha141862@marwadiuniversity.ac.in';
      loginPassword.value = '2120@8030';
      if (alertBox) alertBox.style.display = 'none';
    };
  }

  // Form Submit Handler
  if (loginForm && loginEmail && loginPassword) {
    loginForm.onsubmit = async (e: Event) => {
      e.preventDefault();
      const email = loginEmail.value.trim();
      const password = loginPassword.value.trim();

      if (!email || !password) {
        showError('Please enter both email address and password.');
        return;
      }

      if (btnSubmitLogin) {
        btnSubmitLogin.disabled = true;
        btnSubmitLogin.textContent = 'Signing in to EduNavika…';
      }

      try {
        const user = await authService.login(email, password, selectedRole);
        if (alertBox) {
          alertBox.style.display = 'block';
          alertBox.style.background = '#f0fdf4';
          alertBox.style.color = '#15803d';
          alertBox.style.border = '1px solid #bbf7d0';
          alertBox.innerHTML = `<b>Welcome back, ${user.full_name}!</b> Redirecting to your dashboard…`;
        }

        setTimeout(() => {
          navigate(`${user.role}/dashboard`);
        }, 300);
      } catch (err: any) {
        showError(err.message || 'Unable to sign in. Please verify your email and password.');
        if (btnSubmitLogin) {
          btnSubmitLogin.disabled = false;
          btnSubmitLogin.textContent = 'Sign in to EduNavika';
        }
      }
    };
  }

  // Forgot Password Modal trigger
  if (btnForgotPassLink && loginEmail) {
    btnForgotPassLink.onclick = () => {
      openForgotPasswordModal(loginEmail.value.trim());
    };
  }

  function showError(msg: string) {
    if (alertBox) {
      alertBox.style.display = 'block';
      alertBox.style.background = '#fef2f2';
      alertBox.style.color = '#b91c1c';
      alertBox.style.border = '1px solid #fecaca';
      alertBox.innerHTML = `⚠️ ${msg}`;
    }
  }
}

export function bindResetPasswordEvents(): void {
  const form = document.getElementById('resetPassForm');
  const emailInput = document.getElementById('resetEmailInput') as HTMLInputElement | null;
  const tokenInput = document.getElementById('resetTokenInput') as HTMLInputElement | null;
  const newPassInput = document.getElementById('resetNewPassInput') as HTMLInputElement | null;
  const confirmPassInput = document.getElementById('resetConfirmPassInput') as HTMLInputElement | null;
  const alertBox = document.getElementById('resetAlertBox');
  const btnSubmit = document.getElementById('btnSubmitReset') as HTMLButtonElement | null;

  if (form && emailInput && tokenInput && newPassInput && confirmPassInput) {
    form.onsubmit = async (e: Event) => {
      e.preventDefault();
      const email = emailInput.value.trim();
      const token = tokenInput.value.trim();
      const newPass = newPassInput.value.trim();
      const confirmPass = confirmPassInput.value.trim();

      if (!email || !token || !newPass) {
        showResetAlert('Please fill in all required fields.', false);
        return;
      }
      if (newPass !== confirmPass) {
        showResetAlert('New password and confirm password do not match.', false);
        return;
      }
      if (newPass.length < 6) {
        showResetAlert('Password must be at least 6 characters long.', false);
        return;
      }

      if (btnSubmit) {
        btnSubmit.disabled = true;
        btnSubmit.textContent = 'Updating Password…';
      }

      try {
        const resp = await authService.resetPassword(email, token, newPass);
        showResetAlert(`✅ ${resp.message} Redirecting to sign in…`, true);
        setTimeout(() => {
          navigate('login');
        }, 1500);
      } catch (err: any) {
        showResetAlert(`⚠️ ${err.message || 'Failed to reset password.'}`, false);
        if (btnSubmit) {
          btnSubmit.disabled = false;
          btnSubmit.textContent = 'Update Password';
        }
      }
    };
  }

  function showResetAlert(msg: string, isSuccess: boolean) {
    if (alertBox) {
      alertBox.style.display = 'block';
      alertBox.style.background = isSuccess ? '#f0fdf4' : '#fef2f2';
      alertBox.style.color = isSuccess ? '#15803d' : '#b91c1c';
      alertBox.style.border = `1px solid ${isSuccess ? '#bbf7d0' : '#fecaca'}`;
      alertBox.innerHTML = msg;
    }
  }
}

export function openForgotPasswordModal(prefilledEmail: string = ''): void {
  const overlay = document.getElementById('authModalOverlay');
  const content = document.getElementById('authModalContent');
  if (!overlay || !content) return;

  overlay.style.display = 'flex';
  content.innerHTML = `
    <div style="padding:24px 28px;border-bottom:1px solid #e2e8f0;display:flex;justify-content:space-between;align-items:center;">
      <div>
        <h3 style="margin:0;font-size:18px;font-weight:700;color:#0f172a;">Forgot Password</h3>
        <p style="margin:2px 0 0 0;font-size:12px;color:#64748b;">Receive real-time password reset instructions</p>
      </div>
      <button id="btnCloseForgotModal" style="background:none;border:none;font-size:20px;color:#64748b;cursor:pointer;padding:4px 8px;">✕</button>
    </div>

    <div style="padding:24px 28px;">
      <div id="forgotStatusBox" style="display:none;margin-bottom:16px;padding:12px 14px;border-radius:10px;font-size:13px;line-height:1.4;"></div>

      <div id="forgotInputSection">
        <p style="font-size:13px;color:#475569;margin-top:0;margin-bottom:16px;">
          Enter your registered email address. We will generate an instant secure password reset link for your account.
        </p>
        <div class="field" style="margin-bottom:20px;">
          <label style="display:block;font-size:12.5px;font-weight:600;margin-bottom:6px;color:#334155;">Registered Email</label>
          <input class="input" type="email" id="modalForgotEmail" value="${prefilledEmail}" placeholder="e.g. kachatushar108@gmail.com" style="width:100%;padding:10px 12px;border:1px solid #cbd5e1;border-radius:8px;" required>
        </div>
        <button type="button" id="btnSubmitForgotModal" style="width:100%;padding:12px;background:#3b5998;color:#fff;border:none;border-radius:8px;font-weight:700;cursor:pointer;font-size:14px;">
          Generate Real-Time Reset Link
        </button>
      </div>
    </div>
  `;

  const btnClose = document.getElementById('btnCloseForgotModal');
  if (btnClose) {
    btnClose.onclick = () => {
      overlay.style.display = 'none';
    };
  }

  const btnSubmitForgot = document.getElementById('btnSubmitForgotModal');
  const forgotEmailInput = document.getElementById('modalForgotEmail') as HTMLInputElement | null;
  const statusBox = document.getElementById('forgotStatusBox');

  if (btnSubmitForgot && forgotEmailInput) {
    btnSubmitForgot.onclick = async () => {
      const email = forgotEmailInput.value.trim();
      if (!email) {
        if (statusBox) {
          statusBox.style.display = 'block';
          statusBox.style.background = '#fef2f2';
          statusBox.style.color = '#b91c1c';
          statusBox.innerHTML = '⚠️ Please enter your registered email address.';
        }
        return;
      }

      btnSubmitForgot.textContent = 'Generating Reset Link…';
      btnSubmitForgot.setAttribute('disabled', 'true');

      try {
        const resp = await authService.forgotPassword(email);
        if (statusBox) {
          statusBox.style.display = 'block';
          statusBox.style.background = '#f0fdf4';
          statusBox.style.color = '#15803d';
          statusBox.style.border = '1px solid #bbf7d0';
          statusBox.innerHTML = `
            <div style="font-weight:700;margin-bottom:6px;">✉️ Real-Time Reset Link Ready!</div>
            <div style="font-size:12.5px;color:#166534;margin-bottom:12px;">
              A secure password reset link was dispatched for <b>${email}</b>.
            </div>
            <div style="background:#fff;border:1px dashed #22c55e;border-radius:8px;padding:10px;margin-bottom:12px;word-break:break-all;font-size:12px;font-family:monospace;color:#1e293b;">
              ${resp.reset_link}
            </div>
            <button id="btnOpenResetDirect" style="width:100%;padding:10px;background:#16a34a;color:#fff;border:none;border-radius:8px;font-weight:700;cursor:pointer;">
              Proceed to Reset Password Now →
            </button>
          `;

          const btnDirect = document.getElementById('btnOpenResetDirect');
          if (btnDirect) {
            btnDirect.onclick = () => {
              overlay.style.display = 'none';
              navigate(`reset-password?token=${resp.reset_token}&email=${encodeURIComponent(email)}`);
            };
          }
        }
      } catch (err: any) {
        if (statusBox) {
          statusBox.style.display = 'block';
          statusBox.style.background = '#fef2f2';
          statusBox.style.color = '#b91c1c';
          statusBox.style.border = '1px solid #fecaca';
          statusBox.innerHTML = `⚠️ ${err.message || 'No account found with this email.'}`;
        }
        btnSubmitForgot.textContent = 'Generate Real-Time Reset Link';
        btnSubmitForgot.removeAttribute('disabled');
      }
    };
  }
}
