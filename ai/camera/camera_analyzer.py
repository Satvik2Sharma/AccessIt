"""
Sahayak AI — Camera Capability Analyzer
Intelligently determines which downstream AI perception models are required
based on camera mode, natural language query, intent classification, and Accessibility Twin.
Ensures lightweight execution by running only task-relevant models.
"""

from typing import Dict, Any, List, Optional
from shared.schemas.models import AccessibilityTwin, TaskType, LanguagePreference
from shared.schemas.camera_models import CameraMode
from ai.intent.intent_engine import IntentEngine


class CameraAnalyzer:
    """
    Decides the minimal set of AI models (OCR, YOLO/Detector, ISL, Navigation,
    Scene Fusion) needed for a camera frame request.
    """

    def __init__(self, intent_engine: Optional[IntentEngine] = None):
        self.intent_engine = intent_engine or IntentEngine()

    def plan_capabilities(
        self,
        mode: Union[str, CameraMode] = CameraMode.AUTO,
        query: Optional[str] = None,
        twin: Optional[AccessibilityTwin] = None,
        target_object: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Determines the optimal capability pipeline to execute.

        Returns:
            Dict containing:
                effective_mode: str
                task_type: TaskType
                required_capabilities: List[str]
                target_object: Optional[str]
                rationale: str
        """
        mode_str = mode.value if isinstance(mode, CameraMode) else str(mode).lower()

        # 1. If explicit mode is not AUTO, route directly
        if mode_str != "auto":
            return self._plan_for_explicit_mode(mode_str, target_object, twin)

        # 2. If query is provided, route through Intent Engine
        if query and query.strip():
            intent_data = self.intent_engine.analyze_intent(query.strip(), twin=twin)
            tt = intent_data.get("task_type")
            if isinstance(tt, TaskType):
                task_type = tt
            elif isinstance(tt, str):
                try:
                    task_type = TaskType(tt)
                except ValueError:
                    task_type = TaskType.SEE
            else:
                task_type = TaskType.SEE

            return self._plan_for_task_type(task_type, query, target_object, twin)

        # 3. Default to Accessibility Twin primary preference if no query and auto mode
        if twin and twin.hearing.sign_language:
            return {
                "effective_mode": "isl",
                "task_type": TaskType.COMMUNICATE,
                "required_capabilities": ["isl_gesture"],
                "target_object": None,
                "rationale": "Auto-selected ISL based on twin hearing preference.",
            }

        # 4. Standard default: environmental scene overview
        return {
            "effective_mode": "scene",
            "task_type": TaskType.SEE,
            "required_capabilities": ["object_detection", "ocr", "scene_fusion"],
            "target_object": target_object,
            "rationale": "Default exploratory scene understanding.",
        }

    def _plan_for_explicit_mode(
        self,
        mode_str: str,
        target_object: Optional[str],
        twin: Optional[AccessibilityTwin]
    ) -> Dict[str, Any]:
        if mode_str == "document":
            return {
                "effective_mode": "document",
                "task_type": TaskType.UNDERSTAND_DOCUMENT,
                "required_capabilities": ["ocr", "document_summary"],
                "target_object": None,
                "rationale": "Explicit document reading requested.",
            }
        elif mode_str == "form":
            return {
                "effective_mode": "form",
                "task_type": TaskType.FORM_COMPLETION,
                "required_capabilities": ["ocr", "form_fields", "flow_compiler"],
                "target_object": None,
                "rationale": "Explicit form completion requested.",
            }
        elif mode_str == "see":
            return {
                "effective_mode": "see",
                "task_type": TaskType.FIND_OBJECT,
                "required_capabilities": ["object_detection", "spatial_guidance"],
                "target_object": target_object or "object",
                "rationale": "Targeted object search and clock-direction guidance.",
            }
        elif mode_str == "navigation":
            return {
                "effective_mode": "navigation",
                "task_type": TaskType.SEE,
                "required_capabilities": ["object_detection", "obstacle_detection", "navigation_guidance"],
                "target_object": target_object,
                "rationale": "Local camera-based navigation and obstacle warning.",
            }
        elif mode_str == "isl":
            return {
                "effective_mode": "isl",
                "task_type": TaskType.COMMUNICATE,
                "required_capabilities": ["isl_gesture"],
                "target_object": None,
                "rationale": "Indian Sign Language gesture recognition.",
            }
        elif mode_str == "scene":
            return {
                "effective_mode": "scene",
                "task_type": TaskType.SEE,
                "required_capabilities": ["object_detection", "ocr", "scene_fusion"],
                "target_object": target_object,
                "rationale": "Comprehensive scene understanding requested.",
            }
        else:
            return {
                "effective_mode": "scene",
                "task_type": TaskType.SEE,
                "required_capabilities": ["object_detection", "scene_fusion"],
                "target_object": target_object,
                "rationale": f"Unrecognized mode '{mode_str}', falling back to scene.",
            }

    def _plan_for_task_type(
        self,
        task_type: TaskType,
        query: str,
        target_object: Optional[str],
        twin: Optional[AccessibilityTwin]
    ) -> Dict[str, Any]:
        if task_type in (TaskType.UNDERSTAND_DOCUMENT, TaskType.READ):
            return {
                "effective_mode": "document",
                "task_type": task_type,
                "required_capabilities": ["ocr", "document_summary"],
                "target_object": None,
                "rationale": f"Query '{query}' classified as document understanding.",
            }
        elif task_type == TaskType.FORM_COMPLETION:
            return {
                "effective_mode": "form",
                "task_type": task_type,
                "required_capabilities": ["ocr", "form_fields", "flow_compiler"],
                "target_object": None,
                "rationale": f"Query '{query}' classified as form completion.",
            }
        elif task_type == TaskType.FIND_OBJECT:
            # Extract target object keyword from query if not explicitly passed
            extracted_target = target_object
            if not extracted_target:
                lower = query.lower()
                for obj in ["bottle", "medicine", "keys", "wallet", "glasses", "water", "phone"]:
                    if obj in lower:
                        extracted_target = obj
                        break
            return {
                "effective_mode": "see",
                "task_type": task_type,
                "required_capabilities": ["object_detection", "spatial_guidance"],
                "target_object": extracted_target or "object",
                "rationale": f"Query '{query}' classified as object search.",
            }
        elif task_type == TaskType.COMMUNICATE:
            return {
                "effective_mode": "isl",
                "task_type": task_type,
                "required_capabilities": ["isl_gesture"],
                "target_object": None,
                "rationale": f"Query '{query}' classified as sign communication.",
            }
        else:
            return {
                "effective_mode": "scene",
                "task_type": TaskType.SEE,
                "required_capabilities": ["object_detection", "ocr", "scene_fusion"],
                "target_object": target_object,
                "rationale": f"Query '{query}' classified as general visual query.",
            }
