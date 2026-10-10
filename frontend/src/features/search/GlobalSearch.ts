// Global Search & Command Palette Feature — EduNavika
import { curriculumService, CurriculumHierarchyResponse, APPROVED_SUBJECTS } from '../../services/curriculumService';
import { navigate } from '../../routes/router';
import { icon } from '../../utils/icons';

declare const window: any;

interface SearchResultItem {
  id: string;
  type: 'subject' | 'topic' | 'section' | 'ai';
  title: string;
  subtitle: string;
  iconName: string;
  iconBg: string;
  iconColor: string;
  badge?: string;
  actionText?: string;
  onSelect: () => void;
  secondaryAction?: {
    text: string;
    action: () => void;
  };
}

// App Sections with search keywords
const APP_SECTIONS = [
  {
    title: 'Adaptive Practice',
    route: 'student/practice',
    subtitle: 'Targeted on-device MCQ practice tailored to your mastery',
    keywords: ['practice', 'adaptive', 'quiz', 'test', 'mcq', 'questions', 'exercise', 'assessment'],
    icon: 'target',
    bg: '#EBF3FE',
    color: '#2563EB',
    badge: 'Core Practice',
  },
  {
    title: 'My Learning & Syllabus',
    route: 'student/learning',
    subtitle: 'GSEB Standard 10 curriculum, chapters, and textbooks',
    keywords: ['learning', 'syllabus', 'curriculum', 'chapters', 'topics', 'textbook', 'gseb'],
    icon: 'book',
    bg: '#EEF2FF',
    color: '#4F46E5',
    badge: 'Curriculum',
  },
  {
    title: 'All Subjects',
    route: 'student/subjects',
    subtitle: 'Mathematics, Science, English, Social Science, and more',
    keywords: ['subjects', 'courses', 'classes', 'stream', 'maths', 'science'],
    icon: 'grid',
    bg: '#FDF2F8',
    color: '#DB2777',
    badge: 'Syllabus',
  },
  {
    title: 'Daily Missions & Quests',
    route: 'student/missions',
    subtitle: 'Personalized quests, streaks, and mastery achievements',
    keywords: ['missions', 'daily', 'quests', 'streak', 'challenges', 'goals', 'xp'],
    icon: 'zap',
    bg: '#FEF3C7',
    color: '#D97706',
    badge: 'Gamification',
  },
  {
    title: 'Knowledge Constellation',
    route: 'student/constellation',
    subtitle: 'Interactive mastery graph and concept dependency map',
    keywords: ['constellation', 'graph', 'knowledge', 'prerequisites', 'concept map', 'nodes'],
    icon: 'star',
    bg: '#ECFDF5',
    color: '#059669',
    badge: 'Concept Map',
  },
  {
    title: 'Spaced Revision Plan',
    route: 'student/revision',
    subtitle: 'Personalized retention queue based on your decay curve',
    keywords: ['revision', 'review', 'spaced', 'decay', 'retention', 'forgetting curve'],
    icon: 'refresh',
    bg: '#F0FDF4',
    color: '#16A34A',
    badge: 'Memory Guard',
  },
  {
    title: 'Learning Progress & Analytics',
    route: 'student/analytics',
    subtitle: 'Accuracy, mastery distribution, and performance trends',
    keywords: ['progress', 'analytics', 'accuracy', 'mastery', 'stats', 'performance', 'reports'],
    icon: 'chart',
    bg: '#F5F3FF',
    color: '#7C3AED',
    badge: 'Analytics',
  },
  {
    title: 'Achievements & Badges',
    route: 'student/achievements',
    subtitle: 'Unlocked awards, streaks, and learning milestones',
    keywords: ['achievements', 'badges', 'trophies', 'awards', 'unlocked', 'milestones'],
    icon: 'award',
    bg: '#FFFBEB',
    color: '#B45309',
    badge: 'Badges',
  },
  {
    title: 'Misconception Battle',
    route: 'student/boss-battle',
    subtitle: 'Remediate detected conceptual pitfalls and tricky questions',
    keywords: ['misconception', 'battle', 'boss', 'weakness', 'remediation', 'errors'],
    icon: 'flame',
    bg: '#FEF2F2',
    color: '#DC2626',
    badge: 'Challenge',
  },
  {
    title: 'Memory Guardian',
    route: 'student/memory-guardian',
    subtitle: 'Active recall drills for concepts at risk of being forgotten',
    keywords: ['memory', 'guardian', 'recall', 'retention', 'decay'],
    icon: 'shield',
    bg: '#EFF6FF',
    color: '#1D4ED8',
    badge: 'Recall',
  },
  {
    title: 'Growth Timeline',
    route: 'student/timeline',
    subtitle: 'Chronological activity stream and progress milestones',
    keywords: ['timeline', 'growth', 'activity', 'history', 'stream'],
    icon: 'clock',
    bg: '#F3F4F6',
    color: '#4B5563',
    badge: 'History',
  },
  {
    title: 'Study Materials & Textbooks',
    route: 'student/materials',
    subtitle: 'Official GSEB Standard 10 PDF textbooks and notes',
    keywords: ['materials', 'textbooks', 'books', 'pdf', 'notes', 'study'],
    icon: 'fileText',
    bg: '#ECFEFF',
    color: '#0891B2',
    badge: 'Resources',
  },
  {
    title: 'Student Dashboard',
    route: 'student/dashboard',
    subtitle: 'Home overview with next recommended practice',
    keywords: ['dashboard', 'home', 'overview'],
    icon: 'home',
    bg: '#E0F2FE',
    color: '#0284C7',
    badge: 'Home',
  },
];

