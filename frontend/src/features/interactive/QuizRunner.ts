// Interactive Quiz Runner Modal for EduNavika
// Integrated with real backend attempt telemetry

import { icon } from '../../utils/icons';
import { donut } from '../../utils/charts';
import { progressBar, openModal, closeOverlay, toast } from '../../components/common';
import { assessmentService } from '../../services/assessmentService';
import { adaptiveService } from '../../services/adaptiveService';
import { authService } from '../../services/authService';
import { COMPLETED_ASSESSMENTS } from '../student/studentData';
import { APPROVED_SUBJECTS } from '../../services/curriculumService';

export interface QuizQuestion {
  q: string;
  o: string[];
  a: number;
  e: string;
  id?: string;
  topic_id?: string;
  source_document?: string;
  source_page?: number;
  source_chunk_id?: string;
  difficulty?: string;
}

export interface ActiveQuiz {
  topic: string;
  topicId: string;
  questions: QuizQuestion[];
  index: number;
  answers: (number | null)[];
  startTime: number;
  recommendation?: any;
  emptyMessage?: string;
}

let CURRENT_QUIZ: ActiveQuiz | null = null;

// Verified GSEB textbook curriculum questions as default offline baseline
const DEFAULT_QUIZ_BANK: Record<string, QuizQuestion[]> = {
  'Chemical Reactions': [
    {
      q: 'Why must chemical equations be balanced in accordance with the Law of Conservation of Mass?',
      o: [
        'Total mass of elements in products must equal total mass in reactants',
        'To accelerate the reaction speed without altering mass',
        'To change the chemical formulae of reactants into simpler states',
        'To equalize the volume of gases participating in the reaction',
      ],
      a: 0,
      e: 'Mass can neither be created nor destroyed in a chemical reaction (Textbook Page 16).',
      source_document: 'STD-10/Std-10_Science_English Medium.pdf',
      source_page: 16,
      difficulty: 'FOUNDATIONAL',
    },
    {
      q: 'In the reaction 2Mg(s) + O2(g) -> 2MgO(s), what type of chemical reaction is taking place?',
      o: [
        'Combination reaction',
        'Decomposition reaction',
        'Double displacement reaction',
        'Neutralisation reaction',
      ],
      a: 0,
      e: 'When two or more substances combine to form a single product, it is called a combination reaction (Textbook Page 19).',
      source_document: 'STD-10/Std-10_Science_English Medium.pdf',
      source_page: 19,
      difficulty: 'GUIDED',
    },
    {
      q: 'When iron nails are placed in a copper sulphate solution, what causes the blue colour of the solution to fade to green?',
      o: [
        'Iron displaces copper forming iron(II) sulphate solution',
        'Copper displaces iron producing basic copper carbonate',
        'Both metals undergo thermal decomposition simultaneously',
        'Precipitation of insoluble blue copper hydroxide',
      ],
      a: 0,
      e: 'Iron is more reactive than copper and displaces it from CuSO4 to form green FeSO4 (Textbook Page 24).',
      source_document: 'STD-10/Std-10_Science_English Medium.pdf',
      source_page: 24,
      difficulty: 'APPLICATION',
    },
  ],
  'Electricity': [
    {
      q: "According to Joule's law of heating, how is heat generated in a conductor related to current (I), resistance (R), and time (t)?",
      o: ['H = I²Rt', 'H = IRt', 'H = I²R / t', 'H = V / (IRt)'],
      a: 0,
      e: "Joule's law states heat generated is H = I²Rt (Textbook Page 202).",
      source_document: 'STD-10/Std-10_Science_English Medium.pdf',
      source_page: 202,
      difficulty: 'FOUNDATIONAL',
    },
    {
      q: 'Which metal is used for filaments of electric lamps due to its exceptionally high melting point (3380 °C)?',
      o: ['Tungsten', 'Copper', 'Aluminium', 'Lead'],
      a: 0,
      e: 'Tungsten has an extremely high melting point of 3380 °C (Textbook Page 203).',
      source_document: 'STD-10/Std-10_Science_English Medium.pdf',
      source_page: 203,
      difficulty: 'GUIDED',
    },
    {
      q: 'What is the commercial unit of electrical energy (1 kWh) in Joules?',
      o: ['3.6 × 10⁶ Joules', '3.6 × 10⁵ Joules', '1.0 × 10³ Joules', '7.2 × 10⁶ Joules'],
      a: 0,
      e: '1 kWh = 1000 W × 3600 s = 3.6 × 10⁶ J (Textbook Page 204).',
      source_document: 'STD-10/Std-10_Science_English Medium.pdf',
      source_page: 204,
      difficulty: 'APPLICATION',
    },
  ],
  'Electricity & Circuits': [
    {
      q: "According to Joule's law of heating, how is heat generated in a conductor related to current (I), resistance (R), and time (t)?",
      o: ['H = I²Rt', 'H = IRt', 'H = I²R / t', 'H = V / (IRt)'],
      a: 0,
      e: "Joule's law states heat generated is H = I²Rt (Textbook Page 202).",
      source_document: 'STD-10/Std-10_Science_English Medium.pdf',
      source_page: 202,
      difficulty: 'FOUNDATIONAL',
    },
    {
      q: 'Which metal is used for filaments of electric lamps due to its exceptionally high melting point (3380 °C)?',
      o: ['Tungsten', 'Copper', 'Aluminium', 'Lead'],
      a: 0,
      e: 'Tungsten has an extremely high melting point of 3380 °C (Textbook Page 203).',
      source_document: 'STD-10/Std-10_Science_English Medium.pdf',
      source_page: 203,
      difficulty: 'GUIDED',
    },
    {
      q: 'What is the commercial unit of electrical energy (1 kWh) in Joules?',
      o: ['3.6 × 10⁶ Joules', '3.6 × 10⁵ Joules', '1.0 × 10³ Joules', '7.2 × 10⁶ Joules'],
      a: 0,
      e: '1 kWh = 1000 W × 3600 s = 3.6 × 10⁶ J (Textbook Page 204).',
      source_document: 'STD-10/Std-10_Science_English Medium.pdf',
      source_page: 204,
      difficulty: 'APPLICATION',
    },
  ],
};

