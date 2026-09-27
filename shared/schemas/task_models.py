"""
Sahayak AI — Task, Voice, Navigation, Assistance & Recovery Schemas
Defines structured data contracts for Voice Assistant, Smart Navigation,
Multimodal Assistance, Error Recovery, and Personalization.
"""

from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime
from shared.schemas.models import (
    LanguagePreference,
    InputModality,
    OutputModality,
    VisualPreferences,
    MotorPreferences,
    ComprehensionPreferences,
    HapticPreferences,
    TaskType,
    Barrier,
    TaskStep,
)


# ----------------------------------------------------
# Voice Assistant Schemas
# ----------------------------------------------------

class VoiceCommandRequest(BaseModel):
    transcript: str = Field(description="Transcribed user voice input")
    audio_base64: Optional[str] = Field(default=None, description="Optional raw audio snippet")
    twin_id: Optional[str] = "default_user"
    language_hint: Optional[str] = "auto"
    active_session_id: Optional[str] = None


class VoiceCommandResponse(BaseModel):
    transcript: str
    detected_language: str = "en"
    classified_intent: str
    intent_confidence: float = 0.95
    suggested_action: str
    spoken_reply: str
    display_reply: str
    session_id: Optional[str] = None
    parameters: Dict[str, Any] = Field(default_factory=dict)
    haptic_cue: Optional[str] = "TOUCH_CONFIRM"


class TTSRequest(BaseModel):
    text: str
    language: LanguagePreference = LanguagePreference.ENGLISH
    speed: float = Field(default=1.0, ge=0.5, le=2.0)
    pitch: float = Field(default=1.0, ge=0.5, le=1.5)


class TTSResponse(BaseModel):
    text: str
    language: str
    audio_url: Optional[str] = None
    phonetic_ssml: Optional[str] = None
    duration_estimate_sec: float = 2.0


# ----------------------------------------------------
# Multimodal Assistance Schemas
# ----------------------------------------------------

class AssistancePriority(str, Enum):
    LOW = "LOW"
    NORMAL = "NORMAL"
    HIGH = "HIGH"
    CRITICAL_SAFETY = "CRITICAL_SAFETY"


class AssistanceResponse(BaseModel):
    """
    Unified multimodal response instruction that mobile/web clients can render.
    """
    text_content: str
    spoken_content: str
    language: str = "English"
    visual_card: Optional[Dict[str, Any]] = None
    haptic_pattern: Optional[str] = Field(
        default="SINGLE_PULSE",
        description="'PULSE_LEFT', 'PULSE_RIGHT', 'DOUBLE_PULSE_CENTER', 'SUCCESS_DOUBLE_PULSE', 'HIGH_URGENT', 'SINGLE_PULSE'"
    )
    haptic_intensity: str = Field(default="MEDIUM", description="'LIGHT', 'MEDIUM', 'STRONG'")
    priority: AssistancePriority = AssistancePriority.NORMAL
    next_action: Optional[str] = None
    session_id: Optional[str] = None
    recovery_info: Optional[Dict[str, Any]] = None


class MultimodalAssistanceRequest(BaseModel):
    task_id: Optional[str] = None
    task_type: TaskType = TaskType.FORM_COMPLETION
    current_input: str
    twin_id: Optional[str] = "default_user"
    context_data: Dict[str, Any] = Field(default_factory=dict)


# ----------------------------------------------------
# Smart Navigation Schemas
# ----------------------------------------------------

class ObstacleType(str, Enum):
    DOOR = "DOOR"
    STAIRCASE_UP = "STAIRCASE_UP"
    STAIRCASE_DOWN = "STAIRCASE_DOWN"
    PILLAR = "PILLAR"
    FURNITURE = "FURNITURE"
    PERSON = "PERSON"
    WALL = "WALL"
    GENERAL_OBSTACLE = "GENERAL_OBSTACLE"


class NavigationObstacle(BaseModel):
    obstacle_id: str
    type: ObstacleType
    description: str
    clock_hour: int = Field(default=12, ge=1, le=12)
    relative_direction: str = "straight ahead"
    distance_estimate: str = "within arm's reach"  # 'very close', 'within arm's reach', 'a few steps ahead'
    elevation: str = "table/waist level"
    severity: str = "MEDIUM"  # 'LOW', 'MEDIUM', 'HIGH_URGENT'
    haptic_cue: str = "PULSE_LEFT"


class NavigationState(BaseModel):
    session_id: str
    active: bool = True
    current_destination: Optional[str] = None
    path_clear: bool = True
    heading_degrees: float = 0.0
    detected_obstacles: List[NavigationObstacle] = Field(default_factory=list)
    recent_guidance: Optional[str] = None
    total_steps_guided: int = 0
    updated_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())


class NavigationGuidanceRequest(BaseModel):
    session_id: Optional[str] = None
    target_destination: Optional[str] = "exit"
    camera_scene_description: Optional[str] = None
    detected_labels: List[str] = Field(default_factory=list)
    twin_id: Optional[str] = "default_user"


class NavigationGuidanceResponse(BaseModel):
    session_id: str
    direction: str
    clock_direction: str
    instruction: str
    spoken_guidance: str
    urgency: AssistancePriority = AssistancePriority.NORMAL
    obstacles_in_path: List[NavigationObstacle] = Field(default_factory=list)
    haptic_cue: str = "DOUBLE_PULSE_CENTER"
    is_destination_reached: bool = False


# ----------------------------------------------------
# Error Recovery Schemas
# ----------------------------------------------------

class PipelineStage(str, Enum):
    UNDERSTAND_USER = "UNDERSTAND_USER"
    UNDERSTAND_TASK = "UNDERSTAND_TASK"
    DETECT_BARRIERS = "DETECT_BARRIERS"
    COMPILE_FLOW = "COMPILE_FLOW"
    AI_INFERENCE = "AI_INFERENCE"
    ASSIST = "ASSIST"
    VERIFY = "VERIFY"
    LEARN = "LEARN"
    UNKNOWN = "UNKNOWN"


class RecoveryStatus(str, Enum):
    SUCCESS = "SUCCESS"
    RECOVERED_WITH_FALLBACK = "RECOVERED_WITH_FALLBACK"
    RETRIED_SUCCESSFULLY = "RETRIED_SUCCESSFULLY"
    DEGRADED_MANUAL_PROMPT = "DEGRADED_MANUAL_PROMPT"
    FAILED = "FAILED"


class RecoveryResult(BaseModel):
    failed_stage: PipelineStage
    failure_type: str
    error_message: str
    retry_attempted: bool = False
    fallback_used: bool = False
    fallback_strategy: Optional[str] = None
    recovery_status: RecoveryStatus
    actionable_user_message: str
    spoken_recovery_guidance: str


# ----------------------------------------------------
# Advanced Personalization Schemas
# ----------------------------------------------------

class PersonalizationProfile(BaseModel):
    twin_id: str = "default_user"
    preferred_language: LanguagePreference = LanguagePreference.ENGLISH
    preferred_input_modality: InputModality = InputModality.VOICE
    preferred_output_modality: OutputModality = OutputModality.VOICE_AND_TEXT
    voice_speed: float = 1.0
    haptic_feedback_level: str = "medium"
    high_contrast: bool = False
    large_touch_targets: bool = True
    simplified_language: bool = True
    one_step_at_a_time: bool = True
    interaction_stats: Dict[str, Any] = Field(default_factory=dict)
    updated_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
