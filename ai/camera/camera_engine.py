"""
Sahayak AI — Central Camera Intelligence Engine
Orchestrates camera frame preprocessing, quality validation, intelligent capability routing,
and multimodal result synthesis across OCR, Spatial Vision, ISL, Navigation, and Scene Fusion.
"""

import time
import logging
from typing import Union, Optional, Dict, Any, List
from PIL import Image
import numpy as np

logger = logging.getLogger(__name__)

from shared.schemas.models import (
    AccessibilityTwin,
    TaskType,
    LanguagePreference,
    SpatialObject,
)
from shared.schemas.camera_models import (
    CameraMode,
    CameraAnalysisRequest,
    CameraAnalysisResult,
    FrameQualityMetrics,
)
from ai.camera.image_preprocessor import ImagePreprocessor
from ai.camera.frame_processor import FrameProcessor
from ai.camera.camera_session import camera_session_manager, CameraSession
from ai.camera.camera_analyzer import CameraAnalyzer

from ai.assistance.assistance_engine import AccessibilityAssistanceEngine
from ai.scene.scene_understanding import SceneUnderstandingEngine
from ai.navigation.navigation_engine import NavigationEngine
from ai.recovery.failure_detector import FailureDetector
from ai.recovery.recovery_engine import RecoveryEngine
from ai.accessibility.twin import AccessibilityTwinService


