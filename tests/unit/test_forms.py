"""
Unit Tests for Form Completion Models & Verification
"""

import sys
import os

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from shared.schemas.models import (
    FormRespondRequest,
    VerificationStatus,
)
from ai.verification.verification_service import TaskVerificationService
from ai.task.task_engine import TaskEngine


def test_form_field_validation():
    verif = TaskVerificationService()

    # Valid name
    v1, msg1 = verif.validate_field("full_name", "Rahul Kumar")
    assert v1 is True

    # Invalid empty name
    v2, msg2 = verif.validate_field("full_name", "")
    assert v2 is False

    # Valid Aadhaar
    v3, _ = verif.validate_field("aadhaar", "123456789012")
    assert v3 is True

    # Invalid Aadhaar
    v4, _ = verif.validate_field("aadhaar", "123")
    assert v4 is False


def test_form_verification_aggregation():
    verif = TaskVerificationService()
    task_id = "task_form_test_01"
    required = ["full_name", "dob", "address", "category", "annual_income", "aadhaar", "bank_account"]

    # Initial empty verification
    res1 = verif.verify_form_task(task_id, 7, {}, required)
    assert res1.status == VerificationStatus.IN_PROGRESS
    assert res1.completed_fields == 0

    # Partial fields
    partial = {
        "full_name": {"value": "Rahul", "confirmed": True},
        "dob": {"value": "12/04/2002", "confirmed": True}
    }
    res2 = verif.verify_form_task(task_id, 7, partial, required)
    assert res2.status == VerificationStatus.IN_PROGRESS
    assert res2.completed_fields == 2

    # All completed valid fields
    valid_answers = {
        "full_name": "Varanka Tyagi",
        "dob": "15/08/2003",
        "address": "Block C, Green Park, New Delhi",
        "category": "General",
        "annual_income": "180000",
        "aadhaar": "987654321098",
        "bank_account": "12345678901234",
    }
    all_fields = {k: {"value": v, "confirmed": True} for k, v in valid_answers.items()}
    res3 = verif.verify_form_task(task_id, 7, all_fields, required)
    assert res3.status == VerificationStatus.COMPLETED
    assert res3.completion_percentage == 100.0
    assert res3.verification_token is not None


if __name__ == "__main__":
    test_form_field_validation()
    test_form_verification_aggregation()
    print("All unit/test_forms.py tests passed!")
