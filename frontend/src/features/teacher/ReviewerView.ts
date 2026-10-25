// Authenticated Question Reviewer Portal for EduNavika
// Milestone 5.9: Content Integrity, Visual Diagram Review, and Audit History

import { icon } from '../../utils/icons';
import { pageHead, toast } from '../../components/common';
import { getCurrentUser } from '../../services/authService';
import { competitiveService } from '../../services/competitiveService';

declare const window: any;

interface ReviewState {
  loading: boolean;
  questions: any[];
  selectedQuestionId: string | null;
  detailLoading: boolean;
  selectedDetail: any | null;
  filters: {
    exam: string;
    subject: string;
    reviewState: string;
    issueType: string;
    search: string;
  };
  form: {
    decision: 'APPROVED' | 'NEEDS_CORRECTION' | 'REJECTED';
    notes: string;
    submitting: boolean;
    error: string | null;
  };
}

const state: ReviewState = {
  loading: false,
  questions: [],
  selectedQuestionId: null,
  detailLoading: false,
  selectedDetail: null,
  filters: {
    exam: '',
    subject: '',
    reviewState: '',
    issueType: '',
    search: '',
  },
  form: {
    decision: 'APPROVED',
    notes: '',
    submitting: false,
    error: null,
  },
};

export function teacherReviewerView(): string {
  const user = getCurrentUser();

  // Schedule async data fetch after render
  setTimeout(() => {
    initReviewerView();
  }, 50);

  return `
  <div class="page" id="reviewerViewRoot">
    ${pageHead(
      'Quality & Integrity Portal',
      'Question & Diagram Verification Gate',
      'Audited reviewer portal for visual diagram validation, answer-key provenance, and content integrity before scoring promotion.',
      `
      <div style="display:flex;align-items:center;gap:12px">
        <div style="background:var(--card);border:1px solid var(--border);border-radius:20px;padding:6px 14px;font-size:12px;display:flex;align-items:center;gap:8px">
          <span style="display:inline-block;width:8px;height:8px;border-radius:50%;background:var(--green)"></span>
          <span>Reviewer: <b>${user.full_name || user.email || 'Authorized Reviewer'}</b></span>
          <span class="badge indigo" style="text-transform:uppercase;font-size:10px">${user.role || 'TEACHER'}</span>
        </div>
        <button class="btn btn-sm btn-primary" onclick="window.refreshReviewQueue()">
          ${icon('refresh')} Refresh Queue
        </button>
      </div>
      `
    )}

    <!-- Filter Bar -->
    <div class="card mb-4" style="padding:14px 18px;background:var(--card);border:1px solid var(--border)">
      <div style="display:flex;flex-wrap:wrap;gap:12px;align-items:center;justify-content:space-between">
        <div style="display:flex;flex-wrap:wrap;gap:10px;align-items:center;flex:1">
          <!-- Search -->
          <div style="position:relative;min-width:180px">
            <input type="text" id="reviewSearchInput" class="input" placeholder="Search Q# or stem..." 
              value="${state.filters.search}" oninput="window.handleReviewSearch(this.value)" 
              style="padding-left:30px;height:36px;font-size:12.5px" />
            <span style="position:absolute;left:10px;top:9px;color:var(--text-3)">${icon('search')}</span>
          </div>

          <!-- Exam Filter -->
          <select id="reviewExamFilter" class="input" style="width:140px;height:36px;font-size:12.5px" onchange="window.handleReviewFilter('exam', this.value)">
            <option value="">All Exams</option>
            <option value="NEET" ${state.filters.exam === 'NEET' ? 'selected' : ''}>NEET UG</option>
            <option value="JEE_MAIN" ${state.filters.exam === 'JEE_MAIN' ? 'selected' : ''}>JEE Main</option>
            <option value="JEE_ADVANCED" ${state.filters.exam === 'JEE_ADVANCED' ? 'selected' : ''}>JEE Advanced</option>
          </select>

          <!-- Subject Filter -->
          <select id="reviewSubjectFilter" class="input" style="width:140px;height:36px;font-size:12.5px" onchange="window.handleReviewFilter('subject', this.value)">
            <option value="">All Subjects</option>
            <option value="Physics" ${state.filters.subject === 'Physics' ? 'selected' : ''}>Physics</option>
            <option value="Chemistry" ${state.filters.subject === 'Chemistry' ? 'selected' : ''}>Chemistry</option>
            <option value="Biology" ${state.filters.subject === 'Biology' ? 'selected' : ''}>Biology</option>
          </select>

          <!-- Review State Filter -->
          <select id="reviewStateFilter" class="input" style="width:150px;height:36px;font-size:12.5px" onchange="window.handleReviewFilter('reviewState', this.value)">
            <option value="">All States</option>
            <option value="UNVERIFIED" ${state.filters.reviewState === 'UNVERIFIED' ? 'selected' : ''}>Unverified</option>
            <option value="APPROVED" ${state.filters.reviewState === 'APPROVED' ? 'selected' : ''}>Approved</option>
            <option value="NEEDS_CORRECTION" ${state.filters.reviewState === 'NEEDS_CORRECTION' ? 'selected' : ''}>Needs Correction</option>
            <option value="REJECTED" ${state.filters.reviewState === 'REJECTED' ? 'selected' : ''}>Rejected</option>
          </select>

          <!-- Issue Type Filter -->
          <select id="reviewIssueFilter" class="input" style="width:160px;height:36px;font-size:12.5px" onchange="window.handleReviewFilter('issueType', this.value)">
            <option value="">All Issue Types</option>
            <option value="DIAGRAM" ${state.filters.issueType === 'DIAGRAM' ? 'selected' : ''}>Diagram Questions</option>
            <option value="TEXT_ONLY" ${state.filters.issueType === 'TEXT_ONLY' ? 'selected' : ''}>Text-Only</option>
          </select>
        </div>

        <div style="font-size:12.5px;color:var(--text-2);display:flex;align-items:center;gap:6px">
          <span id="reviewQueueCountBadge" class="badge grey">0 questions loaded</span>
        </div>
      </div>
    </div>

    <!-- Main Review Workspace: Two-Column Split Layout -->
    <div style="display:grid;grid-template-columns:360px 1fr;gap:20px;align-items:start">
      
      <!-- Left Column: Question Queue -->
      <div class="card" style="padding:0;overflow:hidden;border:1px solid var(--border)">
        <div style="padding:14px 16px;border-bottom:1px solid var(--border);display:flex;justify-content:space-between;align-items:center;background:var(--card-head, var(--card))">
          <b style="font-size:13px;letter-spacing:0.02em">Verification Queue</b>
          <span style="font-size:11px;color:var(--text-3)">Click item to inspect</span>
        </div>
        <div id="reviewQueueList" style="max-height:calc(100vh - 280px);overflow-y:auto;padding:8px">
          <div style="padding:32px 16px;text-align:center;color:var(--text-3);font-size:13px">
            <div style="margin-bottom:8px">${icon('refresh')}</div>
            Loading questions awaiting verification...
          </div>
        </div>
      </div>

      <!-- Right Column: Question Detail & Verification Workspace -->
      <div id="reviewDetailContainer" class="card" style="padding:0;overflow:hidden;border:1px solid var(--border);min-height:500px">
        <div style="padding:48px 24px;text-align:center;color:var(--text-3);margin:auto">
          <div style="font-size:36px;margin-bottom:12px">🔍</div>
          <div style="font-weight:700;font-size:15px;color:var(--text);margin-bottom:6px">Select a Question to Review</div>
          <p style="font-size:13px;max-width:400px;margin:0 auto">
            Pick a question from the left queue to inspect diagram fidelity, verify answer-key reconciliation, and record an auditable review decision.
          </p>
        </div>
      </div>

    </div>
  </div>
  `;
}

