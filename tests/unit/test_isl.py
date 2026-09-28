"""
Unit Tests for ISL Sign Language Schemas & Predictor Contract
"""

import sys
import os

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from shared.schemas.models import (
    ISLPredictionRequest,
    ISLPredictionResponse,
    HandLandmark,
)
from ai.isl.sign_classifier import ISLInterpreterService


def test_hand_landmark_schema():
    lm = HandLandmark(x=0.5, y=0.4, z=-0.05)
    assert lm.x == 0.5
    assert lm.y == 0.4
    assert lm.z == -0.05


def test_isl_interpreter_heuristic_prediction():
    service = ISLInterpreterService()
    # Null image or dummy landmark prediction
    res = service.predict_sign(None)
    assert "sign" in res
    assert res["sign"] in ["HELP", "YES", "NO", "WATER", "THANK YOU", "HELLO", "NAMASTE"]
    assert "spoken_output" in res
    assert "confidence" in res
    assert res["confidence"] > 0.5


if __name__ == "__main__":
    test_hand_landmark_schema()
    test_isl_interpreter_heuristic_prediction()
    print("All unit/test_isl.py tests passed!")
