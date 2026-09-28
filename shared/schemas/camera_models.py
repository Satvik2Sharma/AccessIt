"""
Sahayak AI — Camera Intelligence Schema Models
Defines structured data contracts for Camera Frames, Frame Quality Metrics, Intent-Aware Analysis Modes,
Camera Sessions, Object + OCR Fusion, Spatial Localization, and Multimodal Assistance.
"""

from enum import Enum
from typing import List, Optional, Tuple, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime


class AssistancePriority(str, Enum):
    LOW = "LOW"
    NORMAL = "NORMAL"
    HIGH = "HIGH"
    CRITICAL_SAFETY = "CRITICAL_SAFETY"



class CameraMode(str, Enum):
    AUTO = "auto"
    DOCUMENT = "document"
    SEE = "see"
    SCENE = "scene"
    ISL = "isl"
    NAVIGATION = "navigation"
    FORM = "form"


class CameraAnalysisMode(str, Enum):
    AUTO = "AUTO"
    SEE = "SEE"
    READ = "READ"
    FIND = "FIND"
    UNDERSTAND = "UNDERSTAND"
    NAVIGATE = "NAVIGATE"


class FrameQualityMetrics(BaseModel):
    is_valid: bool = True
    blur_score: float = Field(default=100.0, description="Laplacian variance quality metric")
    is_blurry: bool = False
    brightness: float = Field(default=128.0, description="Mean pixel luminance (0-255)")
    is_underexposed: bool = False
    is_overexposed: bool = False
    resolution: List[int] = Field(default_factory=lambda: [640, 480], description="[width, height]")
    quality_verdict: str = Field(default="GOOD", description="'GOOD', 'BLURRY', 'DARK', 'OVEREXPOSED', 'LOW_RES'")
    recommendation: Optional[str] = None


class CameraFrame(BaseModel):
    frame_id: str
    timestamp: float
    width: int
    height: int
    format: str = "jpeg"
    quality: FrameQualityMetrics = Field(default_factory=FrameQualityMetrics)
    hash: Optional[str] = None


class CameraFrameMetadata(BaseModel):
    frame_id: str = Field(default_factory=lambda: f"frame_{datetime.utcnow().strftime('%Y%m%d_%H%M%S_%f')[:20]}")
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    width: Optional[int] = Field(default=None, description="Image frame width in pixels")
    height: Optional[int] = Field(default=None, description="Image frame height in pixels")
    orientation: Optional[int] = Field(default=1, description="EXIF orientation tag (1=normal, 6=90deg, 8=270deg)")
    device_info: Optional[str] = Field(default=None, description="Mobile device model/OS")
    capture_source: str = Field(default="BACK_CAMERA", description="'BACK_CAMERA', 'FRONT_CAMERA', 'GALLERY'")


class CameraObject(BaseModel):
    object_id: str = Field(default_factory=lambda: f"obj_{datetime.utcnow().strftime('%f')[:6]}")
    label: str
    confidence: float = Field(default=0.90, ge=0.0, le=1.0)
    bbox: Optional[Tuple[int, int, int, int]] = Field(
        default=None,
        description="(xmin, ymin, xmax, ymax) pixel coordinates"
    )
    clock_direction: str = Field(
        default="12 o'clock",
        description="12-hour clock direction relative to user (e.g., '2 o'clock')"
    )
    clock_hour: int = Field(default=12, ge=1, le=12)
    relative_direction: str = Field(
        default="straight ahead",
        description="'straight ahead', 'to your left', 'to your right'"
    )
    proximity: str = Field(
        default="near",
        description="'very_near', 'near', 'medium', 'far', 'unknown'"
    )
    elevation: str = Field(
        default="level",
        description="'above', 'level', 'below', 'unknown'"
    )
    associated_text: Optional[str] = Field(
        default=None,
        description="OCR text fused with or positioned on this object"
    )
    haptic_cue: str = Field(
        default="DOUBLE_PULSE_CENTER",
        description="'PULSE_LEFT', 'PULSE_RIGHT', 'DOUBLE_PULSE_CENTER', 'HIGH_URGENT'"
    )
    haptic_intensity: str = Field(default="MEDIUM", description="'LIGHT', 'MEDIUM', 'STRONG', 'HIGH_URGENT'")


class CameraText(BaseModel):
    text_id: str = Field(default_factory=lambda: f"txt_{datetime.utcnow().strftime('%f')[:6]}")
    text: str
    confidence: float = Field(default=0.90, ge=0.0, le=1.0)
    bbox: Optional[Tuple[int, int, int, int]] = None
    language: Optional[str] = "en"


class CameraObjectTextRelation(BaseModel):
    object_id: str
    text_id: Optional[str] = None
    object_label: str
    associated_text: str
    relationship: str = Field(
        default="contained_within",
        description="'contained_within', 'adjacent_above', 'adjacent_below', 'adjacent_right', 'adjacent_left'"
    )
    combined_interpretation: str
    confidence: float = Field(default=0.90, ge=0.0, le=1.0)


