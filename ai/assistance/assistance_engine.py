"""
Sahayak AI — Accessibility Assistance Engine
Orchestrates AI capabilities (OCR, Vision, ISL, Speech, Haptics, Simplification)
based on the user's Accessibility Twin and the active task requirements.
"""

from typing import Dict, Any, List, Optional
from shared.schemas.models import (
    AccessibilityTwin,
    TaskType,
    AccessibleTaskFlow,
    LanguagePreference,
)
from ai.ocr.ocr_engine import DocumentOCREngine
from ai.vision.directional_finder import DirectionalFinder
from ai.isl.sign_classifier import ISLInterpreterService
from ai.scene.scene_fusion import SceneFusion


class AccessibilityAssistanceEngine:
    def __init__(self):
        self.ocr_engine = DocumentOCREngine()
        self.directional_finder = DirectionalFinder()
        self.isl_service = ISLInterpreterService()
        self.scene_fusion = SceneFusion()

    def assist_understand_document(
        self,
        image_bytes: Optional[bytes],
        query: str,
        twin: Optional[AccessibilityTwin] = None
    ) -> Dict[str, Any]:
        """
        Coordinates OCR + Document Parsing + Simplification + Localization.
        """
        user_twin = twin or AccessibilityTwin(id="default_user")
        doc_data = self.ocr_engine.extract_document_info(image_bytes, query or "")
        is_hindi = user_twin.language == LanguagePreference.HINDI

        summary = doc_data["simplified_summary_hi"] if is_hindi else doc_data["simplified_summary_en"]
        voice_prompt = summary

        return {
            "title": doc_data["document_title"],
            "authority": doc_data.get("issuing_authority", "Ministry of Education"),
            "deadlines": doc_data["key_deadlines"],
            "required_documents": doc_data["required_documents"],
            "application_fee": doc_data.get("application_fee", "NIL (Free)"),
            "action_required": doc_data.get("action_required", "Complete and verify application"),
            "spoken_summary": voice_prompt,
            "display_summary": summary,
            "summary_en": doc_data["simplified_summary_en"],
            "summary_hi": doc_data["simplified_summary_hi"],
            "language": user_twin.language.value,
            "raw_ocr_elements_count": doc_data.get("raw_ocr_elements_count", 0),
            "haptic_cue": "SUCCESS_DOUBLE_PULSE" if user_twin.haptics.enabled else None,
        }

    def assist_find_object(
        self,
        target_label: str,
        twin: Optional[AccessibilityTwin] = None
    ) -> Dict[str, Any]:
        """
        Coordinates Object Detection + Spatial Directional Guidance + Haptics.
        """
        user_twin = twin or AccessibilityTwin(id="default_user")
        target = target_label.strip() if target_label else "object"
        # Simulated standard bounding box for Demo: bottle on right side
        sample_bbox = (380, 120, 520, 420)
        guidance = self.directional_finder.compute_spatial_guidance(
            bbox=sample_bbox,
            label=target,
            language="Hindi" if user_twin.language == LanguagePreference.HINDI else "English",
        )
        return guidance

    def assist_sign_communication(
        self,
        image_bytes: Optional[bytes],
        twin: Optional[AccessibilityTwin] = None,
        session_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Coordinates ISL gesture classification + Captioning + TTS.
        """
        prediction = self.isl_service.predict_sign(image_bytes, session_id=session_id)
        return prediction