// Subject alias dictionary for fuzzy search
const SUBJECT_ALIASES: Record<string, string[]> = {
  math: ['math', 'maths', 'mathematics', 'mth', 'algebra', 'geometry', 'calculus', 'arithmetic', 'गणित', 'ગણિત'],
  phy: ['physics', 'phy', 'science', 'mechanics', 'electricity', 'भौतिकी', 'ભૌતિકવિજ્ઞાન'],
  chem: ['chemistry', 'chem', 'chm', 'science', 'reactions', 'रसायन विज्ञान', 'રસાયણવિજ્ઞાન'],
  bio: ['biology', 'bio', 'science', 'life processes', 'जीव विज्ञान', 'જીવવિજ્ઞાન'],
  eng: ['english', 'eng', 'language', 'literature', 'grammar', 'mandela', 'letter to god', 'અંગ્રેજી', 'अंग्रेजी'],
  sst: ['social', 'social science', 'social studies', 'sst', 'history', 'geography', 'civics', 'economics', 'સામાજિક વિજ્ઞાન', 'सामाजिक विज्ञान'],
};

// Cached hierarchy from API
let cachedHierarchy: CurriculumHierarchyResponse | null = null;
let hierarchyLoadAttempted = false;

async function loadHierarchyOnce(): Promise<void> {
  if (hierarchyLoadAttempted) return;
  hierarchyLoadAttempted = true;
  try {
    cachedHierarchy = await curriculumService.getHierarchy(10);
  } catch (err) {
    console.debug('GlobalSearch: hierarchy load fallback to static subjects:', err);
  }
}

// Active search state
let activeIndex = -1;
let currentResults: SearchResultItem[] = [];