class CameraSceneAnalysis(BaseModel):
    scene_type: str = Field(default="indoor", description="'indoor', 'outdoor', 'corridor', 'office', 'classroom'")
    description: str
    objects: List[CameraObject] = Field(default_factory=list)
    text_elements: List[CameraText] = Field(default_factory=list)
    fused_relations: List[CameraObjectTextRelation] = Field(default_factory=list)
    hazards: List[str] = Field(default_factory=list, description="Obstacles, steps, low ceilings, obstacles in path")
    navigable_path_clear: bool = Field(default=True)
    suggested_action: str = Field(default="Proceed straight ahead")
    summary_spoken: str = ""
    summary_display: str = ""
    language: str = "English"


class CameraAnalysisRequest(BaseModel):
    mode: CameraMode = CameraMode.AUTO
    query: Optional[str] = None
    twin_id: Optional[str] = "default_user"
    session_id: Optional[str] = None
    target_object: Optional[str] = None
    skip_duplicate_check: bool = False


class CameraAnalysisResult(BaseModel):
    session_id: Optional[str] = None
    mode: Optional[CameraAnalysisMode] = None
    mode_executed: Optional[str] = None
    status: str = "SUCCESS"  # SUCCESS, DEGRADED, RECOVERY_REQUIRED, SKIPPED_DUPLICATE, COMPLETED
    quality: FrameQualityMetrics = Field(default_factory=FrameQualityMetrics)
    primary_interpretation: Optional[str] = None
    spoken_feedback: Optional[str] = None
    display_feedback: Optional[str] = None
    haptic_cue: Optional[str] = None
    intent: Optional[str] = None
    target_object: Optional[str] = None
    objects: List[CameraObject] = Field(default_factory=list)
    text_elements: List[CameraText] = Field(default_factory=list)
    fused_relations: List[CameraObjectTextRelation] = Field(default_factory=list)
    scene: Optional[CameraSceneAnalysis] = None
    document_data: Optional[Dict[str, Any]] = None
    spatial_objects: List[Dict[str, Any]] = Field(default_factory=list)
    scene_summary: Optional[str] = None
    navigation_instructions: List[Dict[str, Any]] = Field(default_factory=list)
    isl_prediction: Optional[Dict[str, Any]] = None
    recovery_action: Optional[Dict[str, Any]] = None
    target_found: bool = False
    target_guidance: Optional[Dict[str, Any]] = None
    hazards: List[str] = Field(default_factory=list)
    processing_metadata: Dict[str, Any] = Field(default_factory=dict)
    processing_time_ms: float = 0.0
    confidence: float = 0.90


class CameraAssistanceResponse(BaseModel):
    spoken_response: str
    display_response: str
    haptic_cue: str = "DOUBLE_PULSE_CENTER"
    haptic_intensity: str = "MEDIUM"
    priority: AssistancePriority = AssistancePriority.NORMAL
    language: str = "English"
    next_action: Optional[str] = None
    session_id: str
    analysis: Optional[CameraAnalysisResult] = None
    visual_card: Optional[Dict[str, Any]] = None
    recovery_info: Optional[Dict[str, Any]] = None


class CameraError(BaseModel):
    error_code: str
    stage: str
    message: str
    retryable: bool = False
    fallback_used: bool = False
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())


class CameraAnalysisResponse(BaseModel):
    success: bool = True
    session_id: str
    mode: CameraAnalysisMode
    analysis: CameraAnalysisResult
    assistance: CameraAssistanceResponse
    next_action: Optional[str] = None
    processing: Dict[str, Any] = Field(default_factory=dict)
    error: Optional[CameraError] = None

    # Top-level convenience projections for lightweight mobile & web client consumption
    objects: Optional[List[Dict[str, Any]]] = None
    directions: Optional[List[str]] = None
    text: Optional[List[str]] = None
    scene: Optional[str] = None
    guidance: Optional[str] = None
    confidence: Optional[float] = None
    timestamp: Optional[str] = None



class CameraSessionState(BaseModel):
    session_id: str
    twin_id: str = "default_user"
    active_mode: CameraAnalysisMode = CameraAnalysisMode.AUTO
    target_object: Optional[str] = None
    current_intent: Optional[str] = None
    total_frames_processed: int = 0
    last_frame_id: Optional[str] = None
    latest_scene: Optional[CameraSceneAnalysis] = None
    detected_objects: List[CameraObject] = Field(default_factory=list)
    detected_texts: List[CameraText] = Field(default_factory=list)
    fused_relations: List[CameraObjectTextRelation] = Field(default_factory=list)
    hazards: List[str] = Field(default_factory=list)
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    updated_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
