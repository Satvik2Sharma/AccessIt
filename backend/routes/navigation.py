"""
Sahayak AI — Smart Navigation & Obstacle Guidance Routes
Endpoints for Step-by-Step Spatial Direction, Obstacle Warning, and Session State.
"""

from typing import Optional
from fastapi import APIRouter
from shared.schemas.models import (
    NavigationGuidanceRequest,
    NavigationGuidanceResponse,
    NavigationState,
)
from backend.services.pipeline_service import pipeline_service
from backend.services.session_service import session_service

router = APIRouter(tags=["Smart Navigation"])


@router.post("/navigation/guide", response_model=NavigationGuidanceResponse)
async def guide_navigation_step(req: NavigationGuidanceRequest):
    """
    Provides real-time contextual navigation guidance, 12-hour clock directions,
    obstacle avoidance warnings, and directional tactile pulses.
    """
    guidance = pipeline_service.guide_navigation(
        session_id=req.session_id,
        target_destination=req.target_destination or "exit",
        camera_scene_description=req.camera_scene_description,
        detected_labels=req.detected_labels,
        twin_id=req.twin_id or "default_user",
    )
    return guidance


@router.get("/navigation/session", response_model=NavigationState)
async def get_navigation_session_state(session_id: str):
    """
    Retrieves the current state and obstacle tracking history for an active navigation session.
    """
    sess = session_service.get_navigation_session(session_id)
    if not sess:
        # Create a new active session
        session_service.create_navigation_session(custom_id=session_id)
        sess = session_service.get_navigation_session(session_id)

    return NavigationState(
        session_id=session_id,
        active=sess.get("active", True),
        current_destination=sess.get("destination", "exit"),
        path_clear=len(sess.get("obstacles", [])) == 0,
        heading_degrees=sess.get("heading_degrees", 0.0),
        detected_obstacles=sess.get("obstacles", []),
        recent_guidance=sess.get("guidance_history", [{}])[-1].get("guidance") if sess.get("guidance_history") else None,
        total_steps_guided=sess.get("steps_guided", 0),
    )
