"""
Adapt-X — Unit Tests for Authentication & Judge Personas
"""

import sys
import os
import builtins
import typing
builtins.Union = typing.Union

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from shared.schemas.auth_models import (
    AuthModality,
    JudgePersona,
    LoginRequest,
    RegisterRequest,
    GuestLoginRequest,
    UserProfile,
    AuthResponse,
)
from shared.schemas.models import LanguagePreference
from backend.routes.auth import _create_persona_twin, _USER_STORE


def test_persona_twin_generation_low_vision():
    twin = _create_persona_twin(JudgePersona.LOW_VISION, "twin_test_lv", LanguagePreference.ENGLISH)
    assert twin.visual.high_contrast is True
    assert twin.visual.large_text is True
    assert twin.haptics.enabled is True
    assert twin.haptics.intensity == "strong"


def test_persona_twin_generation_motor():
    twin = _create_persona_twin(JudgePersona.MOTOR_DIFFICULTY, "twin_test_m", LanguagePreference.HINDI)
    assert twin.motor.voice_input is True
    assert twin.motor.large_touch_targets is True
    assert twin.motor.dwell_time_ms == 500


def test_persona_twin_generation_hearing():
    twin = _create_persona_twin(JudgePersona.HEARING_IMPAIRMENT, "twin_test_h", LanguagePreference.ENGLISH)
    assert twin.hearing.sign_language is True
    assert twin.hearing.captions is True


def test_persona_twin_generation_elderly():
    twin = _create_persona_twin(JudgePersona.ELDERLY_SIMPLIFIED, "twin_test_e", LanguagePreference.ENGLISH)
    assert twin.comprehension.simplified_language is True
    assert twin.comprehension.one_step_at_a_time is True
    assert twin.comprehension.read_instructions_aloud is True


def test_auth_request_schema_validation():
    req = LoginRequest(username="judge", password="demo", auth_modality=AuthModality.PASSWORD)
    assert req.username == "judge"
    assert req.auth_modality == AuthModality.PASSWORD


if __name__ == "__main__":
    test_persona_twin_generation_low_vision()
    test_persona_twin_generation_motor()
    test_persona_twin_generation_hearing()
    test_persona_twin_generation_elderly()
    test_auth_request_schema_validation()
    print("All unit/test_auth.py tests passed successfully!")
