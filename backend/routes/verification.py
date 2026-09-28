"""
Sahayak AI — Verification Routes
Endpoints for Step-by-Step Task and Form Verification.
"""

from typing import Optional, Dict, Any, List
from fastapi import APIRouter, Query
from pydantic import BaseModel
from shared.schemas.models import VerificationResult
from backend.services.pipeline_service import pipeline_service

router = APIRouter(tags=["Task Verification"])


class VerificationCheckRequest(BaseModel):
    task_id: str
    total_fields: int = 7
    completed_fields: Dict[str, Any] = {}
    required_field_ids: List[str] = ["full_name", "dob", "address", "category", "annual_income", "aadhaar", "bank_account"]


@router.post("/task/verify", response_model=VerificationResult)
async def verify_task_status(task_id: str = Query(...)):
    """
    Retrieves verification status and completion token for an active task.
    """
    return pipeline_service.verification_service.get_verification(task_id)


@router.post("/verification/check", response_model=VerificationResult)
async def run_detailed_verification_check(req: VerificationCheckRequest):
    """
    Executes explicit verification check across completed fields against required schemas.
    """
    return pipeline_service.verification_service.verify_form_task(
        task_id=req.task_id,
        total_fields=req.total_fields,
        completed_fields=req.completed_fields,
        required_field_ids=req.required_field_ids,
    )
