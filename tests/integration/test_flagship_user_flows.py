# Adapt-X — Flagship Real User Flows & Edge Cases Integration Test Suite

import io
import pytest
from PIL import Image, ImageDraw
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)


def _get_test_image_bytes(width: int = 320, height: int = 240) -> bytes:
    img = Image.new("RGB", (width, height), color=(240, 240, 240))
    draw = ImageDraw.Draw(img)
    draw.rectangle([50, 50, 250, 190], outline=(20, 20, 20), width=3)
    draw.text((60, 60), "DOOR HANDLE", fill=(0, 0, 0))
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    return buf.getvalue()


# ==============================================================================
# FLOW 1: Login -> Home -> Camera -> Analyze -> Spatial Guidance & Haptics
# ==============================================================================

def test_user_flow_camera_spatial_guidance():
    # 1. Login with quick-start judge persona
    login_resp = client.post("/api/v1/auth/guest", json={
        "persona": "low_vision",
        "preferred_language": "English",
        "custom_name": "Judge Flow 1",
    })
    assert login_resp.status_code == 200
    token = login_resp.json()["token"]
    twin_id = login_resp.json()["user"]["twin_id"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Start Camera Session
    start_resp = client.post("/api/v1/camera/session", json={
        "twin_id": twin_id,
        "initial_mode": "NAVIGATE",
        "target_object": "door",
    }, headers=headers)
    assert start_resp.status_code == 200
    session_id = start_resp.json()["session_id"]
    assert session_id.startswith("cam_")

    # 3. Analyze Frame (Simulate camera frame)
    img_bytes = _get_test_image_bytes()
    analyze_resp = client.post(
        "/api/v1/camera/analyze",
        data={
            "session_id": session_id,
            "twin_id": twin_id,
            "mode": "NAVIGATE",
            "query": "Where is the door?",
            "skip_duplicate_check": "true",
        },
        files={"image": ("frame.jpg", img_bytes, "image/jpeg")},
        headers=headers,
    )
    assert analyze_resp.status_code == 200
    data = analyze_resp.json()
    assert data["success"] is True
    assert "assistance" in data
    assert "spoken_response" in data["assistance"]
    assert "haptic_cue" in data["assistance"]

    # 4. Reset Camera Session
    reset_resp = client.post("/api/v1/camera/session/reset", data={"session_id": session_id}, headers=headers)
    assert reset_resp.status_code == 200


# ==============================================================================
# FLOW 2: Login -> Read Document -> Understand -> Question -> Task
# ==============================================================================

def test_user_flow_document_reading_qa_task():
    # 1. Register new user
    reg_resp = client.post("/api/v1/auth/register", json={
        "name": "Document Tester",
        "email": "doctest@adaptx.ai",
        "password": "SecurePassword123!",
        "confirm_password": "SecurePassword123!",
        "preferred_language": "Hindi",
    })
    assert reg_resp.status_code == 200
    token = reg_resp.json()["token"]
    twin_id = reg_resp.json()["user"]["twin_id"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Read and comprehend notice
    read_resp = client.post("/api/v1/read", data={
        "query": "इस नोटिस में अंतिम तिथि क्या है?",
        "twin_id": twin_id,
    }, headers=headers)
    assert read_resp.status_code == 200
    doc_data = read_resp.json()
    assert "title" in doc_data
    assert "deadlines" in doc_data
    assert len(doc_data["deadlines"]) > 0

    # 3. Ask question about required documents
    qa_resp = client.post("/api/v1/read", data={
        "query": "कौन से दस्तावेज़ चाहिए?",
        "twin_id": twin_id,
    }, headers=headers)
    assert qa_resp.status_code == 200
    assert "required_documents" in qa_resp.json()


# ==============================================================================
# FLOW 3: Login -> Complete Form -> Step-by-Step -> Verification
# ==============================================================================

def test_user_flow_complete_form_multistep_verification():
    # 1. Login with motor difficulty persona
    login_resp = client.post("/api/v1/auth/guest", json={
        "persona": "motor_difficulty",
        "preferred_language": "Hindi",
    })
    assert login_resp.status_code == 200
    token = login_resp.json()["token"]
    twin_id = login_resp.json()["user"]["twin_id"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Analyze form and get task flow
    flow_resp = client.post("/api/v1/complete/analyze", data={"twin_id": twin_id}, headers=headers)
    assert flow_resp.status_code == 200
    flow = flow_resp.json()
    task_id = flow["task_id"]
    steps = flow["steps"]
    assert len(steps) >= 5

    # 3. Fill all steps sequentially
    sample_answers = {
        "full_name": "राकेश कुमार",
        "dob": "10/05/1995",
        "address": "गांधी मार्ग, लखनऊ",
        "category": "OBC",
        "annual_income": "₹ 1,50,000",
        "aadhaar": "1234 5678 9012",
        "bank_account": "SBI0001234 / 1234567890",
    }

    last_resp = None
    for step in steps:
        field_id = step["field_id"]
        val = sample_answers.get(field_id, "Valid Value")
        resp = client.post("/api/v1/complete/respond", json={
            "task_id": task_id,
            "field_id": field_id,
            "value": val,
            "confirmation_received": True,
            "twin_id": twin_id,
        }, headers=headers)
        assert resp.status_code == 200
        last_resp = resp.json()
        assert last_resp["is_valid"] is True

    # 4. Verification check upon completion
    assert last_resp is not None
    assert "verification" in last_resp
    verif = last_resp["verification"]
    assert verif["status"] == "COMPLETED"
    assert verif["completed_fields"] >= 7
    assert verif["verification_token"] is not None


# ==============================================================================
# FLOW 4: Login -> ISL Gesture -> Recognition -> Voice/Caption
# ==============================================================================

def test_user_flow_isl_gesture_recognition():
    # 1. Login with hearing impairment persona
    login_resp = client.post("/api/v1/auth/guest", json={
        "persona": "hearing_impairment",
        "preferred_language": "English",
    })
    assert login_resp.status_code == 200
    token = login_resp.json()["token"]
    twin_id = login_resp.json()["user"]["twin_id"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Predict sign gesture
    isl_resp = client.post("/api/v1/isl/predict", data={"twin_id": twin_id}, headers=headers)
    assert isl_resp.status_code == 200
    isl_data = isl_resp.json()
    assert isl_data["sign"] == "HELP"
    assert isl_data["confidence"] >= 0.8
    assert "caption" in isl_data
    assert "spoken_output" in isl_data


# ==============================================================================
# ERROR CASES & ROBUSTNESS
# ==============================================================================

def test_error_handling_invalid_auth():
    # Wrong password
    resp = client.post("/api/v1/auth/login", json={
        "email": "doctest@adaptx.ai",
        "password": "WrongPassword999!",
    })
    assert resp.status_code == 401
    assert "detail" in resp.json()

    # Nonexistent user
    resp = client.post("/api/v1/auth/login", json={
        "email": "nobody@nowhere.com",
        "password": "Password123!",
    })
    assert resp.status_code == 401

    # Invalid token for protected endpoint
    resp = client.get("/api/v1/auth/me", headers={"Authorization": "Bearer invalid.token.payload"})
    assert resp.status_code == 401


def test_error_handling_camera_invalid_frame():
    login_resp = client.post("/api/v1/auth/guest", json={"persona": "low_vision"})
    headers = {"Authorization": f"Bearer {login_resp.json()['token']}"}

    # Start session
    s_resp = client.post("/api/v1/camera/session", json={"twin_id": "twin_test"}, headers=headers)
    sid = s_resp.json()["session_id"]

    # Empty frame analysis - should recover gracefully with error and guidance
    resp = client.post(
        "/api/v1/camera/analyze",
        data={
            "session_id": sid,
            "twin_id": "twin_test",
            "mode": "AUTO",
        },
        headers=headers,
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] is False
    assert data["error"]["error_code"] == "INVALID_CAMERA_FRAME"
    assert data["assistance"]["spoken_response"] is not None


def test_error_handling_form_invalid_input():
    login_resp = client.post("/api/v1/auth/guest", json={"persona": "elderly_simplified"})
    headers = {"Authorization": f"Bearer {login_resp.json()['token']}"}

    # Start form
    f_resp = client.post("/api/v1/complete/analyze", data={"twin_id": "twin_test"}, headers=headers)
    task_id = f_resp.json()["task_id"]

    # Submit invalid aadhaar (too short)
    resp = client.post("/api/v1/complete/respond", json={
        "task_id": task_id,
        "field_id": "aadhaar",
        "value": "123", # Invalid
        "twin_id": "twin_test",
    }, headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["is_valid"] is False
    assert "validation_error" in data