export async function initReviewerView(): Promise<void> {
  await fetchQueue();
}

async function fetchQueue(): Promise<void> {
  const queueEl = document.getElementById('reviewQueueList');
  if (queueEl && state.questions.length === 0) {
    queueEl.innerHTML = `
      <div style="padding:32px 16px;text-align:center;color:var(--text-3);font-size:13px">
        <div style="margin-bottom:8px">${icon('refresh')}</div>
        Loading verification queue from backend...
      </div>
    `;
  }

  state.loading = true;
  try {
    const params: any = { limit: 100 };
    if (state.filters.exam) params.exam_code = state.filters.exam;
    if (state.filters.subject) params.subject = state.filters.subject;
    if (state.filters.reviewState) params.review_state = state.filters.reviewState;
    if (state.filters.issueType) params.issue_type = state.filters.issueType;

    const items = await competitiveService.getReviewQuestions(params);
    state.questions = Array.isArray(items) ? items : [];
    renderQueue();

    // Auto-select first item if none selected or current selection missing
    if (state.questions.length > 0 && !state.selectedQuestionId) {
      window.selectReviewQuestion(state.questions[0].id);
    }
  } catch (err: any) {
    if (queueEl) {
      queueEl.innerHTML = `
        <div style="padding:24px 16px;text-align:center;color:var(--coral);font-size:12.5px">
          <b>Error loading queue</b><br>${err.message || 'Server request failed.'}
        </div>
      `;
    }
  } finally {
    state.loading = false;
  }
}

