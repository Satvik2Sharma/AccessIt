"""
Sahayak AI — Scene Understanding Engine
Combines object detection, OCR, spatial analysis and intent-awareness
to produce a structured, task-relevant scene representation.
"""
import logging
from typing import List, Optional, Dict, Any, Tuple, Union
from shared.schemas.models import (
    SpatialObject, SceneAnalysis, AccessibilityTwin, TaskType, LanguagePreference
)
from ai.vision.object_detector import ObjectDetectorAdapter
from ai.vision.clock_direction import ClockDirectionMapper
from ai.vision.elevation_estimator import ElevationEstimator
from ai.vision.proximity_estimator import ProximityEstimator
from ai.ocr.ocr_engine import DocumentOCREngine

logger = logging.getLogger(__name__)


class SceneUnderstandingEngine:
    """
    Orchestrates object detection + OCR + spatial analysis to build
    a structured SceneAnalysis grounded in the user's current task/intent.
    """

    def __init__(self, provider: str = "heuristic"):
        self.detector = ObjectDetectorAdapter(provider=provider)
        self.clock_mapper = ClockDirectionMapper()
        self.elevation_estimator = ElevationEstimator()
        self.proximity_estimator = ProximityEstimator()
        self.ocr_engine = DocumentOCREngine()

    def analyze(
        self,
        image_bytes: Optional[bytes] = None,
        twin: Optional[AccessibilityTwin] = None,
        task_type: Optional[TaskType] = None,
        target_labels: Optional[List[str]] = None,
    ) -> SceneAnalysis:
        """
        Produce a full SceneAnalysis from camera image.

        Args:
            image_bytes: raw JPEG/PNG frame bytes
            twin: user Accessibility Twin for language and preference targeting
            task_type: current task to prioritize relevant objects
            target_labels: optional list of object labels to focus on

        Returns:
            SceneAnalysis with structured objects, text, hazards, and spatial metadata
        """
        is_hindi = twin and twin.language == LanguagePreference.HINDI

        # 1. Detect objects
        raw_detections = self.detector.detect(image_bytes, target_labels=target_labels)

        # 2. Extract text via OCR
        ocr_elements = []
        text_regions: List[str] = []
        if image_bytes:
            try:
                ocr_elements = self.ocr_engine.ocr_image(image_bytes)
                text_regions = [el["text"] for el in ocr_elements if len(el.get("text", "")) > 1]
            except Exception as exc:
                logger.warning("OCR extraction failed during scene analysis: %s", exc)
                text_regions = []

        # 3. Build SpatialObject for each detection
        spatial_objects: List[SpatialObject] = []
        for det in raw_detections:
            bbox = det.get("bbox") or [0.1, 0.1, 0.5, 0.8]
            direction_info = self.clock_mapper.from_bbox(tuple(bbox), normalized=True)
            elevation_info = self.elevation_estimator.estimate(tuple(bbox), normalized=True)
            proximity_info = self.proximity_estimator.estimate(tuple(bbox), normalized=True)

            # Associate nearby text
            associated_text = self._associate_text(det["label"], text_regions)

            obj = SpatialObject(
                label=det["label"],
                confidence=det["confidence"],
                bbox=bbox,
                direction=direction_info["direction"],
                horizontal_zone=direction_info["horizontal_zone"],
                elevation=elevation_info["zone"],
                proximity=proximity_info["zone"],
                associated_text=associated_text,
                haptic_cue=proximity_info["haptic_cue"],
            )
            spatial_objects.append(obj)

        # 4. Detect hazards (objects very close and likely obstacles)
        hazards = [
            f"{obj.label} very close ({obj.direction})"
            for obj in spatial_objects
            if obj.proximity == "very_close"
        ]

        # 5. Prioritize relevant objects by task
        relevant = self._prioritize_by_task(spatial_objects, task_type, target_labels)

        # 6. Build spatial relationship descriptions
        relationships = self._describe_relationships(spatial_objects, is_hindi)

        # 7. Summary
        if spatial_objects:
            top = spatial_objects[0]
            if is_hindi:
                summary = f"{top.label} {top.direction} पर है"
            else:
                summary = f"{top.label} detected at {top.direction}"
        else:
            summary = "हिंदी: कोई वस्तु नहीं मिली" if is_hindi else "No objects detected"

        return SceneAnalysis(
            objects=spatial_objects,
            text_regions=text_regions,
            labels=[o.label for o in spatial_objects],
            spatial_relationships=relationships,
            hazards=hazards,
            relevant_objects=relevant,
            confidence=max((o.confidence for o in spatial_objects), default=0.0),
            task_context=task_type.value if task_type else None,
            summary=summary,
        )

    def _associate_text(self, label: str, text_regions: List[str]) -> Optional[str]:
        """Associate a text region with the object label via keyword matching."""
        label_keywords = label.lower().split()
        for text in text_regions:
            tl = text.lower()
            if any(k in tl for k in label_keywords):
                return text
        return None

    def _prioritize_by_task(self, objects: List[SpatialObject], task_type: Optional[TaskType], target_labels: Optional[List[str]]) -> List[SpatialObject]:
        """Filter objects relevant to the current task."""
        if target_labels:
            target_lower = [t.lower() for t in target_labels]
            return [o for o in objects if any(t in o.label.lower() for t in target_lower)]
        if task_type == TaskType.FIND_OBJECT:
            return objects
        if task_type == TaskType.UNDERSTAND_DOCUMENT:
            return [o for o in objects if "document" in o.label.lower() or "paper" in o.label.lower()]
        return objects

    def _describe_relationships(self, objects: List[SpatialObject], is_hindi: bool) -> List[str]:
        """Generate simple relative position descriptions between pairs of objects."""
        if len(objects) < 2:
            return []
        rels = []
        for i, a in enumerate(objects[:3]):
            for b in objects[i+1:4]:
                if is_hindi:
                    rels.append(f"{a.label} और {b.label} दोनों दिख रहे हैं")
                else:
                    rels.append(f"{a.label} and {b.label} both visible")
        return rels
