"""
Unit Tests for Voice Assistant, Command Processing, and TTS Contracts
"""

import sys
import os
import pytest

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from shared.schemas.models import (
    VoiceCommandRequest,
    VoiceCommandResponse,
    TTSRequest,
    TTSResponse,
    LanguagePreference,
    VoiceCommand,
)
from backend.services.pipeline_service import pipeline_service
from backend.services.session_service import session_service
from ai.voice.speech_to_text import SpeechToTextEngine
from ai.voice.text_to_speech import TextToSpeechEngine
from ai.voice.voice_command import VoiceCommandProcessor


def test_voice_command_form_intent():
    res = pipeline_service.process_voice_command("Please help me fill the scholarship form")
    assert res["classified_intent"] == "FORM_COMPLETION"
    assert "session_id" in res
    assert res["suggested_action"] == "START_FORM_COMPLETION"


def test_voice_command_document_intent():
    res = pipeline_service.process_voice_command("What are the requirements in this circular?")
    assert res["classified_intent"] == "UNDERSTAND_DOCUMENT"
    assert res["suggested_action"] == "SCAN_DOCUMENT"


def test_voice_dialogue_session_tracking():
    sess = session_service.get_or_create_voice_session()
    sid = sess["session_id"]

    pipeline_service.process_voice_command("Where is my bottle?", session_id=sid)
    updated = session_service.get_or_create_voice_session(sid)
    assert updated["turn_count"] >= 1
    assert len(updated["dialogue"]) >= 1


def test_stt_text_input():
    engine = SpeechToTextEngine()
    result = engine.transcribe(text_input="Read this document")
    assert isinstance(result, VoiceCommand)
    assert result.raw_text == "Read this document"
    assert result.source == "text_input"
    assert result.confidence > 0.9


def test_stt_empty_input():
    engine = SpeechToTextEngine()
    result = engine.transcribe()
    assert result.raw_text == ""
    assert result.source == "empty"


def test_tts_english():
    engine = TextToSpeechEngine()
    payload = engine.prepare("Hello", language=LanguagePreference.ENGLISH)
    assert payload["lang_code"] == "en-IN"
    assert "ssml" in payload
    assert "speed_rate" in payload


def test_tts_hindi():
    engine = TextToSpeechEngine()
    payload = engine.prepare("नमस्ते", language=LanguagePreference.HINDI)
    assert payload["lang_code"] == "hi-IN"


def test_voice_command_processor_routes_intent():
    processor = VoiceCommandProcessor()
    result = processor.process(text_input="Help me fill this form")
    assert "voice_command" in result
    assert "intent_analysis" in result
    intent = result["intent_analysis"]
    assert "intent" in intent
    assert intent["intent"] == "FORM_COMPLETION"


def test_voice_command_empty():
    processor = VoiceCommandProcessor()
    result = processor.process()
    assert "error" in result


if __name__ == "__main__":
    test_voice_command_form_intent()
    test_voice_command_document_intent()
    test_voice_dialogue_session_tracking()
    print("All unit/test_voice.py tests passed!")
