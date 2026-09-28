"""
Sahayak AI — Camera Intelligence API Router
Endpoints for device camera stream analysis, frame quality checks, and session management.
"""

from typing import Optional
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from shared.schemas.camera_models import CameraAnalysisResult, CameraMode
from ai.camera.camera_engine import CameraEngine
from ai.camera.camera_session import camera_session_manager

router = APIRouter(prefix="/camera", tags=["Camera Intelligence"])

camera_engine = CameraEngine()


@router.post("/analyze", response_model=CameraAnalysisResult)
async def analyze_camera_frame(
    image: Optional[UploadFile] = File(None),
    mode: str = Form("auto"),
    query: Optional[str] = Form(None),
    twin_id: str = Form("default_user"),
    session_id: Optional[str] = Form(None),
    target_object: Optional[str] = Form(None),
    skip_duplicate_check: bool = Form(False),
):
    """
    Analyzes an incoming camera frame with automated quality estimation,
    duplicate suppression, intelligent capability selection, and accessible multimodal output.
    """
    image_bytes = None
    if image is not None:
        image_bytes = await image.read()

    if not image_bytes:
        # Fallback to simulated blank or placeholder image if none uploaded
        from PIL import Image
        import io
        img = Image.new("RGB", (640, 480), color=(128, 128, 128))
        buf = io.BytesIO()
        img.save(buf, format="JPEG")
        image_bytes = buf.getvalue()

    result = camera_engine.analyze(
        image_input=image_bytes,
        mode=mode,
        query=query,
        twin_id=twin_id,
        session_id=session_id,
        target_object=target_object,
        skip_duplicate_check=skip_duplicate_check,
    )
    return result


@router.post("/session/reset")
async def reset_camera_session(session_id: str = Form(...)):
    """Resets frame history and context for a camera session."""
    session = camera_session_manager.get_or_create(session_id)
    session.reset()
    return {"status": "SUCCESS", "message": f"Camera session {session_id} reset."}