export function initGlobalSearch(): void {
  if (typeof document === 'undefined') return;
  // Eagerly pre-load curriculum hierarchy in background
  loadHierarchyOnce();

  const searchInput = document.getElementById('globalSearch') as HTMLInputElement | null;
  const searchWrap = document.getElementById('tbSearchWrap');
  const dropdown = document.getElementById('searchResultsDropdown');
  const clearBtn = document.getElementById('globalSearchClear');
  const kbdBadge = document.getElementById('globalSearchKbd');

  if (!searchInput || !dropdown) return;

  // Render on input change
  searchInput.oninput = () => {
    const query = searchInput.value.trim();
    if (clearBtn) clearBtn.style.display = query ? 'flex' : 'none';
    if (kbdBadge) kbdBadge.style.display = query ? 'none' : 'inline-block';
    renderSearchResults(query);
  };

  // Render on focus
  searchInput.onfocus = () => {
    renderSearchResults(searchInput.value.trim());
  };

  // Clear button click
  if (clearBtn) {
    clearBtn.onclick = (e) => {
      e.stopPropagation();
      searchInput.value = '';
      clearBtn.style.display = 'none';
      if (kbdBadge) kbdBadge.style.display = 'inline-block';
      searchInput.focus();
      renderSearchResults('');
    };
  }

  // Keyboard navigation
  searchInput.onkeydown = (e: KeyboardEvent) => {
    if (dropdown.classList.contains('hide')) {
      if (e.key === 'ArrowDown' || e.key === 'Enter') {
        renderSearchResults(searchInput.value.trim());
      }
      return;
    }

    if (e.key === 'ArrowDown') {
      e.preventDefault();
      if (currentResults.length > 0) {
        activeIndex = (activeIndex + 1) % currentResults.length;
        updateActiveHighlight();
      }
    } else if (e.key === 'ArrowUp') {
      e.preventDefault();
      if (currentResults.length > 0) {
        activeIndex = (activeIndex - 1 + currentResults.length) % currentResults.length;
        updateActiveHighlight();
      }
    } else if (e.key === 'Enter') {
      e.preventDefault();
      if (currentResults.length > 0) {
        const itemToExecute = activeIndex >= 0 && activeIndex < currentResults.length
          ? currentResults[activeIndex]
          : currentResults[0];
        if (itemToExecute) {
          executeResult(itemToExecute);
        }
      }
    } else if (e.key === 'Escape') {
      e.preventDefault();
      closeDropdown();
      searchInput.blur();
    }
  };

  // Click outside to close
  document.addEventListener('click', (e: MouseEvent) => {
    if (searchWrap && !searchWrap.contains(e.target as Node)) {
      closeDropdown();
    }
  });
}

function closeDropdown(): void {
  const dropdown = document.getElementById('searchResultsDropdown');
  if (dropdown) {
    dropdown.classList.add('hide');
  }
  activeIndex = -1;
}

function updateActiveHighlight(): void {
  const dropdown = document.getElementById('searchResultsDropdown');
  if (!dropdown) return;

  const items = dropdown.querySelectorAll<HTMLElement>('.search-item');
  items.forEach((el, idx) => {
    if (idx === activeIndex) {
      el.classList.add('active');
      el.scrollIntoView({ block: 'nearest', behavior: 'smooth' });
    } else {
      el.classList.remove('active');
    }
  });
}

function executeResult(item: SearchResultItem): void {
  closeDropdown();
  const searchInput = document.getElementById('globalSearch') as HTMLInputElement | null;
  if (searchInput) searchInput.blur();
  item.onSelect();
}

