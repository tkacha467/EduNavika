// Assessment Builder Wizard Modal for EduNavika

import { icon } from '../../utils/icons';
import { openModal, closeOverlay, toast } from '../../components/common';

export interface BuilderState {
  step: number;
  subject: string;
  topic: string;
  count: number;
  questions: Array<{
    q: string;
    o: string[];
    a: number;
    diff: string;
  }>;
}

let BUILDER: BuilderState = {
  step: 0,
  subject: 'Physics',
  topic: '',
  count: 10,
  questions: [],
};

const TOPICS_BY_SUBJECT: Record<string, string[]> = {
  Physics: ['Electricity & Circuits', 'Light — Reflection & Refraction', 'Motion & Force'],
  Mathematics: ['Quadratic Equations', 'Trigonometry', 'Coordinate Geometry', 'Probability'],
  Chemistry: ['Chemical Reactions', 'Acids, Bases & Salts', 'Organic Chemistry'],
  Biology: ['Photosynthesis', 'Life Processes', 'Heredity & Evolution'],
  English: ['Reading Comprehension', 'Grammar — Tenses', 'Letter Writing'],
  'Social Studies': ['Nationalism in India', 'Resources & Development', 'Federalism'],
};

export function openAssessmentBuilder() {
  BUILDER = { step: 0, subject: 'Physics', topic: '', count: 10, questions: [] };
  renderBuilderModal();
}
export const openBuilder = openAssessmentBuilder;

