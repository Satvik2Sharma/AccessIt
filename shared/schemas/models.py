"""
Sahayak AI — Shared Pydantic Data Models
Defines normalized schemas for AccessibilityTwin, Task, Barriers, Flows, and Telemetry.
Strictly avoids medical diagnostic labels; models functional interaction preferences.
"""

from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class LanguagePreference(str, Enum):
    HINDI = "Hindi"
    ENGLISH = "English"
    TAMIL = "Tamil"
    TELUGU = "Telugu"
    BENGALI = "Bengali"
    MARATHI = "Marathi"


class InputModality(str, Enum):
    VOICE = "voice"
    TOUCH = "touch"
    HYBRID = "hybrid"
    SIGN = "sign"


class OutputModality(str, Enum):
    VOICE = "voice"
    TEXT = "text"
    VOICE_AND_TEXT = "voice_and_text"
    HAPTIC = "haptic"


class VisualPreferences(BaseModel):
    large_text: bool = Field(default=False, description="Prefers large 20pt+ typography")
    high_contrast: bool = Field(default=False, description="Needs high contrast (e.g. yellow on black)")
    screen_reader: bool = Field(default=False, description="Uses screen reader accessibility services")
    magnification_level: float = Field(default=1.0, ge=1.0, le=3.0)
    color_inversion: bool = Field(default=False)


class HearingPreferences(BaseModel):
    captions: bool = Field(default=True, description="Needs visual captions for all spoken audio")
    visual_alerts: bool = Field(default=True, description="Visual indicator for system audio cues")
    sign_language: bool = Field(default=False, description="Uses sign language communication")


class MotorPreferences(BaseModel):
    voice_input: bool = Field(default=True, description="Prefers voice commands over keyboard typing")
    large_touch_targets: bool = Field(default=True, description="Expands touch target bounding boxes")
    reduce_scrolling: bool = Field(default=True, description="Avoids deep vertical scrolling")
    dwell_time_ms: int = Field(default=300, description="Touch sensitivity debounce threshold")


class ComprehensionPreferences(BaseModel):
    simplified_language: bool = Field(default=True, description="Replaces bureaucratic jargon with simple words")
    one_step_at_a_time: bool = Field(default=True, description="Flattens complex multi-field workflows into single steps")
    read_instructions_aloud: bool = Field(default=True, description="Speaks guidance automatically")
    show_task_progress: bool = Field(default=True, description="Displays visual progress counter")


class HapticPreferences(BaseModel):
    enabled: bool = Field(default=True, description="Tactile feedback for button clicks and directional cues")
    intensity: str = Field(default="medium", description="light, medium, strong")
    tactile_confirmation: bool = Field(default=True, description="Vibrate on step completion")


class AccessibilityTwin(BaseModel):
    """
    The Accessibility Twin is a dynamic software profile describing functional
    interaction preferences. It is NOT a medical diagnosis.
    """
    id: str = Field(default="default_twin")
    language: LanguagePreference = Field(default=LanguagePreference.ENGLISH)
    secondary_language: Optional[LanguagePreference] = Field(default=LanguagePreference.HINDI)
    visual: VisualPreferences = Field(default_factory=VisualPreferences)
    hearing: HearingPreferences = Field(default_factory=HearingPreferences)
    motor: MotorPreferences = Field(default_factory=MotorPreferences)
    comprehension: ComprehensionPreferences = Field(default_factory=ComprehensionPreferences)
    haptics: HapticPreferences = Field(default_factory=HapticPreferences)
    preferred_input: InputModality = Field(default=InputModality.VOICE)
    preferred_output: OutputModality = Field(default=OutputModality.VOICE_AND_TEXT)


# ----------------------------------------------------
# Task & Barrier Schemas
# ----------------------------------------------------

class TaskType(str, Enum):
    FORM_COMPLETION = "FORM_COMPLETION"
    UNDERSTAND_DOCUMENT = "UNDERSTAND_DOCUMENT"
    COMMUNICATE = "COMMUNICATE"
    SEE = "SEE"
    READ = "READ"
    FIND_OBJECT = "FIND_OBJECT"


class BarrierCategory(str, Enum):
    VISUAL = "VISUAL"
    HEARING = "HEARING"
    MOTOR = "MOTOR"
    COGNITIVE = "COGNITIVE"
    LANGUAGE = "LANGUAGE"
    DIGITAL_LITERACY = "DIGITAL_LITERACY"
    INTERACTION_COMPLEXITY = "INTERACTION_COMPLEXITY"


