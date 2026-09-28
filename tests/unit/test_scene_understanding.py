import pytest
from ai.scene.scene_understanding import SceneUnderstandingEngine
from ai.scene.object_text_fusion import ObjectTextFusion
from shared.schemas.models import SceneAnalysis, SpatialObject, TaskType

def test_scene_analyze_no_image():
    engine = SceneUnderstandingEngine(provider="heuristic")
    scene = engine.analyze(image_bytes=None)
    assert isinstance(scene, SceneAnalysis)
    assert len(scene.objects) > 0
    assert scene.confidence > 0

def test_scene_analyze_with_target():
    engine = SceneUnderstandingEngine(provider="heuristic")
    scene = engine.analyze(image_bytes=None, target_labels=["water bottle"])
    assert any("water" in o.label.lower() for o in scene.relevant_objects)

def test_scene_spatial_object_has_direction():
    engine = SceneUnderstandingEngine(provider="heuristic")
    scene = engine.analyze(image_bytes=None)
    for obj in scene.objects:
        assert obj.direction is not None
        assert obj.elevation is not None
        assert obj.proximity is not None

def test_object_text_fusion():
    fusion = ObjectTextFusion()
    detections = [{"label": "medicine bottle", "confidence": 0.9, "bbox": [0.1, 0.3, 0.3, 0.8]}]
    ocr = [{"text": "Paracetamol 500mg", "confidence": 0.95, "bbox": [110, 300, 300, 800]}]
    result = fusion.fuse(detections, ocr, image_width=1000, image_height=1000)
    assert len(result) == 1
    assert result[0]["label"] == "medicine bottle"

def test_scene_task_type_filter():
    engine = SceneUnderstandingEngine(provider="heuristic")
    scene = engine.analyze(image_bytes=None, task_type=TaskType.UNDERSTAND_DOCUMENT, target_labels=["document"])
    assert scene.task_context == TaskType.UNDERSTAND_DOCUMENT.value
