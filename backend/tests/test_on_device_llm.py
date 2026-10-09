import pytest
import os
from unittest.mock import MagicMock, patch

from backend.app.domain.enums import (
    MasteryLevel,
    PerformanceTrend,
    RetentionRiskLevel,
    RecommendationAction,
    RevisionPriority,
)
from backend.app.schemas.knowledge_profile import TopicKnowledgeProfile
from backend.app.schemas.recommendation import TopicRecommendation
from backend.app.schemas.retrieval import RetrievedContentItem
from backend.app.schemas.explanation import ExplanationResponse
from backend.app.services.prompt_builder import ExplanationPromptBuilder
from backend.app.services.explanation_engine import (
    DeterministicExplanationEngine,
    OnDeviceLLMExplanationEngine,
)


@pytest.fixture
def sample_profile():
    return TopicKnowledgeProfile(
        topic_id="5a321a44-bc06-4db4-a50f-5e53f913b612",
        topic_title="Chemical Reactions and Equations",
        subject_name="Science",
        mastery_level=MasteryLevel.NOVICE,
        accuracy=33.3,
        total_attempts=6,
        correct_attempts=2,
        trend=PerformanceTrend.DECLINING,
        retention_risk=RetentionRiskLevel.HIGH,
        recent_accuracy=40.0,
        average_response_time_ms=12500,
    )


@pytest.fixture
def sample_recommendation():
    return TopicRecommendation(
        topic_id="5a321a44-bc06-4db4-a50f-5e53f913b612",
        topic_title="Chemical Reactions and Equations",
        subject_name="Science",
        action=RecommendationAction.REVISION,
        priority=RevisionPriority.HIGH,
        reason="Mastery is NOVICE and retention risk is HIGH.",
        score=175.0,
        mastery_level=MasteryLevel.NOVICE,
        accuracy=33.3,
        retention_risk=RetentionRiskLevel.HIGH,
        trend=PerformanceTrend.DECLINING,
    )


@pytest.fixture
def sample_contexts():
    return [
        RetrievedContentItem(
            content_id="chunk-ch1-p1",
            topic_id="5a321a44-bc06-4db4-a50f-5e53f913b612",
            topic_title="Chemical Reactions and Equations",
            content_text="A complete chemical equation represents the reactants, products and their physical states symbolically. Chemical equations are balanced to satisfy the law of conservation of mass.",
            content_type="CONCEPT",
            source_document="STD-10/Std-10_Science_English Medium.pdf",
            source_page=14,
            source_reference="Chapter 1: Chemical Reactions and Equations",
            score=5.82,
        ),
        RetrievedContentItem(
            content_id="chunk-ch1-p2",
            topic_id="5a321a44-bc06-4db4-a50f-5e53f913b612",
            topic_title="Chemical Reactions and Equations",
            content_text="In a combination reaction two or more substances combine to form a new single substance.",
            content_type="CONCEPT",
            source_document="STD-10/Std-10_Science_English Medium.pdf",
            source_page=16,
            source_reference="Chapter 1: Chemical Reactions and Equations",
            score=4.15,
        ),
    ]


def test_1_model_path_configuration():
    """Verify OnDeviceLLMExplanationEngine stores and respects the configured model path."""
    engine = OnDeviceLLMExplanationEngine(model_path="D:/custom/path/model.gguf")
    assert engine.model_path == "D:/custom/path/model.gguf"
    assert engine.n_threads == 4
    assert engine.n_ctx == 2048


def test_2_missing_model_deterministic_fallback(sample_profile, sample_recommendation, sample_contexts):
    """When model path does not exist on disk, engine safely triggers DeterministicExplanationEngine fallback."""
    engine = OnDeviceLLMExplanationEngine(model_path="D:/nonexistent/path/fake_model.gguf")
    res = engine.generate(
        student_id="test-student",
        topic_id=sample_profile.topic_id,
        topic_title=sample_profile.topic_title,
        knowledge_profile=sample_profile,
        recommendation=sample_recommendation,
        retrieved_contexts=sample_contexts,
        student_query="Explain balancing equations",
    )
    assert isinstance(res, ExplanationResponse)
    assert res.generation_mode == "DETERMINISTIC_FALLBACK"
    assert res.model_name is None
    assert "Chemical Reactions and Equations" in res.explanation
    assert len(res.sources) == 2


def test_3_prompt_builder_contains_student_profile(sample_profile, sample_recommendation, sample_contexts):
    """Verify student profile signals (mastery, accuracy, trend, risk) appear distinctly in the prompt."""
    prompt = ExplanationPromptBuilder.build_prompt(
        topic_title="Chemical Reactions and Equations",
        knowledge_profile=sample_profile,
        recommendation=sample_recommendation,
        retrieved_contexts=sample_contexts,
    )
    assert "=== STUDENT PROFILE ===" in prompt
    assert "Mastery Level: NOVICE" in prompt
    assert "33.3%" in prompt
    assert "Retention/Forgetting Risk: HIGH" in prompt


def test_4_prompt_builder_contains_recommendation(sample_profile, sample_recommendation, sample_contexts):
    """Verify recommendation context (action, priority, reason) appears in prompt."""
    prompt = ExplanationPromptBuilder.build_prompt(
        topic_title="Chemical Reactions and Equations",
        knowledge_profile=sample_profile,
        recommendation=sample_recommendation,
        retrieved_contexts=sample_contexts,
    )
    assert "=== RECOMMENDATION ===" in prompt
    assert "REVISION" in prompt
    assert "HIGH" in prompt
    assert "Mastery is NOVICE" in prompt


