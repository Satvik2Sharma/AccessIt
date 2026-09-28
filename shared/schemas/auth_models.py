"""
Adapt-X (Sahayak AI) — Authentication & Persona Schemas
Defines structured data contracts for User Authentication, Onboarding,
Preset Accessibility Personas for Hackathon Judges, and Session Management.
"""

from enum import Enum
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
from datetime import datetime
from shared.schemas.models import AccessibilityTwin, LanguagePreference


class AuthModality(str, Enum):
    PASSWORD = "password"
    PIN = "pin"
    BIOMETRIC = "biometric"
    VOICE = "voice"
    GUEST = "guest"


class JudgePersona(str, Enum):
    LOW_VISION = "low_vision"
    MOTOR_DIFFICULTY = "motor_difficulty"
    HEARING_IMPAIRMENT = "hearing_impairment"
    ELDERLY_SIMPLIFIED = "elderly_simplified"
    DEFAULT = "default"


class LoginRequest(BaseModel):
    username: str
    password: Optional[str] = None
    pin: Optional[str] = None
    voice_auth_token: Optional[str] = None
    auth_modality: AuthModality = AuthModality.PASSWORD


class RegisterRequest(BaseModel):
    username: str
    full_name: str
    preferred_language: LanguagePreference = LanguagePreference.ENGLISH
    password: Optional[str] = "AdaptX@2026"
    pin: Optional[str] = "1234"
    initial_twin: Optional[AccessibilityTwin] = None


class GuestLoginRequest(BaseModel):
    persona: JudgePersona = JudgePersona.LOW_VISION
    preferred_language: LanguagePreference = LanguagePreference.ENGLISH
    custom_name: Optional[str] = "Hackathon Judge"


class UserProfile(BaseModel):
    user_id: str
    username: str
    full_name: str
    twin_id: str
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    last_login: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    is_guest: bool = False
    active_persona: Optional[str] = None


class AuthResponse(BaseModel):
    success: bool = True
    token: str
    token_type: str = "Bearer"
    user: UserProfile
    twin: AccessibilityTwin
    message: str = "Authentication successful"
    supported_next_steps: List[str] = Field(
        default_factory=lambda: [
            "DOCUMENT_READING",
            "FORM_COMPLETION",
            "ISL_COMMUNICATION",
            "SPATIAL_CAMERA",
            "SMART_NAVIGATION",
        ]
    )


class PersonaPresetInfo(BaseModel):
    persona_id: str
    title: str
    description: str
    barriers_addressed: List[str]
    twin_configuration: Dict[str, Any]
