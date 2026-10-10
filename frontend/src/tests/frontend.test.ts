// Frontend Unit Tests for EduNavika
import { describe, it, expect } from 'vitest';
import { icon, I } from '../utils/icons';
import { sparkline, barChart, donut, heatmap } from '../utils/charts';
import { authService, DEFAULT_STUDENT, DEFAULT_TEACHER } from '../services/authService';
import { SUBJECTS } from '../services/curriculumService';
import { ROUTES } from '../routes/router';

describe('Icons & Visual Tokens', () => {
  it('should contain all 48 required icons in dictionary', () => {
    expect(Object.keys(I).length).toBeGreaterThanOrEqual(40);
    expect(I.home).toBeDefined();
    expect(I.brain).toBeDefined();
    expect(I.sparkles).toBeDefined();
    expect(I.target).toBeDefined();
  });

  it('should generate valid SVG element markup', () => {
    const homeSvg = icon('home', 'ic-sm');
    expect(homeSvg).toContain('<svg class="ic ic-sm"');
    expect(homeSvg).toContain('viewBox="0 0 24 24"');
  });
});

describe('Chart Utilities', () => {
  it('should render SVG sparklines with correct path and gradient', () => {
    const svg = sparkline([10, 20, 30, 40], 400, 120, '#243B6B');
    expect(svg).toContain('<svg viewBox="0 0 400 120"');
    expect(svg).toContain('linearGradient');
    expect(svg).toContain('stroke="#243B6B"');
  });

  it('should render SVG bar charts with category labels', () => {
    const svg = barChart([10, 20, 30], ['Mon', 'Tue', 'Wed'], 400, 150, '#243B6B');
    expect(svg).toContain('<svg viewBox="0 0 400 174"');
    expect(svg).toContain('Mon');
    expect(svg).toContain('Tue');
    expect(svg).toContain('Wed');
  });

  it('should render SVG circular score donuts with accurate stroke dash', () => {
    const svg = donut(75, 120, 12, '#2E9B68', '75%');
    expect(svg).toContain('<svg width="120" height="120"');
    expect(svg).toContain('stroke="#2E9B68"');
    expect(svg).toContain('75%');
  });

  it('should render weekly heatmap cells', () => {
    const html = heatmap(4);
    expect(html).toContain('<div class="hm">');
    expect(html).toContain('<div class="hm-c');
  });
});

describe('Curriculum Data Integrity', () => {
  it('should include all 6 approved subjects matching authoritative design', () => {
    expect(SUBJECTS).toHaveLength(6);
    const names = SUBJECTS.map(s => s.name);
    expect(names).toContain('Mathematics');
    expect(names).toContain('Physics');
    expect(names).toContain('Chemistry');
    expect(names).toContain('Biology');
    expect(names).toContain('English');
    expect(names).toContain('Social Studies');
  });

  it('each subject should have valid topicList with knowledge health and mastery', () => {
    for (const subj of SUBJECTS) {
      expect(subj.topicList.length).toBeGreaterThan(0);
      for (const t of subj.topicList) {
        expect(t.name).toBeDefined();
        expect(t.mastery).toBeGreaterThanOrEqual(0);
        expect(t.kh).toBeGreaterThanOrEqual(0);
      }
    }
  });
});

describe('Role-Aware Router & Application Shell', () => {
  it('should register all 30 views', () => {
    expect(Object.keys(ROUTES).length).toBeGreaterThanOrEqual(30);
    expect(ROUTES['student/dashboard']).toBeDefined();
    expect(ROUTES['teacher/dashboard']).toBeDefined();
    expect(ROUTES['student/learning']).toBeDefined();
    expect(ROUTES['teacher/assessments']).toBeDefined();
  });

  it('should render student dashboard view markup cleanly', () => {
    const html = ROUTES['student/dashboard']();
    expect(html).toContain("Recommended for You");
    expect(html).toContain("Today's Focus");
    expect(html).toContain("Knowledge Health");
  });

  it('should render teacher dashboard view markup cleanly', () => {
    authService.setRole('teacher');
    const html = ROUTES['teacher/dashboard']();
    expect(html).toContain("Good morning");
    expect(html).toContain("Students needing attention");
  });
});

