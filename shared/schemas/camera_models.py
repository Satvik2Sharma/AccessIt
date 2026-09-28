"""
Sahayak AI — Camera Schema Models
Defines structured data contracts for Camera Intelligence, Frame Processing,
Quality Metrics, and Camera Session Management.
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum


class CameraMode(str, Enum):
    AUTO = "auto"
    DOCUMENT = "document"
    SEE = "see"
    SCENE = "scene"
    ISL = "isl"
    NAVIGATION = "navigation"
    FORM = "form"


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


class CameraAnalysisRequest(BaseModel):
    mode: CameraMode = CameraMode.AUTO
    query: Optional[str] = None
    twin_id: Optional[str] = "default_user"
    session_id: Optional[str] = None
    target_object: Optional[str] = None
    skip_duplicate_check: bool = False


class CameraAnalysisResult(BaseModel):
    mode_executed: str
    status: str = "SUCCESS"  # SUCCESS, DEGRADED, RECOVERY_REQUIRED, SKIPPED_DUPLICATE
    quality: FrameQualityMetrics = Field(default_factory=FrameQualityMetrics)
    primary_interpretation: str
    spoken_feedback: str
    display_feedback: str
    haptic_cue: Optional[str] = None
    document_data: Optional[Dict[str, Any]] = None
    spatial_objects: List[Dict[str, Any]] = Field(default_factory=list)
    scene_summary: Optional[str] = None
    navigation_instructions: List[Dict[str, Any]] = Field(default_factory=list)
    isl_prediction: Optional[Dict[str, Any]] = None
    recovery_action: Optional[Dict[str, Any]] = None
    processing_time_ms: float = 0.0
