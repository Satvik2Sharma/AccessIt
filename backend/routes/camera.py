"""
Sahayak AI — Camera Intelligence Routes
Endpoints for Real-Time Camera Frame Analysis, Mode Resolution, and Stateful Camera Sessions.
"""

from typing import Optional
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Query
from pydantic import BaseModel
from shared.schemas.models import (
    CameraAnalysisMode,
    CameraAnalysisResponse,
    CameraSessionState,
)
from backend.services.camera_service import camera_service
from backend.services.session_service import session_service
try:
    from ai.camera.camera_session import camera_session_manager
except Exception:
    class DummyCameraSessionManager:
        def get_or_create(self, session_id):
            class DummySession:
                def reset(self): pass
            return DummySession()
    camera_session_manager = DummyCameraSessionManager()

router = APIRouter(tags=["Camera Intelligence"])


class CameraSessionCreateRequest(BaseModel):
    twin_id: str = "default_user"
    initial_mode: CameraAnalysisMode = CameraAnalysisMode.AUTO
    target_object: Optional[str] = None


@router.post("/camera/analyze", response_model=CameraAnalysisResponse)
async def analyze_camera_frame(
    image: Optional[UploadFile] = File(None),
    image_base64: Optional[str] = Form(None),
    session_id: Optional[str] = Form(None),
    twin_id: str = Form("default_user"),
    mode: str = Form("AUTO"),
    intent: Optional[str] = Form(None),
    query: Optional[str] = Form(None),
    target_object: Optional[str] = Form(None),
    language: Optional[str] = Form(None),
    skip_duplicate_check: bool = Form(False),
):
    """
    Analyzes a camera frame in an intent-aware mode (AUTO, SEE, READ, FIND, UNDERSTAND, NAVIGATE).
    Returns structured vision detections, OCR texts, object-text fusion, and multimodal assistance prompts.
    """
    # Accept query as intent if intent is not explicitly provided
    effective_intent = intent or query

    # Parse mode enum safely
    try:
        parsed_mode = CameraAnalysisMode(mode.upper())
    except ValueError:
        parsed_mode = CameraAnalysisMode.AUTO

    image_bytes = None
    filename = None
    content_type = None

    if image:
        image_bytes = await image.read()
        filename = image.filename
        content_type = image.content_type
    elif image_base64:
        import base64
        b64_str = image_base64
        if "," in b64_str:
            b64_str = b64_str.split(",", 1)[1]
        try:
            image_bytes = base64.b64decode(b64_str)
            filename = "frame.jpg"
            content_type = "image/jpeg"
        except Exception:
            image_bytes = None


    response = camera_service.analyze_frame(
        image_bytes=image_bytes,
        session_id=session_id,
        twin_id=twin_id,
        requested_mode=parsed_mode,
        intent=effective_intent,
        target_object=target_object,
        language=language,
        filename=filename,
        content_type=content_type,
        skip_duplicate_check=skip_duplicate_check,
    )
    return response


@router.post("/camera/session", response_model=CameraSessionState)
async def create_camera_session(req: CameraSessionCreateRequest):
    """
    Initializes a new stateful camera session for continuous frame analysis.
    """
    sid = session_service.create_camera_session(
        twin_id=req.twin_id,
        initial_mode=req.initial_mode.value,
        target_object=req.target_object,
    )
    sess = session_service.get_camera_session(sid)
    return CameraSessionState(**sess)


@router.get("/camera/session", response_model=CameraSessionState)
async def get_camera_session_state(session_id: str = Query(...)):
    """
    Retrieves the current state, detected entities, and history of an active camera session.
    """
    sess = session_service.get_camera_session(session_id)
    if not sess:
        raise HTTPException(status_code=404, detail=f"Camera session '{session_id}' not found.")
    return CameraSessionState(**sess)


@router.post("/camera/session/reset")
async def reset_camera_session(session_id: str = Form(...)):
    """Resets frame history and context for a camera session."""
    session = camera_session_manager.get_or_create(session_id)
    session.reset()
    # Also reset backend session service if active
    sess = session_service.get_camera_session(session_id)
    if sess:
        sess["total_frames_processed"] = 0
        sess["analysis_history"] = []
    return {"status": "SUCCESS", "message": f"Camera session {session_id} reset."}
