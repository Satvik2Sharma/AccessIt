import pytest
from ai.assistance.assistance_engine import AccessibilityAssistanceEngine
from shared.schemas.models import AccessibilityTwin, LanguagePreference

def test_assist_document_english():
    engine = AccessibilityAssistanceEngine()
    twin = AccessibilityTwin(id="t1", language=LanguagePreference.ENGLISH)
    result = engine.assist_understand_document(None, "What is the deadline?", twin)
    assert "title" in result
    assert "deadlines" in result
    assert "spoken_summary" in result
    assert result["language"] == "English"

def test_assist_document_hindi():
    engine = AccessibilityAssistanceEngine()
    twin = AccessibilityTwin(id="t1", language=LanguagePreference.HINDI)
    result = engine.assist_understand_document(None, "क्या है?", twin)
    assert result["language"] == "Hindi"

def test_assist_find_object():
    engine = AccessibilityAssistanceEngine()
    twin = AccessibilityTwin(id="t1")
    result = engine.assist_find_object("water bottle", twin)
    assert "direction" in result or "clock_hour" in result or "spoken_direction" in result

def test_assist_sign_communication():
    engine = AccessibilityAssistanceEngine()
    twin = AccessibilityTwin(id="t1")
    result = engine.assist_sign_communication(None, twin)
    assert "sign" in result
    assert result["sign"] == "HELP"
