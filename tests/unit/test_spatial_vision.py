import pytest
from ai.vision.object_detector import ObjectDetectorAdapter
from ai.vision.clock_direction import ClockDirectionMapper
from ai.vision.elevation_estimator import ElevationEstimator
from ai.vision.proximity_estimator import ProximityEstimator

def test_clock_direction_right():
    mapper = ClockDirectionMapper()
    result = mapper.compute(0.8, 0.5)
    assert result["horizontal_zone"] == "right"
    assert "clock_hour" in result
    assert 1 <= result["clock_hour"] <= 12

def test_clock_direction_left():
    mapper = ClockDirectionMapper()
    result = mapper.compute(0.1, 0.5)
    assert result["horizontal_zone"] == "left"

def test_clock_direction_center():
    mapper = ClockDirectionMapper()
    result = mapper.compute(0.5, 0.5)
    assert result["horizontal_zone"] == "center"

def test_clock_from_bbox():
    mapper = ClockDirectionMapper()
    result = mapper.from_bbox((0.6, 0.2, 0.9, 0.7), normalized=True)
    assert "direction" in result
    assert "clock_hour" in result

def test_elevation_eye_level():
    estimator = ElevationEstimator()
    result = estimator.estimate((0.1, 0.0, 0.9, 0.3), normalized=True)
    assert result["zone"] == "eye_level"

def test_elevation_table_level():
    estimator = ElevationEstimator()
    result = estimator.estimate((0.1, 0.3, 0.9, 0.7), normalized=True)
    assert result["zone"] == "table_level"

def test_elevation_floor_level():
    estimator = ElevationEstimator()
    result = estimator.estimate((0.1, 0.75, 0.9, 1.0), normalized=True)
    assert result["zone"] == "floor_level"

def test_proximity_very_close():
    estimator = ProximityEstimator()
    result = estimator.estimate((0.1, 0.1, 0.7, 0.9), normalized=True)
    assert result["zone"] == "very_close"

def test_proximity_several_steps():
    estimator = ProximityEstimator()
    result = estimator.estimate((0.45, 0.45, 0.55, 0.55), normalized=True)
    assert result["zone"] == "several_steps"

def test_object_detector_heuristic():
    detector = ObjectDetectorAdapter(provider="heuristic")
    results = detector.detect(image_bytes=None)
    assert len(results) > 0
    assert "label" in results[0]
    assert "confidence" in results[0]

def test_object_detector_target_filter():
    detector = ObjectDetectorAdapter(provider="heuristic")
    results = detector.detect(image_bytes=None, target_labels=["water bottle"])
    assert any("water" in r["label"].lower() for r in results)
