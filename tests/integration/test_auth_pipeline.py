"""
Adapt-X — Integration Tests for Authentication Pipeline & Security
Validates registration validation, password hashing, credential checks, JWT sessions, and logout.
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

from fastapi import HTTPException
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


def test_auth_registration_validation_errors():
    # 1. Invalid email
    try:
        asyncio.run(register(RegisterRequest(name="Test", email="bademail", password="password123")))
        assert False, "Should have rejected bad email"
    except HTTPException as e:
        assert e.status_code == 400
        assert "email" in e.detail.lower()

    # 2. Weak password
    try:
        asyncio.run(register(RegisterRequest(name="Test", email="test@adaptx.ai", password="123")))
        assert False, "Should have rejected weak password"
    except HTTPException as e:
        assert e.status_code == 400
        assert "weak" in e.detail.lower()

    # 3. Password mismatch
    try:
        asyncio.run(register(RegisterRequest(name="Test", email="test@adaptx.ai", password="password123", confirm_password="differentPassword")))
        assert False, "Should have rejected password mismatch"
    except HTTPException as e:
        assert e.status_code == 400
        assert "match" in e.detail.lower()


def test_auth_full_registration_and_login_lifecycle():
    email = "vikram@adaptx.ai"
    password = "SuperSecurePassword123"

    # 1. Successful registration
    reg_res = asyncio.run(register(RegisterRequest(
        name="Vikram Singh",
        email=email,
        password=password,
        confirm_password=password,
        preferred_language=LanguagePreference.HINDI,
    )))
    assert reg_res.success is True
    assert reg_res.user.email == email
    assert reg_res.twin.language == LanguagePreference.HINDI
    token = reg_res.token

    # 2. Duplicate registration rejected
    try:
        asyncio.run(register(RegisterRequest(name="Vikram Dupe", email=email, password=password)))
        assert False, "Should reject duplicate email"
    except HTTPException as e:
        assert e.status_code == 400
        assert "already exists" in e.detail.lower()

    # 3. Successful login
    login_res = asyncio.run(login(LoginRequest(email=email, password=password)))
    assert login_res.success is True
    assert login_res.user.full_name == "Vikram Singh"

    # 4. Wrong password login rejected
    try:
        asyncio.run(login(LoginRequest(email=email, password="WrongPassword")))
        assert False, "Should reject wrong password"
    except HTTPException as e:
        assert e.status_code == 401

    # 5. Nonexistent user login rejected
    try:
        asyncio.run(login(LoginRequest(email="nonexistent@adaptx.ai", password="password123")))
        assert False, "Should reject nonexistent user"
    except HTTPException as e:
        assert e.status_code == 401

    # 6. Authenticated /me endpoint
    me_res = asyncio.run(get_current_user(authorization=f"Bearer {login_res.token}"))
    assert me_res.user.email == email
    assert me_res.twin.language == LanguagePreference.HINDI

    # 7. Unauthenticated /me without token
    try:
        asyncio.run(get_current_user(authorization=None))
        assert False, "Should reject unauthenticated /me"
    except HTTPException as e:
        assert e.status_code == 401

    # 8. Logout
    logout_res = asyncio.run(logout(authorization=f"Bearer {login_res.token}"))
    assert logout_res["status"] == "SUCCESS"


def test_auth_judge_quickstart_guest():
    guest_res = asyncio.run(guest_login(GuestLoginRequest(
        persona=JudgePersona.MOTOR_DIFFICULTY,
        custom_name="Judge Vikram",
    )))
    assert guest_res.success is True
    assert guest_res.user.is_guest is True
    assert guest_res.twin.motor.voice_input is True
    assert guest_res.twin.motor.dwell_time_ms == 500


if __name__ == "__main__":
    test_auth_registration_validation_errors()
    test_auth_full_registration_and_login_lifecycle()
    test_auth_judge_quickstart_guest()
    print("All integration/test_auth_pipeline.py tests passed successfully!")
