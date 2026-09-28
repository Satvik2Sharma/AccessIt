import pytest
from ai.navigation.navigation_engine import NavigationEngine
from shared.schemas.models import AccessibilityTwin, LanguagePreference

def test_navigation_full_pipeline():
    engine = NavigationEngine()
    twin = AccessibilityTwin(id="t1", language=LanguagePreference.ENGLISH)
    result = engine.navigate(image_bytes=None, target_label="water bottle", twin=twin)
    assert "instructions" in result
    assert "hazards" in result
    assert result["disclaimer"] is not None
    for instr in result["instructions"]:
        assert "direction" in instr
        assert "description" in instr

def test_navigation_hindi_instructions():
    engine = NavigationEngine()
    twin = AccessibilityTwin(id="t1", language=LanguagePreference.HINDI)
    result = engine.navigate(image_bytes=None, target_label="medicine bottle", twin=twin)
    assert len(result["instructions"]) > 0
    for instr in result["instructions"]:
        # Hindi instructions have description_hi
        assert "description_hi" in instr
