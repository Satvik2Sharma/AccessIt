"""
Adapt-X — Integration Tests for Authentication & Judge Quick-Start
Validates login, registration, guest judge personas, token checks, and session teardown.
"""

import sys
import os
import asyncio
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
)
from shared.schemas.models import LanguagePreference
from backend.routes.auth import (
    login,
    register,
    guest_login,
    get_current_user,
    get_judge_personas,
    logout,
)


def test_auth_judge_personas_list():
    personas = asyncio.run(get_judge_personas())
    assert len(personas) >= 4
    persona_ids = [p.persona_id for p in personas]
    assert "low_vision" in persona_ids
    assert "motor_difficulty" in persona_ids
    assert "hearing_impairment" in persona_ids
    assert "elderly_simplified" in persona_ids


def test_auth_guest_judge_login():
    req = GuestLoginRequest(persona=JudgePersona.LOW_VISION, custom_name="Lead Judge")
    res = asyncio.run(guest_login(req))
    assert res.success is True
    assert res.token.startswith("adaptx_token_")
    assert res.twin.visual.high_contrast is True
    assert res.user.is_guest is True

    # Validate active token
    me_res = asyncio.run(get_current_user(authorization=f"Bearer {res.token}"))
    assert me_res.user.user_id == res.user.user_id


def test_auth_register_and_login_flow():
    # 1. Register new user
    reg_req = RegisterRequest(
        username="judge_priya",
        full_name="Priya Patel",
        preferred_language=LanguagePreference.HINDI,
        password="securePassword123",
        pin="4321",
    )
    reg_res = asyncio.run(register(reg_req))
    assert reg_res.success is True
    assert reg_res.user.username == "judge_priya"

    # 2. Login with registered credentials
    login_req = LoginRequest(
        username="judge_priya",
        password="securePassword123",
        auth_modality=AuthModality.PASSWORD,
    )
    login_res = asyncio.run(login(login_req))
    assert login_res.success is True
    assert login_res.user.full_name == "Priya Patel"

    # 3. Logout
    logout_res = asyncio.run(logout(authorization=f"Bearer {login_res.token}"))
    assert logout_res["status"] == "SUCCESS"


if __name__ == "__main__":
    test_auth_judge_personas_list()
    test_auth_guest_judge_login()
    test_auth_register_and_login_flow()
    print("All integration/test_auth_pipeline.py tests passed successfully!")
