"""
Adapt-X (Sahayak AI) — Secure Authentication & Persona Routes
Provides robust email/password registration, password hashing (PBKDF2-HMAC-SHA256),
JWT-style signed tokens, session lifecycle, and judge accessibility persona presets.
"""

import os
import re
import time
import json
import hmac
import hashlib
import base64
import uuid
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends, Header
from pydantic import BaseModel

from backend.config import settings
from shared.schemas.models import (
    AccessibilityTwin,
    LanguagePreference,
    VisualPreferences,
    HearingPreferences,
    MotorPreferences,
    ComprehensionPreferences,
    HapticPreferences,
    InputModality,
    OutputModality,
)
from shared.schemas.auth_models import (
    AuthModality,
    JudgePersona,
    LoginRequest,
    RegisterRequest,
    GuestLoginRequest,
    UserProfile,
    AuthResponse,
    PersonaPresetInfo,
)
from backend.services.pipeline_service import pipeline_service

router = APIRouter(prefix="/auth", tags=["Authentication & Personas"])

# Regex pattern for email format verification
EMAIL_REGEX = re.compile(r"^[\w\.-]+@[\w\.-]+\.\w+$")


# ----------------------------------------------------
# 1. Cryptographic Password Hashing (PBKDF2-HMAC-SHA256)
# ----------------------------------------------------

def hash_password(password: str) -> str:
    """Hashes a plaintext password using PBKDF2-HMAC-SHA256 with a unique random salt."""
    salt = os.urandom(16).hex()
    key = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        iterations=100_000,
    ).hex()
    return f"{salt}${key}"


def verify_password(plain_password: str, hashed_value: str) -> bool:
    """Verifies a plaintext password against a salt$key hashed string."""
    try:
        if "$" not in hashed_value:
            # Fallback legacy check
            return plain_password == hashed_value
        salt, expected_key = hashed_value.split("$", 1)
        computed_key = hashlib.pbkdf2_hmac(
            "sha256",
            plain_password.encode("utf-8"),
            salt.encode("utf-8"),
            iterations=100_000,
        ).hex()
        return hmac.compare_digest(computed_key, expected_key)
    except Exception:
        return False


# ----------------------------------------------------
# 2. Signed Token Management (HMAC-SHA256)
# ----------------------------------------------------

def _base64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode("utf-8").rstrip("=")


def _base64url_decode(data: str) -> bytes:
    padding = "=" * (4 - (len(data) % 4)) if len(data) % 4 != 0 else ""
    return base64.urlsafe_b64decode(data + padding)


def create_access_token(user_id: str, email: str, twin_id: str, expires_in_hours: int = 24) -> str:
    """Generates a cryptographically signed HMAC-SHA256 JWT-style token."""
    header = {"alg": "HS256", "typ": "JWT"}
    now_ts = int(time.time())
    payload = {
        "sub": user_id,
        "email": email,
        "twin_id": twin_id,
        "iat": now_ts,
        "exp": now_ts + (expires_in_hours * 3600),
    }

    header_b64 = _base64url_encode(json.dumps(header).encode("utf-8"))
    payload_b64 = _base64url_encode(json.dumps(payload).encode("utf-8"))
    signing_input = f"{header_b64}.{payload_b64}".encode("utf-8")

    signature = hmac.new(
        settings.jwt_secret.encode("utf-8"),
        signing_input,
        hashlib.sha256
    ).digest()
    sig_b64 = _base64url_encode(signature)

    return f"{header_b64}.{payload_b64}.{sig_b64}"


def verify_access_token(token: str) -> Dict[str, Any]:
    """Decodes and validates a signed token signature and expiration timestamp."""
    try:
        parts = token.split(".")
        if len(parts) != 3:
            raise ValueError("Malformed token format.")

        header_b64, payload_b64, sig_b64 = parts
        signing_input = f"{header_b64}.{payload_b64}".encode("utf-8")
        expected_sig = hmac.new(
            settings.jwt_secret.encode("utf-8"),
            signing_input,
            hashlib.sha256
        ).digest()

        actual_sig = _base64url_decode(sig_b64)
        if not hmac.compare_digest(expected_sig, actual_sig):
            raise ValueError("Invalid token signature.")

        payload_bytes = _base64url_decode(payload_b64)
        payload = json.loads(payload_bytes.decode("utf-8"))

        # Check expiration
        if payload.get("exp", 0) < int(time.time()):
            raise ValueError("Token has expired.")

        return payload
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Authentication error: {str(e)}")


