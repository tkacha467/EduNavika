// Interactive Quiz Runner Modal for EduNavika
// Integrated with real backend attempt telemetry

import { icon } from '../../utils/icons';
import { donut } from '../../utils/charts';
import { progressBar, openModal, closeOverlay, toast } from '../../components/common';
import { assessmentService } from '../../services/assessmentService';
import { authService } from '../../services/authService';

export interface QuizQuestion {
  q: string;
  o: string[];
  a: number;
  e: string;
  id?: string;
  topic_id?: string;
}

export interface ActiveQuiz {
  topic: string;
  topicId: string;
  questions: QuizQuestion[];
  index: number;
  answers: (number | null)[];
  startTime: number;
}

let CURRENT_QUIZ: ActiveQuiz | null = null;

const DEFAULT_QUIZ_BANK: Record<string, QuizQuestion[]> = {
  'Electricity & Circuits': [
    { q: 'Which quantity is measured in ohms?', o: ['Current', 'Voltage', 'Resistance', 'Power'], a: 2, e: 'Resistance is measured in ohms (Ω).' },
    { q: "Ohm's law states that —", o: ['V = IR', 'V = I/R', 'I = VR', 'R = VI'], a: 0, e: "Ohm's law: V = I × R." },
    { q: 'Two 4Ω resistors in series give —', o: ['2Ω', '4Ω', '8Ω', '16Ω'], a: 2, e: 'In series, R = R₁ + R₂ = 4 + 4 = 8Ω.' },
    { q: 'In a parallel circuit, the total resistance is —', o: ['The sum of resistances', 'Less than the smallest resistance', 'Equal to the largest resistance', 'Zero'], a: 1, e: 'Parallel resistance is always less than the smallest individual resistance.' },
    { q: 'Ammeter is always connected in —', o: ['Parallel', 'Series', 'Either way', 'Diagonal'], a: 1, e: 'An ammeter measures current and must be in series.' },
  ],
};

function generateFallbackQuestions(topic: string): QuizQuestion[] {
  if (DEFAULT_QUIZ_BANK[topic]) return DEFAULT_QUIZ_BANK[topic];
  return [
    { q: `Which of the following best describes "${topic}"?`, o: ['The core concept covered in this chapter', 'An unrelated topic', 'Only used in labs', 'A historical event'], a: 0, e: `This checks whether you recognise the core concept of ${topic}.` },
    { q: `A key idea in ${topic} is —`, o: ['The main principle studied', 'None of these', 'A different subject', 'Not applicable'], a: 0, e: 'It reinforces the main principle.' },
    { q: `A common application of ${topic} is —`, o: ['Real-world problem solving', 'Not applicable', 'Only in theory', 'Only in exams'], a: 0, e: `${topic} is applied in real contexts.` },
    { q: `The best way to strengthen ${topic} is —`, o: ['Practise varied questions', 'Skip it', 'Memorise blindly', 'Avoid revision'], a: 0, e: 'Varied practice builds durable understanding.' },
    { q: `A frequent mistake with ${topic} is —`, o: ['Skipping the definition', 'Reading the textbook', 'Asking questions', 'Revising regularly'], a: 0, e: 'Skipping definitions leads to weak grounding.' },
  ];
}

export function startQuiz(topic: string, topicId = 'm1', onFinishNavigate?: (route: string) => void) {
  const qs = generateFallbackQuestions(topic);
  CURRENT_QUIZ = {
    topic,
    topicId,
    questions: qs,
    index: 0,
    answers: new Array(qs.length).fill(null),
    startTime: Date.now(),
  };
  renderQuizModal(onFinishNavigate);
}

