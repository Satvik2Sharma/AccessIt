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
        twin: AccessibilityTwin
    ) -> Dict[str, Any]:
        """
        Coordinates OCR + Document Parsing + Simplification + Localization.
        """
        doc_data = self.ocr_engine.extract_document_info(image_bytes, query)
        is_hindi = twin.language == LanguagePreference.HINDI

        summary = doc_data["simplified_summary_hi"] if is_hindi else doc_data["simplified_summary_en"]
        voice_prompt = summary

        return {
            "title": doc_data["document_title"],
            "authority": doc_data["issuing_authority"],
            "deadlines": doc_data["key_deadlines"],
            "required_documents": doc_data["required_documents"],
            "spoken_summary": voice_prompt,
            "display_summary": summary,
            "language": twin.language.value,
            "haptic_cue": "SUCCESS_DOUBLE_PULSE" if twin.haptics.enabled else None,
        }

    def assist_find_object(
        self,
        target_label: str,
        twin: AccessibilityTwin
    ) -> Dict[str, Any]:
        """
        Coordinates Object Detection + Spatial Directional Guidance + Haptics.
        """
        # Simulated standard bounding box for Demo: bottle on right side
        sample_bbox = (380, 120, 520, 420)
        guidance = self.directional_finder.compute_spatial_guidance(
            bbox=sample_bbox,
            label=target_label,
            language="Hindi" if twin.language == LanguagePreference.HINDI else "English",
        )
        return guidance

    def assist_sign_communication(
        self,
        image_bytes: Optional[bytes],
        twin: AccessibilityTwin
    ) -> Dict[str, Any]:
        """
        Coordinates ISL gesture classification + Captioning + TTS.
        """
        prediction = self.isl_service.predict_sign(image_bytes)
        return prediction
