"""
Sahayak AI — Task Engine
Maintains active tasks, field state machine, and progress progression.
"""

import uuid
from typing import Dict, Optional, List, Any
from shared.schemas.models import TaskType, TaskStep, AccessibleTaskFlow


class TaskEngine:
    def __init__(self):
        # In-memory session task store
        self._tasks: Dict[str, Dict[str, Any]] = {}

    def create_form_task(self, total_fields: int = 7) -> str:
        task_id = f"task_form_{uuid.uuid4().hex[:8]}"
        self._tasks[task_id] = {
            "id": task_id,
            "type": TaskType.FORM_COMPLETION,
            "total_fields": total_fields,
            "completed_fields": 0,
            "fields": {},
            "status": "IN_PROGRESS",
        }
        return task_id

    def update_field(
        self,
        task_id: str,
        field_id: str,
        value: str,
        confirmed: bool = True
    ) -> Dict[str, Any]:
        task = self._tasks.get(task_id)
        if not task:
            task = {
                "id": task_id,
                "type": TaskType.FORM_COMPLETION,
                "total_fields": 7,
                "completed_fields": 0,
                "fields": {},
                "status": "IN_PROGRESS",
            }
            self._tasks[task_id] = task

        is_new = field_id not in task["fields"]
        task["fields"][field_id] = {
            "value": value,
            "confirmed": confirmed,
            "valid": True,
        }
        if is_new:
            task["completed_fields"] = len(task["fields"])

        if task["completed_fields"] >= task["total_fields"]:
            task["status"] = "COMPLETED"

        return task

    def get_task(self, task_id: str) -> Optional[Dict[str, Any]]:
        return self._tasks.get(task_id)
