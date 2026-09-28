"""
Sahayak AI — Integration Tests for Camera Intelligence Pipeline
Validates FastAPI camera routes (/api/v1/camera/analyze, /session/reset),
multimodal output formatting, capability routing, and session state continuity.
"""

import io
import pytest
from fastapi.testclient import TestClient
from PIL import Image, ImageDraw

from backend.main import app

client = TestClient(app)


@pytest.fixture
def test_image_bytes():
    """Generates JPEG test image bytes with geometric features."""
    img = Image.new("RGB", (320, 240), color=(240, 240, 240))
    draw = ImageDraw.Draw(img)
    draw.rectangle([50, 50, 250, 190], outline=(20, 20, 20), width=3)
    draw.text((60, 60), "SCHOLARSHIP NOTICE", fill=(0, 0, 0))
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    return buf.getvalue()


def test_api_camera_analyze_auto_scene(test_image_bytes):
    response = client.post(
        "/api/v1/camera/analyze",
        files={"image": ("test.jpg", test_image_bytes, "image/jpeg")},
        data={"mode": "auto", "twin_id": "default_user"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] in ("SUCCESS", "SKIPPED_DUPLICATE")
    assert "quality" in data
    assert "primary_interpretation" in data
    assert "spoken_feedback" in data


def test_api_camera_analyze_explicit_navigation(test_image_bytes):
    response = client.post(
        "/api/v1/camera/analyze",
        files={"image": ("test.jpg", test_image_bytes, "image/jpeg")},
        data={"mode": "navigation", "twin_id": "default_user", "skip_duplicate_check": "true"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["mode_executed"] == "navigation"
    assert "navigation_instructions" in data
    assert len(data["navigation_instructions"]) > 0


def test_api_camera_analyze_query_see(test_image_bytes):
    response = client.post(
        "/api/v1/camera/analyze",
        files={"image": ("test.jpg", test_image_bytes, "image/jpeg")},
        data={"query": "Where is my water bottle?", "twin_id": "default_user", "skip_duplicate_check": "true"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["mode_executed"] == "see"
    assert len(data["spatial_objects"]) > 0


def test_api_camera_analyze_isl(test_image_bytes):
    response = client.post(
        "/api/v1/camera/analyze",
        files={"image": ("test.jpg", test_image_bytes, "image/jpeg")},
        data={"mode": "isl", "twin_id": "default_user", "skip_duplicate_check": "true"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["mode_executed"] == "isl"
    assert data["isl_prediction"] is not None


def test_api_camera_session_reset():
    response = client.post(
        "/api/v1/camera/session/reset",
        data={"session_id": "integration_test_session"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "SUCCESS"
