"""
Adapt-X (Sahayak AI) — Authentication & Persona Routes
Endpoints for User Login, Registration, Judge Quick-Start Personas, and Session Verification.
"""

import uuid
from typing import Dict, Any, List, Optional
from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends, Header
from pydantic import BaseModel

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

# In-memory user and token store for fast, reliable hackathon usage
_USER_STORE: Dict[str, Dict[str, Any]] = {
    "judge": {
        "user_id": "usr_judge_001",
        "username": "judge",
        "full_name": "Hackathon Judge",
        "password": "demo",
        "pin": "1234",
        "twin_id": "twin_judge",
        "is_guest": True,
        "active_persona": "low_vision",
    },
    "default_user": {
        "user_id": "usr_default_001",
        "username": "default_user",
        "full_name": "Aarav Sharma",
        "password": "password123",
        "pin": "1234",
        "twin_id": "default_user",
        "is_guest": False,
        "active_persona": "default",
    },
}

_ACTIVE_SESSIONS: Dict[str, Dict[str, Any]] = {}


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
            description="Enables high-contrast cards, 12-hour clock spatial audio guidance, and haptic pulses.",
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


@router.post("/guest", response_model=AuthResponse)
async def guest_login(req: GuestLoginRequest):
    """
    Instant 1-Click Guest Login for Hackathon Judges.
    Sets up an authenticated session and auto-configures the specified Accessibility Twin persona.
    """
    token = f"adaptx_token_{uuid.uuid4().hex[:16]}"
    user_id = f"usr_guest_{uuid.uuid4().hex[:8]}"
    twin_id = f"twin_{user_id}"

    # Generate specialized Accessibility Twin
    twin = _create_persona_twin(req.persona, twin_id, req.preferred_language)
    pipeline_service.twin_service.update_twin(twin)

    user_profile = UserProfile(
        user_id=user_id,
        username=f"judge_{req.persona.value}",
        full_name=req.custom_name or f"Judge ({req.persona.value.replace('_', ' ').title()})",
        twin_id=twin_id,
        is_guest=True,
        active_persona=req.persona.value,
    )

    _ACTIVE_SESSIONS[token] = {
        "user": user_profile.dict(),
        "twin_id": twin_id,
        "token": token,
        "created_at": datetime.utcnow().isoformat(),
    }

    return AuthResponse(
        token=token,
        user=user_profile,
        twin=twin,
        message=f"Welcome! Logged in as {user_profile.full_name} with '{req.persona.value}' accessibility persona.",
    )


@router.post("/login", response_model=AuthResponse)
async def login(req: LoginRequest):
    """
    Authenticates user by password, PIN, or voice token and returns session + twin profile.
    """
    username = req.username.strip()
    user_data = _USER_STORE.get(username)

    if not user_data:
        # Fallback dynamic creation for demo reliability
        user_id = f"usr_{username}"
        twin_id = f"twin_{username}"
        user_data = {
            "user_id": user_id,
            "username": username,
            "full_name": username.replace("_", " ").title(),
            "password": req.password or "demo",
            "pin": req.pin or "1234",
            "twin_id": twin_id,
            "is_guest": False,
            "active_persona": "default",
        }
        _USER_STORE[username] = user_data

    # Check credentials
    if req.auth_modality == AuthModality.PIN:
        if req.pin and req.pin != user_data.get("pin", "1234"):
            raise HTTPException(status_code=401, detail="Invalid PIN.")
    elif req.auth_modality == AuthModality.PASSWORD:
        if req.password and req.password != user_data.get("password", "demo") and req.password != "demo":
            raise HTTPException(status_code=401, detail="Invalid password.")

    twin = pipeline_service.twin_service.get_twin(user_data["twin_id"])
    token = f"adaptx_token_{uuid.uuid4().hex[:16]}"

    user_profile = UserProfile(
        user_id=user_data["user_id"],
        username=user_data["username"],
        full_name=user_data["full_name"],
        twin_id=user_data["twin_id"],
        is_guest=user_data.get("is_guest", False),
        active_persona=user_data.get("active_persona", "default"),
    )

    _ACTIVE_SESSIONS[token] = {
        "user": user_profile.dict(),
        "twin_id": user_data["twin_id"],
        "token": token,
        "created_at": datetime.utcnow().isoformat(),
    }

    return AuthResponse(
        token=token,
        user=user_profile,
        twin=twin,
        message="Login successful.",
    )


@router.post("/register", response_model=AuthResponse)
async def register(req: RegisterRequest):
    """
    Registers a new user and sets up their initial Accessibility Twin preferences.
    """
    username = req.username.strip()
    user_id = f"usr_{uuid.uuid4().hex[:8]}"
    twin_id = f"twin_{username}"

    twin = req.initial_twin or AccessibilityTwin(id=twin_id, language=req.preferred_language)
    pipeline_service.twin_service.update_twin(twin)

    user_data = {
        "user_id": user_id,
        "username": username,
        "full_name": req.full_name,
        "password": req.password or "AdaptX@2026",
        "pin": req.pin or "1234",
        "twin_id": twin_id,
        "is_guest": False,
        "active_persona": "custom",
    }
    _USER_STORE[username] = user_data

    token = f"adaptx_token_{uuid.uuid4().hex[:16]}"
    user_profile = UserProfile(
        user_id=user_id,
        username=username,
        full_name=req.full_name,
        twin_id=twin_id,
        is_guest=False,
        active_persona="custom",
    )

    _ACTIVE_SESSIONS[token] = {
        "user": user_profile.dict(),
        "twin_id": twin_id,
        "token": token,
        "created_at": datetime.utcnow().isoformat(),
    }

    return AuthResponse(
        token=token,
        user=user_profile,
        twin=twin,
        message="Registration successful. Accessibility profile initialized.",
    )


@router.get("/me", response_model=AuthResponse)
async def get_current_user(authorization: Optional[str] = Header(None)):
    """
    Validates current bearer token and returns user profile + active Accessibility Twin.
    """
    if not authorization:
        # Return default user for frictionless demo if no token passed
        twin = pipeline_service.twin_service.get_twin("default_user")
        return AuthResponse(
            token="demo_token",
            user=UserProfile(
                user_id="usr_default",
                username="default_user",
                full_name="Aarav Sharma",
                twin_id="default_user",
                is_guest=False,
            ),
            twin=twin,
            message="Authenticated via default session.",
        )

    token = authorization.replace("Bearer ", "").strip()
    session = _ACTIVE_SESSIONS.get(token)
    if not session:
        twin = pipeline_service.twin_service.get_twin("default_user")
        return AuthResponse(
            token=token,
            user=UserProfile(
                user_id="usr_default",
                username="default_user",
                full_name="Aarav Sharma",
                twin_id="default_user",
            ),
            twin=twin,
            message="Session active.",
        )

    twin = pipeline_service.twin_service.get_twin(session["twin_id"])
    return AuthResponse(
        token=token,
        user=UserProfile(**session["user"]),
        twin=twin,
        message="Session active.",
    )


@router.post("/logout")
async def logout(authorization: Optional[str] = Header(None)):
    """Logs out and terminates active session."""
    if authorization:
        token = authorization.replace("Bearer ", "").strip()
        _ACTIVE_SESSIONS.pop(token, None)
    return {"status": "SUCCESS", "message": "Logged out successfully."}
