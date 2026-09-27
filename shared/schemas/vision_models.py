"""
Sahayak AI — Vision & Spatial Schema Models
Defines structured data contracts for Spatial Vision, Object Detection,
12-Hour Clock Direction, Proximity, Elevation, and Scene Fusion.
"""

from typing import List, Optional, Tuple, Dict, Any
from pydantic import BaseModel, Field


class BoundingBox(BaseModel):
    xmin: int
    ymin: int
    xmax: int
    ymax: int


class VisionObject(BaseModel):
    label: str
    confidence: float = Field(default=0.9, ge=0.0, le=1.0)
    bbox: Optional[Tuple[int, int, int, int]] = Field(
        default=None,
        description="(xmin, ymin, xmax, ymax) pixel coordinates"
    )
    clock_direction: Optional[str] = Field(
        default="12 o'clock",
        description="12-hour clock direction relative to user (e.g., '2 o'clock')"
    )
    clock_hour: int = Field(default=12, ge=1, le=12)
    relative_direction: str = Field(
        default="straight ahead",
        description="'straight ahead', 'to your left', 'to your right'"
    )
    relative_proximity: str = Field(
        default="within arm's reach",
        description="'very close', 'within arm's reach', 'a few steps ahead'"
    )
    elevation: str = Field(
        default="table/waist level",
        description="'upper/eye level', 'table/waist level', 'low/floor level'"
    )
    associated_texts: List[str] = Field(
        default_factory=list,
        description="OCR text strings located on or adjacent to this object"
    )
    text: Optional[str] = Field(
        default=None,
        description="Combined text string associated with this object"
    )
    haptic_cue: str = Field(
        default="DOUBLE_PULSE_CENTER",
        description="'PULSE_LEFT', 'PULSE_RIGHT', 'DOUBLE_PULSE_CENTER', 'HIGH_URGENT'"
    )
    haptic_intensity: str = Field(default="MEDIUM", description="'LIGHT', 'MEDIUM', 'HIGH_URGENT'")


class TextDetection(BaseModel):
    text: str
    confidence: float = Field(default=0.9, ge=0.0, le=1.0)
    bbox: Optional[Tuple[int, int, int, int]] = None


class ObjectTextRelation(BaseModel):
    """
    Connects a physical detected object with recognized OCR text.
    Example: object='door', text='EXIT' -> combined interpretation='EXIT door'
    """
    object_label: str
    associated_text: str
    spatial_relationship: str = Field(
        default="contained_within",
        description="'contained_within', 'adjacent_above', 'adjacent_below', 'adjacent_right', 'adjacent_left'"
    )
    combined_interpretation: str
    confidence: float = Field(default=0.88, ge=0.0, le=1.0)
    object_bbox: Optional[Tuple[int, int, int, int]] = None
    text_bbox: Optional[Tuple[int, int, int, int]] = None


class SceneAnalysis(BaseModel):
    """
    Structured environmental understanding for assistive guidance.
    """
    scene_description: str
    scene_type: str = Field(default="indoor", description="'indoor', 'outdoor', 'corridor', 'office', 'classroom'")
    detected_objects: List[VisionObject] = Field(default_factory=list)
    detected_texts: List[TextDetection] = Field(default_factory=list)
    fused_relations: List[ObjectTextRelation] = Field(default_factory=list)
    hazards: List[str] = Field(default_factory=list, description="Obstacles, steps, low ceilings, obstacles in path")
    navigable_path_clear: bool = Field(default=True)
    suggested_action: str = Field(default="Proceed straight ahead")
    spoken_scene_summary: str = Field(default="")
    language: str = Field(default="English")


class SpatialGuidanceRequest(BaseModel):
    target_object: str
    twin_id: Optional[str] = "default_user"
    current_heading_degrees: Optional[float] = 0.0


class SpatialGuidanceResponse(BaseModel):
    label: str
    relative_direction: str
    clock_hour: int
    clock_direction: str
    elevation: str
    relative_proximity: str
    spoken_guidance: str
    display_guidance: str
    haptic_cue: str
    haptic_intensity: str
    normalized_coordinates: Dict[str, float] = Field(default_factory=dict)
    area_ratio: float = 0.0
    found: bool = True