export function renderQuizModal(onFinishNavigate?: (route: string) => void) {
  if (!CURRENT_QUIZ) return;
  const q = CURRENT_QUIZ.questions[CURRENT_QUIZ.index];
  const sel = CURRENT_QUIZ.answers[CURRENT_QUIZ.index];
  const pct = Math.round(((CURRENT_QUIZ.index + 1) / CURRENT_QUIZ.questions.length) * 100);

  const modalEl = openModal(
    `
    <div class="modal-h">
      <div style="flex:1"><h3>${CURRENT_QUIZ.topic}</h3><div class="sub">Question ${CURRENT_QUIZ.index + 1} of ${CURRENT_QUIZ.questions.length}</div></div>
      <button class="btn btn-sm btn-icon" id="btnQuizClose">${icon('x')}</button>
    </div>
    <div style="padding:0 24px;margin-top:16px">${progressBar(pct, 'indigo')}</div>
    <div class="modal-b">
      <div style="font-size:15.5px;font-weight:600;line-height:1.5;margin-bottom:20px">${q.q}</div>
      ${q.o
        .map(
          (opt, i) => `
        <div class="quiz-option" data-idx="${i}" style="display:flex;align-items:center;gap:13px;padding:13px 16px;border:1.5px solid ${sel === i ? 'var(--indigo)' : 'var(--border)'};border-radius:var(--r-md);background:${sel === i ? 'var(--indigo-25)' : 'var(--surface)'};cursor:pointer;margin-bottom:10px;transition:.15s">
          <span style="width:26px;height:26px;border-radius:50%;background:${sel === i ? 'var(--indigo)' : 'var(--bg)'};color:${sel === i ? '#fff' : 'var(--text-2)'};display:grid;place-items:center;font-size:12px;font-weight:700;flex:0 0 auto">${'ABCD'[i]}</span>
          <span style="font-size:13.5px">${opt}</span>
        </div>`
        )
        .join('')}
      <div class="flex wrap gap-2 mt-5" style="padding-top:18px;border-top:1px solid var(--border-2)">
        ${CURRENT_QUIZ.questions
          .map(
            (_, i) => `
          <button class="quiz-nav-dot" data-qidx="${i}" style="width:28px;height:28px;border-radius:7px;background:${i === CURRENT_QUIZ!.index ? 'var(--indigo)' : CURRENT_QUIZ!.answers[i] !== null ? 'var(--green-50)' : 'var(--bg)'};color:${i === CURRENT_QUIZ!.index ? '#fff' : CURRENT_QUIZ!.answers[i] !== null ? 'var(--green)' : 'var(--text-3)'};font-size:11.5px;font-weight:700;border:1px solid ${i === CURRENT_QUIZ!.index ? 'var(--indigo)' : CURRENT_QUIZ!.answers[i] !== null ? 'rgba(46,155,104,.3)' : 'var(--border)'}">${i + 1}</button>`
          )
          .join('')}
      </div>
    </div>
    <div class="modal-f">
      <button class="btn" id="btnQuizPrev" ${CURRENT_QUIZ.index === 0 ? 'disabled' : ''}>Previous</button>
      ${
        CURRENT_QUIZ.index < CURRENT_QUIZ.questions.length - 1
          ? `<button class="btn btn-primary" id="btnQuizNext">Next ${icon('chevR')}</button>`
          : `<button class="btn btn-primary" id="btnQuizSubmit">${icon('check')} Submit</button>`
      }
    </div>`,
    { width: 'wide' }
  );

  // Wire up event listeners
  modalEl.querySelector('#btnQuizClose')?.addEventListener('click', () => {
    closeOverlay();
    CURRENT_QUIZ = null;
  });

  modalEl.querySelectorAll('.quiz-option').forEach(el => {
    el.addEventListener('click', () => {
      const idx = Number((el as HTMLElement).dataset.idx);
      if (CURRENT_QUIZ) {
        CURRENT_QUIZ.answers[CURRENT_QUIZ.index] = idx;
        renderQuizModal(onFinishNavigate);
      }
    });
  });

  modalEl.querySelectorAll('.quiz-nav-dot').forEach(el => {
    el.addEventListener('click', () => {
      const qidx = Number((el as HTMLElement).dataset.qidx);
      if (CURRENT_QUIZ) {
        CURRENT_QUIZ.index = qidx;
        renderQuizModal(onFinishNavigate);
      }
    });
  });

  modalEl.querySelector('#btnQuizPrev')?.addEventListener('click', () => {
    if (CURRENT_QUIZ && CURRENT_QUIZ.index > 0) {
      CURRENT_QUIZ.index--;
      renderQuizModal(onFinishNavigate);
    }
  });

  modalEl.querySelector('#btnQuizNext')?.addEventListener('click', () => {
    if (CURRENT_QUIZ && CURRENT_QUIZ.index < CURRENT_QUIZ.questions.length - 1) {
      CURRENT_QUIZ.index++;
      renderQuizModal(onFinishNavigate);
    }
  });

  modalEl.querySelector('#btnQuizSubmit')?.addEventListener('click', () => {
    handleQuizSubmit(onFinishNavigate);
  });
}

