// Centralized Localization & Internationalization (i18n) Engine for EduNavika
// Phase 15: Multilingual Learning Support (English, Hindi, Gujarati)
// 100% Offline, Zero Cloud Dependencies

export type SupportedLanguage = 'en' | 'hi' | 'gu';

export interface TranslationDictionary {
  [key: string]: string;
}

export const TRANSLATIONS: Record<SupportedLanguage, TranslationDictionary> = {
  en: {
    // Nav & Shell
    'nav.dashboard': 'Dashboard',
    'nav.missions': 'Daily Missions',
    'nav.practice': 'Adaptive Practice',
    'nav.constellation': 'Knowledge Constellation',
    'nav.learning': 'My Learning',
    'nav.analytics': 'Learning Progress',
    'nav.revision': 'Revision Plan',
    'nav.achievements': 'Achievements',
    'nav.boss-battle': 'Misconception Battle',
    'nav.memory-guardian': 'Memory Guardian',
    'nav.timeline': 'Growth Timeline',
    'nav.knowledge': 'Knowledge Health',
    'nav.weak': 'Weak Areas',
    'nav.subjects': 'Subjects',
    'nav.materials': 'Study Materials',
    'nav.profile': 'Profile',
    'nav.settings': 'Settings',
    'nav.group.learning': 'Personalized Learning',
    'nav.group.challenges': 'Learning Challenges',
    'nav.group.intelligence': 'Knowledge Intelligence',
    'nav.group.curriculum': 'Curriculum & Resources',
    'nav.group.account': 'Account',
    'shell.onDevice': '🟢 On-Device • Offline Ready',
    'shell.askAi': 'Ask EduNavika AI',
    'shell.search': 'Search topics, subjects, assessments…',
    'shell.notifications': 'Notifications',

    // Common Buttons & Badges
    'btn.refresh': 'Refresh',
    'btn.practice': 'Practice',
    'btn.remediate': 'Remediate',
    'btn.review': 'Review',
    'btn.submit': 'Submit Answer',
    'btn.next': 'Next Question',
    'btn.close': 'Close',
    'btn.cancel': 'Cancel',
    'btn.start': 'Start Practice',
    'btn.explain': 'Explain with AI',
    'badge.improving': '↑ Improving',
    'badge.declining': '↓ Declining',
    'badge.stable': '→ Stable',
    'badge.baseline': 'Baseline',
    'badge.needsAttention': 'Needs attention',
    'badge.stableHealth': 'Stable',
    'badge.unassessed': 'Unassessed',

    // Mastery Levels
    'mastery.MASTERED': 'Mastered',
    'mastery.PROFICIENT': 'Proficient',
    'mastery.DEVELOPING': 'Developing',
    'mastery.NOVICE': 'Novice',
    'mastery.UNASSESSED': 'Unassessed',

    // Retention Risk
    'risk.HIGH': 'High Risk',
    'risk.MODERATE': 'Moderate Risk',
    'risk.LOW': 'Low Risk',
    'risk.NONE': 'Stable',

    // Progress Tracking
    'progress.title': 'Learning Progress & Journey',
    'progress.sub': 'Continuous on-device progress tracking',
    'progress.desc': 'Empirical telemetry, syllabus mastery distribution, and real-time learning history for GSEB Standard 10',
    'progress.solved': 'Questions Solved',
    'progress.accuracy': 'Overall Accuracy',
    'progress.coverage': 'Syllabus Coverage',
    'progress.trend': 'Learning Trend',
    'progress.distribution': 'Syllabus Mastery Distribution',
    'progress.distSub': '4-tier empirical mastery model for',
    'progress.strengths': 'Strengths',
    'progress.developing': 'Developing',
    'progress.weaknesses': 'Weak Areas',
    'progress.topicPerf': 'Curriculum Topic Performance',
    'progress.topicPerfSub': 'GSEB Standard 10 curriculum breakdown with adaptive recommendations',
    'progress.journey': 'Chronological Learning Journey',
    'progress.journeySub': 'Real-time learning event log recorded on-device',
    'progress.noEvents': 'No Learning Events Recorded Yet',
    'progress.noEventsDesc': 'As you practice and submit curriculum questions, your learning events and response times will stream here chronologically.',
    'progress.topicsTotal': 'Supported Topics',
    'progress.units': 'Curriculum Units',
    'progress.recentEvents': 'Recent Events',
    'progress.col.topic': 'Topic',
    'progress.col.attempts': 'Attempts',
    'progress.col.accuracy': 'Accuracy',
    'progress.col.mastery': 'Mastery',
    'progress.col.trend': 'Trend',
    'progress.col.risk': 'Risk',
    'progress.col.recommended': 'Recommended Next',
    'progress.col.action': 'Action',
    'progress.emptyStrengths': 'Achieve ≥ 70% accuracy on active topics to promote them into Strengths.',
    'progress.emptyWeaknesses': '✨ No weak areas detected! Keep up the consistent work.',
    'progress.emptyDeveloping': 'No topics currently in developing tier.',
    'progress.zeroBaseline': 'No topics assessed yet. Complete practice sessions to establish your baseline.',
    'progress.supportedTopicsStudied': 'supported topics studied',

    // Practice Modal & Feedback
    'practice.title': 'Personalized Practice',
    'practice.loading': 'Loading curriculum-grounded question…',
    'practice.sourceCitation': 'Source Citation',
    'practice.textbookPage': 'Textbook Page',
    'practice.selectOption': 'Select an option to submit your answer.',
    'practice.correct': 'Correct Answer! Great Job 🎉',
    'practice.incorrect': 'Incorrect Answer',
    'practice.pedagogicalFeedback': 'Pedagogical Explanation',
    'practice.updatedMastery': 'Updated Mastery Level',
    'practice.updatedAccuracy': 'Topic Accuracy',
    'practice.nextAction': 'Recommended Next Action',
    'practice.practiceNext': 'Practice Next Question',

    // Dashboard
    'dash.welcome': 'Welcome back',
    'dash.aiInsight': 'EduNavika AI Insight',
    'dash.heroAction': 'Start Recommended Practice',
    'dash.subjectPerf': 'Subject Performance & Knowledge Health',
    'dash.subjectPerfSub': 'Mastery, stability estimates, and priority topics across your subjects',
    'dash.seeAll': 'See all subjects →',
    'dash.quickActions': 'Quick Actions',
    'dash.mcqPractice': 'Start MCQ practice',
    'dash.mcqSub': 'Pick a topic and begin',
    'dash.exploreSyllabus': 'Explore GSEB syllabus',
    'dash.exploreSub': 'Standard 10 chapters',
    'dash.studyMaterials': 'Study materials',
    'dash.studySub': 'Textbooks, notes, PDFs',
    'dash.nextAssessment': 'Next Assessment',

    // Revision Planning (Phase 16)
    'revision.title': 'Personalized Revision Plan',
    'revision.sub': 'Automated, spaced revision scheduling',
    'revision.desc': 'EduNavika AI schedules revision based on empirical mastery, retention risk, and time decay to maximize long-term retention.',
    'revision.dueToday': 'Due Today',
    'revision.dueThisWeek': 'Due This Week',
    'revision.upcoming': 'Upcoming Spaced Maintenance',
    'revision.dueTodaySub': 'High-urgency concepts requiring immediate review',
    'revision.dueThisWeekSub': 'Scheduled within the next 7 days to reinforce memory stability',
    'revision.upcomingSub': 'Spaced maintenance for proficient and mastered concepts',
    'revision.empty': 'No Revisions Currently Due 🎉',
    'revision.emptyDesc': 'Your revision queue is clear. As you complete lessons and quizzes, EduNavika AI tracks memory decay and schedules spaced revision here.',
    'revision.priority.URGENT': 'Urgent',
    'revision.priority.HIGH': 'High',
    'revision.priority.MEDIUM': 'Medium',
    'revision.priority.LOW': 'Low Maintenance',
    'revision.dueInDays': 'Due in {n} days',
    'revision.dueTomorrow': 'Due tomorrow',
    'revision.overdue': 'Overdue',
    'revision.todayBadge': 'Today',
    'revision.btnStart': 'Revise Now',
    'revision.source': 'Textbook Page',

    // Gamification & Achievements (Phase 17)
    'gamification.title': 'Learning Achievements',
    'gamification.sub': 'Rewards for genuine curriculum progress',
    'gamification.xp': 'XP',
    'gamification.level': 'Level',
    'gamification.levelProgress': 'Progress to Level {next}',
    'gamification.streak': '{n}-Day Streak',
    'gamification.streakSub': 'Consecutive active learning days',
    'gamification.streakActiveToday': 'Active today 🔥',
    'gamification.streakNotYet': 'Practice today to extend streak!',
    'gamification.dailyGoal': "Today's Learning Goal",
    'gamification.dailyGoalProgress': '{done} of {target} activities completed',
    'gamification.dailyGoalDone': 'Goal achieved for today! 🎉 (+25 XP)',
    'gamification.badges': 'Achievements & Badges',
    'gamification.unlocked': 'Unlocked',
    'gamification.locked': 'Locked',
    'gamification.recent': 'Recent Badges',

    // Settings
    'settings.title': 'Settings',
    'settings.language': 'Language / भाषा / ભાષા',
    'settings.languageHelp': 'Choose your preferred learning interface language.',
    'settings.saved': 'Language preference saved',
  },

  hi: {
    // Nav & Shell
    'nav.dashboard': 'डैशबोर्ड',
    'nav.missions': 'दैनिक लक्ष्य (Missions)',
    'nav.practice': 'अनुकूली अभ्यास',
    'nav.constellation': 'ज्ञान तारामंडल (Constellation)',
    'nav.learning': 'मेरा शिक्षण',
    'nav.analytics': 'सीखने की प्रगति',
    'nav.revision': 'पुनरावलोकन योजना',
    'nav.achievements': 'उपलब्धियां',
    'nav.boss-battle': 'भ्रांति निवारण चुनौती',
    'nav.memory-guardian': 'स्मृति रक्षक (Memory Guardian)',
    'nav.timeline': 'प्रगति समयरेखा',
    'nav.knowledge': 'ज्ञान स्वास्थ्य',
    'nav.weak': 'कमज़ोर क्षेत्र',
    'nav.subjects': 'विषय',
    'nav.materials': 'अध्ययन सामग्री',
    'nav.profile': 'प्रोफ़ाइल',
    'nav.settings': 'सेटिंग्स',
    'nav.group.learning': 'व्यक्तिगत शिक्षण',
    'nav.group.challenges': 'सीखने की चुनौतियां',
    'nav.group.intelligence': 'ज्ञान बुद्धिमत्ता',
    'nav.group.curriculum': 'पाठ्यक्रम एवं संसाधन',
    'nav.group.account': 'खाता',
    'shell.onDevice': '🟢 डिवाइस पर • ऑफ़लाइन तैयार',
    'shell.askAi': 'एडुनाविका एआई से पूछें',
    'shell.search': 'विषय, पाठ, या मूल्यांकन खोजें…',
    'shell.notifications': 'सूचनाएं',

    // Common Buttons & Badges
    'btn.refresh': 'ताज़ा करें',
    'btn.practice': 'अभ्यास करें',
    'btn.remediate': 'सुधार करें',
    'btn.review': 'समीक्षा करें',
    'btn.submit': 'उत्तर जमा करें',
    'btn.next': 'अगला प्रश्न',
    'btn.close': 'बंद करें',
    'btn.cancel': 'रद्द करें',
    'btn.start': 'अभ्यास शुरू करें',
    'btn.explain': 'एआई से समझें',
    'badge.improving': '↑ सुधार जारी',
    'badge.declining': '↓ गिरावट',
    'badge.stable': '→ स्थिर',
    'badge.baseline': 'प्रारंभिक',
    'badge.needsAttention': 'ध्यान देने योग्य',
    'badge.stableHealth': 'संतुलित',
    'badge.unassessed': 'अमूल्यांकित',

    // Mastery Levels
    'mastery.MASTERED': 'दक्ष (Mastered)',
    'mastery.PROFICIENT': 'कुशल (Proficient)',
    'mastery.DEVELOPING': 'प्रगतिशील (Developing)',
    'mastery.NOVICE': 'शुरुआती (Novice)',
    'mastery.UNASSESSED': 'अमूल्यांकित',

    // Retention Risk
    'risk.HIGH': 'उच्च जोखिम',
    'risk.MODERATE': 'मध्यम जोखिम',
    'risk.LOW': 'कम जोखिम',
    'risk.NONE': 'स्थिर',

    // Progress Tracking
    'progress.title': 'सीखने की प्रगति एवं यात्रा',
    'progress.sub': 'डिवाइस पर निरंतर प्रगति ट्रैकिंग',
    'progress.desc': 'जीएसईबी कक्षा 10 के लिए प्रामाणिक टेलीमेट्री, पाठ्यक्रम दक्षता वितरण और वास्तविक समय इतिहास',
    'progress.solved': 'हल किए गए प्रश्न',
    'progress.accuracy': 'कुल सटीकता',
    'progress.coverage': 'पाठ्यक्रम कवरेज',
    'progress.trend': 'सीखने का रुझान',
    'progress.distribution': 'पाठ्यक्रम दक्षता वितरण',
    'progress.distSub': '4-स्तरीय प्रामाणिक दक्षता मॉडल:',
    'progress.strengths': 'मजबूत क्षेत्र',
    'progress.developing': 'प्रगतिशील क्षेत्र',
    'progress.weaknesses': 'कमजोर क्षेत्र',
    'progress.topicPerf': 'पाठ्यक्रम विषयवार प्रदर्शन',
    'progress.topicPerfSub': 'जीएसईबी कक्षा 10 विषय विवरण और अनुकूली सुझाव',
    'progress.journey': 'कालानुक्रमिक सीखने की यात्रा',
    'progress.journeySub': 'डिवाइस पर दर्ज वास्तविक समय शिक्षण इवेंट लॉग',
    'progress.noEvents': 'अभी कोई शिक्षण इवेंट दर्ज नहीं है',
    'progress.noEventsDesc': 'जैसे-जैसे आप पाठ्यक्रम के प्रश्नों का अभ्यास करेंगे, आपके प्रयास और प्रतिक्रिया समय यहाँ कालानुक्रमिक रूप से दिखेंगे।',
    'progress.topicsTotal': 'समर्थित विषय',
    'progress.units': 'पाठ्यक्रम इकाइयाँ',
    'progress.recentEvents': 'हाल के इवेंट्स',
    'progress.col.topic': 'विषय',
    'progress.col.attempts': 'प्रयास',
    'progress.col.accuracy': 'सटीकता',
    'progress.col.mastery': 'दक्षता',
    'progress.col.trend': 'रुझान',
    'progress.col.risk': 'जोखिम',
    'progress.col.recommended': 'अनुशंसित अगला कदम',
    'progress.col.action': 'कार्रवाई',
    'progress.emptyStrengths': 'मजबूत क्षेत्रों में शामिल होने के लिए सक्रिय विषयों पर ≥ 70% सटीकता प्राप्त करें।',
    'progress.emptyWeaknesses': '✨ कोई कमजोर क्षेत्र नहीं मिला! इसी प्रकार निरंतर अभ्यास जारी रखें।',
    'progress.emptyDeveloping': 'वर्तमान में कोई विषय प्रगतिशील श्रेणी में नहीं है।',
    'progress.zeroBaseline': 'अभी किसी विषय का मूल्यांकन नहीं हुआ है। अपनी आधार रेखा स्थापित करने के लिए अभ्यास करें।',
    'progress.supportedTopicsStudied': 'समर्थित विषय पढ़े गए',

    // Practice Modal & Feedback
    'practice.title': 'व्यक्तिगत अनुकूली अभ्यास',
    'practice.loading': 'पाठ्यपुस्तक से जुड़ा प्रश्न लोड हो रहा है…',
    'practice.sourceCitation': 'स्रोत संदर्भ (Textbook Provenance)',
    'practice.textbookPage': 'पाठ्यपुस्तक पृष्ठ',
    'practice.selectOption': 'उत्तर जमा करने के लिए एक विकल्प चुनें।',
    'practice.correct': 'सही उत्तर! बहुत बढ़िया 🎉',
    'practice.incorrect': 'गलत उत्तर',
    'practice.pedagogicalFeedback': 'शैक्षणिक व्याख्या (Explanation)',
    'practice.updatedMastery': 'अद्यतन दक्षता स्तर',
    'practice.updatedAccuracy': 'विषय सटीकता',
    'practice.nextAction': 'अनुशंसित अगली कार्रवाई',
    'practice.practiceNext': 'अगला प्रश्न हल करें',

    // Dashboard
    'dash.welcome': 'स्वागत है',
    'dash.aiInsight': 'एडुनाविका एआई अंतर्दृष्टि',
    'dash.heroAction': 'अनुशंसित अभ्यास शुरू करें',
    'dash.subjectPerf': 'विषय प्रदर्शन एवं ज्ञान स्वास्थ्य',
    'dash.subjectPerfSub': 'आपके विषयों में दक्षता, स्थिरता अनुमान और प्राथमिकता वाले विषय',
    'dash.seeAll': 'सभी विषय देखें →',
    'dash.quickActions': 'त्वरित कार्रवाइयां',
    'dash.mcqPractice': 'एमसीक्यू अभ्यास शुरू करें',
    'dash.mcqSub': 'एक विषय चुनें और शुरू करें',
    'dash.exploreSyllabus': 'जीएसईबी पाठ्यक्रम देखें',
    'dash.exploreSub': 'कक्षा 10 के अध्याय',
    'dash.studyMaterials': 'अध्ययन सामग्री',
    'dash.studySub': 'पाठ्यपुस्तकें, नोट्स, पीडीएफ',
    'dash.nextAssessment': 'आगामी मूल्यांकन',

    // Revision Planning (Phase 16)
    'revision.title': 'व्यक्तिगत पुनरावलोकन योजना',
    'revision.sub': 'स्वचालित, आवधिक पुनरावलोकन समय-सारणी',
    'revision.desc': 'एडुनाविका एआई लंबे समय तक याद रखने के लिए दक्षता, स्मृति क्षय और समय के आधार पर पुनरावलोकन निर्धारित करता है।',
    'revision.dueToday': 'आज देय',
    'revision.dueThisWeek': 'इस सप्ताह देय',
    'revision.upcoming': 'आगामी आवधिक अभ्यास',
    'revision.dueTodaySub': 'अति-महत्वपूर्ण अवधारणाएं जिन्हें तत्काल पुनरावलोकन की आवश्यकता है',
    'revision.dueThisWeekSub': 'स्मृति स्थिरता बढ़ाने के लिए अगले 7 दिनों में निर्धारित',
    'revision.upcomingSub': 'दक्ष और सिद्ध अवधारणाओं के लिए आवधिक रखरखाव',
    'revision.empty': 'वर्तमान में कोई पुनरावलोकन देय नहीं है 🎉',
    'revision.emptyDesc': 'आपकी पुनरावलोकन सूची खाली है। जैसे-जैसे आप अभ्यास पूरा करेंगे, एडुनाविका एआई समय पर पुनरावलोकन निर्धारित करेगा।',
    'revision.priority.URGENT': 'अति आवश्यक',
    'revision.priority.HIGH': 'उच्च',
    'revision.priority.MEDIUM': 'मध्यम',
    'revision.priority.LOW': 'सामान्य',
    'revision.dueInDays': '{n} दिनों में देय',
    'revision.dueTomorrow': 'कल देय',
    'revision.overdue': 'अतिदेय',
    'revision.todayBadge': 'आज',
    'revision.btnStart': 'अभी दोहराएं',
    'revision.source': 'पाठ्यपुस्तक पृष्ठ',

    // Gamification & Achievements (Phase 17)
    'gamification.title': 'अधिगम उपलब्धियाँ',
    'gamification.sub': 'वास्तविक पाठ्यक्रम प्रगति के लिए पुरस्कार',
    'gamification.xp': 'एक्सपी (XP)',
    'gamification.level': 'स्तर',
    'gamification.levelProgress': 'स्तर {next} की ओर प्रगति',
    'gamification.streak': '{n}-दिवसीय निरंतरता',
    'gamification.streakSub': 'लगातार सक्रिय सीखने के दिन',
    'gamification.streakActiveToday': 'आज सक्रिय 🔥',
    'gamification.streakNotYet': 'निरंतरता बढ़ाने के लिए आज अभ्यास करें!',
    'gamification.dailyGoal': 'आज का शिक्षण लक्ष्य',
    'gamification.dailyGoalProgress': '{done} / {target} गतिविधियाँ पूरी हुईं',
    'gamification.dailyGoalDone': 'आज का लक्ष्य पूर्ण! 🎉 (+25 XP)',
    'gamification.badges': 'उपलब्धियाँ एवं बैज',
    'gamification.unlocked': 'अनलॉक किया गया',
    'gamification.locked': 'लॉक किया गया',
    'gamification.recent': 'हाल के बैज',

    // Settings
    'settings.title': 'सेटिंग्स',
    'settings.language': 'भाषा / Language / ભાષા',
    'settings.languageHelp': 'अपनी पसंदीदा शिक्षण इंटरफ़ेस भाषा चुनें।',
    'settings.saved': 'भाषा प्राथमिकता सफलतापूर्वक सुरक्षित की गई',
  },

  gu: {
    // Nav & Shell
    'nav.dashboard': 'ડેશબોર્ડ',
    'nav.missions': 'દૈનિક મિશન (Missions)',
    'nav.practice': 'અનુકૂલિત મહાવરો',
    'nav.constellation': 'જ્ઞાન નક્ષત્રમંડળ (Constellation)',
    'nav.learning': 'મારું શિક્ષણ',
    'nav.analytics': 'શિક્ષણ પ્રગતિ',
    'nav.revision': 'પુનરાવર્તન આયોજન',
    'nav.achievements': 'સિદ્ધિઓ',
    'nav.boss-battle': 'ગેરસમજ નિવારણ પડકાર',
    'nav.memory-guardian': 'સ્મૃતિ રક્ષક (Memory Guardian)',
    'nav.timeline': 'પ્રગતિ સમયરેખા',
    'nav.knowledge': 'જ્ઞાન સ્વાસ્થ્ય',
    'nav.weak': 'નબળા મુદ્દાઓ',
    'nav.subjects': 'વિષયો',
    'nav.materials': 'અભ્યાસ સામગ્રી',
    'nav.profile': 'પ્રોફાઇલ',
    'nav.settings': 'સેટિંગ્સ',
    'nav.group.learning': 'વ્યક્તિગત શિક્ષણ',
    'nav.group.challenges': 'શિક્ષણ પડકારો',
    'nav.group.intelligence': 'જ્ઞાન બુદ્ધિમત્તા',
    'nav.group.curriculum': 'અભ્યાસક્રમ અને સંસાધનો',
    'nav.group.account': 'ખાતું',
    'shell.onDevice': '🟢 ઉપકરણ પર • ઑફલાઇન તૈયાર',
    'shell.askAi': 'એડુનાવિકા AI ને પૂછો',
    'shell.search': 'વિષયો, પ્રકરણો, મૂલ્યાંકન શોધો…',
    'shell.notifications': 'સૂચનાઓ',

    // Common Buttons & Badges
    'btn.refresh': 'તાજું કરો',
    'btn.practice': 'મહાવરો કરો',
    'btn.remediate': 'સુધારો કરો',
    'btn.review': 'પુનરાવર્તન કરો',
    'btn.submit': 'જવાબ સબમિટ કરો',
    'btn.next': 'આગળનો પ્રશ્ન',
    'btn.close': 'બંધ કરો',
    'btn.cancel': 'રદ કરો',
    'btn.start': 'મહાવરો શરૂ કરો',
    'btn.explain': 'AI સાથે સમજો',
    'badge.improving': '↑ સુધારો ચાલુ',
    'badge.declining': '↓ ઘટાડો',
    'badge.stable': '→ સ્થિર',
    'badge.baseline': 'પ્રારંભિક',
    'badge.needsAttention': 'ધ્યાન માંગે છે',
    'badge.stableHealth': 'સંતુલિત',
    'badge.unassessed': 'અચકાસાયેલ',

    // Mastery Levels
    'mastery.MASTERED': 'નિપુણ (Mastered)',
    'mastery.PROFICIENT': 'પ્રવીણ (Proficient)',
    'mastery.DEVELOPING': 'વિકાસશીલ (Developing)',
    'mastery.NOVICE': 'પ્રારંભિક (Novice)',
    'mastery.UNASSESSED': 'અચકાસાયેલ',

    // Retention Risk
    'risk.HIGH': 'ઉચ્ચ જોખમ',
    'risk.MODERATE': 'મધ્યમ જોખમ',
    'risk.LOW': 'ઓછું જોખમ',
    'risk.NONE': 'સ્થિર',

    // Progress Tracking
    'progress.title': 'શિક્ષણ પ્રગતિ અને યાત્રા',
    'progress.sub': 'ઉપકરણ પર સતત પ્રગતિ ટ્રેકિંગ',
    'progress.desc': 'GSEB ધોરણ 10 માટે વાસ્તવિક ટેલિમેટ્રી, અભ્યાસક્રમ નિપુણતા વિતરણ અને લાઈવ શિક્ષણ ઇતિહાસ',
    'progress.solved': 'ઉકેલેલા પ્રશ્નો',
    'progress.accuracy': 'કુલ ચોકસાઈ',
    'progress.coverage': 'અભ્યાસક્રમ કવરેજ',
    'progress.trend': 'શીખવાનો પ્રવાહ',
    'progress.distribution': 'અભ્યાસક્રમ નિપુણતા વહેંચણી',
    'progress.distSub': '4-સ્તરીય વાસ્તવિક નિપુણતા મોડેલ:',
    'progress.strengths': 'સબળા ક્ષેત્રો',
    'progress.developing': 'વિકાસશીલ ક્ષેત્રો',
    'progress.weaknesses': 'નબળા ક્ષેત્રો',
    'progress.topicPerf': 'અભ્યાસક્રમ વિષયવાર કામગીરી',
    'progress.topicPerfSub': 'GSEB ધોરણ 10 અભ્યાસક્રમ વિગતો અને અનુકૂલિત ભલામણો',
    'progress.journey': 'સમયાનુક્રમિક શિક્ષણ યાત્રા',
    'progress.journeySub': 'ઉપકરણ પર નોંધાયેલ લાઈવ લર્નિંગ ઇવેન્ટ લોગ',
    'progress.noEvents': 'હજુ સુધી કોઈ લર્નિંગ ઇવેન્ટ નોંધાઈ નથી',
    'progress.noEventsDesc': 'જેમ જેમ તમે અભ્યાસક્રમના પ્રશ્નોનો મહાવરો કરશો, તમારી પ્રગતિ અને સમય અહીં સમયાનુક્રમે દેખાશે.',
    'progress.topicsTotal': 'સપોર્ટેડ વિષયો',
    'progress.units': 'અભ્યાસક્રમ એકમો',
    'progress.recentEvents': 'તાજેતરની ઇવેન્ટ્સ',
    'progress.col.topic': 'વિષય',
    'progress.col.attempts': 'પ્રયાસો',
    'progress.col.accuracy': 'ચોકસાઈ',
    'progress.col.mastery': 'નિપુણતા',
    'progress.col.trend': 'પ્રવાહ',
    'progress.col.risk': 'જોખમ',
    'progress.col.recommended': 'ભલામણ કરેલ આગલું પગલું',
    'progress.col.action': 'કાર્યવાહી',
    'progress.emptyStrengths': 'સબળા ક્ષેત્રોમાં સ્થાન મેળવવા માટે સક્રિય વિષયો પર ≥ 70% ચોકસાઈ મેળવો.',
    'progress.emptyWeaknesses': '✨ કોઈ નબળા ક્ષેત્રો મળ્યા નથી! આ જ રીતે અભ્યાસ ચાલુ રાખો.',
    'progress.emptyDeveloping': 'હાલમાં કોઈ વિષય વિકાસશીલ શ્રેણીમાં નથી.',
    'progress.zeroBaseline': 'હજુ કોઈ વિષયનું મૂલ્યાંકન થયું નથી. તમારી બેઝલાઇન નક્કી કરવા માટે મહાવરો કરો.',
    'progress.supportedTopicsStudied': 'સપોર્ટેડ વિષયો અભ્યાસ કર્યા',

    // Practice Modal & Feedback
    'practice.title': 'વ્યક્તિગત અનુકૂલિત મહાવરો',
    'practice.loading': 'પાઠ્યપુસ્તક આધારિત પ્રશ્ન લોડ થઈ રહ્યો છે…',
    'practice.sourceCitation': 'સ્ત્રોત સંદર્ભ (Textbook Provenance)',
    'practice.textbookPage': 'પાઠ્યપુસ્તક પાનું',
    'practice.selectOption': 'જવાબ આપવા માટે એક વિકલ્પ પસંદ કરો.',
    'practice.correct': 'સાચો જવાબ! ખૂબ સરસ 🎉',
    'practice.incorrect': 'ખોટો જવાબ',
    'practice.pedagogicalFeedback': 'શૈક્ષણિક સમજૂતી (Explanation)',
    'practice.updatedMastery': 'અદ્યતન નિપુણતા સ્તર',
    'practice.updatedAccuracy': 'વિષય ચોકસાઈ',
    'practice.nextAction': 'ભલામણ કરેલ આગળની કાર્યવાહી',
    'practice.practiceNext': 'આગળનો પ્રશ્ન ઉકેલો',

    // Dashboard
    'dash.welcome': 'સ્વાગત છે',
    'dash.aiInsight': 'એડુનાવિકા AI અંતર્દ્રષ્ટિ',
    'dash.heroAction': 'ભલામણ કરેલ મહાવરો શરૂ કરો',
    'dash.subjectPerf': 'વિષય કામગીરી અને જ્ઞાન સ્વાસ્થ્ય',
    'dash.subjectPerfSub': 'તમારા વિષયોમાં નિપુણતા, સ્થિરતા અંદાજ અને પ્રાથમિકતા વાળા વિષયો',
    'dash.seeAll': 'બધા વિષયો જુઓ →',
    'dash.quickActions': 'ઝડપી કાર્યો',
    'dash.mcqPractice': 'MCQ મહાવરો શરૂ કરો',
    'dash.mcqSub': 'એક વિષય પસંદ કરો અને શરૂ કરો',
    'dash.exploreSyllabus': 'GSEB અભ્યાસક્રમ જુઓ',
    'dash.exploreSub': 'ધોરણ 10 ના પ્રકરણો',
    'dash.studyMaterials': 'અભ્યાસ સામગ્રી',
    'dash.studySub': 'પાઠ્યપુસ્તકો, નોંધો, પીડીએફ',
    'dash.nextAssessment': 'આગામી મૂલ્યાંકન',

    // Revision Planning (Phase 16)
    'revision.title': 'વ્યક્તિગત પુનરાવર્તન આયોજન',
    'revision.sub': 'સ્વચાલિત, સમયાંતરિત પુનરાવર્તન શેડ્યૂલ',
    'revision.desc': 'એડુનાવિકા એઆઈ લાંબા ગાળાના સંસ્મરણ માટે ક્ષમતા, વિસ્મૃતિ જોખમ અને સમય અંતરાલના આધારે પુનરાવર્તન નક્કી કરે છે.',
    'revision.dueToday': 'આજે બાકી',
    'revision.dueThisWeek': 'આ અઠવાડિયે બાકી',
    'revision.upcoming': 'આગામી સમયાંતરિત સંભાળ',
    'revision.dueTodaySub': 'તાત્કાલિક પુનરાવર્તનની જરૂર હોય તેવા અતિ-મહત્વના વિષયો',
    'revision.dueThisWeekSub': 'સ્મૃતિ સ્થિરતા વધારવા માટે આગામી ૭ દિવસમાં નિર્ધારિત',
    'revision.upcomingSub': 'સંપૂર્ણ આવડતવાળા વિષયો માટે સમયાંતરિત જાળવણી',
    'revision.empty': 'હાલમાં કોઈ પુનરાવર્તન બાકી નથી 🎉',
    'revision.emptyDesc': 'તમારી પુનરાવર્તન યાદી ખાલી છે. જેમ જેમ તમે પ્રશ્નો ઉકેલશો, એડુનાવિકા એઆઈ યોગ્ય સમયે અહીં પુનરાવર્તન ગોઠવશે.',
    'revision.priority.URGENT': 'તાત્કાલિક',
    'revision.priority.HIGH': 'ઉચ્ચ',
    'revision.priority.MEDIUM': 'મધ્યમ',
    'revision.priority.LOW': 'સામાન્ય',
    'revision.dueInDays': '{n} દિવસમાં બાકી',
    'revision.dueTomorrow': 'આવતીકાલે બાકી',
    'revision.overdue': 'મુદતવીતી',
    'revision.todayBadge': 'આજે',
    'revision.btnStart': 'હવે પુનરાવર્તન કરો',
    'revision.source': 'પાઠ્યપુસ્તક પાનું',

    // Gamification & Achievements (Phase 17)
    'gamification.title': 'શિક્ષણ સિદ્ધિઓ',
    'gamification.sub': 'વાસ્તવિક અભ્યાસક્રમ પ્રગતિ માટે પ્રોત્સાહન',
    'gamification.xp': 'એક્સપી (XP)',
    'gamification.level': 'સ્તર',
    'gamification.levelProgress': 'સ્તર {next} તરફ પ્રગતિ',
    'gamification.streak': '{n}-દિવસીય નિયમિતતા',
    'gamification.streakSub': 'સતત સક્રિય શીખવાના દિવસો',
    'gamification.streakActiveToday': 'આજે સક્રિય 🔥',
    'gamification.streakNotYet': 'નિયમિતતા જાળવવા આજે મહાવરો કરો!',
    'gamification.dailyGoal': 'આજનો શિક્ષણ લક્ષ્યાંક',
    'gamification.dailyGoalProgress': '{done} / {target} પ્રવૃત્તિઓ પૂર્ણ થઈ',
    'gamification.dailyGoalDone': 'આજનો લક્ષ્યાંક પૂર્ણ! 🎉 (+25 XP)',
    'gamification.badges': 'સિદ્ધિઓ અને બેજ',
    'gamification.unlocked': 'અનલૉક થયેલ',
    'gamification.locked': 'લૉક થયેલ',
    'gamification.recent': 'તાજેતરના બેજ',

    // Settings
    'settings.title': 'સેટિંગ્સ',
    'settings.language': 'ભાષા / Language / भाषा',
    'settings.languageHelp': 'તમારી પસંદગીની શિક્ષણ ઇન્ટરફેસ ભાષા પસંદ કરો.',
    'settings.saved': 'ભાષા પસંદગી સફળતાપૂર્વક સાચવવામાં આવી',
  },
};