# ----------------------------------------------------
# 3. In-Memory Verified User & Token Store
# ----------------------------------------------------

_USER_STORE: Dict[str, Dict[str, Any]] = {
    "judge@adaptx.ai": {
        "user_id": "usr_judge_001",
        "email": "judge@adaptx.ai",
        "username": "judge",
        "full_name": "Hackathon Judge",
        "password_hash": hash_password("demo1234"),
        "pin": "1234",
        "twin_id": "twin_judge",
        "is_guest": True,
        "active_persona": "low_vision",
        "created_at": datetime.utcnow().isoformat(),
    },
    "aarav@adaptx.ai": {
        "user_id": "usr_default_001",
        "email": "aarav@adaptx.ai",
        "username": "aarav",
        "full_name": "Aarav Sharma",
        "password_hash": hash_password("password123"),
        "pin": "1234",
        "twin_id": "default_user",
        "is_guest": False,
        "active_persona": "default",
        "created_at": datetime.utcnow().isoformat(),
    },
}

_ACTIVE_TOKENS: Dict[str, Dict[str, Any]] = {}


def _create_persona_twin(persona: JudgePersona, twin_id: str, language: LanguagePreference) -> AccessibilityTwin:
    """Configures dynamic Accessibility Twin profiles for distinct accessibility needs."""
    if persona == JudgePersona.LOW_VISION:
        return AccessibilityTwin(
            id=twin_id,
            language=language,
            visual=VisualPreferences(
                large_text=True,
                high_contrast=True,
                magnification_level=1.75,
                color_inversion=False,
            ),
            haptics=HapticPreferences(enabled=True, intensity="strong"),
            preferred_input=InputModality.VOICE,
            preferred_output=OutputModality.VOICE_AND_TEXT,
        )
    elif persona == JudgePersona.MOTOR_DIFFICULTY:
        return AccessibilityTwin(
            id=twin_id,
            language=language,
            motor=MotorPreferences(
                voice_input=True,
                large_touch_targets=True,
                reduce_scrolling=True,
                dwell_time_ms=500,
            ),
            preferred_input=InputModality.VOICE,
            preferred_output=OutputModality.VOICE_AND_TEXT,
        )
    elif persona == JudgePersona.HEARING_IMPAIRMENT:
        return AccessibilityTwin(
            id=twin_id,
            language=language,
            hearing=HearingPreferences(
                captions=True,
                visual_alerts=True,
                sign_language=True,
            ),
            preferred_input=InputModality.SIGN,
            preferred_output=OutputModality.TEXT,
        )
    elif persona == JudgePersona.ELDERLY_SIMPLIFIED:
        return AccessibilityTwin(
            id=twin_id,
            language=language,
            visual=VisualPreferences(large_text=True, high_contrast=False),
            comprehension=ComprehensionPreferences(
                simplified_language=True,
                one_step_at_a_time=True,
                read_instructions_aloud=True,
                show_task_progress=True,
            ),
            preferred_input=InputModality.VOICE,
            preferred_output=OutputModality.VOICE_AND_TEXT,
        )
    else:
        return AccessibilityTwin(
            id=twin_id,
            language=language,
            preferred_input=InputModality.VOICE,
            preferred_output=OutputModality.VOICE_AND_TEXT,
        )


# ----------------------------------------------------
# 4. REST Endpoints
# ----------------------------------------------------