class CameraEngine:
    """
    Unified entry point for device camera streams and snapshot analysis.
    Validates frame quality, skips redundant duplicate frames, routes to
    specialized AI subsystems, and formats accessible multimodal feedback.
    """

    def __init__(
        self,
        frame_processor: Optional[FrameProcessor] = None,
        camera_analyzer: Optional[CameraAnalyzer] = None,
        assistance_engine: Optional[AccessibilityAssistanceEngine] = None,
        scene_engine: Optional[SceneUnderstandingEngine] = None,
        navigation_engine: Optional[NavigationEngine] = None,
        failure_detector: Optional[FailureDetector] = None,
        recovery_engine: Optional[RecoveryEngine] = None,
        twin_service: Optional[AccessibilityTwinService] = None,
    ):
        self.preprocessor = ImagePreprocessor()
        self.frame_processor = frame_processor or FrameProcessor()
        self.analyzer = camera_analyzer or CameraAnalyzer()
        self.assistance_engine = assistance_engine or AccessibilityAssistanceEngine()
        self.scene_engine = scene_engine or SceneUnderstandingEngine()
        self.navigation_engine = navigation_engine or NavigationEngine()
        self.failure_detector = failure_detector or FailureDetector()
        self.recovery_engine = recovery_engine or RecoveryEngine()
        self.twin_service = twin_service or AccessibilityTwinService()

    def analyze(
        self,
        image_input: Union[bytes, str, Image.Image, np.ndarray],
        mode: Union[str, CameraMode] = CameraMode.AUTO,
        query: Optional[str] = None,
        twin_id: str = "default_user",
        session_id: Optional[str] = None,
        target_object: Optional[str] = None,
        skip_duplicate_check: bool = False,
    ) -> CameraAnalysisResult:
        """
        Main camera intelligence processing pipeline.

        Args:
            image_input: bytes, PIL Image, numpy array, or base64 string
            mode: 'auto', 'document', 'see', 'scene', 'isl', 'navigation', 'form'
            query: optional natural language intent
            twin_id: accessibility user profile identifier
            session_id: optional persistent stream session ID
            target_object: optional label for find_object / see mode
            skip_duplicate_check: force processing even if frame hasn't changed

        Returns:
            CameraAnalysisResult with structured multimodal responses
        """
        start_time = time.time()
        user_id = twin_id or "default_user"
        twin = self.twin_service.get_twin(user_id)
        session = camera_session_manager.get_or_create(session_id)
        is_hindi = twin.language == LanguagePreference.HINDI

        # 1. Load and normalize image
        try:
            image = self.preprocessor.load_image(image_input)
            image = self.preprocessor.normalize_rotation(image)
        except Exception as e:
            logger.warning("Camera image loading error: %s", e)
            return CameraAnalysisResult(
                mode_executed=str(mode),
                status="ERROR",
                primary_interpretation="Invalid image input.",
                spoken_feedback="कैमरा इमेज लोड नहीं हो सकी।" if is_hindi else "Unable to load camera image.",
                display_feedback="Failed to parse camera input.",
                recovery_action={"type": "invalid_input", "instruction": "Check camera feed and try again."},
                processing_time_ms=round((time.time() - start_time) * 1000, 2),
            )

        # 2. Quality assessment
        quality = self.frame_processor.assess_quality(image)
        if not quality.is_valid:
            rec = quality.recommendation or "Camera resolution is too low."
            return CameraAnalysisResult(
                mode_executed=str(mode),
                status="DEGRADED",
                quality=quality,
                primary_interpretation="Low quality frame.",
                spoken_feedback="कैमरा इमेज बहुत कम रिज़ॉल्यूशन की है।" if is_hindi else rec,
                display_feedback=rec,
                recovery_action=self.recovery_engine.recover({"type": "ocr_low_confidence"}).model_dump(),
                processing_time_ms=round((time.time() - start_time) * 1000, 2),
            )

        # 3. Duplicate frame check
        frame_hash = self.frame_processor.compute_perceptual_hash(image)
        if not skip_duplicate_check and session.is_duplicate(frame_hash) and session.last_analysis_result:
            cached = session.last_analysis_result.copy()
            cached["status"] = "SKIPPED_DUPLICATE"
            cached["processing_time_ms"] = round((time.time() - start_time) * 1000, 2)
            return CameraAnalysisResult(**cached)

        session.record_frame(frame_hash)

        # 4. Capability planning
        plan = self.analyzer.plan_capabilities(
            mode=mode,
            query=query,
            twin=twin,
            target_object=target_object,
        )
        effective_mode = plan["effective_mode"]
        session.set_mode(effective_mode)

        # Convert image to bytes for downstream modules that expect bytes
        image_bytes = self.preprocessor.to_bytes(image)

        # 5. Route to AI subsystems based on planned capability
        result_dict: Dict[str, Any] = {
            "mode_executed": effective_mode,
            "status": "SUCCESS",
            "quality": quality,
            "primary_interpretation": "",
            "spoken_feedback": "",
            "display_feedback": "",
            "haptic_cue": None,
            "document_data": None,
            "spatial_objects": [],
            "scene_summary": None,
            "navigation_instructions": [],
            "isl_prediction": None,
            "recovery_action": None,
        }

        # A. DOCUMENT UNDERSTANDING
        if effective_mode == "document":
            doc_data = self.assistance_engine.assist_understand_document(image_bytes, query or "explain notice", twin)
            result_dict["document_data"] = doc_data
            result_dict["primary_interpretation"] = doc_data.get("title", "Document")
            result_dict["spoken_feedback"] = doc_data.get("spoken_summary", "")
            result_dict["display_feedback"] = doc_data.get("display_summary", "")
            result_dict["haptic_cue"] = doc_data.get("haptic_cue")

            failure = self.failure_detector.check_ocr(doc_data)
            if failure:
                result_dict["status"] = "RECOVERY_REQUIRED"
                result_dict["recovery_action"] = self.recovery_engine.recover(failure).model_dump()

        # B. FORM COMPLETION
        elif effective_mode == "form":
            doc_data = self.assistance_engine.assist_understand_document(image_bytes, query or "fill form", twin)
            result_dict["document_data"] = doc_data
            result_dict["primary_interpretation"] = f"Form: {doc_data.get('title', 'Application')}"
            result_dict["spoken_feedback"] = (
                "फ़ॉर्म मिला। भरने के लिए चरण 1 पर जाएं।" if is_hindi
                else "Form detected. Proceeding with accessible step-by-step assistance."
            )
            result_dict["display_feedback"] = "Form fields detected. Ready to complete."
            result_dict["haptic_cue"] = "DOUBLE_PULSE_CENTER"

        # C. SEE / TARGET OBJECT SEARCH
        elif effective_mode == "see":
            target = plan.get("target_object") or target_object
            scene = self.scene_engine.analyze(
                image_bytes=image_bytes,
                twin=twin,
                task_type=TaskType.SEE,
                target_labels=[target] if target else None,
            )
            result_dict["scene_summary"] = scene.summary
            result_dict["spatial_objects"] = [
                {
                    "label": obj.label,
                    "confidence": obj.confidence,
                    "clock_direction": obj.direction,
                    "relative_direction": obj.horizontal_zone,
                    "proximity": obj.proximity,
                    "elevation": obj.elevation,
                    "haptic_cue": obj.haptic_cue,
                    "associated_text": obj.associated_text,
                    "bbox": obj.bbox,
                }
                for obj in scene.objects
            ]
            if scene.objects:
                primary = scene.relevant_objects[0] if scene.relevant_objects else scene.objects[0]
                result_dict["primary_interpretation"] = f"{primary.label} detected ({primary.direction})"
                result_dict["spoken_feedback"] = scene.summary or f"{primary.label} at {primary.direction}"
                result_dict["display_feedback"] = scene.summary or f"{primary.label} at {primary.direction}"
                result_dict["haptic_cue"] = primary.haptic_cue
            else:
                result_dict["primary_interpretation"] = "No objects detected in view"
                result_dict["spoken_feedback"] = (
                    "दृश्य में कोई स्पष्ट वस्तु नहीं मिली।" if is_hindi
                    else "No objects clearly identified in view. Please move closer or adjust camera."
                )
                result_dict["display_feedback"] = "No objects detected in camera view."
                result_dict["haptic_cue"] = "NONE"

        # D. NAVIGATION
        elif effective_mode == "navigation":
            nav_data = self.navigation_engine.navigate(image_bytes=image_bytes, target_label=target_object, twin=twin)
            result_dict["navigation_instructions"] = nav_data.get("instructions", [])
            result_dict["scene_summary"] = nav_data.get("scene_summary")
            result_dict["primary_interpretation"] = nav_data.get("scene_summary", "Navigation route evaluated")

            instructions = nav_data.get("instructions", [])
            if instructions:
                first = instructions[0]
                result_dict["spoken_feedback"] = first.get("description_hi" if is_hindi else "description", "")
                result_dict["display_feedback"] = first.get("description", "")
                result_dict["haptic_cue"] = first.get("haptic_cue")
            else:
                result_dict["spoken_feedback"] = "रास्ता साफ है।" if is_hindi else "Path clear."
                result_dict["display_feedback"] = "Path clear."

        # E. ISL GESTURE
        elif effective_mode == "isl":
            isl_pred = self.assistance_engine.assist_sign_communication(image_bytes, twin)
            result_dict["isl_prediction"] = isl_pred
            sign = isl_pred.get("sign", "SEARCHING")
            result_dict["primary_interpretation"] = f"ISL Sign: {sign}"
            result_dict["spoken_feedback"] = isl_pred.get("spoken", sign)
            result_dict["display_feedback"] = f"Detected Sign: {sign} ({isl_pred.get('confidence', 0.0):.0%})"
            result_dict["haptic_cue"] = "SUCCESS_DOUBLE_PULSE" if sign != "SEARCHING" else "SINGLE_PULSE"

            failure = self.failure_detector.check_isl(isl_pred)
            if failure:
                result_dict["status"] = "RECOVERY_REQUIRED"
                result_dict["recovery_action"] = self.recovery_engine.recover(failure).model_dump()

        # F. SCENE UNDERSTANDING (DEFAULT)
        else:
            scene = self.scene_engine.analyze(
                image_bytes=image_bytes,
                twin=twin,
                task_type=TaskType.SEE,
                target_labels=[target_object] if target_object else None
            )
            result_dict["scene_summary"] = scene.summary
            result_dict["primary_interpretation"] = scene.summary or "Scene analyzed"
            result_dict["spoken_feedback"] = scene.summary or "Room analyzed"
            result_dict["display_feedback"] = scene.summary or "Scene analyzed"
            result_dict["spatial_objects"] = [o.model_dump() for o in scene.objects]
            result_dict["haptic_cue"] = "DOUBLE_PULSE_CENTER"

        result_dict["processing_time_ms"] = round((time.time() - start_time) * 1000, 2)

        # Cache result in session
        session.last_analysis_result = result_dict.copy()

        return CameraAnalysisResult(**result_dict)
