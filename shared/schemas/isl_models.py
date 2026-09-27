"""
Sahayak AI — ISL (Indian Sign Language) Schema Models
Defines structured data contracts for Gesture Classification, Landmark Inputs,
and Sign Communication Output.
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class HandLandmark(BaseModel):
    x: float
    y: float
    z: float = 0.0


class ISLPredictionRequest(BaseModel):
    twin_id: Optional[str] = "default_user"
    landmarks: Optional[List[List[float]]] = Field(
        default=None,
        description="21 hand landmarks normalized coordinates [x, y, z]"
    )


class ISLPredictionResponse(BaseModel):
    sign: str = Field(description="Identified sign (e.g., 'HELP', 'YES', 'NO', 'WATER', 'THANK YOU')")
    confidence: float = Field(default=0.95, ge=0.0, le=1.0)
    spoken_output: str
    display_caption: str
    hindi_translation: str
    english_translation: str
    haptic_pattern: Optional[str] = "SIGN_CONFIRM"
