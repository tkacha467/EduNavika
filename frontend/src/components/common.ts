// Common Visual Components and Overlay Helpers for EduNavika

import { icon } from '../utils/icons';

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
