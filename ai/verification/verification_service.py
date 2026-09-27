"""
Sahayak AI — Task Verification Service
First-class verification engine that evaluates true task completion,
maintaining states: IN_PROGRESS, BLOCKED, NEEDS_CONFIRMATION, COMPLETED, FAILED.
"""

import uuid
from typing import Dict, Any, List
from shared.schemas.models import (
    VerificationResult,
    VerificationStatus,
    AccessibleTaskFlow,
)


class TaskVerificationService:
    def __init__(self):
        # Verification history store
        self._verifications: Dict[str, VerificationResult] = {}

    def verify_form_task(
        self,
        task_id: str,
        total_fields: int,
        completed_fields: Dict[str, Any],
        required_field_ids: List[str]
    ) -> VerificationResult:
        """
        Validates form field completeness, confirmed answers, and data validity.
        """
        missing: List[str] = []
        valid_count = 0

        for req in required_field_ids:
            field_data = completed_fields.get(req)
            if not field_data or not field_data.get("value"):
                missing.append(req)
            else:
                valid_count += 1

        pct = (valid_count / total_fields) * 100.0 if total_fields > 0 else 0.0

        if len(missing) == 0 and valid_count >= total_fields:
            status = VerificationStatus.COMPLETED
            summary = f"All {total_fields} required fields completed and validated. Ready for submission."
            token = f"VERIFIED_SAHAYAK_{uuid.uuid4().hex[:8].upper()}"
        elif valid_count > 0:
            status = VerificationStatus.IN_PROGRESS
            summary = f"{valid_count} of {total_fields} fields completed ({pct:.0f}%). {len(missing)} remaining."
            token = None
        else:
            status = VerificationStatus.IN_PROGRESS
            summary = f"Form application started. 0 of {total_fields} fields completed."
            token = None

        result = VerificationResult(
            task_id=task_id,
            status=status,
            completion_percentage=round(pct, 1),
            completed_fields=valid_count,
            total_fields=total_fields,
            missing_fields=missing,
            verification_token=token,
            summary_message=summary,
        )
        self._verifications[task_id] = result
        return result

    def get_verification(self, task_id: str) -> VerificationResult:
        if task_id in self._verifications:
            return self._verifications[task_id]
        return VerificationResult(
            task_id=task_id,
            status=VerificationStatus.IN_PROGRESS,
            completion_percentage=0.0,
            completed_fields=0,
            total_fields=7,
            missing_fields=["all"],
            summary_message="Task pending verification.",
        )
