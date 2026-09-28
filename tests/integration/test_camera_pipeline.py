"""
Sahayak AI — Integration Tests for Camera Intelligence Pipeline & Session Continuity
Validates FastAPI camera route handlers, multimodal output formatting,
capability routing, error recovery, and session continuity.
"""

import sys
import os
import io
import asyncio
import builtins
import typing
builtins.Union = typing.Union

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from PIL import Image, ImageDraw
from shared.schemas.models import (
    CameraAnalysisMode,
    CameraAnalysisResponse,
    CameraSessionState,
)
from backend.services.camera_service import camera_service
from backend.services.session_service import session_service
from backend.routes.camera import (
    analyze_camera_frame,
    create_camera_session,
    get_camera_session_state,
    reset_camera_session,
    CameraSessionCreateRequest,
)


def _get_test_image_bytes(width: int = 320, height: int = 240) -> bytes:
    img = Image.new("RGB", (width, height), color=(240, 240, 240))
    draw = ImageDraw.Draw(img)
    draw.rectangle([50, 50, 250, 190], outline=(20, 20, 20), width=3)
    draw.text((60, 60), "SCHOLARSHIP NOTICE", fill=(0, 0, 0))
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    return buf.getvalue()


# ----------------------------------------------------
# 1. API Route Handler Integration Tests
# ----------------------------------------------------

def test_api_camera_analyze_auto_scene():
    img_bytes = _get_test_image_bytes()
    resp = camera_service.analyze_frame(
        image_bytes=img_bytes,
        requested_mode=CameraAnalysisMode.AUTO,
        twin_id="default_user",
    )
    assert resp.success is True
    assert resp.analysis is not None
    assert resp.assistance is not None
    assert resp.assistance.spoken_response is not None


def test_api_camera_analyze_explicit_navigation():
    img_bytes = _get_test_image_bytes()
    resp = camera_service.analyze_frame(
        image_bytes=img_bytes,
        requested_mode=CameraAnalysisMode.NAVIGATE,
        twin_id="default_user",
        skip_duplicate_check=True,
    )
    assert resp.success is True
    assert resp.mode == CameraAnalysisMode.NAVIGATE
    assert resp.assistance is not None
    assert resp.assistance.spoken_response is not None


def test_api_camera_analyze_query_see():
    img_bytes = _get_test_image_bytes()
    resp = camera_service.analyze_frame(
        image_bytes=img_bytes,
        intent="Where is my water bottle?",
        twin_id="default_user",
        skip_duplicate_check=True,
    )
    assert resp.success is True
    assert len(resp.analysis.objects) > 0 or resp.analysis.target_found is True


def test_api_camera_session_lifecycle_api():
    # 1. Create session via create_camera_session
    req = CameraSessionCreateRequest(twin_id="default_user", initial_mode=CameraAnalysisMode.FIND, target_object="door")
    sess_state = asyncio.run(create_camera_session(req))
    sid = sess_state.session_id
    assert sid.startswith("cam_")
    assert sess_state.target_object == "door"

    # 2. Query session via get_camera_session_state
    queried_state = asyncio.run(get_camera_session_state(session_id=sid))
    assert queried_state.session_id == sid
    assert queried_state.target_object == "door"

    # 3. Reset session via reset_camera_session
    reset_res = asyncio.run(reset_camera_session(session_id=sid))
    assert reset_res["status"] == "SUCCESS"


# ----------------------------------------------------
# 2. Service-Level Orchestration & Continuity Tests
# ----------------------------------------------------

def test_camera_pipeline_full_lifecycle():
    img_bytes = _get_test_image_bytes(400, 300)

    # 1. Create session explicitly
    sid = session_service.create_camera_session(
        twin_id="default_user",
        initial_mode="UNDERSTAND",
    )
    assert sid.startswith("cam_")

    # 2. Frame 1: Analyze general scene
    res1 = camera_service.analyze_frame(
        image_bytes=img_bytes,
        session_id=sid,
        twin_id="default_user",
        requested_mode=CameraAnalysisMode.UNDERSTAND,
        intent="What is in front of me?",
    )
    assert res1.success is True
    assert res1.session_id == sid
    assert res1.mode == CameraAnalysisMode.UNDERSTAND
    assert res1.analysis.scene is not None
    assert len(res1.analysis.objects) >= 1
    assert res1.assistance.spoken_response is not None

    # 3. Frame 2: Switch mode to FIND in the same session
    res2 = camera_service.analyze_frame(
        image_bytes=img_bytes,
        session_id=sid,
        twin_id="default_user",
        requested_mode=CameraAnalysisMode.FIND,
        target_object="water bottle",
    )
    assert res2.success is True
    assert res2.session_id == sid
    assert res2.mode == CameraAnalysisMode.FIND
    assert res2.analysis.target_found is True
    assert res2.analysis.target_guidance is not None
    assert "clock_direction" in res2.analysis.target_guidance

    # 4. Verify session state continuity
    session_data = session_service.get_camera_session(sid)
    assert session_data["total_frames_processed"] == 2
    assert len(session_data["analysis_history"]) == 2
    assert session_data["target_object"] == "water bottle"


def test_camera_pipeline_read_mode_ocr():
    notice_path = "shared/demo_data/notices/scholarship_notice.png"
    if os.path.exists(notice_path):
        with open(notice_path, "rb") as f:
            img_bytes = f.read()
    else:
        img_bytes = _get_test_image_bytes()

    res = camera_service.analyze_frame(
        image_bytes=img_bytes,
        requested_mode=CameraAnalysisMode.READ,
        intent="Read this document",
        twin_id="default_user",
    )
    assert res.success is True
    assert res.mode == CameraAnalysisMode.READ
    assert len(res.analysis.text_elements) >= 1
    assert res.assistance.spoken_response is not None


def test_camera_pipeline_error_recovery():
    res = camera_service.analyze_frame(
        image_bytes=b"",
        twin_id="default_user",
    )
    assert res.success is False
    assert res.error is not None
    assert res.error.error_code == "INVALID_CAMERA_FRAME"
    assert res.error.retryable is True
    assert res.assistance.spoken_response is not None


if __name__ == "__main__":
    test_api_camera_analyze_auto_scene()
    test_api_camera_analyze_explicit_navigation()
    test_api_camera_analyze_query_see()
    test_api_camera_session_lifecycle_api()
    test_camera_pipeline_full_lifecycle()
    test_camera_pipeline_read_mode_ocr()
    test_camera_pipeline_error_recovery()
    print("All integration/test_camera_pipeline.py tests passed successfully!")
