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
    image_base64: Optional[str] = Form(None),
    session_id: Optional[str] = Form(None),
    twin_id: str = Form("default_user"),
):
    """
    Coordinates ISL gesture classification from camera frame, produces captions, and TTS spoken output.
    """
    twin = pipeline_service.twin_service.get_twin(twin_id)
    image_bytes = None
    if image:
        image_bytes = await image.read()
    elif image_base64:
        import base64
        b64_str = image_base64
        if "," in b64_str:
            b64_str = b64_str.split(",", 1)[1]
        try:
            image_bytes = base64.b64decode(b64_str)
        except Exception:
            image_bytes = None

    return pipeline_service.assistance_engine.assist_sign_communication(image_bytes, twin, session_id=session_id)

