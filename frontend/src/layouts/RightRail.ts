// Right Rail Widget Component from Final Design/final desgin.html

import { icon } from '../utils/icons';
import { heatmap } from '../utils/charts';

export function renderRightRail(): string {
  return `
  <aside class="rail">
    <div class="rail-inner">
      <div class="ai-card">
        <div class="ai-head"><div class="ai-mark">${icon('sparkles')}</div><b>EduNavika AI</b></div>
        <div class="ai-body">You're most productive in the <b>4–7 PM</b> window. I've scheduled your revision for today at 5:00 PM.</div>
        <div class="ai-actions"><button class="btn btn-sm btn-teal" data-go="student/revision">Open plan</button></div>
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
            <div><b>Review today's queue</b><span>4 topics awaiting</span></div>
          </button>
          <button class="qa-tile" data-go="student/materials">
            <div class="qi" style="background:var(--teal-50);color:var(--teal-600)">${icon('folder')}</div>
            <div><b>Study materials</b><span>Notes, videos, PDFs</span></div>
          </button>
        </div>
      </div>

      <div class="card">
        <div class="card-h" style="padding-bottom:12px"><h3 style="font-size:13.5px">Next Test</h3></div>
        <div class="card-b" style="padding-top:0">
          <div class="flex-b mb-2">
            <span class="badge coral">2 days left</span>
            <span class="tiny">Sept 18, 2026</span>
          </div>
          <div style="font-size:14px;font-weight:700;margin-bottom:2px">Electricity & Circuits — Quiz 2</div>
          <div class="small mb-3">Physics · 30 min · 25 MCQs</div>
          <div class="flex gap-2 mb-3" style="font-size:11.5px;color:var(--text-3)">
            <span>Preparation</span>
            <div class="prog thin" style="flex:1"><i class="fill-amber" style="width:48%"></i></div>
            <b style="color:var(--text)">48%</b>
          </div>
          <button class="btn btn-primary btn-sm" style="width:100%" data-go="student/revision">Revise for this test</button>
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
