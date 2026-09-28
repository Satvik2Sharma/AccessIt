"""
Sahayak AI — Form Completion Routes
Endpoints for Form OCR Analysis, Barrier Extraction, Flow Compilation, and Field Step Responses.
"""

from typing import Optional, Dict, Any
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from shared.schemas.models import (
    AccessibleTaskFlow,
    TaskType,
    VerificationStatus,
    FormRespondRequest,
)
from backend.services.pipeline_service import pipeline_service

router = APIRouter(tags=["Form Completion"])


@router.post("/complete/analyze", response_model=AccessibleTaskFlow)
async def analyze_form_for_completion(
    image: Optional[UploadFile] = File(None),
    twin_id: str = Form("default_user"),
):
    """
    Analyzes form document with REAL OCR, detects barriers against user's Accessibility Twin,
    and compiles a personalized AccessibleTaskFlow.
    """
    twin = pipeline_service.twin_service.get_twin(twin_id)
    task_id = pipeline_service.task_engine.create_form_task(total_fields=7)

    # Process Real OCR on uploaded image (or demo form fallback on disk)
    image_bytes = await image.read() if image else None
    discovered_fields = pipeline_service.assistance_engine.ocr_engine.extract_form_fields(image_bytes)

    # Detect Barriers
    barriers = pipeline_service.barrier_engine.detect_barriers(
        task_type=TaskType.FORM_COMPLETION,
        task_context={"total_fields": len(discovered_fields) or 7, "document_type": "physical_form"},
        twin=twin,
    )

    # Compile Accessible Flow
    flow = pipeline_service.flow_compiler.compile_form_flow(
        task_id=task_id,
        twin=twin,
        barriers=barriers,
    )

    # Initialize verification state
    pipeline_service.verification_service.verify_form_task(
        task_id=task_id,
        total_fields=flow.total_steps,
        completed_fields={},
        required_field_ids=[s.field_id for s in flow.steps],
    )

    return flow


@router.post("/complete/respond")
async def submit_form_field_response(req: FormRespondRequest):
    """
    Submits user answer (voice/text), validates input constraints, updates state, and advances.
    """
    twin = pipeline_service.twin_service.get_twin(req.twin_id)

    # 1. Semantic Field Validation
    is_valid, validation_msg = pipeline_service.verification_service.validate_field(req.field_id, req.value)
    if not is_valid:
        current_task = pipeline_service.task_engine.get_task(req.task_id) or {
            "completed_fields": 0, "total_fields": 7, "fields": {}
        }
        ver = pipeline_service.verification_service.get_verification(req.task_id)
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
    task = pipeline_service.task_engine.update_field(
        task_id=req.task_id,
        field_id=req.field_id,
        value=req.value,
        confirmed=req.confirmation_received,
    )

    # 3. Record Learning Telemetry
    pipeline_service.learning_service.record_interaction(
        step_id=req.field_id,
        modality_used="voice" if twin.motor.voice_input else "touch",
        duration_seconds=3.2,
        retries=0,
        success=True,
    )

    # 4. Run First-Class Verification
    required_ids = ["full_name", "dob", "address", "category", "annual_income", "aadhaar", "bank_account"]
    ver_result = pipeline_service.verification_service.verify_form_task(
        task_id=req.task_id,
        total_fields=len(required_ids),
        completed_fields=task["fields"],
        required_field_ids=required_ids,
    )

    # 5. Find Next Step
    completed_keys = set(task["fields"].keys())
    next_step = None
    flow = pipeline_service.flow_compiler.compile_form_flow(req.task_id, twin, [])
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
