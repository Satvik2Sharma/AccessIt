"""
Sahayak AI — ISL Sign Communication Routes
Endpoints for Indian Sign Language gesture classification and translation.
"""

from typing import Optional, Dict, Any
from fastapi import APIRouter, UploadFile, File, Form
from backend.services.pipeline_service import pipeline_service

router = APIRouter(tags=["Indian Sign Language"])


@router.post("/isl/predict")
async def predict_sign_language(
    image: Optional[UploadFile] = File(None),
    twin_id: str = Form("default_user"),
):
    """
    Coordinates ISL gesture classification from camera frame, produces captions, and TTS spoken output.
    """
    twin = pipeline_service.twin_service.get_twin(twin_id)
    image_bytes = await image.read() if image else None
    return pipeline_service.assistance_engine.assist_sign_communication(image_bytes, twin)