@router.get("/personas", response_model=List[PersonaPresetInfo])
async def get_judge_personas():
    """
    Returns preset accessibility personas allowing hackathon judges to instantly test
    the platform across different functional barrier profiles.
    """
    return [
        PersonaPresetInfo(
            persona_id="low_vision",
            title="Low Vision & Glare Sensitivity",
            description="Enables high-contrast cards, 12-hour clock spatial audio guidance, and tactile haptic pulses.",
            barriers_addressed=["Small text", "Low contrast documents", "Spatial orientation without visual cues"],
            twin_configuration={"high_contrast": True, "large_text": True, "haptics": "strong", "output": "voice_and_text"},
        ),
        PersonaPresetInfo(
            persona_id="motor_difficulty",
            title="Motor & Tremor Assistance",
            description="Enables hands-free voice commands, debounce dwell thresholds, and large touch hitboxes.",
            barriers_addressed=["Accidental multi-taps", "Complex pinch-to-zoom", "Small checkbox targets"],
            twin_configuration={"voice_input": True, "large_targets": True, "dwell_time_ms": 500},
        ),
        PersonaPresetInfo(
            persona_id="hearing_impairment",
            title="Deaf & Hard of Hearing (ISL Sign Talk)",
            description="Prioritizes visual captions, real-time Indian Sign Language (ISL) recognition, and optical alerts.",
            barriers_addressed=["Audio cues", "Speech recognition only flows", "Complex text jargon"],
            twin_configuration={"captions": True, "sign_language": True, "input": "sign", "output": "text"},
        ),
        PersonaPresetInfo(
            persona_id="elderly_simplified",
            title="Cognitive & Bureaucratic Jargon Relief",
            description="Flattens government/scholarship multi-step forms into friendly one-step-at-a-time voice prompts.",
            barriers_addressed=["Complex bureaucratic terminology", "Cognitive overload", "Missed deadlines"],
            twin_configuration={"simplified_language": True, "one_step_at_a_time": True, "read_aloud": True},
        ),
    ]


@router.post("/register", response_model=AuthResponse)
async def register(req: RegisterRequest):
    """
    Registers a new user with email, name, password validation, and sets up their Accessibility Twin.
    """
    # 1. Validate email format
    email = req.email.strip().lower()
    if not EMAIL_REGEX.match(email):
        raise HTTPException(status_code=400, detail="Invalid email format. Please provide a valid email address.")

    # 2. Validate password strength
    password = req.password
    if not password or len(password) < 6:
        raise HTTPException(status_code=400, detail="Password is too weak. Must be at least 6 characters.")

    # 3. Check password confirmation if provided
    if req.confirm_password and req.confirm_password != password:
        raise HTTPException(status_code=400, detail="Passwords do not match.")

    # 4. Check duplicate email / username
    if email in _USER_STORE:
        raise HTTPException(status_code=400, detail="An account with this email already exists.")

    username = req.username.strip().lower() if req.username else email.split("@")[0]
    for u in _USER_STORE.values():
        if u["username"] == username:
            username = f"{username}_{uuid.uuid4().hex[:4]}"
            break

    user_id = f"usr_{uuid.uuid4().hex[:8]}"
    twin_id = f"twin_{username}"

    # 5. Initialize Accessibility Twin
    twin = req.initial_twin or AccessibilityTwin(id=twin_id, language=req.preferred_language)
    pipeline_service.twin_service.update_twin(twin)

    # 6. Store user with hashed password
    user_record = {
        "user_id": user_id,
        "email": email,
        "username": username,
        "full_name": req.name.strip(),
        "password_hash": hash_password(password),
        "pin": req.pin or "1234",
        "twin_id": twin_id,
        "is_guest": False,
        "active_persona": "custom",
        "created_at": datetime.utcnow().isoformat(),
    }
    _USER_STORE[email] = user_record

    # 7. Generate authenticated session token
    token = create_access_token(user_id=user_id, email=email, twin_id=twin_id)
    _ACTIVE_TOKENS[token] = user_record

    user_profile = UserProfile(
        user_id=user_id,
        email=email,
        username=username,
        full_name=req.name.strip(),
        twin_id=twin_id,
        is_guest=False,
        active_persona="custom",
    )

    return AuthResponse(
        token=token,
        user=user_profile,
        twin=twin,
        message="Registration successful. Accessibility profile initialized.",
    )