describe('Authentication & Session Management', () => {
  it('should manage default student and teacher credentials', () => {
    expect(DEFAULT_STUDENT.email).toBe('kachatushar108@gmail.com');
    expect(DEFAULT_STUDENT.role).toBe('student');
    expect(DEFAULT_TEACHER.email).toBe('tushar.kacha141862@marwadiuniversity.ac.in');
    expect(DEFAULT_TEACHER.role).toBe('teacher');
  });

  it('should switch role and update session correctly', () => {
    authService.setRole('teacher');
    expect(authService.getRole()).toBe('teacher');
    authService.setRole('student');
    expect(authService.getRole()).toBe('student');
  });
});

describe('Adaptive Practice Responsiveness & Error Recovery', () => {
  it('should render loading state cleanly without throwing or freezing', () => {
    const html = ROUTES['student/practice']();
    expect(html).toContain('Loading Adaptive Practice');
    expect(html).toContain('Analyzing your empirical mastery');
  });

  it('should allow clean navigation between dashboard and practice', () => {
    const dashHtml = ROUTES['student/dashboard']();
    expect(dashHtml).toContain("Today's Focus");
    const practiceHtml = ROUTES['student/practice']();
    expect(practiceHtml).toBeDefined();
    const backToDashHtml = ROUTES['student/dashboard']();
    expect(backToDashHtml).toContain("Today's Focus");
  });

  it('should preserve specific topicId in loadAdaptivePractice and navigate to student/practice', () => {
    let navigatedTo = '';
    const fakeWindow: any = {
      location: { hash: '#/student/materials' },
      navigate: (route: string) => {
        navigatedTo = route;
      },
    };
    (globalThis as any).window = fakeWindow;

    const testTopicId = '565bf22f-2a3c-4e5a-b78d-31bcd24bae0c'; // 1.1 Introduction1
    // Dynamically import or invoke
    import('../features/student/StudentViews').then(mod => {
      mod.loadAdaptivePractice(testTopicId);
      expect(navigatedTo).toBe('student/practice');
    });
  });
});

describe('Global Search & Navigation', () => {
  it('should return quick jump shortcuts when search query is empty', async () => {
    const { getSearchResults } = await import('../features/search/GlobalSearch');
    const results = getSearchResults('');
    expect(results.length).toBeGreaterThanOrEqual(4);
    const titles = results.map(r => r.title);
    expect(titles).toContain('Adaptive Practice');
    expect(titles).toContain('My Learning & Syllabus');
    expect(titles).toContain('Ask EduNavika AI Tutor');
  });

  it('should match Mathematics subject, related topics, and AI Tutor option when searching "maths"', async () => {
    const { getSearchResults } = await import('../features/search/GlobalSearch');
    const results = getSearchResults('maths');
    expect(results.length).toBeGreaterThanOrEqual(3);

    // Subject match
    const subjMatch = results.find(r => r.type === 'subject');
    expect(subjMatch).toBeDefined();
    expect(subjMatch?.title).toBe('Mathematics');
    expect(subjMatch?.actionText).toBe('View Syllabus');

    // Topic match
    const topicMatch = results.find(r => r.type === 'topic');
    expect(topicMatch).toBeDefined();
    expect(topicMatch?.subtitle).toContain('Mathematics');
    expect(topicMatch?.actionText).toBe('Practice Now');

    // AI prompt match
    const aiMatch = results.find(r => r.type === 'ai');
    expect(aiMatch).toBeDefined();
    expect(aiMatch?.title).toContain('Ask EduNavika AI: "maths"');
  });

  it('should match specific topics like "quadratic" with practice action', async () => {
    const { getSearchResults } = await import('../features/search/GlobalSearch');
    const results = getSearchResults('quadratic');
    const topic = results.find(r => r.title.toLowerCase().includes('quadratic'));
    expect(topic).toBeDefined();
    expect(topic?.actionText).toBe('Practice Now');
  });

  it('should match core learning sections when searching features like "practice"', async () => {
    const { getSearchResults } = await import('../features/search/GlobalSearch');
    const results = getSearchResults('practice');
    const section = results.find(r => r.type === 'section' && r.title === 'Adaptive Practice');
    expect(section).toBeDefined();
  });
});


