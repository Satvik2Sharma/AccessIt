"""
Unit Tests for Accessibility Twin and Personalization Schemas
"""

import sys
import os

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from shared.schemas.models import (
    AccessibilityTwin,
    LanguagePreference,
    InputModality,
    OutputModality,
    PersonalizationProfile,
)
from ai.accessibility.twin import AccessibilityTwinService


def test_default_twin_creation():
    service = AccessibilityTwinService()
    twin = service.get_twin("default_user")
    assert twin is not None
    assert twin.id == "default_user"
    assert twin.language in [LanguagePreference.HINDI, LanguagePreference.ENGLISH]
    assert twin.comprehension.simplified_language is True
    assert twin.motor.voice_input is True


def test_twin_profile_update():
    service = AccessibilityTwinService()
    twin = service.get_twin("custom_user")
    twin.language = LanguagePreference.HINDI
    twin.visual.high_contrast = True
    twin.visual.large_text = True
    twin.haptics.enabled = True
    twin.haptics.intensity = "strong"

    updated = service.update_twin(twin)
    assert updated.language == LanguagePreference.HINDI
    assert updated.visual.high_contrast is True
    assert updated.visual.large_text is True
    assert updated.haptics.intensity == "strong"


def test_personalization_profile_schema():
    profile = PersonalizationProfile(
        twin_id="user_123",
        preferred_language=LanguagePreference.HINDI,
        voice_speed=1.2,
        high_contrast=True,
    )
    assert profile.twin_id == "user_123"
    assert profile.preferred_language == LanguagePreference.HINDI
    assert profile.voice_speed == 1.2
    assert profile.high_contrast is True


if __name__ == "__main__":
    test_default_twin_creation()
    test_twin_profile_update()
    test_personalization_profile_schema()
    print("All unit/test_twin.py tests passed!")
