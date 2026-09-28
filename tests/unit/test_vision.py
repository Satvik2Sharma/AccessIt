"""
Unit Tests for Spatial Vision, 12-Hour Clock Direction, Elevation, and Scene Fusion
"""

import sys
import os

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from shared.schemas.models import (
    VisionObject,
    SceneAnalysis,
    ObjectTextRelation,
)
from ai.vision.directional_finder import DirectionalFinder
from ai.scene.scene_fusion import SceneFusion


def test_directional_finder_clock_hours():
    finder = DirectionalFinder(frame_width=640, frame_height=480)

    # 1. Dead center (around 12 o'clock)
    res_center = finder.compute_spatial_guidance((280, 200, 360, 320), "water bottle", "English")
    assert res_center["clock_hour"] == 12
    assert "straight ahead" in res_center["relative_direction"]

    # 2. Top-Right (around 1 or 2 o'clock)
    res_tr = finder.compute_spatial_guidance((450, 50, 550, 150), "keys", "Hindi")
    assert res_tr["clock_hour"] in [1, 2]
    assert res_tr["haptic_cue"] == "PULSE_RIGHT"


def test_scene_fusion_object_text_association():
    fusion = SceneFusion()
    objects = [
        {"label": "door", "bbox": (100, 50, 280, 420)},
        {"label": "water dispenser", "bbox": (350, 150, 500, 400)},
    ]
    texts = [
        {"text": "EMERGENCY EXIT", "bbox": (120, 80, 260, 130), "confidence": 0.95},
        {"text": "DRINKING WATER", "bbox": (360, 170, 490, 210), "confidence": 0.94},
    ]

    fused = fusion.fuse(objects, texts)
    assert len(fused["objects"]) == 2

    # Check that door object got associated with 'EMERGENCY EXIT'
    door_obj = fused["objects"][0]
    assert door_obj["label"] == "door"
    assert "EMERGENCY EXIT" in door_obj["associated_texts"]
    assert "EMERGENCY EXIT" in door_obj["text"]


if __name__ == "__main__":
    test_directional_finder_clock_hours()
    test_scene_fusion_object_text_association()
    print("All unit/test_vision.py tests passed!")
