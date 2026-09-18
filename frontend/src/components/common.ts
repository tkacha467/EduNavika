// Common Visual Components and Overlay Helpers for EduNavika

import { icon } from '../utils/icons';
import { getCurrentUser, authService } from '../services/authService';

export function pageHead(kicker: string, title: string, sub = '', actions = ''): string {
  return `<div class="page-head mb-5" style="display:flex;align-items:flex-end;gap:20px;flex-wrap:wrap">
    <div style="flex:1;min-width:260px">
      <div style="font-size:11.5px;font-weight:700;color:var(--indigo);text-transform:uppercase;letter-spacing:.06em;margin-bottom:6px">${kicker}</div>
      <h1 class="h1" style="margin-bottom:6px">${title}</h1>
      ${sub ? `<p class="body" style="max-width:680px">${sub}</p>` : ''}
    </div>
    ${actions ? `<div class="flex wrap gap-2">${actions}</div>` : ''}
  </div>`;
}

export function statBlock(label: string, value: string | number, delta = '', iconName = '', deltaTone = ''): string {
  return `<div class="stat">
    <div class="lbl">${iconName ? icon(iconName) : ''} ${label}</div>
    <div class="val">${value}</div>
    ${delta ? `<div class="delta ${deltaTone}">${deltaTone === 'up' ? icon('arrowUp') : deltaTone === 'down' ? icon('arrowDown') : ''} ${delta}</div>` : ''}
  </div>`;
}

export function statusBadge(status: string): string {
  const map: Record<string, { c: string; t: string }> = {
    strong: { c: 'green', t: 'Strong' },
    steady: { c: 'indigo', t: 'Steady' },
    review: { c: 'amber', t: 'Review due' },
    risk: { c: 'coral', t: 'At risk' },
    low: { c: 'green', t: 'Low' },
    medium: { c: 'amber', t: 'Medium' },
    high: { c: 'coral', t: 'High' },
    ok: { c: 'green', t: 'On track' },
    watch: { c: 'amber', t: 'Watch' },
    completed: { c: 'green', t: 'Completed' },
    draft: { c: 'grey', t: 'Draft' },
    scheduled: { c: 'teal', t: 'Scheduled' },
  };
  const m = map[status] || { c: 'grey', t: status };
  return `<span class="badge ${m.c} dot">${m.t}</span>`;
}

export function riskBadge(risk: string): string {
  const map: Record<string, { c: string; t: string }> = {
    low: { c: 'green', t: 'Low risk' },
    medium: { c: 'amber', t: 'Medium risk' },
    high: { c: 'coral', t: 'High risk' },
  };
  const m = map[risk] || { c: 'grey', t: risk };
  return `<span class="badge ${m.c}">${m.t}</span>`;
}

export function aiInsight(title: string, text: string, actionLabel = '', action = ''): string {
  return `<div class="ai-card">
    <div class="ai-head">
      <div class="ai-mark">${icon('sparkles')}</div>
      <b>${title}</b>
    </div>
    <div class="ai-body">${text}</div>
    ${actionLabel ? `<div class="ai-actions"><button class="btn btn-sm btn-teal" onclick="${action}">${actionLabel}</button></div>` : ''}
  </div>`;
}

export function progressBar(pct: number, color = 'indigo'): string {
  return `<div class="prog"><i class="fill-${color}" style="width:${Math.max(0, Math.min(100, pct))}%"></i></div>`;
}

export function emptyState(title: string, message: string, iconName = 'alert'): string {
  return `<div class="empty">
    <div class="empty-ic">${icon(iconName)}</div>
    <b>${title}</b>
    <span>${message}</span>
  </div>`;
}

export function toast(title: string, sub = '', type = 'info') {
  const toastRoot = document.getElementById('toastRoot');
  if (!toastRoot) return;
  const el = document.createElement('div');
  el.className = 'toast ' + (type === 'good' ? 'good' : type === 'warn' ? 'warn' : type === 'bad' ? 'bad' : type === 'teal' ? 'teal' : '');
  const icn = type === 'good' ? 'check' : type === 'warn' ? 'alert' : type === 'bad' ? 'alert' : type === 'teal' ? 'sparkles' : 'bell';
  el.innerHTML = `<span class="tic">${icon(icn)}</span><div><b>${title}</b>${sub ? `<span>${sub}</span>` : ''}</div>`;
  toastRoot.appendChild(el);
  setTimeout(() => {
    el.style.transition = '.3s';
    el.style.opacity = '0';
    el.style.transform = 'translateX(20px)';
    setTimeout(() => el.remove(), 300);
  }, 3600);
}

