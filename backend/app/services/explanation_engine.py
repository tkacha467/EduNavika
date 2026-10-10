from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
import re

from backend.app.domain.enums import MasteryLevel, PerformanceTrend, RetentionRiskLevel, RecommendationAction
from backend.app.schemas.knowledge_profile import TopicKnowledgeProfile
from backend.app.schemas.recommendation import TopicRecommendation
from backend.app.schemas.retrieval import RetrievedContentItem
from backend.app.schemas.explanation import (
    StructuredExplanation,
    QuickCheckItem,
    PersonalizationContext,
    ExplanationSource,
    ExplanationResponse,
)


class ExplanationEngineInterface(ABC):
    """
    Abstract interface for Explanation Engines (Deterministic / Small On-Device Language Model).
    Ensures identical contracts whether using deterministic pedagogical templates or local on-device SLM.
    """

    @abstractmethod
    def generate(
        self,
        student_id: str,
        topic_id: str,
        topic_title: str,
        knowledge_profile: TopicKnowledgeProfile,
        recommendation: Optional[TopicRecommendation],
        retrieved_contexts: List[RetrievedContentItem],
        student_query: Optional[str] = None,
        recent_error_notes: Optional[List[str]] = None,
        language: Optional[str] = "en",
    ) -> ExplanationResponse:
        pass


