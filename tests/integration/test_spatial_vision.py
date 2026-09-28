"""
Integration Test for Spatial Vision, 12-Hour Clock Direction, and Scene Fusion
"""

import sys
import os

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from backend.services.pipeline_service import pipeline_service


def test_spatial_guidance_and_scene_fusion():
    # 1. Spatial Guidance
    spatial_res = pipeline_service.compute_spatial_guidance("water bottle", "default_user")
    assert spatial_res["found"] is True
    assert "clock_direction" in spatial_res
    assert "haptic_cue" in spatial_res
    assert spatial_res["clock_hour"] in range(1, 13)

    # 2. Scene Analysis & Fusion
    scene_res = pipeline_service.analyze_scene_and_fusion()
    assert scene_res.navigable_path_clear is True
    assert len(scene_res.detected_objects) >= 2
    assert len(scene_res.fused_relations) >= 1
    assert any("door" in r.object_label for r in scene_res.fused_relations)


if __name__ == "__main__":
    test_spatial_guidance_and_scene_fusion()
    print("Integration test_spatial_vision.py passed successfully!")