def test_5_prompt_builder_contains_curriculum_and_page_citations(sample_profile, sample_recommendation, sample_contexts):
    """Verify curriculum excerpts and textbook page citations appear in prompt."""
    prompt = ExplanationPromptBuilder.build_prompt(
        topic_title="Chemical Reactions and Equations",
        knowledge_profile=sample_profile,
        recommendation=sample_recommendation,
        retrieved_contexts=sample_contexts,
    )
    assert "=== CURRICULUM CONTEXT ===" in prompt
    assert "[Textbook Page 14]" in prompt
    assert "law of conservation of mass" in prompt


def test_6_prompt_builder_contains_student_question(sample_profile, sample_recommendation, sample_contexts):
    """Verify custom student query is clearly formatted in the prompt."""
    prompt = ExplanationPromptBuilder.build_prompt(
        topic_title="Chemical Reactions and Equations",
        knowledge_profile=sample_profile,
        recommendation=sample_recommendation,
        retrieved_contexts=sample_contexts,
        student_query="I don't understand how to balance chemical equations",
    )
    assert "=== STUDENT QUESTION ===" in prompt
    assert "I don't understand how to balance chemical equations" in prompt


def test_7_mock_local_inference_boundary_success(sample_profile, sample_recommendation, sample_contexts):
    """Verify that when local LLM succeeds, generation_mode is LOCAL_LLM with model_name and latency."""
    engine = OnDeviceLLMExplanationEngine(model_path="dummy_valid.gguf")

    # Mock the internal llama instance
    mock_llm = MagicMock()
    mock_llm.create_chat_completion.return_value = {
        "choices": [
            {
                "message": {
                    "content": (
                        "**Core Concept:** A chemical equation represents reactants transforming into products.\n"
                        "**Step by Step:**\n"
                        "- Count atoms of each element on both sides.\n"
                        "- Add coefficients to balance atoms without altering subscripts.\n"
                        "**Common Misconception:** Changing subscripts like H2O to H2O2.\n"
                        "**Quick Check:** Why must equations be balanced? (Key: Conservation of mass)"
                    )
                }
            }
        ]
    }

    with patch.object(engine, "_get_llm", return_value=mock_llm):
        res = engine.generate(
            student_id="test-student",
            topic_id=sample_profile.topic_id,
            topic_title=sample_profile.topic_title,
            knowledge_profile=sample_profile,
            recommendation=sample_recommendation,
            retrieved_contexts=sample_contexts,
            student_query="How do I balance equations?",
        )

    assert res.generation_mode == "LOCAL_LLM"
    assert res.model_name == "Qwen2.5-0.5B-Instruct"
    assert res.inference_time_ms is not None
    assert res.teaching_level == "FOUNDATIONAL_REMEDIATION"
    assert "Conservation of mass" in res.structured_explanation.quick_check.expected_concept
    assert len(res.sources) == 2


def test_8_mock_local_inference_exception_falls_back(sample_profile, sample_recommendation, sample_contexts):
    """If local LLM raises an exception during generation, it seamlessly falls back to DETERMINISTIC_FALLBACK."""
    engine = OnDeviceLLMExplanationEngine(model_path="dummy_valid.gguf")

    mock_llm = MagicMock()
    mock_llm.create_chat_completion.side_effect = RuntimeError("Simulated local OOM / CPU exception")

    with patch.object(engine, "_get_llm", return_value=mock_llm):
        res = engine.generate(
            student_id="test-student",
            topic_id=sample_profile.topic_id,
            topic_title=sample_profile.topic_title,
            knowledge_profile=sample_profile,
            recommendation=sample_recommendation,
            retrieved_contexts=sample_contexts,
        )

    assert res.generation_mode == "DETERMINISTIC_FALLBACK"
    assert res.model_name is None
    assert "Building Fundamentals" in res.structured_explanation.title


def test_9_no_external_api_calls_in_engine_modules():
    """Verify that explanation engine and prompt builder files have zero external cloud AI SDKs or HTTP libraries."""
    import backend.app.services.explanation_engine as ee_mod
    import backend.app.services.prompt_builder as pb_mod

    ee_code = open(ee_mod.__file__, "r", encoding="utf-8").read()
    pb_code = open(pb_mod.__file__, "r", encoding="utf-8").read()

    forbidden = ["openai", "google.generativeai", "anthropic", "requests.", "httpx.", "urllib.request"]
    for word in forbidden:
        assert word not in ee_code, f"Found forbidden cloud/network reference '{word}' in explanation_engine.py"
        assert word not in pb_code, f"Found forbidden cloud/network reference '{word}' in prompt_builder.py"


def test_10_empty_model_path_defaults_cleanly_to_fallback(sample_profile, sample_recommendation, sample_contexts):
    """When EDUNAVIKA_LOCAL_MODEL_PATH is blank or empty string, fallback occurs cleanly without errors."""
    engine = OnDeviceLLMExplanationEngine(model_path="")
    res = engine.generate(
        student_id="test-student",
        topic_id=sample_profile.topic_id,
        topic_title=sample_profile.topic_title,
        knowledge_profile=sample_profile,
        recommendation=sample_recommendation,
        retrieved_contexts=sample_contexts,
    )
    assert res.generation_mode == "DETERMINISTIC_FALLBACK"
    assert res.model_name is None
