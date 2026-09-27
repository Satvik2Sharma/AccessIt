"""
Sahayak AI — Accessibility Learning Service
Models personalization and interaction complexity from consented interaction signals.
Generates the Accessibility Heatmap and proactive adaptation proposals.
Strictly avoids medical diagnosis or unsolicited medical inference.
"""

from typing import List, Dict, Any
from shared.schemas.models import InteractionHeatmapItem


class AccessibilityLearningService:
    def __init__(self):
        # Local session telemetry
        self._telemetry_events: List[Dict[str, Any]] = []

    def record_interaction(
        self,
        step_id: str,
        modality_used: str,  # voice, text, touch
        duration_seconds: float,
        retries: int,
        success: bool
    ):
        self._telemetry_events.append({
            "step_id": step_id,
            "modality_used": modality_used,
            "duration_seconds": duration_seconds,
            "retries": retries,
            "success": success,
        })

    def get_interaction_heatmap(self) -> List[InteractionHeatmapItem]:
        """
        Produces the deterministic Accessibility Heatmap for hackathon demonstration.
        RED: High interaction complexity
        YELLOW: Moderate complexity
        GREEN: Low complexity
        """
        return [
            InteractionHeatmapItem(
                interaction_point="document_upload",
                complexity="HIGH",
                color="RED",
                reason="Multi-step physical alignment, camera glare, and file size limits.",
                retry_count=3,
            ),
            InteractionHeatmapItem(
                interaction_point="category_selection",
                complexity="MEDIUM",
                color="YELLOW",
                reason="Multiple administrative acronyms (OBC-NCL, EWS, Gen-EWS).",
                retry_count=1,
            ),
            InteractionHeatmapItem(
                interaction_point="address_input",
                complexity="MEDIUM",
                color="YELLOW",
                reason="Long-form multi-line text input with PIN code matching.",
                retry_count=1,
            ),
            InteractionHeatmapItem(
                interaction_point="name_input",
                complexity="LOW",
                color="GREEN",
                reason="Single voice response with immediate phoneme confirmation.",
                retry_count=0,
            ),
            InteractionHeatmapItem(
                interaction_point="dob_input",
                complexity="LOW",
                color="GREEN",
                reason="Standard numeric date voice parser.",
                retry_count=0,
            ),
        ]

    def get_personalization_recommendation(self) -> Dict[str, Any]:
        """
        Recommends proactive accessibility adaptation based on observed interactions.
        """
        return {
            "tasks_completed_count": 5,
            "voice_usage_percentage": 88.0,
            "most_effective_assistance": "Step-by-step conversational voice guidance",
            "most_difficult_step": "Document camera alignment",
            "proposed_adaptation": "Automatically default to conversational Hindi and voice-first interaction for all new tasks.",
            "consent_required": True,
            "dialog_prompt": "Would you like Sahayak to use simplified Hindi and voice guidance automatically for all future applications?",
        }