function renderQueue(): void {
  const queueEl = document.getElementById('reviewQueueList');
  const countBadge = document.getElementById('reviewQueueCountBadge');
  if (!queueEl) return;

  let filtered = state.questions;
  if (state.filters.search.trim()) {
    const q = state.filters.search.toLowerCase().trim();
    filtered = filtered.filter(item => {
      const qNum = String(item.question_number || '');
      const stem = String(item.question_text || '').toLowerCase();
      const code = String(item.paper_identifier || '').toLowerCase();
      return qNum.includes(q) || stem.includes(q) || code.includes(q);
    });
  }

  if (countBadge) {
    countBadge.textContent = `${filtered.length} questions loaded`;
  }

  if (filtered.length === 0) {
    queueEl.innerHTML = `
      <div style="padding:36px 16px;text-align:center;color:var(--text-3);font-size:13px">
        No questions matching current filter criteria.
      </div>
    `;
    return;
  }

  queueEl.innerHTML = filtered.map(item => {
    const isSelected = item.id === state.selectedQuestionId;
    const vStatus = item.verification_status || 'UNVERIFIED';
    const isDiag = !!item.has_diagram;

    let badgeClass = 'amber';
    if (vStatus === 'APPROVED') badgeClass = 'green';
    else if (vStatus === 'REJECTED') badgeClass = 'coral';
    else if (vStatus === 'NEEDS_CORRECTION') badgeClass = 'teal';

    const shortStem = (item.question_text || 'No text extracted')
      .replace(/<[^>]+>/g, '')
      .substring(0, 75);

    return `
      <div onclick="window.selectReviewQuestion('${item.id}')" 
        style="padding:10px 12px;margin-bottom:6px;border-radius:8px;cursor:pointer;transition:all .15s ease;
               border:1px solid ${isSelected ? 'var(--indigo)' : 'var(--border)'};
               background:${isSelected ? 'rgba(99, 102, 241, 0.08)' : 'var(--card)'};">
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:5px">
          <div style="display:flex;align-items:center;gap:6px">
            <span style="font-weight:800;font-size:12.5px;color:var(--text)">Q#${item.question_number || '—'}</span>
            <span class="badge grey" style="font-size:10px">${item.subject_name || 'Science'}</span>
          </div>
          <span class="badge ${badgeClass}" style="font-size:10px;text-transform:uppercase">${vStatus}</span>
        </div>
        
        <div style="font-size:12px;color:var(--text-2);line-height:1.4;margin-bottom:6px;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden">
          ${shortStem}...
        </div>

        <div style="display:flex;justify-content:space-between;align-items:center;font-size:10.5px;color:var(--text-3)">
          <span>${item.paper_identifier || 'NEET 2021'}</span>
          ${isDiag ? `<span style="color:var(--indigo);font-weight:600">🖼️ Has Diagram</span>` : ''}
        </div>
      </div>
    `;
  }).join('');
}

