"""
Sahayak AI — Document-to-Task Generator
Converts extracted document information into actionable TaskEngine tasks.
Integrates with the existing TaskEngine — does NOT create a second task system.
"""
from typing import Dict, Any, Optional, List
from ai.task.task_engine import TaskEngine
from shared.schemas.models import TaskType


class DocumentTaskGenerator:
    """
    Converts extracted document data (from OCR engine) into structured tasks
    by delegating to the existing TaskEngine.
    """

    def __init__(self, task_engine: Optional[TaskEngine] = None):
        self.task_engine = task_engine or TaskEngine()

    def generate_from_document(
        self,
        doc_info: Dict[str, Any],
        twin_id: str = "default_user",
    ) -> Dict[str, Any]:
        """
        Convert extracted document data into a structured task.

        Args:
            doc_info: result from DocumentOCREngine.extract_document_info()
            twin_id: user twin identifier

        Returns:
            dict with task_id, title, deadlines, required_actions, milestones
        """
        title = doc_info.get("document_title", "Document Task")
        deadlines = doc_info.get("key_deadlines", [])
        required_docs = doc_info.get("required_documents", [])
        action_items = doc_info.get("action_items", [])

        # Create a generic task via the existing TaskEngine
        task_id = self.task_engine.create_generic_task(
            task_type=TaskType.UNDERSTAND_DOCUMENT,
            title=f"Complete requirements for: {title}",
            metadata={
                "document_title": title,
                "deadlines": deadlines,
                "required_documents": required_docs,
            },
        )
        task = self.task_engine.get_task(task_id)

        # Decompose into milestones via existing TaskEngine
        milestones = self.task_engine.decompose_task(
            query="Analyze document",
            task_type=TaskType.UNDERSTAND_DOCUMENT,
        )

        return {
            "task_id": task_id,
            "title": title,
            "deadlines": deadlines,
            "required_documents": required_docs,
            "action_items": action_items,
            "milestones": milestones,
            "source": "document",
            "task_type": TaskType.UNDERSTAND_DOCUMENT.value,
            "status": task["status"] if task else "IN_PROGRESS",
        }

    def generate_submission_task(
        self,
        doc_info: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Create a form submission task from a document with application fields.
        Delegates to the existing TaskEngine form flow.
        """
        title = doc_info.get("document_title", "Application Form")
        deadlines = doc_info.get("key_deadlines", [])

        task_id = self.task_engine.create_form_task()
        task = self.task_engine.get_task(task_id)
        return {
            "task_id": task_id,
            "title": f"Submit: {title}",
            "deadline": deadlines[0] if deadlines else "Check document",
            "required_action": "application_submission",
            "source": "document",
            "task_type": TaskType.FORM_COMPLETION.value,
            "status": task["status"] if task else "IN_PROGRESS",
        }
