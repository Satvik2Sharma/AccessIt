"""
Unit Tests for Intent Engine & Voice Command Classification
"""

import sys
import os

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from shared.schemas.models import TaskType, AccessibilityTwin
from ai.intent.intent_engine import IntentEngine
from ai.accessibility.twin import AccessibilityTwinService


def test_document_intent_classification():
    engine = IntentEngine()
    twin = AccessibilityTwinService().get_twin("default_user")

    t1, c1, _ = engine.classify_intent("What is important in this circular?", twin)
    assert t1 == TaskType.UNDERSTAND_DOCUMENT
    assert c1 > 0.5

    t2, c2, _ = engine.classify_intent("मुझे नोटिस समझा दो", twin)
    assert t2 == TaskType.UNDERSTAND_DOCUMENT
    assert c2 > 0.5


def test_form_intent_classification():
    engine = IntentEngine()
    twin = AccessibilityTwinService().get_twin("default_user")

    t1, c1, _ = engine.classify_intent("Help me fill this scholarship form", twin)
    assert t1 == TaskType.FORM_COMPLETION
    assert c1 > 0.5

    t2, c2, _ = engine.classify_intent("scholarship form bharna hai", twin)
    assert t2 == TaskType.FORM_COMPLETION
    assert c2 > 0.5


def test_spatial_and_sign_intent_classification():
    engine = IntentEngine()
    twin = AccessibilityTwinService().get_twin("default_user")

    t1, c1, _ = engine.classify_intent("Where is my water bottle?", twin)
    assert t1 == TaskType.FIND_OBJECT
    assert c1 > 0.5

    t2, c2, _ = engine.classify_intent("Translate sign language gestures", twin)
    assert t2 == TaskType.COMMUNICATE
    assert c2 > 0.5


if __name__ == "__main__":
    test_document_intent_classification()
    test_form_intent_classification()
    test_spatial_and_sign_intent_classification()
    print("All unit/test_intent.py tests passed!")