export async function selectReviewQuestion(questionId: string): Promise<void> {
  state.selectedQuestionId = questionId;
  renderQueue();

  const container = document.getElementById('reviewDetailContainer');
  if (!container) return;

  container.innerHTML = `
    <div style="padding:48px 24px;text-align:center;color:var(--text-3);font-size:13px">
      <div style="margin-bottom:10px">${icon('refresh')}</div>
      Loading question detail and audit logs...
    </div>
  `;

  state.detailLoading = true;
  try {
    const detail = await competitiveService.getQuestionReviewDetail(questionId);
    state.selectedDetail = detail;
    renderDetail();
  } catch (err: any) {
    container.innerHTML = `
      <div style="padding:32px 20px;text-align:center;color:var(--coral);font-size:13px">
        <b>Failed to load question detail</b><br>
        ${err.message || 'Network or authorization error.'}
      </div>
    `;
  } finally {
    state.detailLoading = false;
  }
}

function renderDetail(): void {
  const container = document.getElementById('reviewDetailContainer');
  if (!container || !state.selectedDetail) return;

  const q = state.selectedDetail;
  const isDiag = !!q.diagram_asset_url;
  const vStatus = q.verification_status || 'UNVERIFIED';
  const aStatus = q.answer_verification_status || 'UNVERIFIED';
  const isScoringEligible = q.is_scoring_eligible;
  const isQuarantined = q.is_quarantined;

  let vBadgeClass = 'amber';
  if (vStatus === 'APPROVED') vBadgeClass = 'green';
  else if (vStatus === 'REJECTED') vBadgeClass = 'coral';
  else if (vStatus === 'NEEDS_CORRECTION') vBadgeClass = 'teal';

  let aBadgeClass = aStatus === 'OFFICIAL_KEY_VERIFIED' ? 'green' : 'amber';

  container.innerHTML = `
    <!-- Top Inspection Bar -->
    <div style="padding:16px 20px;border-bottom:1px solid var(--border);background:var(--card-head, var(--card));display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:12px">
      <div>
        <div style="display:flex;align-items:center;gap:8px;margin-bottom:4px">
          <span style="font-size:17px;font-weight:800;color:var(--text)">Question #${q.question_number}</span>
          <span class="badge indigo">${q.exam_code} ${q.exam_year || ''}</span>
          <span class="badge grey">${q.subject_name || 'Subject'}</span>
          <span class="badge grey">${q.paper_identifier || ''}</span>
        </div>
        <div style="font-size:11.5px;color:var(--text-3)">
          Internal ID: <code>${q.id}</code> · Standard: ${q.standard_grade || 12}
        </div>
      </div>

      <!-- State Pills: Strictly Separated -->
      <div style="display:flex;gap:8px;align-items:center;flex-wrap:wrap">
        <div style="text-align:right">
          <div style="font-size:10px;text-transform:uppercase;color:var(--text-3);font-weight:700">Visual Review</div>
          <span class="badge ${vBadgeClass}">${vStatus}</span>
        </div>
        <div style="text-align:right">
          <div style="font-size:10px;text-transform:uppercase;color:var(--text-3);font-weight:700">Answer Key</div>
          <span class="badge ${aBadgeClass}">${aStatus}</span>
        </div>
        <div style="text-align:right">
          <div style="font-size:10px;text-transform:uppercase;color:var(--text-3);font-weight:700">Scoring Gate</div>
          <span class="badge ${isScoringEligible ? 'green' : 'coral'}">${isScoringEligible ? 'CLEARED' : 'BLOCKED'}</span>
        </div>
      </div>
    </div>

    <!-- Body Scroll Area -->
    <div style="padding:20px;max-height:calc(100vh - 340px);overflow-y:auto">
      
      <!-- Integrity Gate Banner -->
      ${!isScoringEligible ? `
        <div style="background:rgba(239, 68, 68, 0.08);border:1px solid rgba(239, 68, 68, 0.25);border-radius:8px;padding:12px 14px;margin-bottom:18px;display:flex;align-items:center;gap:12px">
          <div style="font-size:22px">🛡️</div>
          <div style="font-size:12px;color:var(--text-2);flex:1">
            <b style="color:var(--coral)">Not eligible for student practice or scoring.</b>
            Requires explicit visual approval, official NTA answer-key verification, and legal rights clearance.
            ${isQuarantined ? '<span style="color:var(--coral);font-weight:700"> Currently Quarantined.</span>' : ''}
          </div>
        </div>
      ` : `
        <div style="background:rgba(16, 185, 129, 0.08);border:1px solid rgba(16, 185, 129, 0.25);border-radius:8px;padding:12px 14px;margin-bottom:18px;display:flex;align-items:center;gap:12px">
          <div style="font-size:22px">✓</div>
          <div style="font-size:12px;color:var(--text-2);flex:1">
            <b style="color:var(--green)">All integrity gates passed.</b> Question is verified and eligible for scored practice.
          </div>
        </div>
      `}

      <!-- Question Stem & Diagram -->
      <div style="margin-bottom:20px">
        <div style="font-size:11px;font-weight:700;color:var(--text-3);text-transform:uppercase;margin-bottom:6px">Question Stem</div>
        <div style="font-size:14.5px;color:var(--text);line-height:1.6;padding:14px;background:var(--bg);border-radius:8px;border:1px solid var(--border)">
          ${q.question_text || '<em>No stem text found.</em>'}
        </div>

        ${isDiag ? `
          <div style="margin-top:14px;padding:14px;background:var(--card);border:1px solid var(--border);border-radius:8px">
            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:10px">
              <span style="font-size:12px;font-weight:700;color:var(--indigo)">Stem Diagram Asset</span>
              <a href="${q.diagram_asset_url}" target="_blank" style="font-size:11.5px;color:var(--indigo);text-decoration:none">
                Open Full Asset ↗
              </a>
            </div>
            <div style="text-align:center;padding:10px;background:var(--bg);border-radius:6px">
              <img src="${q.diagram_asset_url}" alt="Question ${q.question_number} Diagram" 
                style="max-height:260px;max-width:100%;object-fit:contain;border-radius:4px" />
            </div>
            <div style="margin-top:8px;font-size:11px;color:var(--text-3);font-family:monospace">
              Path: ${q.diagram_asset_url}
            </div>
          </div>
        ` : ''}
      </div>

      <!-- Options Grid -->
      <div style="margin-bottom:24px">
        <div style="font-size:11px;font-weight:700;color:var(--text-3);text-transform:uppercase;margin-bottom:8px">Answer Options</div>
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px">
          ${(q.options || []).map((opt: any) => {
            const isCorrect = opt.is_correct;
            return `
              <div style="padding:12px;border-radius:8px;border:1px solid ${isCorrect ? 'var(--green)' : 'var(--border)'};background:${isCorrect ? 'rgba(16, 185, 129, 0.05)' : 'var(--bg)'}">
                <div style="display:flex;align-items:center;gap:8px;margin-bottom:6px">
                  <span style="width:24px;height:24px;border-radius:50%;display:grid;place-items:center;font-size:12px;font-weight:800;background:${isCorrect ? 'var(--green)' : 'var(--border)'};color:${isCorrect ? '#fff' : 'var(--text-2)'}">
                    ${opt.option_key}
                  </span>
                  <span style="font-size:13px;color:var(--text);font-weight:600;flex:1">Option ${opt.option_key}</span>
                  ${isCorrect ? `<span class="badge green" style="font-size:10px">Declared Correct</span>` : ''}
                </div>
                <div style="font-size:13px;color:var(--text);line-height:1.45;margin-left:32px">
                  ${opt.option_text || ''}
                </div>
                ${opt.diagram_asset_url ? `
                  <div style="margin-top:8px;margin-left:32px">
                    <img src="${opt.diagram_asset_url}" alt="Option ${opt.option_key}" style="max-height:120px;border-radius:4px;border:1px solid var(--border)">
                  </div>
                ` : ''}
              </div>
            `;
          }).join('')}
        </div>
      </div>

      <!-- Audit History & Verification Timeline -->
      <div style="margin-bottom:24px">
        <div style="font-size:11px;font-weight:700;color:var(--text-3);text-transform:uppercase;margin-bottom:8px">Verification & Audit Log</div>
        <div style="background:var(--bg);border-radius:8px;border:1px solid var(--border);padding:12px">
          ${(q.audit_history && q.audit_history.length > 0) ? `
            <div style="display:flex;flex-direction:column;gap:8px">
              ${q.audit_history.map((log: any) => `
                <div style="font-size:12px;border-bottom:1px solid var(--border);padding-bottom:8px">
                  <div style="display:flex;justify-content:space-between;color:var(--text-2);margin-bottom:2px">
                    <span><b>${log.actor || 'System'}</b> (${log.action || 'REVIEW'})</span>
                    <span style="color:var(--text-3)">${new Date(log.created_at).toLocaleString()}</span>
                  </div>
                  <div style="color:var(--text);margin-top:2px">${log.notes || 'No review notes provided.'}</div>
                </div>
              `).join('')}
            </div>
          ` : `
            <div style="font-size:12px;color:var(--text-3);padding:8px 0;text-align:center">
              No previous human review actions recorded.
            </div>
          `}
        </div>
      </div>

      <!-- Reviewer Action Form -->
      <div style="background:var(--card);border:1px solid var(--border);border-radius:8px;padding:16px">
        <div style="font-size:13px;font-weight:800;color:var(--text);margin-bottom:12px">Record Audited Decision</div>
        
        <div style="display:flex;gap:12px;margin-bottom:14px">
          <label style="flex:1;cursor:pointer">
            <input type="radio" name="reviewDecisionRadio" value="APPROVED" 
              ${state.form.decision === 'APPROVED' ? 'checked' : ''} onchange="window.setReviewDecision('APPROVED')" style="display:none">
            <div id="btnDecisionApproved" style="padding:10px 14px;border-radius:6px;text-align:center;font-size:12.5px;font-weight:700;transition:all .15s ease;
                 border:2px solid ${state.form.decision === 'APPROVED' ? 'var(--green)' : 'var(--border)'};
                 background:${state.form.decision === 'APPROVED' ? 'rgba(16, 185, 129, 0.1)' : 'var(--bg)'};
                 color:${state.form.decision === 'APPROVED' ? 'var(--green)' : 'var(--text-2)'}">
              ✓ Approve Visual Asset
            </div>
          </label>

          <label style="flex:1;cursor:pointer">
            <input type="radio" name="reviewDecisionRadio" value="NEEDS_CORRECTION" 
              ${state.form.decision === 'NEEDS_CORRECTION' ? 'checked' : ''} onchange="window.setReviewDecision('NEEDS_CORRECTION')" style="display:none">
            <div id="btnDecisionNeedsCorrection" style="padding:10px 14px;border-radius:6px;text-align:center;font-size:12.5px;font-weight:700;transition:all .15s ease;
                 border:2px solid ${state.form.decision === 'NEEDS_CORRECTION' ? 'var(--teal)' : 'var(--border)'};
                 background:${state.form.decision === 'NEEDS_CORRECTION' ? 'rgba(20, 184, 166, 0.1)' : 'var(--bg)'};
                 color:${state.form.decision === 'NEEDS_CORRECTION' ? 'var(--teal)' : 'var(--text-2)'}">
              ⚠ Needs Correction
            </div>
          </label>

          <label style="flex:1;cursor:pointer">
            <input type="radio" name="reviewDecisionRadio" value="REJECTED" 
              ${state.form.decision === 'REJECTED' ? 'checked' : ''} onchange="window.setReviewDecision('REJECTED')" style="display:none">
            <div id="btnDecisionRejected" style="padding:10px 14px;border-radius:6px;text-align:center;font-size:12.5px;font-weight:700;transition:all .15s ease;
                 border:2px solid ${state.form.decision === 'REJECTED' ? 'var(--coral)' : 'var(--border)'};
                 background:${state.form.decision === 'REJECTED' ? 'rgba(239, 68, 68, 0.1)' : 'var(--bg)'};
                 color:${state.form.decision === 'REJECTED' ? 'var(--coral)' : 'var(--text-2)'}">
              ✕ Reject Asset
            </div>
          </label>
        </div>

        <div style="margin-bottom:12px">
          <label style="display:block;font-size:12px;font-weight:600;color:var(--text);margin-bottom:4px">
            Reviewer Audit Notes ${state.form.decision !== 'APPROVED' ? '<span style="color:var(--coral)">* (Required for Rejection or Correction)</span>' : '<span style="color:var(--text-3)">(Optional for Approval)</span>'}
          </label>
          <textarea id="reviewNotesInput" class="input" rows="3" placeholder="Provide clear observations on diagram fidelity, crop boundaries, or option alignment..." 
            oninput="window.setReviewNotes(this.value)" style="width:100%;font-size:12.5px;padding:8px 10px">${state.form.notes}</textarea>
        </div>

        ${state.form.error ? `
          <div style="color:var(--coral);font-size:12px;margin-bottom:10px">
            ⚠️ ${state.form.error}
          </div>
        ` : ''}

        <div style="display:flex;justify-content:flex-end;gap:10px">
          <button class="btn btn-primary" onclick="window.submitQuestionReviewDecision()" ${state.form.submitting ? 'disabled' : ''}>
            ${state.form.submitting ? 'Submitting Decision...' : 'Commit Audited Review'}
          </button>
        </div>
      </div>

    </div>
  `;
}