class DeterministicExplanationEngine(ExplanationEngineInterface):
    """
    Deterministic Local Explanation Engine.
    Generates structured, pedagogical explanations strictly grounded in retrieved curriculum
    textbook material, dynamically tailored to the student's empirical mastery and learning pace.
    No external network or cloud AI API calls are made.
    """

    def generate(
        self,
        student_id: str,
        topic_id: str,
        topic_title: str,
        knowledge_profile: TopicKnowledgeProfile,
        recommendation: Optional[TopicRecommendation],
        retrieved_contexts: List[RetrievedContentItem],
        student_query: Optional[str] = None,
        recent_error_notes: Optional[List[str]] = None,
        language: Optional[str] = "en",
    ) -> ExplanationResponse:
        mastery = knowledge_profile.mastery_level
        accuracy = knowledge_profile.accuracy
        recent_acc = knowledge_profile.recent_accuracy
        trend = knowledge_profile.trend
        risk = knowledge_profile.retention_risk

        # Extract textbook grounding
        sources: List[ExplanationSource] = [
            ExplanationSource(
                source_document=c.source_document,
                source_page=c.source_page,
                source_reference=c.source_reference,
                content_type=c.content_type,
                relevance_score=c.score,
            )
            for c in retrieved_contexts
        ]

        # Extract representative curriculum excerpt from top retrieved chunk
        top_chunk_text = ""
        top_page_ref = ""
        if retrieved_contexts:
            top_chunk = retrieved_contexts[0]
            # Clean text snippet
            clean_text = " ".join(top_chunk.content_text.split()[:80])
            top_chunk_text = clean_text
            if top_chunk.source_page:
                top_page_ref = f" (Refer to Textbook Page {top_chunk.source_page})"

        # Determine pedagogical teaching strategy based on empirical knowledge profile
        lang = (language or "en").lower()
        if mastery in (MasteryLevel.UNASSESSED, MasteryLevel.NOVICE) or accuracy < 50.0:
            teaching_level = "FOUNDATIONAL_REMEDIATION"
            structured = self._build_novice_explanation(
                topic_title=topic_title,
                accuracy=accuracy,
                recent_acc=recent_acc,
                top_chunk_text=top_chunk_text,
                top_page_ref=top_page_ref,
                student_query=student_query,
                recommendation=recommendation,
                recent_error_notes=recent_error_notes,
                language=lang,
            )
            if lang == "hi":
                next_action = f"{topic_title} पर 3 लक्षित बुनियादी अभ्यास प्रश्न हल करें।"
            elif lang == "gu":
                next_action = f"{topic_title} પર 3 લક્ષિત પાયાના મહાવરા પ્રશ્નો ઉકેલો."
            else:
                next_action = f"Complete 3 targeted foundational practice exercises on {topic_title}."

        elif mastery == MasteryLevel.DEVELOPING or accuracy < 70.0:
            teaching_level = "GUIDED_STRENGTHENING"
            structured = self._build_developing_explanation(
                topic_title=topic_title,
                accuracy=accuracy,
                recent_acc=recent_acc,
                top_chunk_text=top_chunk_text,
                top_page_ref=top_page_ref,
                student_query=student_query,
                recommendation=recommendation,
                language=lang,
            )
            if lang == "hi":
                next_action = f"दक्षता हासिल करने के लिए {topic_title} पर 4 बहु-चरणीय समस्याएं हल करें।"
            elif lang == "gu":
                next_action = f"પ્રવીણતા મેળવવા માટે {topic_title} પર 4 બહુ-પગલાંવાળા પ્રશ્નો ઉકેલો."
            else:
                next_action = f"Solve 4 multi-step problem checks on {topic_title} to achieve proficiency."

        elif mastery == MasteryLevel.PROFICIENT or accuracy < 85.0:
            teaching_level = "ADVANCED_APPLICATION"
            structured = self._build_proficient_explanation(
                topic_title=topic_title,
                accuracy=accuracy,
                top_chunk_text=top_chunk_text,
                top_page_ref=top_page_ref,
                student_query=student_query,
                language=lang,
            )
            if lang == "hi":
                next_action = f"{topic_title} पर 2 बोर्ड-परीक्षा स्तर के अनुप्रयोग प्रश्न हल करें।"
            elif lang == "gu":
                next_action = f"{topic_title} પર 2 બોર્ડ-પરીક્ષા સ્તરના પ્રશ્નો ઉકેલો."
            else:
                next_action = f"Attempt 2 board-exam application questions on {topic_title}."

        else:  # MASTERED
            teaching_level = "SYNTHESIS_AND_MASTERY"
            structured = self._build_mastered_explanation(
                topic_title=topic_title,
                accuracy=accuracy,
                top_chunk_text=top_chunk_text,
                top_page_ref=top_page_ref,
                language=lang,
            )
            if lang == "hi":
                next_action = f"{topic_title} के लिए अंतर-अध्याय संबंध और आवधिक पुनरावलोकन का अभ्यास करें।"
            elif lang == "gu":
                next_action = f"{topic_title} માટે પ્રકરણ જોડાણો અને સમયાંતરે પુનરાવર્તન તપાસો."
            else:
                next_action = f"Explore cross-chapter connections and periodic retention reviews for {topic_title}."

        # Compile narrative explanation paragraph combining structured sections
        narrative_parts = [
            f"**{structured.title}**",
            f"\n*{structured.why_this_matters}*",
            f"\n**Core Concept:** {structured.core_concept}",
            "\n**Step-by-Step Breakdown:**",
        ]
        for step in structured.step_by_step:
            narrative_parts.append(f"- {step}")
        narrative_parts.append(f"\n**Common Misconception to Avoid:** {structured.common_mistake}")
        narrative_parts.append(f"\n**Quick Understanding Check:** {structured.quick_check.question} (Key: {structured.quick_check.expected_concept})")

        full_explanation_text = "\n".join(narrative_parts)

        personalization = PersonalizationContext(
            mastery_level=mastery,
            accuracy=accuracy,
            recent_accuracy=recent_acc,
            trend=trend,
            retention_risk=risk,
        )

        return ExplanationResponse(
            student_id=student_id,
            topic_id=topic_id,
            topic_title=topic_title,
            explanation=full_explanation_text,
            structured_explanation=structured,
            teaching_level=teaching_level,
            personalization=personalization,
            sources=sources,
            next_action=next_action,
            generation_mode="DETERMINISTIC_FALLBACK",
            model_name=None,
            inference_time_ms=0,
        )

    def _build_novice_explanation(
        self,
        topic_title: str,
        accuracy: float,
        recent_acc: Optional[float],
        top_chunk_text: str,
        top_page_ref: str,
        student_query: Optional[str],
        recommendation: Optional[TopicRecommendation],
        recent_error_notes: Optional[List[str]],
        language: str = "en",
    ) -> StructuredExplanation:
        acc_display = f"{recent_acc:.1f}%" if recent_acc is not None else f"{accuracy:.1f}%"
        query_note = f" You asked: \"{student_query}\"." if student_query else ""

        if language == "hi":
            title = f"बुनियादी अवधारणाएं: {topic_title}"
            why_this_matters = (
                f"आप वर्तमान में इस विषय की नींव स्थापित कर रहे हैं (सटीकता: {acc_display})।{query_note} "
                f"रटने के बजाय, मूल नियमों पर ध्यान केंद्रित करने से आपकी समझ तेजी से बढ़ेगी।"
            )
            core_concept = (
                f"जीएसईबी कक्षा 10 पाठ्यक्रम के अनुसार{top_page_ref}: {top_chunk_text}..."
                if top_chunk_text else
                f"रासायनिक समीकरण द्रव्यमान का संरक्षण करते हुए अभिकारकों के उत्पादों में बदलने का वर्णन करता है।"
            )
            step_by_step = [
                "चरण 1: बाईं ओर (LHS) अभिकारकों और दाईं ओर (RHS) उत्पादों की पहचान करें।",
                "चरण 2: दोनों पक्षों में प्रत्येक रासायनिक तत्व के परमाणुओं की गणना करें।",
                "चरण 3: सूत्रों के आगे गुणांक लगाकर तत्वों को संतुलित करें (पाद-अंक कभी न बदलें!)।",
                "चरण 4: जांचें कि दोनों पक्षों में प्रत्येक तत्व के कुल परमाणु समान हैं।",
            ]
            common_mistake = (
                "अक्सर विद्यार्थी सूत्र के पाद-अंक (subscript) बदल देते हैं (जैसे H2O को H2O2 करना)। "
                "ऐसा करने से पदार्थ ही बदल जाता है! केवल आगे गुणांक लगाएं।"
            )
            quick_check = QuickCheckItem(
                question="अभिकारक पक्ष के परमाणुओं की संख्या उत्पाद पक्ष के बराबर क्यों होनी चाहिए?",
                expected_concept="द्रव्यमान संरक्षण का नियम बताता है कि रासायनिक अभिक्रिया में द्रव्यमान का निर्माण या विनाश नहीं हो सकता।",
            )
        elif language == "gu":
            title = f"પાયાના સિદ્ધાંતો: {topic_title}"
            why_this_matters = (
                f"તમે હાલમાં આ વિષયની શરૂઆત કરી રહ્યા છો (ચોકસાઈ: {acc_display}).{query_note} "
                f"ગોખવાને બદલે મૂળ નિયમો સમજવાથી તમારો આત્મવિશ્વાસ વધશે."
            )
            core_concept = (
                f"GSEB ધોરણ 10 અભ્યાસક્રમ સંદર્ભ{top_page_ref}: {top_chunk_text}..."
                if top_chunk_text else
                f"રાસાયણિક સમીકરણ દળનું સંરક્ષણ રાખીને પ્રક્રિયકોનું નીપજોમાં રૂપાંતર દર્શાવે છે."
            )
            step_by_step = [
                "પગલું 1: ડાબી બાજુ (LHS) પ્રક્રિયકો અને જમણી બાજુ (RHS) નીપજો ઓળખો.",
                "પગલું 2: બંને બાજુ દરેક રાસાયણિક તત્વના પરમાણુઓની ગણતરી કરો.",
                "પગલું 3: સૂત્ર આગળ સહગુણક મૂકીને તત્વો સંતુલિત કરો (સૂત્રના સબસ્ક્રિપ્ટ ક્યારેય ન બદલો!).",
                "પગલું 4: ચકાસો કે બંને બાજુ દરેક તત્વના કુલ પરમાણુઓ સમાન છે.",
            ]
            common_mistake = (
                "મોટાભાગના વિદ્યાર્થીઓ સૂત્રના સબસ્ક્રિપ્ટ બદલી નાખે છે (દા.ત. H2O ને બદલે H2O2 કરવું). "
                "સબસ્ક્રિપ્ટ બદલવાથી મૂળ રાસાયણિક પદાર્થ જ બદલાઈ જાય છે! માત્ર આગળ સહગુણક લગાવો."
            )
            quick_check = QuickCheckItem(
                question="પ્રક્રિયક બાજુના પરમાણુઓની સંખ્યા નીપજ બાજુ જેટલી જ કેમ હોવી જોઈએ?",
                expected_concept="દળ સંરક્ષણનો નિયમ દર્શાવે છે કે રાસાયણિક પ્રક્રિયામાં દળ કે પરમાણુઓનું સર્જન કે વિનાશ થતો નથી.",
            )
        else:
            title = f"Building Fundamentals: {topic_title}"
            why_this_matters = (
                f"You are currently establishing this topic (recent accuracy is {acc_display}).{query_note} "
                f"Rather than memorizing, focusing on the core rules will quickly boost your confidence."
            )
            core_concept = (
                f"According to the GSEB Standard 10 curriculum{top_page_ref}: "
                f"{top_chunk_text}..."
                if top_chunk_text else
                f"A chemical equation describes reactants turning into products while conserving mass."
            )
            step_by_step = [
                "Step 1: Identify all Reactants on the Left Hand Side (LHS) and Products on the Right Hand Side (RHS).",
                "Step 2: Count the individual atoms of each chemical element on both LHS and RHS.",
                "Step 3: Equalize elements one at a time by placing coefficients in front of formulas (never alter molecular subscripts!).",
                "Step 4: Verify that the total number of atoms for every element matches on both sides.",
            ]
            common_mistake = (
                "A frequent error is changing formula subscripts (e.g. turning H2O into H2O2) instead of "
                "multiplying the whole molecule with a coefficient (e.g. 2 H2O). Changing subscripts alters the chemical substance itself!"
            )
            quick_check = QuickCheckItem(
                question="Why must the number of atoms on the reactant side equal the product side?",
                expected_concept="The Law of Conservation of Mass dictates that mass/atoms cannot be created or destroyed in a chemical reaction.",
            )

        return StructuredExplanation(
            title=title,
            why_this_matters=why_this_matters,
            core_concept=core_concept,
            step_by_step=step_by_step,
            common_mistake=common_mistake,
            quick_check=quick_check,
        )

    def _build_developing_explanation(
        self,
        topic_title: str,
        accuracy: float,
        recent_acc: Optional[float],
        top_chunk_text: str,
        top_page_ref: str,
        student_query: Optional[str],
        recommendation: Optional[TopicRecommendation],
        language: str = "en",
    ) -> StructuredExplanation:
        acc_display = f"{recent_acc:.1f}%" if recent_acc is not None else f"{accuracy:.1f}%"

        if language == "hi":
            title = f"दक्षता सुदृढ़ीकरण: {topic_title}"
            why_this_matters = (
                f"आपकी समझ अच्छी तरह विकसित हो रही है ({acc_display} सटीकता)। "
                f"अब हम बुनियादी नियमों से आगे बढ़कर बहु-तत्वीय अभिक्रियाओं की ओर बढ़ते हैं।"
            )
            core_concept = (
                f"पाठ्यक्रम संदर्भ{top_page_ref}: {top_chunk_text}..."
                if top_chunk_text else
                f"रासायनिक अभिक्रियाओं में नए पदार्थ बनाने के लिए बंध टूटते और बनते हैं।"
            )
            step_by_step = [
                "1. सबसे अधिक परमाणु या भारी धातु वाले यौगिक से संतुलन शुरू करें।",
                "2. इसके बाद अधातुओं (जैसे कार्बन, सल्फर) को संतुलित करें, हाइड्रोजन और ऑक्सीजन को अंत के लिए रखें।",
                "3. यदि भिन्नात्मक गुणांक आते हैं, तो पूरे समीकरण को हर से गुणा करें।",
                "4. पूर्ण अभिक्रिया स्थिति दर्शाने के लिए भौतिक अवस्था संकेत (s, l, g, aq) जोड़ें।",
            ]
            common_mistake = (
                "बहु-परमाणुक आयनों को संतुलित करते समय कोष्ठक के अंदर के सभी तत्वों को गुणा करना भूल जाना (उदा. Ca(OH)2 में 2 O और 2 H हैं)।"
            )
            quick_check = QuickCheckItem(
                question="Fe + H2O -> Fe3O4 + H2 में, पहले किस तत्व को संतुलित करना सबसे अच्छा है?",
                expected_concept="सबसे अधिक परमाणु संख्या वाले यौगिक (Fe3O4) में आयरन (Fe) या ऑक्सीजन (O)।",
            )
        elif language == "gu":
            title = f"નિપુણતા સુદ્રઢીકરણ: {topic_title}"
            why_this_matters = (
                f"તમારી સમજ સારી રીતે વિકસી રહી છે ({acc_display} ચોકસાઈ). "
                f"હવે આપણે મૂળ નિયમોથી આગળ વધીને વધુ જટિલ રાસાયણિક સમીકરણો તરફ આગળ વધીએ."
            )
            core_concept = (
                f"અભ્યાસક્રમ સંદર્ભ{top_page_ref}: {top_chunk_text}..."
                if top_chunk_text else
                f"રાસાયણિક પ્રક્રિયાઓમાં નવા પદાર્થો બનાવવા માટે બંધ તૂટે છે અને નવા બંધ રચાય છે."
            )
            step_by_step = [
                "1. સૌથી વધુ પરમાણુઓ અથવા ભારે ધાતુ ધરાવતા સંયોજનથી સંતુલન શરૂ કરો.",
                "2. ત્યારબાદ અધાતુઓ (જેમ કે કાર્બન, સલ્ફર) સંતુલિત કરો, હાઇડ્રોજન અને ઓક્સિજન છેલ્લે રાખો.",
                "3. જો અપૂર્ણાંક સહગુણકો આવે, તો સમગ્ર સમીકરણને છેદ વડે ગુણો.",
                "4. પ્રક્રિયાની સ્થિતિ દર્શાવવા માટે ભૌતિક અવસ્થા સંકેતો (s, l, g, aq) ઉમેરો.",
            ]
            common_mistake = (
                "બહુપરમાણ્વીય આયનો સંતુલિત કરતી વખતે કૌંસની અંદરના બધા તત્વોને ગુણવાનું ભૂલી જવું (દા.ત. Ca(OH)2 માં 2 O અને 2 H છે)."
            )
            quick_check = QuickCheckItem(
                question="Fe + H2O -> Fe3O4 + H2 માં, પહેલા કયા તત્વને સંતુલિત કરવું શ્રેષ્ઠ છે?",
                expected_concept="સૌથી વધુ પરમાણુઓ ધરાવતા સંયોજન (Fe3O4) માં આયર્ન (Fe) અથવા ઓક્સિજન (O).",
            )
        else:
            title = f"Strengthening Mastery: {topic_title}"
            why_this_matters = (
                f"Your understanding is developing well ({acc_display} accuracy). "
                f"Now we bridge the gap from basic rules to handling multi-element chemical reactions."
            )
            core_concept = (
                f"Curriculum Reference{top_page_ref}: {top_chunk_text}..."
                if top_chunk_text else
                f"Chemical reactions involve the breaking and forming of bonds to produce new substances."
            )
            step_by_step = [
                "1. Start balancing with the compound having the maximum number of atoms or heaviest metal first.",
                "2. Next, balance non-metals (like Carbon, Sulfur, Nitrogen), saving Hydrogen and Oxygen for last.",
                "3. If fractional coefficients arise, multiply the entire equation by the common denominator.",
                "4. Add physical state notations (s, l, g, aq) to communicate complete reaction conditions.",
            ]
            common_mistake = (
                "Forgetting to multiply all elements inside parentheses when balancing polyatomic ions (e.g. Ca(OH)2 has 2 O and 2 H)."
            )
            quick_check = QuickCheckItem(
                question="In Fe + H2O -> Fe3O4 + H2, which element is best to balance first?",
                expected_concept="Iron (Fe) or Oxygen (O) in the compound with highest atom count (Fe3O4).",
            )

        return StructuredExplanation(
            title=title,
            why_this_matters=why_this_matters,
            core_concept=core_concept,
            step_by_step=step_by_step,
            common_mistake=common_mistake,
            quick_check=quick_check,
        )

    def _build_proficient_explanation(
        self,
        topic_title: str,
        accuracy: float,
        top_chunk_text: str,
        top_page_ref: str,
        student_query: Optional[str],
        language: str = "en",
    ) -> StructuredExplanation:
        if language == "hi":
            title = f"उन्नत अनुप्रयोग: {topic_title}"
            why_this_matters = (
                f"आपकी दक्षता मजबूत है ({accuracy:.1f}% सटीकता)। "
                f"आइए परीक्षा-स्तरीय प्रश्नों, अभिक्रिया स्थितियों और वर्गीकरण पर ध्यान केंद्रित करें।"
            )
            core_concept = (
                f"पाठ्यपुस्तक आधार{top_page_ref}: {top_chunk_text}..."
                if top_chunk_text else
                f"अभिक्रियाओं को संयोजन, वियोजन, विस्थापन, द्वि-विस्थापन या रेडॉक्स के रूप में वर्गीकृत किया जा सकता है।"
            )
            step_by_step = [
                "1. अभिक्रिया प्रकारों का मूल्यांकन करें: ऑक्सीकरण अवस्थाओं और इलेक्ट्रॉन स्थानांतरण की पहचान करें।",
                "2. तीर के ऊपर दर्शाए गए विशिष्ट उत्प्रेरक, तापमान या दबाव पर ध्यान दें।",
                "3. संतुलित रससमीकरणमिति (stoichiometry) को अवक्षेपण और गैस उत्सर्जन प्रेक्षणों से जोड़ें।",
            ]
            common_mistake = (
                "दर्शक आयनों की अनदेखी करना या विस्थापन को द्वि-विस्थापन के साथ भ्रमित करना।"
            )
            quick_check = QuickCheckItem(
                question="ऊष्माक्षेपी विस्थापन और ऊष्माशोषी वियोजन में क्या अंतर है?",
                expected_concept="ऊष्माक्षेपी परिवेश में ऊष्मा छोड़ती है; वियोजन के लिए ऊर्जा की आवश्यकता होती है।",
            )
        elif language == "gu":
            title = f"ઉન્નત પ્રયોજન: {topic_title}"
            why_this_matters = (
                f"તમારી પ્રવીણતા ઉત્તમ છે ({accuracy:.1f}% ચોકસાઈ). "
                f"ચાલો બોર્ડ પરીક્ષા સ્તરના પ્રશ્નો, પ્રક્રિયા પરિસ્થિતિઓ અને વર્ગીકરણ પર ધ્યાન આપીએ."
            )
            core_concept = (
                f"પાઠ્યપુસ્તક આધાર{top_page_ref}: {top_chunk_text}..."
                if top_chunk_text else
                f"પ્રક્રિયાઓને સંયોગીકરણ, વિઘટન, વિસ્થાપન, દ્વિ-વિસ્થાપન કે રેડોક્સ તરીકે વર્ગીકૃત કરી શકાય છે."
            )
            step_by_step = [
                "1. પ્રક્રિયા પ્રકારો ચકાસો: ઓક્સિડેશન અવસ્થાઓ અને ઇલેક્ટ્રોન ટ્રાન્સફર ઓળખો.",
                "2. તીર ઉપર દર્શાવેલ ઉદ્દીપક, તાપમાન કે દબાણની શરતો નોંધો.",
                "3. સંતુલિત સમીકરણને અવક્ષેપન અને વાયુ ઉદ્ભવ સાથે જોડો.",
            ]
            common_mistake = (
                "દર્શક આયનોને અવગણવા અથવા વિસ્થાપન અને દ્વિ-વિસ્થાપનને ભેગા કરી દેવા."
            )
            quick_check = QuickCheckItem(
                question="ઉષ્માક્ષેપક વિસ્થાપન અને ઉષ્માશોષક વિઘટન વચ્ચે શું તફાવત છે?",
                expected_concept="ઉષ્માક્ષેપક પર્યાવરણમાં ગરમી મુક્ત કરે છે; વિઘટન માટે ઊર્જાની જરૂર પડે છે.",
            )
        else:
            title = f"Advanced Application: {topic_title}"
            why_this_matters = (
                f"You have strong proficiency ({accuracy:.1f}% accuracy). "
                f"Let's focus on exam-level questions, reaction conditions, and classification."
            )
            core_concept = (
                f"Textbook Grounding{top_page_ref}: {top_chunk_text}..."
                if top_chunk_text else
                f"Reactions can be classified as combination, decomposition, displacement, double displacement, or redox."
            )
            step_by_step = [
                "1. Evaluate reaction types: identify oxidation states and electron transfer (redox).",
                "2. Note specific catalysts, temperature, or pressure requirements indicated above the reaction arrow.",
                "3. Connect balanced stoichiometry to real-world precipitation and gas evolution observations.",
            ]
            common_mistake = (
                "Overlooking spectator ions or confusing displacement with double displacement reactions."
            )
            quick_check = QuickCheckItem(
                question="What distinguishes an exothermic displacement from an endothermic decomposition?",
                expected_concept="Exothermic releases heat into surroundings; decomposition requires energy input (thermal/electrical/photolytic).",
            )

        return StructuredExplanation(
            title=title,
            why_this_matters=why_this_matters,
            core_concept=core_concept,
            step_by_step=step_by_step,
            common_mistake=common_mistake,
            quick_check=quick_check,
        )

    def _build_mastered_explanation(
        self,
        topic_title: str,
        accuracy: float,
        top_chunk_text: str,
        top_page_ref: str,
        language: str = "en",
    ) -> StructuredExplanation:
        if language == "hi":
            title = f"विषय दक्षता संश्लेषण: {topic_title}"
            why_this_matters = (
                f"आप {topic_title} में पूरी तरह निपुण हैं ({accuracy:.1f}% कुल प्रदर्शन)। "
                f"दीर्घकालिक स्मृति सुदृढ़ीकरण के लिए यहाँ त्वरित संकल्पना संश्लेषण है।"
            )
            core_concept = (
                f"पाठ्यक्रम संदर्भ{top_page_ref}: {top_chunk_text}..."
                if top_chunk_text else
                f"रासायनिक निरूपण, अभिक्रिया प्रकारों और संरक्षण नियमों पर पूर्ण दक्षता।"
            )
            step_by_step = [
                "1. अभिक्रिया वर्गीकरण का संश्लेषण: संयोजन, वियोजन, विस्थापन, रेडॉक्स।",
                "2. संक्षारण की रोकथाम, विकृतगंधिता शमन और औद्योगिक अनुप्रयोगों का विश्लेषण करें।",
                "3. प्रतियोगी बोर्ड परीक्षा प्रश्नों के लिए संतुलित आयनिक और आणविक समीकरण बनाएं।",
            ]
            common_mistake = (
                "यह मान लेना कि सभी ऑक्सीकरण अभिक्रियाओं में ऑक्सीजन ही शामिल होती है, न कि इलेक्ट्रॉनों की हानि।"
            )
            quick_check = QuickCheckItem(
                question="CuO + H2 -> Cu + H2O में, किस पदार्थ का ऑक्सीकरण होता है और किसका अपचयन?",
                expected_concept="H2 का H2O में ऑक्सीकरण होता है; CuO का Cu में अपचयन होता है।",
            )
        elif language == "gu":
            title = f"વિષય નિપુણતા સંશ્લેષણ: {topic_title}"
            why_this_matters = (
                f"તમે {topic_title} માં સંપૂર્ણ નિપુણ છો ({accuracy:.1f}% એકંદર કામગીરી). "
                f"લાંબા ગાળાના સ્મરણ માટે અહીં ઝડપી સંકલ્પના સંશ્લેષણ છે."
            )
            core_concept = (
                f"અભ્યાસક્રમ સંદર્ભ{top_page_ref}: {top_chunk_text}..."
                if top_chunk_text else
                f"રાસાયણિક સમીકરણો, પ્રક્રિયા પ્રકારો અને સંરક્ષણ નિયમો પર સંપૂર્ણ નિપુણતા."
            )
            step_by_step = [
                "1. પ્રક્રિયા વર્ગીકરણ સંશ્લેષણ: સંયોગીકરણ, વિઘટન, વિસ્થાપન, રેડોક્સ.",
                "2. ક્ષારણ અટકાવવા અને ઔદ્યોગિક પ્રયોજનોનું વિશ્લેષણ કરો.",
                "3. બોર્ડ પરીક્ષાના પ્રશ્નો માટે સંતુલિત આયનીય અને આણ્વિય સમીકરણો રચો.",
            ]
            common_mistake = (
                "એવું માની લેવું કે બધા ઓક્સિડેશનમાં માત્ર ઓક્સિજન જ સંકળાયેલ હોય છે, ઇલેક્ટ્રોન ગુમાવવાનું નહીં."
            )
            quick_check = QuickCheckItem(
                question="CuO + H2 -> Cu + H2O માં, કયા પદાર્થનું ઓક્સિડેશન અને કયા પદાર્થનું રિડક્શન થાય છે?",
                expected_concept="H2 નું H2O માં ઓક્સિડેશન થાય છે; CuO નું Cu માં રિડક્શન થાય છે.",
            )
        else:
            title = f"Topic Mastery Synthesis: {topic_title}"
            why_this_matters = (
                f"You have mastered {topic_title} ({accuracy:.1f}% overall performance). "
                f"Here is a rapid concept synthesis for long-term memory consolidation."
            )
            core_concept = (
                f"Curriculum Reference{top_page_ref}: {top_chunk_text}..."
                if top_chunk_text else
                f"Full mastery over chemical representations, reaction types, and conservation laws."
            )
            step_by_step = [
                "1. Synthesize reaction classification: Combination, Decomposition, Displacement, Redox.",
                "2. Analyze industrial applications such as corrosion prevention, rancidity mitigation, and synthesis.",
                "3. Formulate balanced ionic and molecular equations for competitive board examination questions.",
            ]
            common_mistake = (
                "Assuming all oxidation reactions involve oxygen rather than loss of electrons."
            )
            quick_check = QuickCheckItem(
                question="In CuO + H2 -> Cu + H2O, which substance is oxidized and which is reduced?",
                expected_concept="H2 is oxidized to H2O; CuO is reduced to Cu.",
            )

        return StructuredExplanation(
            title=title,
            why_this_matters=why_this_matters,
            core_concept=core_concept,
            step_by_step=step_by_step,
            common_mistake=common_mistake,
            quick_check=quick_check,
        )