export function getSearchResults(query: string): SearchResultItem[] {
  const q = query.toLowerCase().trim();
  const results: SearchResultItem[] = [];

  // When query is empty, show Quick Navigation shortcuts
  if (!q) {
    // Top app shortcuts
    results.push({
      id: 'sec-practice',
      type: 'section',
      title: 'Adaptive Practice',
      subtitle: 'Targeted on-device MCQ practice tailored to your mastery',
      iconName: 'target',
      iconBg: '#EBF3FE',
      iconColor: '#2563EB',
      badge: 'Quick Jump',
      actionText: 'Open',
      onSelect: () => navigate('student/practice'),
    });
    results.push({
      id: 'sec-learning',
      type: 'section',
      title: 'My Learning & Syllabus',
      subtitle: 'Explore Standard 10 chapters, concepts, and textbooks',
      iconName: 'book',
      iconBg: '#EEF2FF',
      iconColor: '#4F46E5',
      badge: 'Quick Jump',
      actionText: 'Open',
      onSelect: () => navigate('student/learning'),
    });
    results.push({
      id: 'sec-revision',
      type: 'section',
      title: 'Spaced Revision Plan',
      subtitle: 'Review concepts scheduled by your forgetting decay curve',
      iconName: 'refresh',
      iconBg: '#F0FDF4',
      iconColor: '#16A34A',
      badge: 'Quick Jump',
      actionText: 'Open',
      onSelect: () => navigate('student/revision'),
    });
    results.push({
      id: 'sec-constellation',
      type: 'section',
      title: 'Knowledge Constellation',
      subtitle: 'Interactive map of concept mastery and prerequisites',
      iconName: 'star',
      iconBg: '#ECFDF5',
      iconColor: '#059669',
      badge: 'Quick Jump',
      actionText: 'Open',
      onSelect: () => navigate('student/constellation'),
    });
    results.push({
      id: 'sec-ai',
      type: 'ai',
      title: 'Ask EduNavika AI Tutor',
      subtitle: 'Ask any syllabus question for a step-by-step grounded explanation',
      iconName: 'sparkles',
      iconBg: '#E0F2FE',
      iconColor: '#0284C7',
      badge: 'AI Assistant',
      actionText: 'Ask AI',
      onSelect: () => {
        if (typeof window.openAIPanel === 'function') window.openAIPanel();
      },
    });
    return results;
  }

  // 1. Search Subjects
  const allSubjects = APPROVED_SUBJECTS;
  for (const subj of allSubjects) {
    const aliases = SUBJECT_ALIASES[subj.id] || [];
    const nameMatch = subj.name.toLowerCase().includes(q) || subj.code.toLowerCase().includes(q);
    const aliasMatch = aliases.some(a => a.includes(q) || q.includes(a));

    if (nameMatch || aliasMatch) {
      results.push({
        id: `subj-${subj.id}`,
        type: 'subject',
        title: subj.name,
        subtitle: `Grade 10 · ${subj.topics} Curriculum Topics · ${subj.code}`,
        iconName: 'book',
        iconBg: subj.bg || '#EEF2FF',
        iconColor: subj.color || '#4F46E5',
        badge: 'Subject',
        actionText: 'View Syllabus',
        onSelect: () => {
          if (typeof window.openSubject === 'function') {
            window.openSubject(subj.id);
          } else {
            navigate('student/learning');
          }
        },
      });
    }
  }

  // Also match backend hierarchy subjects if loaded
  if (cachedHierarchy && cachedHierarchy.subjects) {
    for (const hSubj of cachedHierarchy.subjects) {
      const alreadyInList = results.some(r => r.type === 'subject' && r.title.toLowerCase() === hSubj.name.toLowerCase());
      if (!alreadyInList && (hSubj.name.toLowerCase().includes(q) || hSubj.code.toLowerCase().includes(q))) {
        results.push({
          id: `hsubj-${hSubj.id}`,
          type: 'subject',
          title: hSubj.name,
          subtitle: `Grade 10 · ${hSubj.total_chapters} Chapters · GSEB`,
          iconName: 'book',
          iconBg: '#E8EDF7',
          iconColor: '#243B6B',
          badge: 'Subject',
          actionText: 'View Syllabus',
          onSelect: () => navigate('student/learning'),
        });
      }
    }
  }

  // 2. Search Topics & Chapters
  let matchedTopicsCount = 0;
  const maxTopicResults = 5;

  // From APPROVED_SUBJECTS
  for (const subj of APPROVED_SUBJECTS) {
    if (matchedTopicsCount >= maxTopicResults) break;
    const subjAliases = SUBJECT_ALIASES[subj.id] || [];
    const isSubjMatch = (subj.name.toLowerCase().includes(q) || subjAliases.some(a => a.includes(q) || q.includes(a))) && q.length >= 3;

    for (const topic of subj.topicList) {
      if (matchedTopicsCount >= maxTopicResults) break;
      const topicTitle = topic.title || topic.name || '';
      const topicMatches = topicTitle.toLowerCase().includes(q);

      if (topicMatches || isSubjMatch) {
        matchedTopicsCount++;
        results.push({
          id: `topic-${topic.id}`,
          type: 'topic',
          title: topicTitle,
          subtitle: `${subj.name} · Topic #${topic.order_index || 1}`,
          iconName: 'target',
          iconBg: '#EBF3FE',
          iconColor: '#2563EB',
          badge: 'Practice Available',
          actionText: 'Practice Now',
          onSelect: () => {
            if (typeof window.loadAdaptivePractice === 'function') {
              window.loadAdaptivePractice(topic.id);
            } else {
              navigate('student/practice');
            }
          },
          secondaryAction: {
            text: 'Syllabus',
            action: () => {
              if (typeof window.openSubject === 'function') {
                window.openSubject(subj.id);
              } else {
                navigate('student/learning');
              }
            },
          },
        });
      }
    }
  }

  // From cached backend hierarchy (if more topics match)
  if (cachedHierarchy && cachedHierarchy.subjects && matchedTopicsCount < maxTopicResults) {
    for (const hSubj of cachedHierarchy.subjects) {
      if (matchedTopicsCount >= maxTopicResults) break;
      for (const hChap of hSubj.chapters || []) {
        if (matchedTopicsCount >= maxTopicResults) break;
        for (const hTop of hChap.topics || []) {
          if (matchedTopicsCount >= maxTopicResults) break;
          const already = results.some(r => r.id === `topic-${hTop.id}` || r.title.toLowerCase() === hTop.title.toLowerCase());
          if (!already && (hTop.title.toLowerCase().includes(q) || hChap.title.toLowerCase().includes(q))) {
            matchedTopicsCount++;
            results.push({
              id: `htopic-${hTop.id}`,
              type: 'topic',
              title: hTop.title,
              subtitle: `${hSubj.name} · Chapter ${hChap.chapter_number}: ${hChap.title}`,
              iconName: 'target',
              iconBg: '#EBF3FE',
              iconColor: '#2563EB',
              badge: hTop.practice_available ? 'Practice Available' : 'Curriculum Topic',
              actionText: 'Practice Now',
              onSelect: () => {
                if (typeof window.loadAdaptivePractice === 'function') {
                  window.loadAdaptivePractice(hTop.id);
                } else {
                  navigate('student/practice');
                }
              },
            });
          }
        }
      }
    }
  }

  // 3. Search App Sections
  for (const sec of APP_SECTIONS) {
    const titleMatch = sec.title.toLowerCase().includes(q);
    const subMatch = sec.subtitle.toLowerCase().includes(q);
    const keywordMatch = sec.keywords.some(k => k.includes(q) || q.includes(k));

    if (titleMatch || subMatch || keywordMatch) {
      results.push({
        id: `sec-${sec.route}`,
        type: 'section',
        title: sec.title,
        subtitle: sec.subtitle,
        iconName: sec.icon,
        iconBg: sec.bg,
        iconColor: sec.color,
        badge: sec.badge,
        actionText: 'Go to Section',
        onSelect: () => navigate(sec.route),
      });
    }
  }

  // 4. Always provide AI Tutor Prompt option for user's query
  results.push({
    id: 'ai-tutor-query',
    type: 'ai',
    title: `Ask EduNavika AI: "${query}"`,
    subtitle: 'Get an instant on-device explanation grounded in your Standard 10 textbook',
    iconName: 'sparkles',
    iconBg: '#E0F2FE',
    iconColor: '#0284C7',
    badge: 'On-Device AI',
    actionText: 'Ask AI',
    onSelect: () => {
      if (typeof window.openAIPanel === 'function') {
        window.openAIPanel();
        if (typeof window.sendAI === 'function') {
          setTimeout(() => {
            window.sendAI(query);
          }, 150);
        }
      }
    },
  });

  return results;
}

