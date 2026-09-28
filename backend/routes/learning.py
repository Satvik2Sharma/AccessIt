"""
Sahayak AI — Learning Telemetry & Personalization Routes
Endpoints for Interaction Heatmaps and Adaptive Personalization Profiles.
"""

from typing import Optional, Dict, Any
from fastapi import APIRouter
from pydantic import BaseModel
from shared.schemas.models import PersonalizationProfile
from backend.services.pipeline_service import pipeline_service

router = APIRouter(tags=["Learning & Personalization"])


class PersonalizationUpdateRequest(BaseModel):
    twin_id: str = "default_user"
    updates: Dict[str, Any] = {}


@router.get("/learning/heatmap")
async def get_heatmap():
    """
    Retrieves cognitive barrier interaction heatmap and system personalization recommendation.
    """
    heatmap = pipeline_service.learning_service.get_interaction_heatmap()
    recommendation = pipeline_service.learning_service.get_personalization_recommendation()
    return {
        "heatmap": heatmap,
        "recommendation": recommendation,
    }


@router.get("/learning/personalization", response_model=PersonalizationProfile)
async def get_personalization(twin_id: str = "default_user"):
    """
    Retrieves the active personalization profile and interaction telemetry for a user.
    """
    return pipeline_service.update_and_get_personalization(twin_id=twin_id)


@router.post("/learning/personalization", response_model=PersonalizationProfile)
async def update_personalization(req: PersonalizationUpdateRequest):
    """
    Updates user interaction preferences (speech rate, haptic intensity, high contrast, simplification).
    """
    return pipeline_service.update_and_get_personalization(twin_id=req.twin_id, updates=req.updates)
