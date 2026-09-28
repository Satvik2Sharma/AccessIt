import pytest
from ai.learning.learning_service import AccessibilityLearningService
from shared.schemas.models import PersonalizationSuggestion

def test_pattern_suggestions_empty_baseline():
    service = AccessibilityLearningService()
    suggestions = service.get_pattern_suggestions()
    assert len(suggestions) >= 1
    assert "pattern_type" in suggestions[0]
    assert suggestions[0]["consent_required"] is True

def test_pattern_suggestions_voice_dominant():
    service = AccessibilityLearningService()
    for i in range(10):
        service.record_interaction(f"step_{i}", "voice", 3.0, 0, True)
    suggestions = service.get_pattern_suggestions()
    types = [s["pattern_type"] for s in suggestions]
    assert "preferred_modality" in types

def test_pattern_suggestions_high_retries():
    service = AccessibilityLearningService()
    for i in range(5):
        service.record_interaction("aadhaar_input", "voice", 20.0, 3, False)
    suggestions = service.get_pattern_suggestions()
    types = [s["pattern_type"] for s in suggestions]
    assert any(t in ("repeated_interaction_barrier", "task_failure_pattern") for t in types)

def test_pattern_suggestion_consent_required():
    service = AccessibilityLearningService()
    service.record_interaction("form_step", "voice", 2.0, 0, True)
    suggestions = service.get_pattern_suggestions()
    for s in suggestions:
        assert s["consent_required"] is True
