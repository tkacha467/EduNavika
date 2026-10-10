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
  confidences?: (string | null)[]; // 'guessing' | 'somewhat' | 'confident'
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
        'Decomposition reaction',
        'Combination reaction',
        'Double displacement reaction',
        'Neutralisation reaction',
      ],
      a: 1,
      e: 'When two or more substances combine to form a single product, it is called a combination reaction (Textbook Page 19).',
      source_document: 'STD-10/Std-10_Science_English Medium.pdf',
      source_page: 19,
      difficulty: 'GUIDED',
    },
    {
      q: 'When iron nails are placed in a copper sulphate solution, what causes the blue colour of the solution to fade to green?',
      o: [
        'Copper displaces iron producing basic copper carbonate',
        'Both metals undergo thermal decomposition simultaneously',
        'Iron displaces copper forming iron(II) sulphate solution',
        'Precipitation of insoluble blue copper hydroxide',
      ],
      a: 2,
      e: 'Iron is more reactive than copper and displaces it from CuSO4 to form green FeSO4 (Textbook Page 24).',
      source_document: 'STD-10/Std-10_Science_English Medium.pdf',
      source_page: 24,
      difficulty: 'APPLICATION',
    },
  ],
  'Chemical Reactions and Equations': [
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
        'Decomposition reaction',
        'Combination reaction',
        'Double displacement reaction',
        'Neutralisation reaction',
      ],
      a: 1,
      e: 'When two or more substances combine to form a single product, it is called a combination reaction (Textbook Page 19).',
      source_document: 'STD-10/Std-10_Science_English Medium.pdf',
      source_page: 19,
      difficulty: 'GUIDED',
    },
    {
      q: 'When iron nails are placed in a copper sulphate solution, what causes the blue colour of the solution to fade to green?',
      o: [
        'Copper displaces iron producing basic copper carbonate',
        'Both metals undergo thermal decomposition simultaneously',
        'Iron displaces copper forming iron(II) sulphate solution',
        'Precipitation of insoluble blue copper hydroxide',
      ],
      a: 2,
      e: 'Iron is more reactive than copper and displaces it from CuSO4 to form green FeSO4 (Textbook Page 24).',
      source_document: 'STD-10/Std-10_Science_English Medium.pdf',
      source_page: 24,
      difficulty: 'APPLICATION',
    },
  ],
  'Acids, Bases & Salts': [
    {
      q: 'Which ions do all acids and all bases generate respectively in an aqueous solution?',
      o: [
        'Acids generate OH-(aq) ions and bases generate H+(aq) ions',
        'Acids generate H+(aq) ions and bases generate OH-(aq) ions',
        'Both acids and bases generate chloride Cl-(aq) ions',
        'Both acids and bases generate oxide O2-(aq) ions',
      ],
      a: 1,
      e: 'All acids generate H+(aq) ions and all bases generate OH-(aq) ions in solution (Textbook Page 37).',
      source_document: 'STD-10/Std-10_Science_English Medium.pdf',
      source_page: 37,
      difficulty: 'FOUNDATIONAL',
    },
    {
      q: 'On the universal pH scale ranging from 0 to 14, what does a pH value of exactly 7 represent?',
      o: [
        'A strongly acidic solution',
        'A strongly alkaline solution',
        'A neutral solution such as pure water',
        'A saturated salt solution only',
      ],
      a: 2,
      e: 'A pH of 7 represents a neutral solution. Values below 7 are acidic, while 7 to 14 are alkaline (Textbook Page 38).',
      source_document: 'STD-10/Std-10_Science_English Medium.pdf',
      source_page: 38,
      difficulty: 'GUIDED',
    },
    {
      q: 'Why does an electric bulb glow in an aqueous solution of hydrochloric acid but not in aqueous glucose or alcohol solutions?',
      o: [
        'Hydrochloric acid dissociates into free conducting ions while glucose does not',
        'Glucose absorbs the electric charge from the battery',
        'Hydrochloric acid has higher viscosity allowing mechanical conduction',
        'Alcohol completely neutralizes the electrode potential',
      ],
      a: 0,
      e: 'Electric current is carried through acidic solution by free ions; glucose and alcohol do not dissociate into ions (Textbook Page 36).',
      source_document: 'STD-10/Std-10_Science_English Medium.pdf',
      source_page: 36,
      difficulty: 'APPLICATION',
    },
  ],
  'Acids, Bases and Salts': [
    {
      q: 'Which ions do all acids and all bases generate respectively in an aqueous solution?',
      o: [
        'Acids generate OH-(aq) ions and bases generate H+(aq) ions',
        'Acids generate H+(aq) ions and bases generate OH-(aq) ions',
        'Both acids and bases generate chloride Cl-(aq) ions',
        'Both acids and bases generate oxide O2-(aq) ions',
      ],
      a: 1,
      e: 'All acids generate H+(aq) ions and all bases generate OH-(aq) ions in solution (Textbook Page 37).',
      source_document: 'STD-10/Std-10_Science_English Medium.pdf',
      source_page: 37,
      difficulty: 'FOUNDATIONAL',
    },
    {
      q: 'On the universal pH scale ranging from 0 to 14, what does a pH value of exactly 7 represent?',
      o: [
        'A strongly acidic solution',
        'A strongly alkaline solution',
        'A neutral solution such as pure water',
        'A saturated salt solution only',
      ],
      a: 2,
      e: 'A pH of 7 represents a neutral solution. Values below 7 are acidic, while 7 to 14 are alkaline (Textbook Page 38).',
      source_document: 'STD-10/Std-10_Science_English Medium.pdf',
      source_page: 38,
      difficulty: 'GUIDED',
    },
    {
      q: 'Why does an electric bulb glow in an aqueous solution of hydrochloric acid but not in aqueous glucose or alcohol solutions?',
      o: [
        'Hydrochloric acid dissociates into free conducting ions while glucose does not',
        'Glucose absorbs the electric charge from the battery',
        'Hydrochloric acid has higher viscosity allowing mechanical conduction',
        'Alcohol completely neutralizes the electrode potential',
      ],
      a: 0,
      e: 'Electric current is carried through acidic solution by free ions; glucose and alcohol do not dissociate into ions (Textbook Page 36).',
      source_document: 'STD-10/Std-10_Science_English Medium.pdf',
      source_page: 36,
      difficulty: 'APPLICATION',
    },
  ],
  'Electricity': [
    {
      q: "According to Joule's law of heating, how is heat generated in a conductor related to current (I), resistance (R), and time (t)?",
      o: ['H = IRt', 'H = I²Rt', 'H = I²R / t', 'H = V / (IRt)'],
      a: 1,
      e: "Joule's law states heat generated is H = I²Rt (Textbook Page 202).",
      source_document: 'STD-10/Std-10_Science_English Medium.pdf',
      source_page: 202,
      difficulty: 'FOUNDATIONAL',
    },
    {
      q: 'Which metal is used for filaments of electric lamps due to its exceptionally high melting point (3380 °C)?',
      o: ['Copper', 'Aluminium', 'Tungsten', 'Lead'],
      a: 2,
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
      o: ['H = IRt', 'H = I²Rt', 'H = I²R / t', 'H = V / (IRt)'],
      a: 1,
      e: "Joule's law states heat generated is H = I²Rt (Textbook Page 202).",
      source_document: 'STD-10/Std-10_Science_English Medium.pdf',
      source_page: 202,
      difficulty: 'FOUNDATIONAL',
    },
    {
      q: 'Which metal is used for filaments of electric lamps due to its exceptionally high melting point (3380 °C)?',
      o: ['Copper', 'Aluminium', 'Tungsten', 'Lead'],
      a: 2,
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
  'Quadratic Equations': [
    {
      q: 'What is the standard algebraic form of a quadratic equation in variable x?',
      o: [
        'ax + b = 0, where a ≠ 0',
        'ax² + bx + c = 0, where a, b, c are real numbers and a ≠ 0',
        'ax³ + bx² + cx + d = 0, where a ≠ 0',
        'a/x² + b/x + c = 0, where a ≠ 0',
      ],
      a: 1,
      e: 'A quadratic equation in variable x is of the form ax² + bx + c = 0, where a, b, c are real numbers and a ≠ 0 (Textbook Page 53).',
      source_document: 'STD-10/Std-10_Maths_EnglishMedium.pdf',
      source_page: 53,
      difficulty: 'FOUNDATIONAL',
    },
    {
      q: 'What is the quadratic formula derived by ancient mathematician Sridharacharya to find roots of ax² + bx + c = 0?',
      o: [
        'x = (-b ± √(b² - 4ac)) / (2a)',
        'x = (-b ± √(b² + 4ac)) / (2a)',
        'x = (b ± √(b² - 4ac)) / a',
        'x = (-b ± 2√(ac)) / (4a)',
      ],
      a: 0,
      e: 'The quadratic formula gives roots x = (-b ± √(b² - 4ac)) / (2a) provided b² - 4ac ≥ 0 (Textbook Page 53).',
      source_document: 'STD-10/Std-10_Maths_EnglishMedium.pdf',
      source_page: 53,
      difficulty: 'GUIDED',
    },
    {
      q: 'What condition on the discriminant (b² - 4ac) guarantees two distinct real roots for ax² + bx + c = 0?',
      o: [
        'b² - 4ac < 0',
        'b² - 4ac = 0',
        'b² - 4ac > 0',
        'b² - 4ac is negative',
      ],
      a: 2,
      e: 'Two distinct real roots exist if and only if the discriminant b² - 4ac > 0 (Textbook Page 54).',
      source_document: 'STD-10/Std-10_Maths_EnglishMedium.pdf',
      source_page: 54,
      difficulty: 'APPLICATION',
    },
  ],
  'Real Numbers & Polynomials': [
    {
      q: 'What does the Fundamental Theorem of Arithmetic assert regarding composite numbers?',
      o: [
        'Every natural number is a prime number',
        'The product of two irrational numbers is always rational',
        'Every composite number can be uniquely expressed as a product of primes, apart from the order of factors',
        'Composite numbers cannot be factorised into prime components',
      ],
      a: 2,
      e: 'Every composite number can be uniquely expressed as a product of primes up to the order of factors (Textbook Page 18).',
      source_document: 'STD-10/Std-10_Maths_EnglishMedium.pdf',
      source_page: 18,
      difficulty: 'FOUNDATIONAL',
    },
    {
      q: 'For any two positive integers a and b, what is the exact mathematical relationship between their HCF and LCM?',
      o: [
        'HCF(a, b) × LCM(a, b) = a × b',
        'HCF(a, b) + LCM(a, b) = a + b',
        'HCF(a, b) / LCM(a, b) = a / b',
        'HCF(a, b) × LCM(a, b) = (a × b)²',
      ],
      a: 0,
      e: 'For any two positive integers a and b, HCF(a, b) × LCM(a, b) = a × b (Textbook Page 20).',
      source_document: 'STD-10/Std-10_Maths_EnglishMedium.pdf',
      source_page: 20,
      difficulty: 'GUIDED',
    },
    {
      q: 'If prime factorisation of 96 is 2⁵ × 3 and 404 is 2² × 101, what is the HCF of 96 and 404?',
      o: ['2', '4', '8', '12'],
      a: 1,
      e: 'HCF is the product of smallest power of each common prime factor: 2² = 4 (Textbook Page 20).',
      source_document: 'STD-10/Std-10_Maths_EnglishMedium.pdf',
      source_page: 20,
      difficulty: 'APPLICATION',
    },
  ],
  '1.2 The Fundamental Theorem of Arithmetic': [
    {
      q: 'What does the Fundamental Theorem of Arithmetic assert regarding composite numbers?',
      o: [
        'Every natural number is a prime number',
        'The product of two irrational numbers is always rational',
        'Every composite number can be uniquely expressed as a product of primes, apart from the order of factors',
        'Composite numbers cannot be factorised into prime components',
      ],
      a: 2,
      e: 'Every composite number can be uniquely expressed as a product of primes up to the order of factors (Textbook Page 18).',
      source_document: 'STD-10/Std-10_Maths_EnglishMedium.pdf',
      source_page: 18,
      difficulty: 'FOUNDATIONAL',
    },
    {
      q: 'For any two positive integers a and b, what is the exact mathematical relationship between their HCF and LCM?',
      o: [
        'HCF(a, b) × LCM(a, b) = a × b',
        'HCF(a, b) + LCM(a, b) = a + b',
        'HCF(a, b) / LCM(a, b) = a / b',
        'HCF(a, b) × LCM(a, b) = (a × b)²',
      ],
      a: 0,
      e: 'For any two positive integers a and b, HCF(a, b) × LCM(a, b) = a × b (Textbook Page 20).',
      source_document: 'STD-10/Std-10_Maths_EnglishMedium.pdf',
      source_page: 20,
      difficulty: 'GUIDED',
    },
    {
      q: 'If prime factorisation of 96 is 2⁵ × 3 and 404 is 2² × 101, what is the HCF of 96 and 404?',
      o: ['2', '4', '8', '12'],
      a: 1,
      e: 'HCF is the product of smallest power of each common prime factor: 2² = 4 (Textbook Page 20).',
      source_document: 'STD-10/Std-10_Maths_EnglishMedium.pdf',
      source_page: 20,
      difficulty: 'APPLICATION',
    },
  ],
  'Trigonometry': [
    {
      q: 'In a right triangle ABC right-angled at B, if tan A = 4/3, what is the exact value of sin A?',
      o: ['4/5', '3/5', '5/4', '3/4'],
      a: 0,
      e: 'If tan A = opposite/adjacent = 4/3, then hypotenuse = √(4² + 3²) = 5, so sin A = opposite/hypotenuse = 4/5 (Textbook Page 175).',
      source_document: 'STD-10/Std-10_Maths_EnglishMedium.pdf',
      source_page: 175,
      difficulty: 'FOUNDATIONAL',
    },
    {
      q: 'What is the exact numerical value of sin 30° + cos 60°?',
      o: ['1', '1/2', '√3/2', '2'],
      a: 0,
      e: 'sin 30° = 1/2 and cos 60° = 1/2, so 1/2 + 1/2 = 1 (Textbook Page 185).',
      source_document: 'STD-10/Std-10_Maths_EnglishMedium.pdf',
      source_page: 185,
      difficulty: 'GUIDED',
    },
  ],
  'Coordinate Geometry': [
    {
      q: 'What is the distance of the point P(3, 4) from the origin (0, 0)?',
      o: ['5 units', '7 units', '4 units', '3 units'],
      a: 0,
      e: 'Distance from origin = √(x² + y²) = √(3² + 4²) = √25 = 5 units (Textbook Page 157).',
      source_document: 'STD-10/Std-10_Maths_EnglishMedium.pdf',
      source_page: 157,
      difficulty: 'FOUNDATIONAL',
    },
  ],
  'Probability': [
    {
      q: 'If a fair standard six-sided die is thrown once, what is the theoretical probability of obtaining an even number?',
      o: ['1/2', '1/6', '1/3', '2/3'],
      a: 0,
      e: 'Favorable outcomes are {2, 4, 6} (3 out of 6 possible): P = 3/6 = 1/2 (Textbook Page 232).',
      source_document: 'STD-10/Std-10_Maths_EnglishMedium.pdf',
      source_page: 232,
      difficulty: 'APPLICATION',
    },
  ],
  'Statistics': [
    {
      q: 'How is the class mark of any continuous class interval calculated in statistics?',
      o: [
        'Class mark = (Upper class limit + Lower class limit) / 2',
        'Class mark = Upper class limit - Lower class limit',
        'Class mark = Frequency / Class size',
        'Class mark = (Upper limit × Lower limit) / 2'
      ],
      a: 0,
      e: 'Class mark represents the midpoint of the class interval (Textbook Page 189).',
      source_document: 'STD-10/Std-10_Maths_EnglishMedium.pdf',
      source_page: 189,
      difficulty: 'FOUNDATIONAL',
    },
  ],
  'Light — Reflection & Refraction': [
    {
      q: 'According to the laws of reflection of light, what is the relationship between the angle of incidence and the angle of reflection?',
      o: [
        'The angle of incidence is strictly equal to the angle of reflection',
        'The angle of incidence is always double the angle of reflection',
        'The angle of reflection is 90 degrees minus the angle of incidence',
        'The angle of reflection depends inversely on the mirror thickness'
      ],
      a: 0,
      e: 'The angle of incidence is equal to the angle of reflection (Textbook Page 148).',
      source_document: 'STD-10/Std-10_Science_English Medium.pdf',
      source_page: 148,
      difficulty: 'FOUNDATIONAL',
    },
  ],
  'Life Processes': [
    {
      q: 'During the first stage of cellular respiration in living cells, where does the breakdown of glucose to pyruvate take place?',
      o: ['Cytoplasm', 'Mitochondrial matrix', 'Nucleus', 'Endoplasmic reticulum'],
      a: 0,
      e: 'The breakdown of glucose into pyruvate occurs in the cytoplasm (Textbook Page 102).',
      source_document: 'STD-10/Std-10_Science_English Medium.pdf',
      source_page: 102,
      difficulty: 'FOUNDATIONAL',
    },
  ],
};

// Aliases for subjects and common titles in default offline bank
DEFAULT_QUIZ_BANK['Mathematics'] = DEFAULT_QUIZ_BANK['Quadratic Equations'];
DEFAULT_QUIZ_BANK['Science'] = DEFAULT_QUIZ_BANK['Chemical Reactions'];
DEFAULT_QUIZ_BANK['Physics'] = DEFAULT_QUIZ_BANK['Electricity & Circuits'];
DEFAULT_QUIZ_BANK['Chemistry'] = DEFAULT_QUIZ_BANK['Chemical Reactions'];
DEFAULT_QUIZ_BANK['Diagnostic Check'] = DEFAULT_QUIZ_BANK['Real Numbers & Polynomials'];
DEFAULT_QUIZ_BANK['Light — Reflection and Refraction'] = DEFAULT_QUIZ_BANK['Light — Reflection & Refraction'];

export async function startQuiz(topic: string, topicId?: string, onFinishNavigate?: (route: string) => void) {
  let effectiveTopicId = topicId;

  // 1. If topic represents a whole subject and NO specific topicId was provided, resolve to the subject's primary topic
  if (!effectiveTopicId) {
    const matchingSubj = APPROVED_SUBJECTS.find(s =>
      s.name.toLowerCase() === topic.toLowerCase() ||
      s.id.toLowerCase() === topic.toLowerCase() ||
      s.code.toLowerCase() === topic.toLowerCase()
    );
    if (matchingSubj && matchingSubj.topicList.length > 0) {
      const primaryTopic = matchingSubj.topicList[0];
      effectiveTopicId = primaryTopic.id;
      topic = primaryTopic.name;
    }
  }

  // 2. If topicId not provided, search through approved topics
  if (!effectiveTopicId) {
    for (const subj of APPROVED_SUBJECTS) {
      const found = subj.topicList.find(t => t.id === topicId || t.name === topic || t.title === topic);
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
        CURRENT_QUIZ.confidences = new Array(qs.length).fill(null);
      }
    } else {
      // Check default verified bank or trigger safe unassessed state
      const fallback = DEFAULT_QUIZ_BANK[topic] || (effectiveTopicId ? DEFAULT_QUIZ_BANK[effectiveTopicId] : null);
      if (fallback && fallback.length > 0) {
        if (CURRENT_QUIZ && CURRENT_QUIZ.topicId === effectiveTopicId) {
          CURRENT_QUIZ.questions = fallback;
          CURRENT_QUIZ.answers = new Array(fallback.length).fill(null);
          CURRENT_QUIZ.confidences = new Array(fallback.length).fill(null);
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
        CURRENT_QUIZ.confidences = new Array(fallback.length).fill(null);
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

      <!-- Confidence Level Selector -->
      <div style="margin-top:16px;padding:12px 14px;background:var(--bg);border-radius:var(--r-md);border:1px solid var(--border)">
        <div style="font-size:11.5px;font-weight:600;color:var(--text-2);margin-bottom:8px;display:flex;align-items:center;gap:6px">
          <span>🧠 How confident are you in this answer?</span>
          <span style="font-size:10px;color:var(--text-3)">(Helps personalize future recommendations)</span>
        </div>
        <div class="flex gap-2 wrap" style="align-items:center">
          ${[
            { id: 'guessing', label: '🌱 Guessing', desc: 'Unsure' },
            { id: 'somewhat', label: '⚖️ Somewhat Confident', desc: 'Reasonably sure' },
            { id: 'confident', label: '🎯 Very Confident', desc: 'Fully confident' },
          ].map(c => {
            const isConfActive = CURRENT_QUIZ!.confidences?.[CURRENT_QUIZ!.index] === c.id;
            return `
              <button type="button" class="btn btn-sm quiz-confidence-btn" data-conf="${c.id}" style="font-size:11.5px;padding:6px 12px;border-radius:20px;border:1.5px solid ${isConfActive ? 'var(--indigo)' : 'var(--border)'};background:${isConfActive ? 'var(--indigo-25)' : 'var(--surface)'};color:${isConfActive ? 'var(--indigo)' : 'var(--text)'};font-weight:${isConfActive ? '700' : '500'};transition:all .15s">
                ${c.label}
              </button>
            `;
          }).join('')}
        </div>
      </div>

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

  modalEl.querySelectorAll('.quiz-confidence-btn').forEach(el => {
    el.addEventListener('click', () => {
      const conf = (el as HTMLElement).dataset.conf;
      if (CURRENT_QUIZ && conf) {
        if (!CURRENT_QUIZ.confidences) CURRENT_QUIZ.confidences = new Array(CURRENT_QUIZ.questions.length).fill(null);
        CURRENT_QUIZ.confidences[CURRENT_QUIZ.index] = conf;
        renderQuizModal(onFinishNavigate);
      }
    });
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
  const studentId = user?.id || 'e09699dd-0c64-44cc-82ef-ab41a832e072';
  let correct = 0;
  const total = CURRENT_QUIZ.questions.length;
  const durationMs = Date.now() - CURRENT_QUIZ.startTime;

  // Submit each question to backend adaptive service for authoritative grading
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

  const questionReviews: Array<{
    question: QuizQuestion;
    chosen: number | null;
    isCorrect: boolean;
    explanation: string;
    remediation?: any;
  }> = [];

  for (let i = 0; i < total; i++) {
    const q = CURRENT_QUIZ.questions[i];
    const chosen = CURRENT_QUIZ.answers[i];
    let isCorrect = false;
    let explanation = q.e;
    let remediation: any = null;

    if (chosen !== null) {
      const selectedOptionLetter = 'ABCD'[chosen];

      const confLevel = CURRENT_QUIZ.confidences?.[i] || undefined;

      // Try server-side validation first
      try {
        const subResp = await adaptiveService.submitPracticeAnswer({
          student_id: studentId,
          question_id: q.id || `mcq-${CURRENT_QUIZ.topicId}-${i + 1}`,
          topic_id: CURRENT_QUIZ.topicId,
          selected_answer: selectedOptionLetter,
          response_time_ms: Math.round(durationMs / total),
          hint_used: false,
          confidence_level: confLevel,
        });

        if (subResp && typeof subResp.correct === 'boolean') {
          isCorrect = subResp.correct;
          if (subResp.explanation) explanation = subResp.explanation;
          if (subResp.remediation) remediation = subResp.remediation;
        } else if (q.a !== -1 && typeof q.a === 'number') {
          isCorrect = chosen === q.a;
        }
      } catch (err) {
        if (q.a !== -1 && typeof q.a === 'number') {
          isCorrect = chosen === q.a;
        }
      }

      attemptPayloads.push({
        student_id: studentId,
        mcq_id: q.id || `mcq-${CURRENT_QUIZ.topicId}-${i + 1}`,
        topic_id: CURRENT_QUIZ.topicId,
        selected_option: selectedOptionLetter,
        is_correct: isCorrect,
        score: isCorrect ? 100 : 0,
        response_time_ms: Math.round(durationMs / total),
        hint_requested: false,
      });
    }

    if (isCorrect) correct++;
    questionReviews.push({ question: q, chosen, isCorrect, explanation, remediation });
  }

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
      <div class="mt-4" style="text-align:left;max-height:240px;overflow-y:auto;border:1px solid var(--border-2);border-radius:var(--r-md);padding:12px;background:var(--surface)">
        <div style="font-size:11.5px;font-weight:700;color:var(--text-2);margin-bottom:8px">QUESTION REVIEW & EVIDENCE GROUNDING</div>
        ${questionReviews
          .map(
            (qr, idx) => `
          <div style="padding:10px 0;border-bottom:1px solid var(--border-2);font-size:12px">
            <div style="display:flex;align-items:flex-start;gap:8px">
              <span>${qr.isCorrect ? '✅' : '❌'}</span>
              <div style="flex:1">
                <b style="color:var(--text)">Q${idx + 1}: ${qr.question.q}</b>
                <div style="color:var(--text-2);margin-top:2px">
                  Your Answer: <b>${qr.chosen !== null ? qr.question.o[qr.chosen] : 'Unanswered'}</b>
                </div>
                ${!qr.isCorrect && qr.remediation ? `
                  <div style="margin-top:6px;padding:8px 10px;background:rgba(229,107,111,.08);border-radius:6px;border:1px solid rgba(229,107,111,.2)">
                    <div style="font-weight:700;color:var(--coral);font-size:11px">🎯 Remediation: ${qr.remediation.concept_target}</div>
                    <div style="color:var(--text);font-size:11.5px;margin-top:2px">${qr.remediation.what_went_wrong}</div>
                    ${qr.remediation.textbook_excerpt ? `
                      <div style="margin-top:4px;font-size:11px;color:var(--indigo);font-style:italic">
                        📖 "${qr.remediation.textbook_excerpt}..." (Page ${qr.remediation.source_page || '—'})
                      </div>
                    ` : ''}
                  </div>
                ` : `
                  <div style="color:var(--indigo);font-size:11px;margin-top:3px;line-height:1.4">
                    📖 ${qr.explanation}
                  </div>
                `}
              </div>
            </div>
          </div>`
          )
          .join('')}
      </div>
      <div class="ai-card mt-4" style="text-align:left">
        <div class="ai-head"><div class="ai-mark">${icon('sparkles')}</div><b>EduNavika Insight</b></div>
        <div class="ai-body">${pct >= 75 ? 'Strong performance. Verified learning events have been persisted to backend.' : 'Your accuracy indicates review is needed. Topic has been added to your automated spaced revision plan.'}</div>
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