export function renderBuilderModal() {
  const subjects = ['Mathematics', 'Physics', 'Chemistry', 'Biology', 'English', 'Social Studies'];
  let body = '';

  if (BUILDER.step === 0) {
    body = `
      <div class="field">
        <label>Subject</label>
        <div class="flex wrap gap-2">
          ${subjects
            .map(
              s =>
                `<button class="btn btn-sm b-subj-btn" data-subj="${s}" style="${
                  BUILDER.subject === s ? 'background:var(--indigo);color:#fff;border-color:var(--indigo)' : ''
                }">${s}</button>`
            )
            .join('')}
        </div>
      </div>
      <div class="field">
        <label>Topic</label>
        <div class="flex wrap gap-2 mb-3">
          ${(TOPICS_BY_SUBJECT[BUILDER.subject] || [])
            .map(
              t =>
                `<button class="btn btn-sm b-topic-btn" data-top="${t}" style="${
                  BUILDER.topic === t ? 'background:var(--indigo);color:#fff;border-color:var(--indigo)' : ''
                }">${t}</button>`
            )
            .join('')}
        </div>
        <input class="input" id="customTopicInput" placeholder="…or type a custom topic" value="${BUILDER.topic}">
      </div>
      <div class="field">
        <label>Number of questions</label>
        <div class="flex wrap gap-2">
          ${[5, 10, 15, 20]
            .map(
              n =>
                `<button class="btn btn-sm b-count-btn" data-cnt="${n}" style="${
                  BUILDER.count === n ? 'background:var(--indigo);color:#fff;border-color:var(--indigo)' : ''
                }">${n}</button>`
            )
            .join('')}
        </div>
      </div>
      <div class="ai-card">
        <div class="ai-head"><div class="ai-mark">${icon('bulb')}</div><b>How this works</b></div>
        <div class="ai-body">EduNavika AI will retrieve relevant curriculum content and generate fresh MCQs. You will review every question before publishing.</div>
      </div>`;
  } else if (BUILDER.step === 1) {
    body = `
      <div class="center mb-5">
        <div class="spinner mb-4"></div>
        <div class="h3">Generating your MCQ exam…</div>
        <p class="small mt-2">${BUILDER.topic || 'Topic'} · ${BUILDER.subject} · ${BUILDER.count} questions</p>
      </div>
      <div class="flex-c" style="gap:12px">
        ${[
          { l: 'Retrieving approved curriculum content', done: true },
          { l: 'Generating fresh MCQs from retrieved material', done: true },
          { l: 'Validating structure, answers and difficulty', done: false },
          { l: 'Checking against previously delivered questions', done: false },
        ]
          .map(
            s => `
          <div class="flex gap-3" style="font-size:13.5px;color:${s.done ? 'var(--text)' : 'var(--text-3)'}">
            <div style="width:20px;height:20px;border-radius:50%;display:grid;place-items:center;flex:0 0 auto;background:${s.done ? 'var(--green)' : 'var(--border)'};color:${s.done ? '#fff' : 'var(--text-3)'}">${s.done ? icon('check', 'ic-xs') : ''}</div>
            ${s.l}
          </div>`
          )
          .join('')}
      </div>`;
  } else {
    body = `
      <div class="flex-b mb-4">
        <div><div class="h4">${BUILDER.topic || 'Generated exam'}</div><div class="tiny">${BUILDER.subject} · ${BUILDER.questions.length} questions · validated</div></div>
        <span class="badge green">${icon('check', 'ic-xs')} Validated</span>
      </div>
      <div style="max-height:420px;overflow-y:auto;padding-right:6px">
        ${BUILDER.questions
          .map(
            (q, i) => `
          <div class="card pad mb-3" style="border:1px solid var(--border-2)">
            <div class="flex-b mb-3"><span class="badge indigo">Q${i + 1}</span><span class="badge grey">${q.diff}</span></div>
            <div style="font-size:13.5px;font-weight:600;margin-bottom:11px">${q.q}</div>
            ${q.o
              .map(
                (o, j) =>
                  `<div style="padding:5px 0;font-size:12.5px;color:${j === q.a ? 'var(--green)' : 'var(--text-2)'};font-weight:${j === q.a ? '600' : '400'}">${'ABCD'[j]}. ${o}${j === q.a ? ' ✓' : ''}</div>`
              )
              .join('')}
          </div>`
          )
          .join('')}
      </div>`;
  }

  const modalEl = openModal(
    `
    <div class="modal-h">
      <div style="flex:1"><h3>${icon('sparkles', 'ic-sm')} MCQ Exam Builder</h3><div class="sub">Real-time, curriculum-grounded question generation</div></div>
      <button class="btn btn-sm btn-icon" id="btnBuilderClose">${icon('x')}</button>
    </div>
    <div class="modal-b">${body}</div>
    <div class="modal-f">
      ${BUILDER.step === 2 ? `<button class="btn" id="btnBuilderRegen">${icon('refresh')} Regenerate</button>` : ''}
      ${BUILDER.step === 0 ? `<button class="btn btn-primary" id="btnBuilderGen">${icon('sparkles')} Generate exam</button>` : ''}
      ${BUILDER.step === 2 ? `<button class="btn btn-primary" id="btnBuilderPub">${icon('check')} Approve & publish</button>` : ''}
    </div>`,
    { width: 'wide' }
  );

  modalEl.querySelector('#btnBuilderClose')?.addEventListener('click', closeOverlay);

  modalEl.querySelectorAll('.b-subj-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      BUILDER.subject = (btn as HTMLElement).dataset.subj || 'Physics';
      BUILDER.topic = '';
      renderBuilderModal();
    });
  });

  modalEl.querySelectorAll('.b-topic-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      BUILDER.topic = (btn as HTMLElement).dataset.top || '';
      renderBuilderModal();
    });
  });

  const customInput = modalEl.querySelector('#customTopicInput') as HTMLInputElement | null;
  if (customInput) {
    customInput.addEventListener('input', () => {
      BUILDER.topic = customInput.value;
    });
  }

  modalEl.querySelectorAll('.b-count-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      BUILDER.count = Number((btn as HTMLElement).dataset.cnt || 10);
      renderBuilderModal();
    });
  });

  modalEl.querySelector('#btnBuilderGen')?.addEventListener('click', () => {
    if (!BUILDER.topic && customInput && customInput.value) {
      BUILDER.topic = customInput.value;
    }
    if (!BUILDER.topic) {
      toast('Please select a topic', '', 'warn');
      return;
    }
    BUILDER.step = 1;
    renderBuilderModal();
    setTimeout(() => {
      const diffs = ['Easy', 'Medium', 'Medium', 'Hard'];
      BUILDER.questions = Array.from({ length: BUILDER.count }, (_, i) => ({
        q: `Sample ${BUILDER.topic || BUILDER.subject} question ${i + 1}: which of the following is correct?`,
        o: ['The correct option', 'An alternative', 'Another option', 'None of these'],
        a: 0,
        diff: diffs[i % diffs.length],
      }));
      BUILDER.step = 2;
      renderBuilderModal();
    }, 1500);
  });

  modalEl.querySelector('#btnBuilderRegen')?.addEventListener('click', () => {
    BUILDER.step = 0;
    renderBuilderModal();
  });

  modalEl.querySelector('#btnBuilderPub')?.addEventListener('click', () => {
    closeOverlay();
    toast('Exam published', 'Grade 10 · Section A', 'good');
  });
}