class OnDeviceLLMExplanationEngine(ExplanationEngineInterface):
    """
    On-Device SLM (Small Language Model) Explanation Engine using quantized GGUF weights.
    Loads models locally via llama-cpp-python on CPU.
    Guarantees:
    - 100% offline, privacy-preserving execution on local device.
    - Zero external network, cloud API, or third-party client calls.
    - Conservative CPU execution with fallback to DeterministicExplanationEngine on any failure.
    """

    def __init__(
        self,
        model_path: Optional[str] = None,
        n_threads: int = 4,
        n_ctx: int = 2048,
        fallback_engine: Optional[ExplanationEngineInterface] = None,
    ):
        import os
        from backend.app.core.config import settings

        self.model_path = model_path if model_path is not None else settings.EDUNAVIKA_LOCAL_MODEL_PATH
        self.n_threads = n_threads
        self.n_ctx = n_ctx
        self.fallback_engine = fallback_engine or DeterministicExplanationEngine()
        self._llm = None
        self._load_attempted = False
        self._load_error: Optional[str] = None

    def _get_llm(self):
        """
        Lazily loads the local GGUF model if model_path exists.
        CPU-first inference: n_gpu_layers=0 strictly forces CPU execution.
        """
        import os
        if self._llm is not None:
            return self._llm
        if self._load_attempted:
            return None

        self._load_attempted = True
        if not self.model_path or not os.path.exists(self.model_path):
            self._load_error = f"Model path '{self.model_path}' is not configured or does not exist."
            return None

        try:
            import sys
            if sys.platform == "win32":
                try:
                    import ctypes
                    # SEM_FAILCRITICALERRORS (0x0001) | SEM_NOGPFAULTERRORBOX (0x0002)
                    _flags = 0x0001 | 0x0002
                    ctypes.windll.kernel32.SetErrorMode(_flags)
                    _prev = ctypes.c_uint()
                    ctypes.windll.kernel32.SetThreadErrorMode(_flags, ctypes.byref(_prev))
                except Exception:
                    pass

            from llama_cpp import Llama
            # Force CPU execution (n_gpu_layers=0)
            self._llm = Llama(
                model_path=self.model_path,
                n_ctx=self.n_ctx,
                n_threads=self.n_threads,
                n_gpu_layers=0,
                verbose=False,
            )
            return self._llm
        except Exception as e:
            self._load_error = str(e)
            return None

    def generate(
        self,
        student_id: str,
        topic_id: str,
        topic_title: str,
        knowledge_profile: TopicKnowledgeProfile,
        recommendation: Optional[TopicRecommendation],
        retrieved_contexts: List[RetrievedContentItem],
        student_query: Optional[str] = None,
        recent_error_notes: Optional[List[str]] = None,
        language: Optional[str] = "en",
    ) -> ExplanationResponse:
        import time
        from backend.app.services.prompt_builder import ExplanationPromptBuilder

        lang = (language or "en").lower()
        llm = self._get_llm()
        if llm is None or lang in ("hi", "gu"):
            # High-confidence deterministic local fallback for Hindi/Gujarati to prevent SLM hallucination and ensure 100% offline accuracy
            return self.fallback_engine.generate(
                student_id=student_id,
                topic_id=topic_id,
                topic_title=topic_title,
                knowledge_profile=knowledge_profile,
                recommendation=recommendation,
                retrieved_contexts=retrieved_contexts,
                student_query=student_query,
                recent_error_notes=recent_error_notes,
                language=lang,
            )

        # Build prompt using dedicated prompt builder
        system_prompt = ExplanationPromptBuilder.SYSTEM_INSTRUCTION
        user_prompt = ExplanationPromptBuilder.build_prompt(
            topic_title=topic_title,
            knowledge_profile=knowledge_profile,
            recommendation=recommendation,
            retrieved_contexts=retrieved_contexts,
            student_query=student_query,
            recent_error_notes=recent_error_notes,
        )

        try:
            start_time = time.perf_counter()
            response = llm.create_chat_completion(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                max_tokens=380,
                temperature=0.3,
                top_p=0.85,
            )
            elapsed_ms = int((time.perf_counter() - start_time) * 1000)

            raw_text = response["choices"][0]["message"]["content"].strip()

            # Parse structured explanation safely
            structured = self._parse_llm_response(raw_text, topic_title, knowledge_profile)

            # Determine teaching level
            mastery = knowledge_profile.mastery_level
            accuracy = knowledge_profile.accuracy
            if mastery in (MasteryLevel.UNASSESSED, MasteryLevel.NOVICE) or accuracy < 50.0:
                teaching_level = "FOUNDATIONAL_REMEDIATION"
                next_action = f"Complete 3 targeted foundational practice exercises on {topic_title}."
            elif mastery == MasteryLevel.DEVELOPING or accuracy < 70.0:
                teaching_level = "GUIDED_STRENGTHENING"
                next_action = f"Solve 4 multi-step problem checks on {topic_title} to achieve proficiency."
            elif mastery == MasteryLevel.PROFICIENT or accuracy < 85.0:
                teaching_level = "ADVANCED_APPLICATION"
                next_action = f"Attempt 2 board-exam application questions on {topic_title}."
            else:
                teaching_level = "SYNTHESIS_AND_MASTERY"
                next_action = f"Consolidate high-order applications and revision questions for {topic_title}."

            sources = [
                ExplanationSource(
                    source_document=c.source_document,
                    source_page=c.source_page,
                    source_reference=c.source_reference,
                    content_type=c.content_type,
                    relevance_score=c.score,
                )
                for c in retrieved_contexts
            ]

            personalization = PersonalizationContext(
                mastery_level=mastery,
                accuracy=accuracy,
                recent_accuracy=knowledge_profile.recent_accuracy,
                trend=knowledge_profile.trend,
                retention_risk=knowledge_profile.retention_risk,
            )

            return ExplanationResponse(
                student_id=student_id,
                topic_id=topic_id,
                topic_title=topic_title,
                explanation=raw_text,
                structured_explanation=structured,
                teaching_level=teaching_level,
                personalization=personalization,
                sources=sources,
                next_action=next_action,
                generation_mode="LOCAL_LLM",
                model_name="Qwen2.5-0.5B-Instruct",
                inference_time_ms=elapsed_ms,
            )

        except Exception as e:
            # Safe fallback if inference fails or crashes
            fb_res = self.fallback_engine.generate(
                student_id=student_id,
                topic_id=topic_id,
                topic_title=topic_title,
                knowledge_profile=knowledge_profile,
                recommendation=recommendation,
                retrieved_contexts=retrieved_contexts,
                student_query=student_query,
                recent_error_notes=recent_error_notes,
            )
            return fb_res

    def _parse_llm_response(
        self,
        raw_text: str,
        topic_title: str,
        knowledge_profile: TopicKnowledgeProfile,
    ) -> StructuredExplanation:
        """
        Safely parses the LLM generated response into StructuredExplanation.
        Uses regex heuristics for sections; falls back cleanly to robust defaults if sections are not delineated.
        """
        lines = [line.strip() for line in raw_text.split("\n") if line.strip()]

        title = f"AI Explanation: {topic_title}"
        why_this_matters = f"Tailored for your current {knowledge_profile.mastery_level.value} level."
        core_concept = ""
        step_by_step = []
        common_mistake = ""
        quick_check_q = f"What is the main principle of {topic_title}?"
        quick_check_ans = "Refer to the core concept."

        current_sec = None
        for line in lines:
            lower = line.lower()
            if "core concept" in lower:
                current_sec = "core"
                cleaned = re.sub(r"(?i)\**\s*core concept\s*\**[:\-]*", "", line).strip()
                if cleaned:
                    core_concept = cleaned
            elif "step by step" in lower or "steps" in lower:
                current_sec = "steps"
            elif "common misconception" in lower or "common mistake" in lower:
                current_sec = "mistake"
                cleaned = re.sub(r"(?i)\**\s*(common misconception|common mistake)\s*\**[:\-]*", "", line).strip()
                if cleaned:
                    common_mistake = cleaned
            elif "quick check" in lower:
                current_sec = "check"
                cleaned = re.sub(r"(?i)\**\s*quick check\s*\**[:\-]*", "", line).strip()
                if cleaned:
                    # Check if answer key is embedded in parentheses or dash, e.g. (Key: Conservation of mass)
                    ans_match = re.search(r"\((?:Key|Answer|Expected):\s*(.+?)\)", cleaned, re.IGNORECASE)
                    if ans_match:
                        quick_check_ans = ans_match.group(1).strip()
                        quick_check_q = re.sub(r"\((?:Key|Answer|Expected):\s*.+?\)", "", cleaned, flags=re.IGNORECASE).strip()
                    else:
                        quick_check_q = cleaned
            elif current_sec == "core":
                if not core_concept:
                    core_concept = line
                else:
                    core_concept += " " + line
            elif current_sec == "steps":
                if line.startswith(("-", "*", "1.", "2.", "3.", "4.")):
                    step_by_step.append(line.lstrip("-*1234. "))
            elif current_sec == "mistake":
                if not common_mistake:
                    common_mistake = line
                else:
                    common_mistake += " " + line
            elif current_sec == "check":
                if "answer" in lower or "key" in lower or "expected" in lower:
                    quick_check_ans = line
                elif quick_check_q == f"What is the main principle of {topic_title}?":
                    quick_check_q = line

        if not core_concept:
            core_concept = raw_text[:200] + "..." if len(raw_text) > 200 else raw_text
        if not step_by_step:
            step_by_step = [
                f"Review key definitions of {topic_title}.",
                "Practice step-by-step example problems from the textbook.",
            ]
        if not common_mistake:
            common_mistake = "Confusing core terminology under examination pressure."

        return StructuredExplanation(
            title=title,
            why_this_matters=why_this_matters,
            core_concept=core_concept,
            step_by_step=step_by_step,
            common_mistake=common_mistake,
            quick_check=QuickCheckItem(
                question=quick_check_q,
                expected_concept=quick_check_ans,
            ),
        )