async function handleQuizSubmit(onFinishNavigate?: (route: string) => void) {
  if (!CURRENT_QUIZ) return;
  const user = authService.getUser();
  const studentId = user?.id || 'stu-tushar-kacha-001';
  let correct = 0;
  const total = CURRENT_QUIZ.questions.length;
  const durationMs = Date.now() - CURRENT_QUIZ.startTime;

  // Record attempts to backend asynchronously
  CURRENT_QUIZ.questions.forEach((q, i) => {
    const chosen = CURRENT_QUIZ!.answers[i];
    const isCorrect = chosen === q.a;
    if (isCorrect) correct++;

    if (chosen !== null) {
      assessmentService.recordAttempt({
        student_id: studentId,
        mcq_id: q.id || `mcq-${CURRENT_QUIZ!.topicId}-${i + 1}`,
        topic_id: CURRENT_QUIZ!.topicId,
        selected_option: 'ABCD'[chosen],
        is_correct: isCorrect,
        score: isCorrect ? 100 : 0,
        response_time_ms: Math.round(durationMs / total),
        hint_requested: false,
      });
    }
  });

  // Increment real user stats
  if (user) {
    user.todayGoal = (user.todayGoal || 0) + 1;
    user.streak = Math.max(1, user.streak || 1);
    user.weeklyGoal = Math.min(100, Math.round(((user.todayGoal || 1) / 3) * 100));
    if (typeof localStorage !== 'undefined') {
      localStorage.setItem('edunavika_user', JSON.stringify(user));
    }
  }

  const pct = Math.round((correct / total) * 100);
  const color = pct >= 75 ? '#2E9B68' : pct >= 55 ? '#E9A23B' : '#E56B6F';
  const label = pct >= 75 ? 'Excellent — well done!' : pct >= 55 ? 'Decent — a short revision will help.' : 'This topic needs another revision pass.';
  const tone = pct >= 75 ? 'good' : pct >= 55 ? 'warn' : 'bad';

  const resEl = openModal(
    `
    <div class="modal-h">
      <div style="flex:1"><h3>Result — ${CURRENT_QUIZ.topic}</h3></div>
      <button class="btn btn-sm btn-icon" id="btnResClose">${icon('x')}</button>
    </div>
    <div class="modal-b center">
      ${donut(pct, 150, 13, color)}
      <div class="h2 mt-4">${correct} of ${total} correct</div>
      <p class="body mt-2">${label}</p>
      <div class="grid g-3 mt-5">
        <div class="card pad-sm center"><div class="tiny">Score</div><div style="font-size:20px;font-weight:800;font-family:Manrope">${pct}%</div></div>
        <div class="card pad-sm center"><div class="tiny">Time</div><div style="font-size:20px;font-weight:800;font-family:Manrope">${Math.round(durationMs / 1000)}s</div></div>
        <div class="card pad-sm center"><div class="tiny">Knowledge impact</div><div style="font-size:20px;font-weight:800;font-family:Manrope;color:var(--green)">+5%</div></div>
      </div>
      <div class="ai-card mt-5" style="text-align:left">
        <div class="ai-head"><div class="ai-mark">${icon('sparkles')}</div><b>EduNavika Insight</b></div>
        <div class="ai-body">${pct >= 75 ? 'Strong performance. Your learning events have been persisted to the backend.' : 'Your accuracy on applied questions indicates review is needed. Topic has been noted for spaced revision.'}</div>
      </div>
    </div>
    <div class="modal-f">
      <button class="btn" id="btnResDone">Close</button>
      <button class="btn btn-primary" id="btnResPlan">${icon('refresh')} Update revision plan</button>
    </div>`,
    { width: 'wide' }
  );

  resEl.querySelector('#btnResClose')?.addEventListener('click', () => {
    closeOverlay();
    CURRENT_QUIZ = null;
  });
  resEl.querySelector('#btnResDone')?.addEventListener('click', () => {
    closeOverlay();
    CURRENT_QUIZ = null;
    if (typeof window !== 'undefined' && (window as any).navigate) {
      (window as any).navigate('student/dashboard');
    }
  });
  resEl.querySelector('#btnResPlan')?.addEventListener('click', () => {
    closeOverlay();
    CURRENT_QUIZ = null;
    if (onFinishNavigate) onFinishNavigate('student/revision');
  });

  toast('Assessment recorded', 'Learning events persisted to backend', tone);
}
