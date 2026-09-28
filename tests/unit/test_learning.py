"""
Unit Tests for Telemetry, Learning Service, and Heatmaps
"""

import sys
import os

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from ai.learning.learning_service import AccessibilityLearningService


def test_interaction_recording():
    service = AccessibilityLearningService()
    service.record_interaction("aadhaar", "voice", 4.2, retries=0, success=True)
    service.record_interaction("bank_account", "touch", 12.5, retries=2, success=True)

    heatmap = service.get_interaction_heatmap()
    assert isinstance(heatmap, list)
    assert len(heatmap) >= 1


def test_personalization_recommendation():
    service = AccessibilityLearningService()
    rec = service.get_personalization_recommendation()
    assert rec is not None
    assert isinstance(rec, dict)
    assert "proposed_adaptation" in rec


if __name__ == "__main__":
    test_interaction_recording()
    test_personalization_recommendation()
    print("All unit/test_learning.py tests passed!")
