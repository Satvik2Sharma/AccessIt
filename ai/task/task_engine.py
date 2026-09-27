"""
Sahayak AI — Enhanced Task Engine
Maintains active tasks, step state machine, sub-task decomposition, and progress tracking.
"""

import uuid
from typing import Dict, Optional, List, Any
from shared.schemas.models import TaskType, TaskStep, AccessibleTaskFlow


class TaskEngine:
    def __init__(self):
        # In-memory session task store
        self._tasks: Dict[str, Dict[str, Any]] = {}

    def create_form_task(self, total_fields: int = 7) -> str:
        """Creates a form completion task (Hackathon Demo 2)."""
        task_id = f"task_form_{uuid.uuid4().hex[:8]}"
        self._tasks[task_id] = {
            "id": task_id,
            "type": TaskType.FORM_COMPLETION,
            "title": "Application Form Completion",
            "total_fields": total_fields,
            "completed_fields": 0,
            "fields": {},
            "status": "IN_PROGRESS",
        }
        return task_id

    def create_generic_task(
        self,
        task_type: TaskType,
        title: str,
        total_steps: int = 1,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Creates a generic accessibility task (document comprehension, search, etc.)."""
        prefix = task_type.value.lower()
        task_id = f"task_{prefix}_{uuid.uuid4().hex[:8]}"
        self._tasks[task_id] = {
            "id": task_id,
            "type": task_type,
            "title": title,
            "total_steps": total_steps,
            "completed_steps": 0,
            "current_step": 0,
            "status": "IN_PROGRESS",
            "metadata": metadata or {},
            "history": [],
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
                "title": "Application Form",
                "total_fields": 7,
                "completed_fields": 0,
                "fields": {},
                "status": "IN_PROGRESS",
            }
            self._tasks[task_id] = task

        is_new = field_id not in task.get("fields", {})
        if "fields" not in task:
            task["fields"] = {}

        task["fields"][field_id] = {
            "value": value,
            "confirmed": confirmed,
            "valid": True,
        }
        if is_new:
            task["completed_fields"] = len(task["fields"])

        if task["completed_fields"] >= task.get("total_fields", 7):
            task["status"] = "COMPLETED"

        return task

    def advance_step(
        self,
        task_id: str,
        step_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Advances a multi-step task to the next step."""
        task = self.get_task(task_id)
        if not task:
            raise ValueError(f"Task with ID {task_id} not found.")

        task["completed_steps"] = task.get("completed_steps", 0) + 1
        task["current_step"] = task["completed_steps"]
        if step_data:
            task.setdefault("history", []).append(step_data)

        if task["completed_steps"] >= task.get("total_steps", 1):
            task["status"] = "COMPLETED"

        return task

    def decompose_task(self, query: str, task_type: TaskType) -> List[Dict[str, Any]]:
        """
        Decomposes complex requests into discrete accessible milestones.
        """
        if task_type == TaskType.UNDERSTAND_DOCUMENT:
            return [
                {"step": 1, "action": "OCR_SCAN", "label": "Scan or upload document"},
                {"step": 2, "action": "EXTRACT_KEY_FACTS", "label": "Extract critical deadlines & eligibility"},
                {"step": 3, "action": "SIMPLIFIED_SUMMARY", "label": "Read aloud simplified summary in preferred language"},
            ]
        elif task_type == TaskType.FIND_OBJECT:
            return [
                {"step": 1, "action": "CAMERA_FEED", "label": "Aim camera towards area of interest"},
                {"step": 2, "action": "OBJECT_LOCALIZATION", "label": "Detect target object bounding box"},
                {"step": 3, "action": "DIRECTIONAL_CUE", "label": "Provide clock-face audio & haptic guidance"},
            ]
        elif task_type == TaskType.COMMUNICATE:
            return [
                {"step": 1, "action": "GESTURE_TRACKING", "label": "Track 21 3D hand landmarks"},
                {"step": 2, "action": "SIGN_CLASSIFICATION", "label": "Identify ISL sign"},
                {"step": 3, "action": "MULTIMODAL_OUTPUT", "label": "Speak translation and trigger tactile alert"},
            ]
        else:
            return [
                {"step": 1, "action": "EXECUTE", "label": f"Execute {task_type.value}"}
            ]

    def get_task(self, task_id: str) -> Optional[Dict[str, Any]]:
        return self._tasks.get(task_id)