class BarrierSeverity(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    BLOCKER = "BLOCKER"


class Barrier(BaseModel):
    category: BarrierCategory
    severity: BarrierSeverity
    description: str
    remediation_strategy: str


class TaskStep(BaseModel):
    step_id: str
    step_number: int
    total_steps: int
    field_id: str
    label: str
    spoken_prompt: str
    display_prompt: str
    input_type: str = "VOICE_OR_TEXT"
    is_required: bool = True
    current_value: Optional[str] = None
    is_confirmed: bool = False
    validation_status: str = "PENDING"  # PENDING, VALID, INVALID


class AccessibleTaskFlow(BaseModel):
    task_id: str
    task_type: TaskType
    strategy: str
    total_steps: int
    current_step_index: int = 0
    steps: List[TaskStep] = Field(default_factory=list)
    detected_barriers: List[Barrier] = Field(default_factory=list)


class VerificationStatus(str, Enum):
    IN_PROGRESS = "IN_PROGRESS"
    BLOCKED = "BLOCKED"
    NEEDS_CONFIRMATION = "NEEDS_CONFIRMATION"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class VerificationResult(BaseModel):
    task_id: str
    status: VerificationStatus
    completion_percentage: float = Field(ge=0.0, le=100.0)
    completed_fields: int
    total_fields: int
    missing_fields: List[str] = Field(default_factory=list)
    verification_token: Optional[str] = None
    summary_message: str


class InteractionHeatmapItem(BaseModel):
    interaction_point: str
    complexity: str  # LOW, MEDIUM, HIGH
    color: str  # GREEN, YELLOW, RED
    reason: str
    retry_count: int = 0


# ----------------------------------------------------
# Re-exports of specialized domain schemas
# ----------------------------------------------------
from shared.schemas.vision_models import (
    VisionObject,
    TextDetection,
    ObjectTextRelation,
    SceneAnalysis,
    SpatialGuidanceRequest,
    SpatialGuidanceResponse,
)
from shared.schemas.document_models import (
    DocumentSummary,
    DocumentQuestion,
    DocumentAnswer,
    DocumentTask,
    DocumentTaskExtractionRequest,
    DocumentTaskExtractionResponse,
)
from shared.schemas.form_models import (
    FormFieldAnalysis,
    FormRespondRequest,
    FormRespondResponse,
)
from shared.schemas.isl_models import (
    HandLandmark,
    ISLPredictionRequest,
    ISLPredictionResponse,
)
from shared.schemas.task_models import (
    VoiceCommandRequest,
    VoiceCommandResponse,
    TTSRequest,
    TTSResponse,
    AssistancePriority,
    AssistanceResponse,
    MultimodalAssistanceRequest,
    ObstacleType,
    NavigationObstacle,
    NavigationState,
    NavigationGuidanceRequest,
    NavigationGuidanceResponse,
    PipelineStage,
    RecoveryStatus,
    RecoveryResult,
    PersonalizationProfile,
)
from shared.schemas.camera_models import (
    CameraMode,
    FrameQualityMetrics,
    CameraFrame,
    CameraAnalysisRequest,
    CameraAnalysisResult,
)


# ====================================================
# Extended AI Capabilities Schemas
# ====================================================

class SpatialObject(BaseModel):
    """A detected physical object with spatial metadata."""
    label: str
    confidence: float = Field(ge=0.0, le=1.0)
    bbox: Optional[List[float]] = None  # [xmin, ymin, xmax, ymax] normalized 0-1
    direction: Optional[str] = None  # e.g. "2 o'clock"
    horizontal_zone: Optional[str] = None  # left, center, right
    elevation: Optional[str] = None  # eye_level, table_level, floor_level
    proximity: Optional[str] = None  # very_close, arm_reach, nearby, several_steps
    associated_text: Optional[str] = None
    haptic_cue: Optional[str] = None


class VoiceCommand(BaseModel):
    """Represents a parsed voice utterance."""
    raw_text: str
    language: str = "English"
    intent: Optional[str] = None
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    entities: Dict[str, Any] = Field(default_factory=dict)
    source: str = "stt"  # stt, text_input, test


class NavigationInstruction(BaseModel):
    """A single navigation guidance instruction."""
    direction: str  # left, right, forward, stop, slight_left, slight_right
    description: str
    description_hi: Optional[str] = None
    urgency: str = "NORMAL"  # NORMAL, HIGH, EMERGENCY
    haptic_cue: Optional[str] = None
    obstacle_detected: bool = False
    obstacle_label: Optional[str] = None


class RecoveryAction(BaseModel):
    """An error recovery action suggestion."""
    failure_type: str
    strategy: str
    description: str
    description_hi: Optional[str] = None
    can_retry: bool = True
    max_retries: int = 3
    user_instruction: str
    user_instruction_hi: Optional[str] = None


class PersonalizationSuggestion(BaseModel):
    """A consented personalization adaptation proposal."""
    pattern_type: str  # preferred_language, preferred_modality, barrier_type, etc.
    observation: str
    suggested_adaptation: str
    consent_required: bool = True
    dialog_prompt: str
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    task_count: int = 0
