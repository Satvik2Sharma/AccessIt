import pytest
from ai.navigation.navigation_engine import NavigationEngine
from ai.navigation.obstacle_detector import ObstacleDetector
from ai.navigation.guidance_engine import GuidanceEngine
from shared.schemas.models import SpatialObject, NavigationInstruction

def test_navigation_no_image():
    engine = NavigationEngine()
    result = engine.navigate(image_bytes=None, target_label="water bottle")
    assert "instructions" in result
    assert len(result["instructions"]) > 0
    assert "scene_summary" in result
    assert "disclaimer" in result

def test_obstacle_detector_close_object():
    detector = ObstacleDetector()
    obj = SpatialObject(
        label="chair", confidence=0.9,
        bbox=[0.3, 0.2, 0.7, 0.8],
        proximity="very_close", horizontal_zone="center",
        direction="12 o'clock"
    )
    obstacles = detector.detect_obstacles([obj])
    assert len(obstacles) == 1
    assert obstacles[0]["severity"] == "HIGH"

def test_guidance_engine_target():
    engine = GuidanceEngine()
    obj = SpatialObject(
        label="water bottle", confidence=0.9,
        bbox=[0.6, 0.2, 0.9, 0.8],
        proximity="arm_reach", horizontal_zone="right",
        direction="3 o'clock"
    )
    instructions = engine.guide([obj], target_label="water bottle")
    assert len(instructions) > 0
    directions = [i.direction for i in instructions]
    assert any(d in ["right", "forward", "slight_right"] for d in directions)

def test_guidance_engine_no_obstacles():
    engine = GuidanceEngine()
    instructions = engine.guide([])
    assert len(instructions) == 1
    assert instructions[0].direction == "forward"
