"""
Sahayak AI — Form Completion Schema Models
Defines structured data contracts for Form Analysis, Step Compilation,
Semantic Field Validation, and Form Progress State.
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from shared.schemas.models import VerificationResult, TaskStep


class FormFieldAnalysis(BaseModel):
    field_id: str
    label: str
    field_type: str = "text"
    is_required: bool = True
    bounding_box: Optional[List[int]] = None
    extracted_value: Optional[str] = None


class FormRespondRequest(BaseModel):
    task_id: str
    field_id: str
    value: str
    confirmation_received: bool = True
    twin_id: Optional[str] = "default_user"


class FormRespondResponse(BaseModel):
    task_id: str
    completed_field: str
    is_valid: bool
    validation_message: Optional[str] = None
    completed_fields_count: int
    total_fields: int
    verification: Optional[VerificationResult] = None
    next_step: Optional[TaskStep] = None
    is_complete: bool