function renderSearchResults(query: string): void {
  const dropdown = document.getElementById('searchResultsDropdown');
  if (!dropdown) return;

  const results = getSearchResults(query);
  currentResults = results;
  activeIndex = results.length > 0 ? 0 : -1;

  if (results.length === 0) {
    dropdown.innerHTML = `
      <div style="padding:20px;text-align:center;color:var(--text-3)">
        <div style="font-size:24px;margin-bottom:6px">🔍</div>
        <div style="font-size:13px;font-weight:600;color:var(--text)">No curriculum results found</div>
        <div style="font-size:12px;margin-top:2px">Try searching for a subject like "Mathematics" or topic like "Chemical Reactions".</div>
      </div>
    `;
    dropdown.classList.remove('hide');
    return;
  }

  // Group results by category
  const subjects = results.filter(r => r.type === 'subject');
  const topics = results.filter(r => r.type === 'topic');
  const sections = results.filter(r => r.type === 'section');
  const aiItems = results.filter(r => r.type === 'ai');

  let html = '';

  // Render header info
  if (query) {
    html += `
      <div style="display:flex;align-items:center;justify-content:space-between;padding:8px 14px 4px;font-size:11px;font-weight:700;color:var(--text-3);text-transform:uppercase;letter-spacing:.05em">
        <span>Search Results for "${escapeHtml(query)}"</span>
        <span style="font-weight:600;color:var(--text-4)">Press Enter to open</span>
      </div>`;
  } else {
    html += `
      <div style="display:flex;align-items:center;justify-content:space-between;padding:8px 14px 4px;font-size:11px;font-weight:700;color:var(--text-3);text-transform:uppercase;letter-spacing:.05em">
        <span>⚡ Quick Shortcuts</span>
        <span style="font-weight:600;color:var(--text-4)">Type to search</span>
      </div>`;
  }

  // Subjects group
  if (subjects.length > 0) {
    html += `<div class="search-section-title">📚 Subjects</div>`;
    subjects.forEach((item) => {
      html += renderResultItemHtml(item);
    });
  }

  // Topics group
  if (topics.length > 0) {
    html += `<div class="search-section-title">🎯 Topics & Practice</div>`;
    topics.forEach((item) => {
      html += renderResultItemHtml(item);
    });
  }

  // Sections group
  if (sections.length > 0) {
    html += `<div class="search-section-title">🧭 App Features & Tools</div>`;
    sections.forEach((item) => {
      html += renderResultItemHtml(item);
    });
  }

  // AI item
  if (aiItems.length > 0) {
    html += `<div class="search-section-title">🤖 AI Learning Assistant</div>`;
    aiItems.forEach((item) => {
      html += renderResultItemHtml(item);
    });
  }

  dropdown.innerHTML = html;
  dropdown.classList.remove('hide');

  // Bind click handlers to rendered rows
  const itemEls = dropdown.querySelectorAll<HTMLElement>('.search-item');
  itemEls.forEach((el) => {
    const itemId = el.getAttribute('data-id');
    const matchedItem = currentResults.find(r => r.id === itemId);
    if (!matchedItem) return;

    el.onclick = (e) => {
      // Check if secondary button was clicked
      const target = e.target as HTMLElement;
      if (target.closest('.search-item-sec-btn') && matchedItem.secondaryAction) {
        e.stopPropagation();
        closeDropdown();
        matchedItem.secondaryAction.action();
        return;
      }
      executeResult(matchedItem);
    };

    el.onmouseenter = () => {
      const idx = currentResults.findIndex(r => r.id === itemId);
      if (idx !== -1) {
        activeIndex = idx;
        updateActiveHighlight();
      }
    };
  });

  updateActiveHighlight();
}