@router.post("/login", response_model=AuthResponse)
async def login(req: LoginRequest):
    """
    Authenticates user by email/username and password or PIN. Returns access token and Accessibility Twin.
    """
    identifier = (req.email or req.username or "").strip().lower()
    if not identifier:
        raise HTTPException(status_code=400, detail="Email or username is required.")

    # Look up by email or username
    user_record = None
    if identifier in _USER_STORE:
        user_record = _USER_STORE[identifier]
    else:
        for u in _USER_STORE.values():
            if u["username"].lower() == identifier or u["email"].lower() == identifier:
                user_record = u
                break

    if not user_record:
        # Nonexistent user
        raise HTTPException(status_code=401, detail="Invalid email or password.")

    # Validate credential based on modality
    if req.auth_modality == AuthModality.PIN:
        if not req.pin or req.pin != user_record.get("pin", "1234"):
            raise HTTPException(status_code=401, detail="Invalid PIN.")
    else:
        password = req.password or ""
        if not password or not verify_password(password, user_record.get("password_hash", "")):
            raise HTTPException(status_code=401, detail="Invalid email or password.")

    twin = pipeline_service.twin_service.get_twin(user_record["twin_id"])
    token = create_access_token(
        user_id=user_record["user_id"],
        email=user_record["email"],
        twin_id=user_record["twin_id"]
    )
    _ACTIVE_TOKENS[token] = user_record

    user_profile = UserProfile(
        user_id=user_record["user_id"],
        email=user_record["email"],
        username=user_record["username"],
        full_name=user_record["full_name"],
        twin_id=user_record["twin_id"],
        is_guest=user_record.get("is_guest", False),
        active_persona=user_record.get("active_persona", "default"),
    )

    return AuthResponse(
        token=token,
        user=user_profile,
        twin=twin,
        message="Login successful.",
    )


@router.post("/guest", response_model=AuthResponse)
async def guest_login(req: GuestLoginRequest):
    """
    Instant 1-Click Guest Login for Hackathon Judges.
    Sets up an authenticated session and auto-configures the specified Accessibility Twin persona.
    """
    user_id = f"usr_guest_{uuid.uuid4().hex[:8]}"
    email = f"judge_{req.persona.value}_{uuid.uuid4().hex[:4]}@adaptx.ai"
    username = f"judge_{req.persona.value}"
    twin_id = f"twin_{user_id}"

    twin = _create_persona_twin(req.persona, twin_id, req.preferred_language)
    pipeline_service.twin_service.update_twin(twin)

    user_record = {
        "user_id": user_id,
        "email": email,
        "username": username,
        "full_name": req.custom_name or f"Judge ({req.persona.value.replace('_', ' ').title()})",
        "password_hash": hash_password("judge_demo"),
        "pin": "1234",
        "twin_id": twin_id,
        "is_guest": True,
        "active_persona": req.persona.value,
        "created_at": datetime.utcnow().isoformat(),
    }
    _USER_STORE[email] = user_record

    token = create_access_token(user_id=user_id, email=email, twin_id=twin_id)
    _ACTIVE_TOKENS[token] = user_record

    user_profile = UserProfile(
        user_id=user_id,
        email=email,
        username=username,
        full_name=user_record["full_name"],
        twin_id=twin_id,
        is_guest=True,
        active_persona=req.persona.value,
    )

    return AuthResponse(
        token=token,
        user=user_profile,
        twin=twin,
        message=f"Welcome! Logged in as {user_profile.full_name} with '{req.persona.value}' accessibility persona.",
    )


@router.get("/me", response_model=AuthResponse)
async def get_current_user(authorization: Optional[str] = Header(None)):
    """
    Validates bearer token signature and expiration, returning user profile and active Accessibility Twin.
    """
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header is required.")

    token = authorization.replace("Bearer ", "").strip()
    payload = verify_access_token(token)

    # Check active token or user store
    user_id = payload.get("sub")
    email = payload.get("email")
    twin_id = payload.get("twin_id", "default_user")

    user_record = _ACTIVE_TOKENS.get(token) or _USER_STORE.get(email)
    if not user_record:
        # Fallback profile from payload
        user_record = {
            "user_id": user_id,
            "email": email,
            "username": email.split("@")[0] if email else "user",
            "full_name": "Authenticated User",
            "twin_id": twin_id,
            "is_guest": False,
            "active_persona": "custom",
        }

    twin = pipeline_service.twin_service.get_twin(twin_id)
    user_profile = UserProfile(
        user_id=user_record["user_id"],
        email=user_record.get("email", email or "user@adaptx.ai"),
        username=user_record.get("username", "user"),
        full_name=user_record.get("full_name", "User"),
        twin_id=twin_id,
        is_guest=user_record.get("is_guest", False),
        active_persona=user_record.get("active_persona"),
    )

    return AuthResponse(
        token=token,
        user=user_profile,
        twin=twin,
        message="Session active.",
    )


@router.post("/logout")
async def logout(authorization: Optional[str] = Header(None)):
    """Logs out by revoking the active session token."""
    if authorization:
        token = authorization.replace("Bearer ", "").strip()
        _ACTIVE_TOKENS.pop(token, None)
    return {"status": "SUCCESS", "message": "Logged out successfully."}