export function openModal(html: string, { width = '', dismissable = true } = {}): HTMLElement {
  const overlayRoot = document.getElementById('overlayRoot')!;
  const o = document.createElement('div');
  o.className = 'overlay';
  o.innerHTML = `<div class="modal ${width}">${html}</div>`;
  o.addEventListener('click', e => {
    if (e.target === o && dismissable) closeOverlay();
  });
  overlayRoot.appendChild(o);
  return o;
}

export function openDrawer(html: string): HTMLElement {
  const overlayRoot = document.getElementById('overlayRoot')!;
  const o = document.createElement('div');
  o.className = 'overlay';
  o.style.padding = '0';
  o.style.justifyContent = 'flex-end';
  o.style.alignItems = 'stretch';
  o.innerHTML = `<div class="drawer">${html}</div>`;
  o.addEventListener('click', e => {
    if (e.target === o) closeOverlay();
  });
  overlayRoot.appendChild(o);
  return o;
}

export function closeOverlay() {
  const overlayRoot = document.getElementById('overlayRoot');
  if (overlayRoot) overlayRoot.innerHTML = '';
}

export function openChangePasswordModal(): void {
  const user = getCurrentUser();
  const html = `
    <div class="modal-h">
      <div>
        <h3>Change Password</h3>
        <p class="tiny">Update login credentials for ${user.email}</p>
      </div>
      <button class="btn btn-icon" onclick="window.closeOverlay()">✕</button>
    </div>
    <div class="modal-b">
      <div id="changePassAlert" style="display:none;margin-bottom:14px;padding:10px 12px;border-radius:8px;font-size:12.5px;"></div>
      <form id="changePassForm" onsubmit="return false;">
        <div class="field mb-3">
          <label class="lbl-sm">Account Email</label>
          <input class="input" type="text" value="${user.email}" readonly style="background:var(--bg-2);color:var(--text-3);cursor:not-allowed">
        </div>
        <div class="field mb-3">
          <label class="lbl-sm">Current Password</label>
          <input class="input" type="password" id="currentPassInput" placeholder="Enter current password" required>
        </div>
        <div class="field mb-3">
          <label class="lbl-sm">New Password</label>
          <input class="input" type="password" id="newPassInput" placeholder="Enter new password (min 6 characters)" required>
        </div>
        <div class="field mb-4">
          <label class="lbl-sm">Confirm New Password</label>
          <input class="input" type="password" id="confirmPassInput" placeholder="Re-enter new password" required>
        </div>
        <div class="flex-b">
          <button type="button" class="btn" onclick="window.closeOverlay()">Cancel</button>
          <button type="submit" id="btnSubmitChangePass" class="btn btn-primary">Update Password</button>
        </div>
      </form>
    </div>
  `;
  openModal(html);

  const form = document.getElementById('changePassForm');
  const curInput = document.getElementById('currentPassInput') as HTMLInputElement | null;
  const newInput = document.getElementById('newPassInput') as HTMLInputElement | null;
  const confInput = document.getElementById('confirmPassInput') as HTMLInputElement | null;
  const alertBox = document.getElementById('changePassAlert');
  const btnSubmit = document.getElementById('btnSubmitChangePass') as HTMLButtonElement | null;

  if (form && curInput && newInput && confInput) {
    form.onsubmit = async (e: Event) => {
      e.preventDefault();
      const currentPass = curInput.value.trim();
      const newPass = newInput.value.trim();
      const confirmPass = confInput.value.trim();

      if (!currentPass || !newPass) {
        showAlert('Please fill in both current and new passwords.', false);
        return;
      }
      if (newPass !== confirmPass) {
        showAlert('New password and confirmation do not match.', false);
        return;
      }
      if (newPass.length < 6) {
        showAlert('New password must be at least 6 characters long.', false);
        return;
      }

      if (btnSubmit) {
        btnSubmit.disabled = true;
        btnSubmit.textContent = 'Saving…';
      }

      try {
        const resp = await authService.changePassword(user.email, currentPass, newPass);
        toast(resp.message || 'Password updated successfully!', '', 'good');
        closeOverlay();
      } catch (err: any) {
        showAlert(err.message || 'Current password is incorrect.', false);
        if (btnSubmit) {
          btnSubmit.disabled = false;
          btnSubmit.textContent = 'Update Password';
        }
      }
    };
  }

  function showAlert(msg: string, success: boolean) {
    if (alertBox) {
      alertBox.style.display = 'block';
      alertBox.style.background = success ? '#f0fdf4' : '#fef2f2';
      alertBox.style.color = success ? '#15803d' : '#b91c1c';
      alertBox.style.border = `1px solid ${success ? '#bbf7d0' : '#fecaca'}`;
      alertBox.innerHTML = msg;
    }
  }
}

if (typeof window !== 'undefined') {
  (window as any).openChangePasswordModal = openChangePasswordModal;
  (window as any).closeOverlay = closeOverlay;
  (window as any).toast = toast;
}

