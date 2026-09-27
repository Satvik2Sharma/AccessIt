"""
Integration Test for Form Completion Pipeline
Simulates: Analyze form image -> receive flow -> submit fields -> verify completion.
"""

import sys
import os

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from shared.schemas.models import (
    AccessibilityTwin,
    FormRespondRequest,
    VerificationStatus,
)
from backend.services.pipeline_service import pipeline_service


def test_form_completion_end_to_end():
    twin = pipeline_service.twin_service.get_twin("default_user")

    # 1. Create task & flow
    task_id = pipeline_service.task_engine.create_form_task(total_fields=7)
    barriers = pipeline_service.barrier_engine.detect_barriers("FORM_COMPLETION", {"total_fields": 7}, twin)
    flow = pipeline_service.flow_compiler.compile_form_flow(task_id, twin, barriers)

    assert flow.total_steps == 7
    assert flow.task_id == task_id

    # 2. Complete each field sequentially
    field_values = {
        "full_name": "Varanka Tyagi",
        "dob": "15/08/2003",
        "address": "Block C, Green Park, New Delhi",
        "category": "General",
        "annual_income": "180000",
        "aadhaar": "987654321098",
        "bank_account": "12345678901234",
    }

    completed_fields_dict = {}
    for step in flow.steps:
        val = field_values[step.field_id]
        is_valid, _ = pipeline_service.verification_service.validate_field(step.field_id, val)
        assert is_valid is True

        pipeline_service.task_engine.update_field(task_id, step.field_id, val, confirmed=True)
        completed_fields_dict[step.field_id] = {"value": val, "confirmed": True, "field_id": step.field_id}

    # 3. Verify Completed Task
    ver_res = pipeline_service.verification_service.verify_form_task(
        task_id=task_id,
        total_fields=7,
        completed_fields=completed_fields_dict,
        required_field_ids=list(field_values.keys()),
    )
    assert ver_res.status == VerificationStatus.COMPLETED
    assert ver_res.completion_percentage == 100.0
    assert len(ver_res.missing_fields) == 0


if __name__ == "__main__":
    test_form_completion_end_to_end()
    print("Integration test_complete_form.py passed successfully!")