// Current active language state (persisted in localStorage and synchronized with backend)
const STORAGE_KEY = 'edunavika_language';
let currentLanguage: SupportedLanguage = 'en';

// Initialize from storage safely
if (typeof window !== 'undefined') {
  try {
    const saved = localStorage.getItem(STORAGE_KEY) as SupportedLanguage | null;
    if (saved && (saved === 'en' || saved === 'hi' || saved === 'gu')) {
      currentLanguage = saved;
    }
  } catch {
    currentLanguage = 'en';
  }
}

export function getLanguage(): SupportedLanguage {
  return currentLanguage;
}

export function setLanguage(lang: SupportedLanguage, persistToBackend = true): void {
  if (lang !== 'en' && lang !== 'hi' && lang !== 'gu') return;
  currentLanguage = lang;
  if (typeof window !== 'undefined') {
    try {
      localStorage.setItem(STORAGE_KEY, lang);
    } catch {
      // storage unavailable
    }
    // Update active select in topbar or settings if present
    const topSelect = document.getElementById('topbarLangSelect') as HTMLSelectElement | null;
    if (topSelect && topSelect.value !== lang) topSelect.value = lang;
    const settingsSelect = document.getElementById('settingsLangSelect') as HTMLSelectElement | null;
    if (settingsSelect && settingsSelect.value !== lang) settingsSelect.value = lang;

    // Dispatch custom event for reactive view refresh
    window.dispatchEvent(new CustomEvent('edunavika:languageChange', { detail: { language: lang } }));
  }

  if (persistToBackend) {
    syncLanguageToBackend(lang);
  }
}

async function syncLanguageToBackend(lang: SupportedLanguage): Promise<void> {
  if (typeof window === 'undefined') return;
  try {
    const userStr = localStorage.getItem('edunavika_user');
    if (!userStr) return;
    const user = JSON.parse(userStr);
    const studentId = user.id || user.student_id;
    if (studentId) {
      await fetch(`/api/v1/students/${studentId}/language`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ preferred_language: lang }),
      });
    }
  } catch {
    // Offline / network failure handled gracefully
  }
}

/**
 * Translates a key according to the active language.
 * Falls back to English if key is missing in target language.
 */
export function t(key: string, fallback?: string): string {
  const dict = TRANSLATIONS[currentLanguage] || TRANSLATIONS.en;
  if (dict[key]) return dict[key];
  if (TRANSLATIONS.en[key]) return TRANSLATIONS.en[key];
  return fallback !== undefined ? fallback : key;
}

// Expose on global window object for inline event handlers and quick access
if (typeof window !== 'undefined') {
  (window as any).getLanguage = getLanguage;
  (window as any).setLanguage = setLanguage;
  (window as any).t = t;
}
