"""
Sahayak AI — Spatial Vision & Directional Guidance Routes
Endpoints for Object Finding, 12-Hour Clock Direction, Elevation, and Proximity Guidance.
"""

from typing import Optional, Dict, Any
from fastapi import APIRouter, Form
from shared.schemas.models import (
    SpatialGuidanceRequest,
    SpatialGuidanceResponse,
)
from backend.services.pipeline_service import pipeline_service

router = APIRouter(tags=["Spatial Vision & Object Guidance"])


@router.post("/see")
async def see_and_find_object(
    target_object: str = Form("bottle"),
    twin_id: str = Form("default_user"),
):
    """
    Finds target object and computes 12-hour clock direction, vertical elevation, and tactile cues.
    """
    twin = pipeline_service.twin_service.get_twin(twin_id)
    return pipeline_service.assistance_engine.assist_find_object(target_object, twin)


@router.post("/see/spatial", response_model=SpatialGuidanceResponse)
async def compute_spatial_guidance(req: SpatialGuidanceRequest):
    """
    Extended spatial guidance endpoint accepting JSON request with optional user heading.
    """
    guidance = pipeline_service.compute_spatial_guidance(
        target_object=req.target_object,
        twin_id=req.twin_id or "default_user",
        heading_degrees=req.current_heading_degrees or 0.0,
    )
    return guidance
