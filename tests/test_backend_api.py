"""
Sahayak AI — Backend Integration Tests
Tests all FastAPI REST endpoints end-to-end to ensure complete pipeline connectivity.
"""

import sys
import os
import pytest
from fastapi.testclient import TestClient

# Ensure project root is in python path
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from backend.main import app

client = TestClient(app)


def test_health_endpoint():
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "pipeline" in data


def test_profile_endpoints():
    # 1. Get default profile
    res_get = client.get("/api/v1/accessibility/profile?twin_id=default_user")
    assert res_get.status_code == 200
    profile = res_get.json()
    assert profile["id"] == "default_user"

    # 2. Update profile
    profile["visual"]["high_contrast"] = True
    res_post = client.post("/api/v1/accessibility/profile", json=profile)
    assert res_post.status_code == 200
    assert res_post.json()["visual"]["high_contrast"] is True


def test_intent_endpoint():
    res = client.post("/api/v1/intent", json={"query": "What is the deadline for this notice?"})
    assert res.status_code == 200
    data = res.json()
    assert data["intent"] == "UNDERSTAND_DOCUMENT"
    assert data["confidence"] > 0.5


def test_form_completion_flow():
    # 1. Analyze form and get compiled flow
    res_analyze = client.post("/api/v1/complete/analyze", data={"twin_id": "default_user"})
    assert res_analyze.status_code == 200
    flow = res_analyze.json()
    task_id = flow["task_id"]
    assert len(flow["steps"]) == 7

    # 2. Respond to Step 1 (Full Name)
    res_step1 = client.post(
        "/api/v1/complete/respond",
        json={
            "task_id": task_id,
            "field_id": "full_name",
            "value": "Varanka Tyagi",
            "confirmation_received": True,
            "twin_id": "default_user",
        },
    )
    assert res_step1.status_code == 200
    data = res_step1.json()
    assert data["completed_field"] == "full_name"
    assert data["completed_fields_count"] == 1
    assert data["is_complete"] is False


def test_document_understanding_endpoint():
    res = client.post(
        "/api/v1/read",
        data={"query": "What are the scholarship requirements?", "twin_id": "default_user"},
    )
    assert res.status_code == 200
    data = res.json()
    assert "title" in data
    assert "deadlines" in data
    assert "required_documents" in data


def test_isl_predict_endpoint():
    res = client.post("/api/v1/isl/predict", data={"twin_id": "default_user"})
    assert res.status_code == 200
    data = res.json()
    assert data["sign"] == "HELP"
    assert "spoken_output" in data


def test_spatial_guidance_endpoint():
    res = client.post("/api/v1/see", data={"target_object": "water bottle", "twin_id": "default_user"})
    assert res.status_code == 200
    data = res.json()
    assert "relative_direction" in data
    assert "clock_direction" in data
    assert "haptic_cue" in data


def test_learning_heatmap_endpoint():
    res = client.get("/api/v1/learning/heatmap")
    assert res.status_code == 200
    data = res.json()
    assert "heatmap" in data
    assert "recommendation" in data
    assert len(data["heatmap"]) > 0
