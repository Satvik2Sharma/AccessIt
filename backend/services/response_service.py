"""
Sahayak AI — Response Normalization Service
Formats and normalizes backend outputs into consistent multimodal response envelopes
containing text, spoken audio prompts, visual cards, tactile haptics, and priority metadata.
"""

from typing import Dict, Any, Optional, List
from shared.schemas.models import (
    AccessibilityTwin,
    LanguagePreference,
    AssistanceResponse,
    AssistancePriority,
    RecoveryResult,
)


class ResponseService:
    @staticmethod
    def format_multimodal_response(
        text_content: str,
        spoken_content: Optional[str] = None,
        twin: Optional[AccessibilityTwin] = None,
        visual_card: Optional[Dict[str, Any]] = None,
        haptic_pattern: str = "SINGLE_PULSE",
        haptic_intensity: str = "MEDIUM",
        priority: AssistancePriority = AssistancePriority.NORMAL,
        next_action: Optional[str] = None,
        session_id: Optional[str] = None,
        recovery_info: Optional[Dict[str, Any]] = None,
    ) -> AssistanceResponse:
        """
        Creates a unified multimodal response envelope adapted to the user's Accessibility Twin.
        """
        lang = twin.language.value if twin and hasattr(twin, "language") else "English"
        spoken = spoken_content or text_content

        # Adapt haptics based on user preferences
        if twin and hasattr(twin, "haptics") and not twin.haptics.enabled:
            haptic_pattern_val = None
            haptic_intensity_val = "NONE"
        else:
            haptic_pattern_val = haptic_pattern
            haptic_intensity_val = (
                twin.haptics.intensity if (twin and hasattr(twin, "haptics")) else haptic_intensity
            )

        return AssistanceResponse(
            text_content=text_content,
            spoken_content=spoken,
            language=lang,
            visual_card=visual_card,
            haptic_pattern=haptic_pattern_val,
            haptic_intensity=haptic_intensity_val,
            priority=priority,
            next_action=next_action,
            session_id=session_id,
            recovery_info=recovery_info,
        )

    @staticmethod
    def format_spatial_vision_response(
        guidance: Dict[str, Any],
        twin: Optional[AccessibilityTwin] = None
    ) -> Dict[str, Any]:
        """Normalizes spatial vision output into standard response structure."""
        return {
            "label": guidance.get("label", "object"),
            "relative_direction": guidance.get("relative_direction", "straight ahead"),
            "clock_hour": guidance.get("clock_hour", 12),
            "clock_direction": guidance.get("clock_direction", "12 o'clock"),
            "elevation": guidance.get("elevation", "table/waist level"),
            "relative_proximity": guidance.get("relative_proximity", "within arm's reach"),
            "spoken_guidance": guidance.get("spoken_guidance", ""),
            "display_guidance": guidance.get("display_guidance", ""),
            "haptic_cue": guidance.get("haptic_cue", "DOUBLE_PULSE_CENTER"),
            "haptic_intensity": guidance.get("haptic_intensity", "MEDIUM"),
            "normalized_coordinates": guidance.get("normalized_coordinates", {"x": 0.5, "y": 0.5}),
            "area_ratio": guidance.get("area_ratio", 0.1),
            "found": True,
        }

    @staticmethod
    def format_navigation_response(
        session_id: str,
        direction: str,
        clock_direction: str,
        instruction: str,
        spoken_guidance: str,
        obstacles: List[Dict[str, Any]],
        urgency: AssistancePriority = AssistancePriority.NORMAL,
        haptic_cue: str = "DOUBLE_PULSE_CENTER",
        is_reached: bool = False
    ) -> Dict[str, Any]:
        """Normalizes navigation instructions for mobile rendering."""
        return {
            "session_id": session_id,
            "direction": direction,
            "clock_direction": clock_direction,
            "instruction": instruction,
            "spoken_guidance": spoken_guidance,
            "urgency": urgency.value,
            "obstacles_in_path": obstacles,
            "haptic_cue": haptic_cue,
            "is_destination_reached": is_reached,
        }

    @staticmethod
    def format_document_qa_response(
        document_id: str,
        question: str,
        answer: str,
        supporting_info: List[str],
        confidence: float = 0.92,
        source_section: Optional[str] = None,
        related_actions: Optional[List[str]] = None,
        language: str = "English",
        twin: Optional[AccessibilityTwin] = None
    ) -> Dict[str, Any]:
        """Formats document question answering responses."""
        return {
            "document_id": document_id,
            "question": question,
            "answer": answer,
            "spoken_answer": answer,
            "supporting_extracted_info": supporting_info,
            "confidence": confidence,
            "source_section": source_section or "Notice Key Details",
            "related_actions": related_actions or ["Review Deadlines", "Gather Documents"],
            "language": language,
            "haptic_cue": "TOUCH_CONFIRM" if (twin and twin.haptics.enabled) else None,
        }

    @staticmethod
    def format_recovery_response(recovery: RecoveryResult) -> Dict[str, Any]:
        """Formats error recovery status for client inspection."""
        return {
            "failed_stage": recovery.failed_stage.value,
            "failure_type": recovery.failure_type,
            "error_message": recovery.error_message,
            "retry_attempted": recovery.retry_attempted,
            "fallback_used": recovery.fallback_used,
            "fallback_strategy": recovery.fallback_strategy,
            "recovery_status": recovery.recovery_status.value,
            "actionable_user_message": recovery.actionable_user_message,
            "spoken_recovery_guidance": recovery.spoken_recovery_guidance,
        }


response_service = ResponseService()
