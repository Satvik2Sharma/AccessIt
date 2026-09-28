"""
Sahayak AI — Camera Intelligence Orchestrator Service
Integrates the mobile camera stream with the 7-Stage Intent-Aware Accessibility Pipeline.
Handles frame validation, image preprocessing, session context, selective AI inference,
Object + OCR text fusion, spatial guidance, and multimodal response generation.
"""

import io
import os
import time
import logging
from datetime import datetime
from typing import Dict, Any, Optional, List, Tuple
from PIL import Image, ImageOps

from shared.schemas.models import (
    AccessibilityTwin,
    LanguagePreference,
    AssistancePriority,
    CameraAnalysisMode,
    CameraFrameMetadata,
    CameraObject,
    CameraText,
    CameraObjectTextRelation,
    CameraSceneAnalysis,
    CameraAnalysisResult,
    CameraAssistanceResponse,
    CameraError,
    CameraAnalysisResponse,
    PipelineStage,
    RecoveryStatus,
)
from backend.services.session_service import session_service
from backend.services.response_service import response_service
from backend.services.pipeline_service import pipeline_service

logger = logging.getLogger("sahayak.camera")

SUPPORTED_MIME_TYPES = {
    "image/jpeg",
    "image/jpg",
    "image/png",
    "image/webp",
    "image/bmp",
    "application/octet-stream",  # Raw byte streams from camera
}

SUPPORTED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".bmp"}
MAX_FRAME_SIZE_BYTES = int(os.getenv("MAX_CAMERA_FRAME_SIZE", 15 * 1024 * 1024))  # 15MB


