// Right Rail Widget Component for EduNavika AppShell

import { icon } from '../utils/icons';

export function renderRightRail(): string {
  return `
  <aside class="rail">
    <div class="rail-inner">
      <div class="ai-card">
        <div class="ai-head"><div class="ai-mark">${icon('sparkles')}</div><b>EduNavika AI</b></div>
        <div class="ai-body">Your learning workspace is active. Start a practice quiz to calibrate your knowledge health and generate your personalized revision plan.</div>
        <div class="ai-actions"><button class="btn btn-sm btn-teal" data-go="student/assessments">Start practice</button></div>
      </div>

      <div class="card">
        <div class="card-h" style="padding-bottom:12px"><h3 style="font-size:13.5px">Quick Actions</h3></div>
        <div class="card-b" style="padding-top:0;display:flex;flex-direction:column;gap:8px">
          <button class="qa-tile" data-go="student/assessments">
            <div class="qi">${icon('clipboard')}</div>
            <div><b>Start MCQ practice</b><span>Pick a topic and begin</span></div>
          </button>
          <button class="qa-tile" data-go="student/revision">
            <div class="qi" style="background:var(--amber-50);color:#B4731A">${icon('refresh')}</div>
            <div><b>Revision plan</b><span>Adaptive spaced practice</span></div>
          </button>
          <button class="qa-tile" data-go="student/materials">
            <div class="qi" style="background:var(--teal-50);color:var(--teal-600)">${icon('folder')}</div>
            <div><b>Study materials</b><span>Curriculum textbooks & notes</span></div>
          </button>
        </div>
      </div>

      <div class="card">
        <div class="card-h" style="padding-bottom:12px"><h3 style="font-size:13.5px">Diagnostic Assessment</h3></div>
        <div class="card-b" style="padding-top:0">
          <div class="flex-b mb-2">
            <span class="badge indigo">Standard 10</span>
            <span class="tiny">GSEB</span>
          </div>
          <div style="font-size:14px;font-weight:700;margin-bottom:2px">Baseline Knowledge Check</div>
          <div class="small mb-3">Mathematics & Science · 10 MCQs</div>
          <button class="btn btn-primary btn-sm" style="width:100%" data-go="student/assessments">Take Practice Check</button>
        </div>
      </div>
    </div>
  </aside>`;
}