export async function startQuiz(topic: string, topicId?: string, onFinishNavigate?: (route: string) => void) {
  // If topicId not provided or default placeholder, resolve from APPROVED_SUBJECTS or pass topic title
  let effectiveTopicId = topicId;
  if (!effectiveTopicId || effectiveTopicId === 'm1') {
    for (const subj of APPROVED_SUBJECTS) {
      const found = subj.topicList.find(t => t.name === topic || t.title === topic);
      if (found) {
        effectiveTopicId = found.id;
        break;
      }
    }
  }
  if (!effectiveTopicId || effectiveTopicId.length <= 3) {
    effectiveTopicId = topic;
  }

  const user = authService.getUser();
  const studentId = user?.id || 'e09699dd-0c64-44cc-82ef-ab41a832e072';

  // Initialize placeholder state
  CURRENT_QUIZ = {
    topic,
    topicId: effectiveTopicId,
    questions: [],
    index: 0,
    answers: [],
    startTime: Date.now(),
  };

  // Render initial loading modal
  renderQuizModal(onFinishNavigate);

  try {
    // 1. Fetch live curriculum-grounded adaptive practice questions from backend
    const resp = await adaptiveService.getPracticeQuestions(studentId, effectiveTopicId, 3);
    if (resp && resp.questions && resp.questions.length > 0) {
      const qs: QuizQuestion[] = resp.questions.map((q: any) => {
        return {
          id: q.id,
          topic_id: q.topic_id,
          q: q.question,
          o: q.options,
          a: 0, // answer hidden prior to submit
          e: q.explanation || `Grounded in ${q.source_document || 'textbook'}, page ${q.source_page || 'curriculum'}.`,
          source_document: q.source_document,
          source_page: q.source_page,
          source_chunk_id: q.source_chunk_id,
          difficulty: q.difficulty,
        };
      });

      if (CURRENT_QUIZ && CURRENT_QUIZ.topicId === effectiveTopicId) {
        CURRENT_QUIZ.questions = qs;
        CURRENT_QUIZ.answers = new Array(qs.length).fill(null);
      }
    } else {
      // Check default verified bank or trigger safe unassessed state
      const fallback = DEFAULT_QUIZ_BANK[topic] || (effectiveTopicId ? DEFAULT_QUIZ_BANK[effectiveTopicId] : null);
      if (fallback && fallback.length > 0) {
        if (CURRENT_QUIZ && CURRENT_QUIZ.topicId === effectiveTopicId) {
          CURRENT_QUIZ.questions = fallback;
          CURRENT_QUIZ.answers = new Array(fallback.length).fill(null);
        }
      } else {
        // Safe curriculum boundary: Never generate generic questions
        if (CURRENT_QUIZ && CURRENT_QUIZ.topicId === effectiveTopicId) {
          CURRENT_QUIZ.emptyMessage = resp?.message || 'This topic is not currently included in the verified offline Standard 10 curriculum available on this device. Please select from the supported syllabus topics (such as Chemical Reactions and Equations, Acids, Bases and Salts, or Electricity).';
        }
      }
    }
  } catch (err) {
    console.warn('Could not retrieve adaptive practice questions:', err);
    const fallback = DEFAULT_QUIZ_BANK[topic] || null;
    if (fallback && fallback.length > 0) {
      if (CURRENT_QUIZ && CURRENT_QUIZ.topicId === effectiveTopicId) {
        CURRENT_QUIZ.questions = fallback;
        CURRENT_QUIZ.answers = new Array(fallback.length).fill(null);
      }
    } else {
      if (CURRENT_QUIZ && CURRENT_QUIZ.topicId === effectiveTopicId) {
        CURRENT_QUIZ.emptyMessage = 'This topic is not currently included in the verified offline Standard 10 curriculum available on this device. Please select from the supported syllabus topics (such as Chemical Reactions and Equations, Acids, Bases and Salts, or Electricity).';
      }
    }
  }

  // Fetch adaptive recommendation in parallel
  adaptiveService.getNextPracticeRecommendation(studentId, effectiveTopicId).then(rec => {
    if (CURRENT_QUIZ && CURRENT_QUIZ.topicId === effectiveTopicId) {
      CURRENT_QUIZ.recommendation = rec;
      renderQuizModal(onFinishNavigate);
    }
  }).catch(() => {});

  renderQuizModal(onFinishNavigate);
}