function renderResultItemHtml(item: SearchResultItem): string {
  const isAi = item.type === 'ai';
  return `
    <div class="search-item" data-id="${item.id}" role="option" style="${isAi ? 'background:rgba(2,132,199,.05);border:1px dashed rgba(2,132,199,.3);' : ''}">
      <div class="search-item-icon" style="background:${item.iconBg};color:${item.iconColor}">
        ${icon(item.iconName, 'ic-sm')}
      </div>
      <div class="search-item-info">
        <div style="display:flex;align-items:center;gap:6px">
          <span class="search-item-title">${escapeHtml(item.title)}</span>
          ${item.badge ? `<span class="badge" style="font-size:9.5px;padding:1px 5px;background:${item.iconBg};color:${item.iconColor};font-weight:700">${item.badge}</span>` : ''}
        </div>
        <div class="search-item-meta">${escapeHtml(item.subtitle)}</div>
      </div>
      <div style="display:flex;align-items:center;gap:6px;flex:0 0 auto">
        ${item.secondaryAction ? `
          <button type="button" class="search-item-sec-btn" style="font-size:11px;padding:3px 7px;border-radius:6px;background:var(--bg);border:1px solid var(--border);color:var(--text-3);cursor:pointer" title="View Syllabus">
            ${item.secondaryAction.text}
          </button>
        ` : ''}
        <span class="search-item-action">${item.actionText || 'Open'} →</span>
      </div>
    </div>
  `;
}

function escapeHtml(str: string): string {
  return (str || '')
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}
