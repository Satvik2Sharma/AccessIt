import pytest
from ai.voice.voice_command import VoiceCommandProcessor
from shared.schemas.models import AccessibilityTwin, LanguagePreference

def test_voice_pipeline_english():
    processor = VoiceCommandProcessor()
    twin = AccessibilityTwin(id="t1", language=LanguagePreference.ENGLISH)
    result = processor.process(text_input="What is the deadline in this notice?", twin=twin)
    assert result["voice_command"]["raw_text"] == "What is the deadline in this notice?"
    assert "intent_analysis" in result
    assert result["intent_analysis"]["intent"] == "UNDERSTAND_DOCUMENT"

def test_voice_pipeline_hindi_twin():
    processor = VoiceCommandProcessor()
    twin = AccessibilityTwin(id="t1", language=LanguagePreference.HINDI)
    result = processor.process(text_input="Form भरने में मदद करो", twin=twin)
    assert "intent_analysis" in result

def test_voice_pipeline_no_input():
    processor = VoiceCommandProcessor()
    result = processor.process()
    assert "error" in result
