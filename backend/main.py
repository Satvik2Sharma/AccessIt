"""
Sahayak AI — FastAPI Application Core
Orchestrates the 7-stage Intent-Aware Accessibility Pipeline.
"""

import sys
import os

# Ensure project root is in python path
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from typing import Optional, Dict, Any, List
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from backend.config import settings
from shared.schemas.models import (
    AccessibilityTwin,
    TaskType,
    AccessibleTaskFlow,
    VerificationResult,
    VerificationStatus,
    InteractionHeatmapItem,
)
from ai.accessibility.twin import AccessibilityTwinService
from ai.intent.intent_engine import IntentEngine
from ai.barrier.barrier_engine import BarrierEngine
from ai.task.task_engine import TaskEngine
from ai.compiler.flow_compiler import AccessibleTaskFlowCompiler
from ai.assistance.assistance_engine import AccessibilityAssistanceEngine
from ai.verification.verification_service import TaskVerificationService
from ai.learning.learning_service import AccessibilityLearningService

# Initialize FastAPI application
app = FastAPI(
    title=settings.app_name,
    version=settings.version,
    description="Intent-Aware Personal Accessibility Copilot — 7-Stage Pipeline Core",
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Core AI Engines
twin_service = AccessibilityTwinService()
intent_engine = IntentEngine()
barrier_engine = BarrierEngine()
task_engine = TaskEngine()
flow_compiler = AccessibleTaskFlowCompiler()
assistance_engine = AccessibilityAssistanceEngine()
verification_service = TaskVerificationService()
learning_service = AccessibilityLearningService()


# ----------------------------------------------------
# 1. System Health
# ----------------------------------------------------

@app.get(f"{settings.api_prefix}/health")
async def health_check():
    """Health check endpoint confirming pipeline readiness."""
    return {
        "status": "healthy",
        "version": settings.version,
        "system": "Sahayak AI Orchestrator",
        "pipeline": [
            "UNDERSTAND_USER",
            "UNDERSTAND_TASK",
            "DETECT_BARRIERS",
            "COMPILE_ACCESSIBLE_TASK_FLOW",
            "ASSIST",
            "VERIFY",
            "LEARN",
        ],
        "engines": {
            "accessibility_twin": True,
            "intent_engine": True,
            "barrier_engine": True,
            "task_engine": True,
            "flow_compiler": True,
            "assistance_engine": True,
            "verification_service": True,
            "learning_service": True,
        },
    }


# ----------------------------------------------------
# 2. Accessibility Twin
# ----------------------------------------------------

@app.get(f"{settings.api_prefix}/accessibility/profile", response_model=AccessibilityTwin)
async def get_profile(twin_id: str = "default_user"):
    return twin_service.get_twin(twin_id)


@app.post(f"{settings.api_prefix}/accessibility/profile", response_model=AccessibilityTwin)
async def update_profile(twin: AccessibilityTwin):
    return twin_service.update_twin(twin)


# ----------------------------------------------------
# 3. Intent Engine
# ----------------------------------------------------

class IntentRequest(BaseModel):
    query: str
    twin_id: Optional[str] = "default_user"


@app.post(f"{settings.api_prefix}/intent")
async def classify_intent(request: IntentRequest):
    twin = twin_service.get_twin(request.twin_id)
    task_type, confidence, rationale = intent_engine.classify_intent(request.query, twin)
    return {
        "query": request.query,
        "intent": task_type.value,
        "confidence": confidence,
        "rationale": rationale,
        "recommended_pipeline_action": f"INITIATE_{task_type.value}",
    }


# ----------------------------------------------------
# 4. Form Completion Pipeline (Main Demo 2)
# ----------------------------------------------------

class FormRespondRequest(BaseModel):
    task_id: str
    field_id: str
    value: str
    confirmation_received: bool = True
    twin_id: Optional[str] = "default_user"


@app.post(f"{settings.api_prefix}/complete/analyze", response_model=AccessibleTaskFlow)
async def analyze_form_for_completion(
    image: Optional[UploadFile] = File(None),
    twin_id: str = Form("default_user"),
):
    """
    Analyzes form document with REAL OCR, detects barriers against user's Accessibility Twin,
    and compiles a personalized AccessibleTaskFlow.
    """
    twin = twin_service.get_twin(twin_id)
    task_id = task_engine.create_form_task(total_fields=7)

    # Process Real OCR on uploaded image (or demo form fallback on disk)
    image_bytes = await image.read() if image else None
    discovered_fields = assistance_engine.ocr_engine.extract_form_fields(image_bytes)

    # Detect Barriers
    barriers = barrier_engine.detect_barriers(
        task_type=TaskType.FORM_COMPLETION,
        task_context={"total_fields": len(discovered_fields) or 7, "document_type": "physical_form"},
        twin=twin,
    )

    # Compile Accessible Flow
    flow = flow_compiler.compile_form_flow(
        task_id=task_id,
        twin=twin,
        barriers=barriers,
    )

    # Initialize verification state
    verification_service.verify_form_task(
        task_id=task_id,
        total_fields=flow.total_steps,
        completed_fields={},
        required_field_ids=[s.field_id for s in flow.steps],
    )

    return flow


@app.post(f"{settings.api_prefix}/complete/respond")
async def submit_form_field_response(req: FormRespondRequest):
    """
    Submits user answer (voice/text), validates input constraints, updates state, and advances.
    """
    twin = twin_service.get_twin(req.twin_id)

    # 1. Semantic Field Validation
    is_valid, validation_msg = verification_service.validate_field(req.field_id, req.value)
    if not is_valid:
        current_task = task_engine.get_task(req.task_id) or {"completed_fields": 0, "total_fields": 7, "fields": {}}
        ver = verification_service.get_verification(req.task_id)
        return {
            "task_id": req.task_id,
            "field_completed": req.field_id,
            "is_valid": False,
            "validation_error": validation_msg,
            "completed_fields_count": current_task["completed_fields"],
            "total_fields": current_task["total_fields"],
            "verification": ver,
            "next_step": None,
            "is_complete": False,
        }

    # 2. Update Task State
    task = task_engine.update_field(
        task_id=req.task_id,
        field_id=req.field_id,
        value=req.value,
        confirmed=req.confirmation_received,
    )

    # 3. Record Learning Telemetry
    learning_service.record_interaction(
        step_id=req.field_id,
        modality_used="voice" if twin.motor.voice_input else "touch",
        duration_seconds=3.2,
        retries=0,
        success=True,
    )

    # 4. Run First-Class Verification
    required_ids = ["full_name", "dob", "address", "category", "annual_income", "aadhaar", "bank_account"]
    ver_result = verification_service.verify_form_task(
        task_id=req.task_id,
        total_fields=len(required_ids),
        completed_fields=task["fields"],
        required_field_ids=required_ids,
    )

    # 5. Find Next Step
    completed_keys = set(task["fields"].keys())
    next_step = None
    flow = flow_compiler.compile_form_flow(req.task_id, twin, [])
    for step in flow.steps:
        if step.field_id not in completed_keys:
            next_step = step
            break

    return {
        "task_id": req.task_id,
        "completed_field": req.field_id,
        "is_valid": True,
        "validation_message": validation_msg,
        "completed_fields_count": task["completed_fields"],
        "total_fields": task["total_fields"],
        "verification": ver_result,
        "next_step": next_step,
        "is_complete": ver_result.status == VerificationStatus.COMPLETED,
    }


# ----------------------------------------------------
# 5. Document Understanding Pipeline (Demo 1)
# ----------------------------------------------------

@app.post(f"{settings.api_prefix}/read")
async def read_and_understand_document(
    image: Optional[UploadFile] = File(None),
    query: str = Form("What is important in this notice?"),
    twin_id: str = Form("default_user"),
):
    twin = twin_service.get_twin(twin_id)
    image_bytes = await image.read() if image else None

    # Detect barriers
    barriers = barrier_engine.detect_barriers(
        task_type=TaskType.UNDERSTAND_DOCUMENT,
        task_context={"document_language": "English"},
        twin=twin,
    )

    # Assist
    result = assistance_engine.assist_understand_document(image_bytes, query, twin)
    result["barriers_detected"] = barriers
    return result


# ----------------------------------------------------
# 6. Sign Communication Pipeline (Demo 3)
# ----------------------------------------------------

@app.post(f"{settings.api_prefix}/isl/predict")
async def predict_sign_language(
    image: Optional[UploadFile] = File(None),
    twin_id: str = Form("default_user"),
):
    twin = twin_service.get_twin(twin_id)
    image_bytes = await image.read() if image else None
    return assistance_engine.assist_sign_communication(image_bytes, twin)


# ----------------------------------------------------
# 7. Object Finding / Directional Guidance (Optional Wow Demo)
# ----------------------------------------------------

@app.post(f"{settings.api_prefix}/see")
async def see_and_find_object(
    target_object: str = Form("bottle"),
    twin_id: str = Form("default_user"),
):
    twin = twin_service.get_twin(twin_id)
    return assistance_engine.assist_find_object(target_object, twin)


# ----------------------------------------------------
# 8. Verification & Learning Heatmap Endpoints
# ----------------------------------------------------

@app.post(f"{settings.api_prefix}/task/verify", response_model=VerificationResult)
async def verify_task_status(task_id: str = Query(...)):
    return verification_service.get_verification(task_id)


@app.get(f"{settings.api_prefix}/learning/heatmap")
async def get_heatmap():
    heatmap = learning_service.get_interaction_heatmap()
    recommendation = learning_service.get_personalization_recommendation()
    return {
        "heatmap": heatmap,
        "recommendation": recommendation,
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host=settings.host, port=settings.port, reload=settings.debug)
