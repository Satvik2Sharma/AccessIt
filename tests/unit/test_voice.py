"""
Unit Tests for Voice Assistant, Command Processing, and TTS Contracts
"""

import sys
import os

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from shared.schemas.models import (
    VoiceCommandRequest,
    VoiceCommandResponse,
    TTSRequest,
    TTSResponse,
    LanguagePreference,
)
from backend.services.pipeline_service import pipeline_service
from backend.services.session_service import session_service


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


if __name__ == "__main__":
    test_voice_command_form_intent()
    test_voice_command_document_intent()
    test_voice_dialogue_session_tracking()
    print("All unit/test_voice.py tests passed!")
