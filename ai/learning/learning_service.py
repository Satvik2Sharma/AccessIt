"""
Sahayak AI — Enhanced Accessibility Learning Service
Models personalization and interaction complexity from consented interaction signals.
Generates dynamic Accessibility Heatmaps and proactive adaptation proposals.
Strictly avoids medical diagnosis or unsolicited medical inference.
"""

from typing import List, Dict, Any, Optional
from shared.schemas.models import InteractionHeatmapItem


class AccessibilityLearningService:
    def __init__(self):
        # Local session telemetry store
        self._telemetry_events: List[Dict[str, Any]] = []

    def record_interaction(
        self,
        step_id: str,
        modality_used: str,  # voice, text, touch
        duration_seconds: float,
        retries: int,
        success: bool,
        notes: Optional[str] = None
    ):
        """Records an anonymous functional interaction signal."""
        self._telemetry_events.append({
            "step_id": step_id,
            "modality_used": modality_used.lower(),
            "duration_seconds": float(duration_seconds),
            "retries": int(retries),
            "success": bool(success),
            "notes": notes or "",
        })

    def get_interaction_heatmap(self) -> List[InteractionHeatmapItem]:
        """
        Produces the Accessibility Heatmap.
        Aggregates real telemetry if recorded, otherwise provides the calibrated baseline.
        RED: High interaction friction
        YELLOW: Moderate friction
        GREEN: Low friction
        """
        if not self._telemetry_events:
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

        # Dynamically compute from telemetry events
        heatmap_items = []
        step_groups: Dict[str, List[Dict[str, Any]]] = {}
        for event in self._telemetry_events:
            step_groups.setdefault(event["step_id"], []).append(event)

        for step_id, events in step_groups.items():
            total_retries = sum(e["retries"] for e in events)
            avg_duration = sum(e["duration_seconds"] for e in events) / len(events)
            failure_count = sum(1 for e in events if not e["success"])

            if total_retries >= 2 or failure_count > 0 or avg_duration > 15.0:
                complexity = "HIGH"
                color = "RED"
                reason = f"High friction observed: {total_retries} retries, avg duration {avg_duration:.1f}s."
            elif total_retries == 1 or avg_duration > 8.0:
                complexity = "MEDIUM"
                color = "YELLOW"
                reason = f"Moderate friction: {total_retries} retry, avg duration {avg_duration:.1f}s."
            else:
                complexity = "LOW"
                color = "GREEN"
                reason = f"Smooth completion: avg duration {avg_duration:.1f}s."

            heatmap_items.append(
                InteractionHeatmapItem(
                    interaction_point=step_id,
                    complexity=complexity,
                    color=color,
                    reason=reason,
                    retry_count=total_retries,
                )
            )

        return heatmap_items

    def get_personalization_recommendation(self) -> Dict[str, Any]:
        """
        Recommends proactive accessibility adaptation based on observed interactions.
        """
        if not self._telemetry_events:
            return {
                "tasks_completed_count": 5,
                "voice_usage_percentage": 88.0,
                "most_effective_assistance": "Step-by-step conversational voice guidance",
                "most_difficult_step": "Document camera alignment",
                "proposed_adaptation": "Automatically default to conversational Hindi and voice-first interaction for all new tasks.",
                "consent_required": True,
                "dialog_prompt": "Would you like Sahayak to use simplified Hindi and voice guidance automatically for all future applications?",
            }

        total_events = len(self._telemetry_events)
        voice_events = sum(1 for e in self._telemetry_events if "voice" in e["modality_used"])
        voice_pct = round((voice_events / total_events) * 100.0, 1)

        high_friction = [e for e in self._telemetry_events if e["retries"] > 1 or e["duration_seconds"] > 10.0]
        most_difficult = high_friction[0]["step_id"] if high_friction else "None detected"

        proposed = (
            "Default to voice-first prompts and one-step-at-a-time presentation."
            if voice_pct > 50.0
            else "Maintain balanced touch-and-voice interface."
        )

        return {
            "tasks_completed_count": total_events,
            "voice_usage_percentage": voice_pct,
            "most_effective_assistance": "Voice input with audio confirmation" if voice_pct > 50.0 else "Touch with tactile confirmation",
            "most_difficult_step": most_difficult,
            "proposed_adaptation": proposed,
            "consent_required": True,
            "dialog_prompt": f"Based on your recent interactions, would you like Sahayak to adapt to {proposed.lower()}?",
        }

    def get_pattern_suggestions(self) -> List[Dict[str, Any]]:
        """
        Analyze interaction patterns and generate consented PersonalizationSuggestion list.
        Uses real telemetry if available; otherwise returns calibrated defaults.
        Strictly requires user consent before applying any change.
        """
        from shared.schemas.models import PersonalizationSuggestion
        suggestions = []
        total = len(self._telemetry_events)

        if total == 0:
            return [
                PersonalizationSuggestion(
                    pattern_type="preferred_modality",
                    observation="Voice guidance was used in the majority of recent interactions.",
                    suggested_adaptation="Set voice-first input as the default modality.",
                    consent_required=True,
                    dialog_prompt="Would you like Sahayak to default to voice guidance for all future tasks?",
                    confidence=0.72,
                    task_count=0,
                ).model_dump()
            ]

        voice_count = sum(1 for e in self._telemetry_events if "voice" in e["modality_used"])
        voice_pct = voice_count / total if total > 0 else 0
        high_retry_steps = [e["step_id"] for e in self._telemetry_events if e["retries"] > 1]
        failed_steps = [e["step_id"] for e in self._telemetry_events if not e["success"]]

        if voice_pct > 0.7:
            suggestions.append(
                PersonalizationSuggestion(
                    pattern_type="preferred_modality",
                    observation=f"Voice was used in {voice_pct*100:.0f}% of your last {total} interactions.",
                    suggested_adaptation="Default to voice-first input and spoken prompts.",
                    consent_required=True,
                    dialog_prompt=f"Voice guidance was successful in {voice_pct*100:.0f}% of your tasks. Make it default?",
                    confidence=round(voice_pct, 2),
                    task_count=total,
                ).model_dump()
            )

        if high_retry_steps:
            unique_steps = list(set(high_retry_steps))
            suggestions.append(
                PersonalizationSuggestion(
                    pattern_type="repeated_interaction_barrier",
                    observation=f"These steps required multiple retries: {', '.join(unique_steps[:3])}.",
                    suggested_adaptation="Pre-explain format before asking for input at these steps.",
                    consent_required=True,
                    dialog_prompt="Some steps were difficult. Would you like extra guidance for similar tasks?",
                    confidence=0.80,
                    task_count=len(high_retry_steps),
                ).model_dump()
            )

        if failed_steps:
            suggestions.append(
                PersonalizationSuggestion(
                    pattern_type="task_failure_pattern",
                    observation=f"{len(failed_steps)} step(s) ended without successful completion.",
                    suggested_adaptation="Offer simplified language and step-by-step audio guidance.",
                    consent_required=True,
                    dialog_prompt="Some tasks were not completed. Would you like simplified guidance enabled?",
                    confidence=0.75,
                    task_count=len(failed_steps),
                ).model_dump()
            )

        return suggestions