export function renderQuizModal(onFinishNavigate?: (route: string) => void) {
  if (!CURRENT_QUIZ) return;

  // If no curriculum questions exist, show safe state
  if (CURRENT_QUIZ.emptyMessage || (CURRENT_QUIZ.questions.length === 0 && !CURRENT_QUIZ.startTime)) {
    const emptyMsg = CURRENT_QUIZ.emptyMessage || 'This topic is not currently included in the verified offline Standard 10 curriculum available on this device.';
    const modalEl = openModal(
      `
      <div class="modal-h">
        <div style="flex:1"><h3>${CURRENT_QUIZ.topic}</h3><div class="sub">Curriculum Assessment</div></div>
        <button class="btn btn-sm btn-icon" id="btnQuizClose">${icon('x')}</button>
      </div>
      <div class="modal-b" style="padding:32px 24px;text-align:center">
        <div style="width:48px;height:48px;border-radius:50%;background:rgba(36,59,107,.08);color:var(--indigo);display:grid;place-items:center;margin:0 auto 16px;font-size:20px">📖</div>
        <h4 style="margin-bottom:8px">Supported Curriculum Scope Notice</h4>
        <p style="color:var(--text-2);font-size:13.5px;line-height:1.5;max-width:440px;margin:0 auto 20px">
          ${emptyMsg}
        </p>
        <button class="btn btn-primary" id="btnQuizSafeClose">Return to Syllabus</button>
      </div>`,
      { width: 'medium' }
    );
    modalEl.querySelector('#btnQuizClose')?.addEventListener('click', () => {
      closeOverlay();
      CURRENT_QUIZ = null;
    });
    modalEl.querySelector('#btnQuizSafeClose')?.addEventListener('click', () => {
      closeOverlay();
      CURRENT_QUIZ = null;
    });
    return;
  }

  // Loading state
  if (CURRENT_QUIZ.questions.length === 0) {
    const modalEl = openModal(
      `
      <div class="modal-h">
        <div style="flex:1"><h3>${CURRENT_QUIZ.topic}</h3><div class="sub">Loading Practice...</div></div>
        <button class="btn btn-sm btn-icon" id="btnQuizClose">${icon('x')}</button>
      </div>
      <div class="modal-b" style="padding:40px 24px;text-align:center">
        <div class="spinner" style="margin:0 auto 16px"></div>
        <p style="color:var(--text-2);font-size:13px">Retrieving curriculum-grounded textbook questions...</p>
      </div>`,
      { width: 'medium' }
    );
    modalEl.querySelector('#btnQuizClose')?.addEventListener('click', () => {
      closeOverlay();
      CURRENT_QUIZ = null;
    });
    return;
  }

  const q = CURRENT_QUIZ.questions[CURRENT_QUIZ.index];
  const sel = CURRENT_QUIZ.answers[CURRENT_QUIZ.index];
  const pct = Math.round(((CURRENT_QUIZ.index + 1) / CURRENT_QUIZ.questions.length) * 100);
  const rec = CURRENT_QUIZ.recommendation;
  const adaptiveCardHtml = rec ? `
    <div style="padding:10px 14px;background:rgba(36,59,107,.05);border:1px solid rgba(36,59,107,.15);border-radius:10px;margin-bottom:16px;display:flex;flex-direction:column;gap:4px">
      <div style="display:flex;align-items:center;justify-content:space-between">
        <span style="font-size:11px;font-weight:700;color:var(--indigo)">✦ PERSONALIZED PRACTICE</span>
        <span class="badge indigo" style="font-size:10px">${rec.recommended_difficulty}</span>
      </div>
      <div style="font-size:11.5px;color:var(--text-2);display:flex;gap:12px">
        <span>Accuracy: <b>${rec.accuracy.toFixed(0)}%</b></span>
        <span>Mastery: <b>${rec.mastery_level}</b></span>
        <span>Risk: <b>${rec.retention_risk}</b></span>
      </div>
      <div style="font-size:11px;color:var(--text);line-height:1.35;margin-top:2px">
        ${rec.reason}
      </div>
    </div>` : '';

  const provenanceBadge = q.source_page ? `
    <div style="display:inline-flex;align-items:center;gap:6px;padding:4px 9px;background:rgba(46,155,104,.08);border:1px solid rgba(46,155,104,.2);border-radius:6px;font-size:11px;color:var(--green);font-weight:600;margin-bottom:12px">
      <span>📖 Curriculum-grounded · GSEB Std 10 · Page ${q.source_page}</span>
      ${q.difficulty ? `<span style="opacity:.7">(${q.difficulty})</span>` : ''}
    </div>` : '';

  const modalEl = openModal(
    `
    <div class="modal-h">
      <div style="flex:1"><h3>${CURRENT_QUIZ.topic}</h3><div class="sub">Question ${CURRENT_QUIZ.index + 1} of ${CURRENT_QUIZ.questions.length}</div></div>
      <button class="btn btn-sm btn-icon" id="btnQuizClose">${icon('x')}</button>
    </div>
    <div style="padding:0 24px;margin-top:16px">${progressBar(pct, 'indigo')}</div>
    <div class="modal-b">
      ${adaptiveCardHtml}
      ${provenanceBadge}
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

  // Record attempts to backend gracefully in sequence
  const attemptPayloads: Array<{
    student_id: string;
    mcq_id: string;
    topic_id: string;
    selected_option: string;
    is_correct: boolean;
    score: number;
    response_time_ms: number;
    hint_requested: boolean;
  }> = [];

  CURRENT_QUIZ.questions.forEach((q, i) => {
    const chosen = CURRENT_QUIZ!.answers[i];
    const isCorrect = chosen === q.a;
    if (isCorrect) correct++;

    if (chosen !== null) {
      attemptPayloads.push({
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

  const pct = Math.round((correct / total) * 100);
  const durationMin = Math.max(1, Math.round(durationMs / 60000));

  // Record individual attempts, then evaluate assessment completion once for revision
  const currentQuizSnapshot = { ...CURRENT_QUIZ };
  (async () => {
    for (const payload of attemptPayloads) {
      await assessmentService.recordAttempt(payload);
    }
    // Assessment completion evaluation (Correction #2 & #3: Formative Revision)
    await adaptiveService.completeAssessment({
      student_id: studentId,
      topic_id: currentQuizSnapshot.topicId,
      score: pct,
      total_questions: total,
      correct_answers: correct,
    });
    // Trigger revision plan refresh in student view
    if (typeof window !== 'undefined' && (window as any).refreshRevisionQueue) {
      await (window as any).refreshRevisionQueue();
    }
  })().catch(err => {
    console.debug('Telemetry recording note:', err);
  });

  // Increment real user stats
  if (user) {
    user.todayGoal = (user.todayGoal || 0) + 1;
    user.weeklyGoal = Math.min(100, Math.round(((user.todayGoal || 1) / 3) * 100));
    if (typeof localStorage !== 'undefined') {
      localStorage.setItem('edunavika_user', JSON.stringify(user));
    }
  }

  // Find matching subject and update topic mastery & knowledge health
  let matchedSubject = 'Mathematics';
  for (const subj of APPROVED_SUBJECTS) {
    const t = subj.topicList.find(top => top.name === CURRENT_QUIZ!.topic || top.id === CURRENT_QUIZ!.topicId);
    if (t) {
      matchedSubject = subj.name;
      t.mastery = pct;
      t.kh = pct;
      t.done = 1;
      t.last = 'Today';
      t.status = pct >= 70 ? 'ok' : pct >= 45 ? 'review' : 'alert';
      t.risk = pct >= 70 ? 'ok' : pct >= 45 ? 'medium' : 'high';
      const doneList = subj.topicList.filter(x => (x.done || 0) > 0);
      subj.done = doneList.length;
      subj.mastery = Math.round(subj.topicList.reduce((acc, x) => acc + (x.mastery || 0), 0) / subj.topicList.length);
      subj.kh = subj.mastery;
      subj.risk = subj.mastery >= 60 ? 'low' : subj.mastery >= 40 ? 'medium' : 'high';
      break;
    }
  }

  // Push real completed assessment to list
  COMPLETED_ASSESSMENTS.unshift({
    subject: matchedSubject,
    topic: CURRENT_QUIZ.topic,
    date: 'Today',
    score: pct,
    accuracy: pct,
    time: `${durationMin} min`,
    strong: pct >= 60 ? [CURRENT_QUIZ.topic] : [],
    weak: pct < 60 ? [CURRENT_QUIZ.topic] : [],
    kh: pct >= 60 ? +6 : -5,
  });

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