// Global Window Bindings for UI Interactivity
window.refreshReviewQueue = () => {
  fetchQueue();
};

window.handleReviewSearch = (val: string) => {
  state.filters.search = val;
  renderQueue();
};

window.handleReviewFilter = (key: string, val: string) => {
  (state.filters as any)[key] = val;
  fetchQueue();
};

window.setReviewDecision = (decision: 'APPROVED' | 'NEEDS_CORRECTION' | 'REJECTED') => {
  state.form.decision = decision;
  state.form.error = null;
  renderDetail();
};

window.setReviewNotes = (notes: string) => {
  state.form.notes = notes;
};

window.submitQuestionReviewDecision = async () => {
  if (!state.selectedQuestionId) return;

  const decision = state.form.decision;
  const notes = state.form.notes.trim();

  // Client-side validation enforcing required notes for non-approval
  if ((decision === 'REJECTED' || decision === 'NEEDS_CORRECTION') && notes.length < 5) {
    state.form.error = 'Reviewer audit notes of at least 5 characters are required for rejection or correction requests.';
    renderDetail();
    return;
  }

  state.form.submitting = true;
  state.form.error = null;
  renderDetail();

  try {
    const payload: any = {
      decision: decision,
      review_notes: notes || undefined,
    };

    if (state.selectedDetail && state.selectedDetail.diagram_asset_url) {
      payload.asset_ids_reviewed = [state.selectedDetail.diagram_asset_url];
    }

    await competitiveService.submitQuestionReview(state.selectedQuestionId, payload);
    toast(`Review decision committed: ${decision}`, '', 'good');

    // Reset notes
    state.form.notes = '';
    // Reload question detail and update queue item
    await selectReviewQuestion(state.selectedQuestionId);
    await fetchQueue();
  } catch (err: any) {
    state.form.error = err.message || 'Failed to submit review decision. Ensure you have authorized reviewer permissions.';
    renderDetail();
  } finally {
    state.form.submitting = false;
  }
};
