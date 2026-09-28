import pytest
from ai.scene.scene_understanding import SceneUnderstandingEngine
from ai.navigation.navigation_engine import NavigationEngine
from shared.schemas.models import AccessibilityTwin, TaskType, LanguagePreference

def test_vision_pipeline_no_image():
    engine = SceneUnderstandingEngine()
    twin = AccessibilityTwin(id="t1")
    scene = engine.analyze(image_bytes=None, twin=twin, task_type=TaskType.SEE)
    assert len(scene.objects) > 0
    assert scene.summary is not None

def test_vision_pipeline_hindi_twin():
    engine = SceneUnderstandingEngine()
    twin = AccessibilityTwin(id="t1", language=LanguagePreference.HINDI)
    scene = engine.analyze(image_bytes=None, twin=twin)
    assert scene.summary is not None

def test_navigation_pipeline_no_image():
    engine = NavigationEngine()
    result = engine.navigate(image_bytes=None, target_label="medicine bottle")
    assert "instructions" in result
    assert len(result["instructions"]) > 0
    assert result["disclaimer"] is not None

def test_navigation_pipeline_obstacle_handling():
    engine = NavigationEngine()
    result = engine.navigate(image_bytes=None)
    assert "instructions" in result
    instr = result["instructions"]
    assert all("direction" in i for i in instr)
