"""
Sahayak AI — Navigation Engine
Orchestrates scene analysis → obstacle detection → guidance generation.
Provides camera-based LOCAL navigation only (not GPS/map).
"""
from typing import Optional, List, Dict, Any
from shared.schemas.models import (
    NavigationInstruction, SceneAnalysis, AccessibilityTwin, TaskType
)
from ai.scene.scene_understanding import SceneUnderstandingEngine
from ai.navigation.guidance_engine import GuidanceEngine


class NavigationEngine:
    """
    Full local navigation pipeline:
    Camera Frame → Scene Analysis → Obstacle Detection → Guidance Instructions.

    IMPORTANT: Provides camera-based local scene guidance only.
    Does NOT claim GPS, map accuracy, or outdoor route navigation.
    """

    def __init__(self, vision_provider: str = "heuristic"):
        self.scene_engine = SceneUnderstandingEngine(provider=vision_provider)
        self.guidance_engine = GuidanceEngine()

    def navigate(
        self,
        image_bytes: Optional[bytes] = None,
        target_label: Optional[str] = None,
        twin: Optional[AccessibilityTwin] = None,
    ) -> Dict[str, Any]:
        """
        Generate navigation guidance from a camera frame.

        Args:
            image_bytes: raw camera frame bytes
            target_label: object to navigate toward (optional)
            twin: Accessibility Twin

        Returns:
            dict with scene_summary, instructions, and obstacle_count
        """
        target_list = [target_label] if target_label else None
        scene = self.scene_engine.analyze(
            image_bytes=image_bytes,
            twin=twin,
            task_type=TaskType.FIND_OBJECT,
            target_labels=target_list,
        )

        instructions = self.guidance_engine.guide(
            objects=scene.objects,
            target_label=target_label,
            twin=twin,
        )

        return {
            "scene_summary": scene.summary,
            "objects_detected": len(scene.objects),
            "instructions": [i.model_dump() for i in instructions],
            "obstacle_count": len(scene.hazards),
            "hazards": scene.hazards,
            "disclaimer": "Local camera-based guidance only. Not GPS navigation.",
        }
