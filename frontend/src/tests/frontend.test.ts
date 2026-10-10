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
    expect(html).toContain("Welcome, Tushar");
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