class CameraService:
    def __init__(self):
        self.max_frame_size = MAX_FRAME_SIZE_BYTES

    # ----------------------------------------------------
    # 1. Frame Validation
    # ----------------------------------------------------
    def validate_image_frame(
        self,
        image_bytes: Optional[bytes],
        filename: Optional[str] = None,
        content_type: Optional[str] = None,
    ) -> Tuple[bool, Optional[str], Optional[Tuple[int, int]]]:
        """
        Validates presence, non-zero size, MIME type/extension, and decodability of a camera frame.
        Returns: (is_valid, error_message, (width, height))
        """
        if not image_bytes or len(image_bytes) == 0:
            return False, "Camera frame payload is empty or missing.", None

        if len(image_bytes) > self.max_frame_size:
            max_mb = self.max_frame_size / (1024 * 1024)
            return False, f"Camera frame exceeds maximum size limit of {max_mb:.1f}MB.", None

        if content_type and content_type.lower() not in SUPPORTED_MIME_TYPES:
            # Check filename extension fallback
            if filename:
                ext = os.path.splitext(filename)[1].lower()
                if ext not in SUPPORTED_EXTENSIONS:
                    return False, f"Unsupported image MIME type '{content_type}'.", None
            else:
                return False, f"Unsupported image MIME type '{content_type}'.", None

        # Verify decodability via Pillow
        try:
            with Image.open(io.BytesIO(image_bytes)) as img:
                img.verify()

            # Re-open to read dimensions after verify()
            with Image.open(io.BytesIO(image_bytes)) as img:
                width, height = img.size
                if width <= 0 or height <= 0:
                    return False, "Image has invalid zero or negative dimensions.", None
                return True, None, (width, height)
        except Exception as e:
            return False, f"Corrupted image frame could not be decoded: {str(e)}", None

    # ----------------------------------------------------
    # 2. Frame Preprocessing Interface
    # ----------------------------------------------------
    def preprocess_frame(
        self,
        image_bytes: bytes,
        max_dimension: int = 1280,
        normalize_orientation: bool = True,
        source: str = "BACK_CAMERA"
    ) -> Tuple[bytes, CameraFrameMetadata]:
        """
        Normalizes frame orientation and resizes image if it exceeds max_dimension to optimize inference latency.
        """
        try:
            with Image.open(io.BytesIO(image_bytes)) as img:
                if normalize_orientation:
                    img = ImageOps.exif_transpose(img) or img

                # Convert RGBA / Palette to RGB
                if img.mode != "RGB":
                    img = img.convert("RGB")

                width, height = img.size
                if max(width, height) > max_dimension:
                    img.thumbnail((max_dimension, max_dimension), Image.Resampling.LANCZOS)
                    width, height = img.size

                buf = io.BytesIO()
                img.save(buf, format="JPEG", quality=88)
                processed_bytes = buf.getvalue()

                metadata = CameraFrameMetadata(
                    width=width,
                    height=height,
                    orientation=1,
                    capture_source=source,
                )
                return processed_bytes, metadata
        except Exception as e:
            logger.warning(f"Preprocessing fallback: {e}")
            metadata = CameraFrameMetadata(capture_source=source)
            return image_bytes, metadata

    # ----------------------------------------------------
    # 3. Intent & Mode Resolution
    # ----------------------------------------------------
    def resolve_mode_and_intent(
        self,
        requested_mode: Optional[CameraAnalysisMode] = None,
        intent: Optional[str] = None,
        target_object: Optional[str] = None,
        twin: Optional[AccessibilityTwin] = None
    ) -> Tuple[CameraAnalysisMode, str]:
        """
        Determines the optimal analysis mode based on explicit request or intent query.
        """
        if requested_mode and requested_mode != CameraAnalysisMode.AUTO:
            return requested_mode, intent or f"EXPLICIT_{requested_mode.value}"

        if target_object:
            return CameraAnalysisMode.FIND, intent or f"FIND_{target_object.upper()}"

        if intent:
            intent_lower = intent.lower()
            if any(w in intent_lower for w in ["read", "text", "sign", "notice", "written", "padho", "likha"]):
                return CameraAnalysisMode.READ, intent
            if any(w in intent_lower for w in ["find", "where is", "dhundo", "kahan"]):
                return CameraAnalysisMode.FIND, intent
            if any(w in intent_lower for w in ["navigate", "obstacle", "walk", "rasta", "door", "step"]):
                return CameraAnalysisMode.NAVIGATE, intent
            if any(w in intent_lower for w in ["see", "look", "what is this", "kya hai"]):
                return CameraAnalysisMode.UNDERSTAND, intent

        # Default fallback mode
        return CameraAnalysisMode.UNDERSTAND, intent or "GENERAL_SCENE_UNDERSTANDING"

    # ----------------------------------------------------
    # 4. Primary Orchestration: Analyze Camera Frame
    # ----------------------------------------------------
    def analyze_frame(
        self,
        image_bytes: Optional[bytes],
        session_id: Optional[str] = None,
        twin_id: str = "default_user",
        requested_mode: CameraAnalysisMode = CameraAnalysisMode.AUTO,
        intent: Optional[str] = None,
        target_object: Optional[str] = None,
        language: Optional[str] = None,
        filename: Optional[str] = None,
        content_type: Optional[str] = None,
        skip_duplicate_check: bool = False,
    ) -> CameraAnalysisResponse:
        """
        Main entry point for camera frame intelligence.
        Orchestrates validation, session retrieval, selective AI analysis, fusion, and multimodal response.
        """
        start_time = time.time()
        twin = pipeline_service.twin_service.get_twin(twin_id)
        active_lang = language or twin.language.value
        is_hindi = active_lang.lower() == "hindi" or twin.language == LanguagePreference.HINDI

        # 1. Validate Image Frame
        is_valid, val_error, dimensions = self.validate_image_frame(image_bytes, filename, content_type)
        if not is_valid:
            error = CameraError(
                error_code="INVALID_CAMERA_FRAME",
                stage="FRAME_VALIDATION",
                message=val_error or "Invalid camera frame.",
                retryable=True,
                fallback_used=False,
            )
            empty_analysis = CameraAnalysisResult(
                session_id=session_id or "cam_err",
                mode=requested_mode,
                intent=intent,
                status="FAILED",
            )
            empty_assistance = CameraAssistanceResponse(
                spoken_response="कृपया कैमरे को स्थिर रखें और पुनः प्रयास करें।" if is_hindi else "Camera frame invalid. Please hold steady and try again.",
                display_response=val_error or "Invalid frame",
                session_id=session_id or "cam_err",
                language=active_lang,
                priority=AssistancePriority.HIGH,
            )
            return CameraAnalysisResponse(
                success=False,
                session_id=session_id or "cam_err",
                mode=requested_mode,
                analysis=empty_analysis,
                assistance=empty_assistance,
                error=error,
            )

        # 2. Retrieve or Create Camera Session
        resolved_mode, resolved_intent = self.resolve_mode_and_intent(
            requested_mode, intent, target_object, twin
        )
        cam_session = session_service.get_or_create_camera_session(
            session_id=session_id,
            twin_id=twin_id,
            mode=resolved_mode.value,
            target_object=target_object,
        )
        sid = cam_session["session_id"]

        # 3. Preprocess Frame
        processed_bytes, frame_meta = self.preprocess_frame(image_bytes)

        # 4. Selective AI Execution by Mode
        detected_objects: List[CameraObject] = []
        detected_texts: List[CameraText] = []
        fused_relations: List[CameraObjectTextRelation] = []
        hazards: List[str] = []
        scene_analysis: Optional[CameraSceneAnalysis] = None
        target_found = False
        target_guidance: Optional[Dict[str, Any]] = None

        try:
            # Check if AI Camera engine is available under ai.camera
            ai_camera_engine = self._get_ai_camera_adapter()

            if ai_camera_engine is not None:
                mode_map = {
                    CameraAnalysisMode.READ: "document",
                    CameraAnalysisMode.SEE: "see",
                    CameraAnalysisMode.FIND: "see",
                    CameraAnalysisMode.NAVIGATE: "navigation",
                    CameraAnalysisMode.UNDERSTAND: "scene",
                    CameraAnalysisMode.AUTO: "auto",
                }
                mode_str = mode_map.get(resolved_mode, "auto")
                raw_ai_res = ai_camera_engine.analyze(
                    image_input=processed_bytes,
                    mode=mode_str,
                    query=resolved_intent,
                    twin_id=twin_id,
                    session_id=sid,
                    target_object=target_object,
                    skip_duplicate_check=skip_duplicate_check,
                )

                # Extract objects
                for idx, so in enumerate(getattr(raw_ai_res, "spatial_objects", [])):
                    if isinstance(so, dict):
                        detected_objects.append(
                            CameraObject(
                                object_id=f"obj_{idx+1}",
                                label=so.get("label", "object"),
                                confidence=0.92,
                                clock_direction=so.get("clock_direction", "12 o'clock"),
                                clock_hour=int(so.get("clock_direction", "12").split()[0]) if so.get("clock_direction", "12").split()[0].isdigit() else 12,
                                relative_direction="straight ahead" if "12" in so.get("clock_direction", "") else ("to your right" if any(h in so.get("clock_direction", "") for h in ["1", "2", "3", "4", "5"]) else "to your left"),
                                proximity="near",
                                elevation=so.get("elevation", "level"),
                                associated_text=so.get("associated_text"),
                                haptic_cue=raw_ai_res.haptic_cue or "DOUBLE_PULSE_CENTER",
                            )
                        )

                # Extract texts
                doc_data = getattr(raw_ai_res, "document_data", None)
                if doc_data and isinstance(doc_data, dict):
                    for idx, txt in enumerate(doc_data.get("ocr_lines", [])):
                        detected_texts.append(
                            CameraText(
                                text_id=f"txt_{idx+1}",
                                text=txt if isinstance(txt, str) else txt.get("text", ""),
                                confidence=0.90,
                            )
                        )

                if resolved_mode in [CameraAnalysisMode.FIND, CameraAnalysisMode.SEE]:
                    target_found = len(detected_objects) > 0 or getattr(raw_ai_res, "status", "") == "SUCCESS"
                    if detected_objects:
                        target_guidance = {
                            "target": target_object or detected_objects[0].label,
                            "clock_direction": detected_objects[0].clock_direction,
                            "proximity": detected_objects[0].proximity,
                            "haptic_cue": detected_objects[0].haptic_cue,
                        }

            # If objects or texts still need domain pipeline augmentation:
            if not detected_texts and resolved_mode in [CameraAnalysisMode.READ, CameraAnalysisMode.UNDERSTAND]:
                # Run Real OCR
                ocr_results = pipeline_service.assistance_engine.ocr_engine.ocr_image(processed_bytes)
                for idx, item in enumerate(ocr_results):
                    detected_texts.append(
                        CameraText(
                            text_id=f"txt_{idx+1}",
                            text=item["text"],
                            confidence=item.get("confidence", 0.90),
                            bbox=tuple(item["bbox"]) if item.get("bbox") else None,
                        )
                    )

            if not detected_objects and target_object:
                # Targeted spatial vision search for specific object
                spatial_res = pipeline_service.compute_spatial_guidance(target_object, twin_id=twin_id)
                target_found = spatial_res.get("found", False)
                if target_found:
                    target_guidance = spatial_res
                    primary_obj = CameraObject(
                        object_id="obj_target_1",
                        label=spatial_res.get("label", target_object),
                        confidence=0.92,
                        bbox=(380, 120, 520, 420),
                        clock_direction=spatial_res.get("clock_direction", "12 o'clock"),
                        clock_hour=spatial_res.get("clock_hour", 12),
                        relative_direction=spatial_res.get("relative_direction", "straight ahead"),
                        proximity="near",
                        elevation="level",
                        haptic_cue=spatial_res.get("haptic_cue", "DOUBLE_PULSE_CENTER"),
                        haptic_intensity="MEDIUM",
                    )
                    detected_objects.append(primary_obj)

            # Fuse Objects + OCR Text
            if detected_objects and detected_texts:
                raw_objs = [{"label": o.label, "bbox": o.bbox} for o in detected_objects if o.bbox]
                raw_txts = [{"text": t.text, "bbox": t.bbox, "confidence": t.confidence} for t in detected_texts if t.bbox]
                fused_dict = pipeline_service.assistance_engine.scene_fusion.fuse(raw_objs, raw_txts)
                for fo in fused_dict.get("objects", []):
                    if fo.get("text"):
                        fused_relations.append(
                            CameraObjectTextRelation(
                                object_id="obj_fused_1",
                                object_label=fo.get("label", "object"),
                                associated_text=fo.get("text", ""),
                                relationship="contained_within",
                                combined_interpretation=f"{fo.get('text')} ({fo.get('label')})",
                                confidence=0.94,
                            )
                        )

            # Build Scene Analysis
            if resolved_mode == CameraAnalysisMode.NAVIGATE:
                nav_guide = pipeline_service.guide_navigation(
                    session_id=sid,
                    target_destination=target_object or "exit",
                    detected_labels=[o.label for o in detected_objects],
                    twin_id=twin_id,
                )
                scene_desc = nav_guide.instruction
                scene_spoken = nav_guide.spoken_guidance
                hazards = [o.description for o in nav_guide.obstacles_in_path]
            elif resolved_mode == CameraAnalysisMode.READ:
                scene_desc = f"Text detected with {len(detected_texts)} line(s)."
                all_text_preview = " ".join([t.text for t in detected_texts[:4]])
                scene_spoken = (
                    f"दस्तावेज़ में लिखा है: {all_text_preview}" if is_hindi else f"Detected text: {all_text_preview}"
                )
            elif resolved_mode == CameraAnalysisMode.FIND:
                scene_desc = f"Target {target_object or 'object'} located."
                scene_spoken = (
                    f"{target_object or 'Target'} {detected_objects[0].clock_direction if detected_objects else 'straight ahead'} पर है।"
                    if is_hindi else
                    f"{target_object or 'Target'} is at {detected_objects[0].clock_direction if detected_objects else '12 o clock'}."
                )
            else:
                if detected_objects:
                    scene_desc = f"Detected {len(detected_objects)} object(s)."
                    scene_spoken = (
                        f"आपके सामने {detected_objects[0].label} {detected_objects[0].clock_direction} पर है।"
                        if is_hindi else
                        f"I see {detected_objects[0].label} at {detected_objects[0].clock_direction}."
                    )
                else:
                    scene_desc = "Camera frame analyzed. No distinct objects identified."
                    scene_spoken = (
                        "कैमरा फ़्रेम का विश्लेषण संपन्न हुआ। कोई स्पष्ट वस्तु नहीं मिली।"
                        if is_hindi else
                        "Camera frame analyzed. No distinct objects identified."
                    )

            scene_analysis = CameraSceneAnalysis(
                scene_type="indoor",
                description=scene_desc,
                objects=detected_objects,
                text_elements=detected_texts,
                fused_relations=fused_relations,
                hazards=hazards,
                navigable_path_clear=len(hazards) == 0,
                suggested_action="Proceed" if len(hazards) == 0 else "Caution: obstacle ahead",
                summary_spoken=scene_spoken,
                summary_display=scene_desc,
                language=active_lang,
            )


        except Exception as e:
            logger.error(f"Error during camera AI execution: {e}", exc_info=True)
            recovery = pipeline_service.build_recovery_result(
                stage=PipelineStage.AI_INFERENCE,
                error_message=str(e),
                fallback_used=True,
                strategy="CAMERA_SAFE_ASSIST_FALLBACK"
            )
            scene_spoken = recovery.spoken_recovery_guidance
            scene_desc = recovery.actionable_user_message

        # 5. Synthesize Multimodal Assistance Response
        haptic_cue = "DOUBLE_PULSE_CENTER"
        if detected_objects:
            haptic_cue = detected_objects[0].haptic_cue

        priority = AssistancePriority.HIGH if hazards else AssistancePriority.NORMAL

        visual_card = {
            "mode": resolved_mode.value,
            "title": f"Camera Assist: {resolved_mode.value}",
            "objects_count": len(detected_objects),
            "text_count": len(detected_texts),
            "fused_count": len(fused_relations),
            "primary_label": detected_objects[0].label if detected_objects else None,
            "high_contrast": twin.visual.high_contrast,
        }

        # 6. Update Session Context
        session_service.update_camera_session(
            session_id=sid,
            frame_id=frame_meta.frame_id,
            objects=[o.dict() for o in detected_objects],
            texts=[t.dict() for t in detected_texts],
            fused_relations=[r.dict() for r in fused_relations],
            scene=scene_analysis.dict() if scene_analysis else None,
            hazards=hazards,
            mode=resolved_mode.value,
            intent=resolved_intent,
            target_object=target_object,
        )

        elapsed_ms = round((time.time() - start_time) * 1000, 1)

        analysis_result = CameraAnalysisResult(
            session_id=sid,
            mode=resolved_mode,
            intent=resolved_intent,
            target_object=target_object,
            objects=detected_objects,
            text_elements=detected_texts,
            fused_relations=fused_relations,
            scene=scene_analysis,
            target_found=target_found,
            target_guidance=target_guidance,
            hazards=hazards,
            processing_metadata={
                "latency_ms": elapsed_ms,
                "frame_width": frame_meta.width,
                "frame_height": frame_meta.height,
            },
            confidence=0.92,
            status="COMPLETED",
        )

        assistance_response = CameraAssistanceResponse(
            spoken_response=scene_spoken,
            display_response=scene_desc,
            haptic_cue=haptic_cue,
            haptic_intensity=twin.haptics.intensity if twin.haptics.enabled else "MEDIUM",
            priority=priority,
            language=active_lang,
            next_action="CONTINUE_SCAN" if resolved_mode in [CameraAnalysisMode.NAVIGATE, CameraAnalysisMode.SEE] else "AWAIT_COMMAND",
            session_id=sid,
            analysis=analysis_result,
            visual_card=visual_card,
        )

        return CameraAnalysisResponse(
            success=True,
            session_id=sid,
            mode=resolved_mode,
            analysis=analysis_result,
            assistance=assistance_response,
            next_action=assistance_response.next_action,
            processing={"latency_ms": elapsed_ms, "timestamp": datetime.utcnow().isoformat()},
            error=None,
        )

    # ----------------------------------------------------
    # Helper: AI Camera Adapter Discovery
    # ----------------------------------------------------
    def _get_ai_camera_adapter(self):
        """Attempts to discover AI camera engine if implemented by AI teammate."""
        try:
            import ai.camera.camera_engine as ai_cam
            if hasattr(ai_cam, "CameraEngine"):
                return ai_cam.CameraEngine()
        except ImportError:
            pass
        return None


camera_service = CameraService()
