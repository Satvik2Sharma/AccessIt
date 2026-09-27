"""
Sahayak AI — Scene Understanding & Object + OCR Fusion Routes
Endpoints for Comprehensive Environment Analysis and Fusing Detected Objects with OCR Text.
"""

from typing import Optional, Dict, Any, List
from fastapi import APIRouter
from pydantic import BaseModel
from shared.schemas.models import SceneAnalysis
from backend.services.pipeline_service import pipeline_service

router = APIRouter(tags=["Scene Understanding & Fusion"])


class SceneAnalysisRequest(BaseModel):
    scene_description: Optional[str] = None
    objects: Optional[List[Dict[str, Any]]] = None
    texts: Optional[List[Dict[str, Any]]] = None
    twin_id: Optional[str] = "default_user"


class SceneFusionRequest(BaseModel):
    objects: List[Dict[str, Any]]
    texts: List[Dict[str, Any]]
    twin_id: Optional[str] = "default_user"


@router.post("/scene/analyze", response_model=SceneAnalysis)
async def analyze_scene(req: SceneAnalysisRequest):
    """
    Performs full scene understanding, identifying objects, spatial relationships,
    nearby OCR signage (e.g., 'EMERGENCY EXIT' on 'door'), and potential environmental hazards.
    """
    analysis = pipeline_service.analyze_scene_and_fusion(
        scene_description=req.scene_description,
        raw_objects=req.objects,
        raw_texts=req.texts,
        twin_id=req.twin_id or "default_user",
    )
    return analysis


@router.post("/scene/fusion")
async def fuse_objects_and_text(req: SceneFusionRequest):
    """
    Explicitly fuses detected vision bounding boxes with recognized OCR text bounding boxes.
    """
    fused = pipeline_service.assistance_engine.scene_fusion.fuse(
        objects=req.objects,
        texts=req.texts,
    )
    return fused
