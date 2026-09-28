"""
Adapt-X — Unit Tests for Authentication, Password Hashing, JWT Tokens & Schemas
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
from backend.routes.auth import (
    hash_password,
    verify_password,
    create_access_token,
    verify_access_token,
    _create_persona_twin,
    EMAIL_REGEX,
)


def test_password_hashing_and_verification():
    raw_pass = "SecurePass@2026"
    hashed = hash_password(raw_pass)
    assert hashed != raw_pass
    assert "$" in hashed
    assert verify_password(raw_pass, hashed) is True
    assert verify_password("WrongPassword", hashed) is False


def test_token_creation_and_validation():
    token = create_access_token("usr_123", "test@adaptx.ai", "twin_123", expires_in_hours=2)
    assert token is not None
    assert len(token.split(".")) == 3

    payload = verify_access_token(token)
    assert payload["sub"] == "usr_123"
    assert payload["email"] == "test@adaptx.ai"
    assert payload["twin_id"] == "twin_123"


def test_invalid_token_tampering():
    token = create_access_token("usr_123", "test@adaptx.ai", "twin_123")
    tampered_token = token[:-5] + "ABCDE"
    try:
        verify_access_token(tampered_token)
        assert False, "Should have raised HTTPException for tampered token"
    except Exception as e:
        assert "401" in str(e) or "signature" in str(e).lower()


def test_email_regex_validation():
    assert EMAIL_REGEX.match("valid.user@adaptx.ai") is not None
    assert EMAIL_REGEX.match("not-an-email") is None
    assert EMAIL_REGEX.match("missing@domain") is None


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


if __name__ == "__main__":
    test_password_hashing_and_verification()
    test_token_creation_and_validation()
    test_invalid_token_tampering()
    test_email_regex_validation()
    test_persona_twin_generation_low_vision()
    test_persona_twin_generation_motor()
    test_persona_twin_generation_hearing()
    test_persona_twin_generation_elderly()
    print("All unit/test_auth.py tests passed successfully!")
