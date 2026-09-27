"""
Sahayak AI — Accessibility Twin Service
Models functional interaction requirements and capabilities without medical diagnosis.
"""

from typing import Optional, Dict
from shared.schemas.models import (
    AccessibilityTwin,
    LanguagePreference,
    InputModality,
    OutputModality,
    VisualPreferences,
    HearingPreferences,
    MotorPreferences,
    ComprehensionPreferences,
    HapticPreferences,
)


class AccessibilityTwinService:
    def __init__(self):
        # In-memory storage for hackathon MVP (local on-device persistence)
        self._twins: Dict[str, AccessibilityTwin] = {}
        self._initialize_default_profile()

    def _initialize_default_profile(self):
        default_twin = AccessibilityTwin(
            id="default_user",
            language=LanguagePreference.HINDI,
            secondary_language=LanguagePreference.ENGLISH,
            visual=VisualPreferences(
                large_text=True,
                high_contrast=False,
                screen_reader=False,
                magnification_level=1.2,
            ),
            hearing=HearingPreferences(
                captions=True,
                visual_alerts=True,
                sign_language=False,
            ),
            motor=MotorPreferences(
                voice_input=True,
                large_touch_targets=True,
                reduce_scrolling=True,
            ),
            comprehension=ComprehensionPreferences(
                simplified_language=True,
                one_step_at_a_time=True,
                read_instructions_aloud=True,
                show_task_progress=True,
            ),
            haptics=HapticPreferences(
                enabled=True,
                intensity="strong",
                tactile_confirmation=True,
            ),
            preferred_input=InputModality.VOICE,
            preferred_output=OutputModality.VOICE_AND_TEXT,
        )
        self._twins[default_twin.id] = default_twin

    def get_twin(self, twin_id: str = "default_user") -> AccessibilityTwin:
        if twin_id not in self._twins:
            self._initialize_default_profile()
        return self._twins.get(twin_id, self._twins["default_user"])

    def update_twin(self, twin: AccessibilityTwin) -> AccessibilityTwin:
        self._twins[twin.id] = twin
        return twin
