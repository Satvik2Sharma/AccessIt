"""
Integration Test for ISL Indian Sign Language Pipeline
"""

import sys
import os

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from backend.services.pipeline_service import pipeline_service


def test_isl_prediction_pipeline():
    twin = pipeline_service.twin_service.get_twin("default_user")
    res = pipeline_service.assistance_engine.assist_sign_communication(image_bytes=None, twin=twin)

    assert "sign" in res
    assert "spoken_output" in res
    assert ("caption" in res or "display_caption" in res)
    assert res["sign"] == "HELP"


if __name__ == "__main__":
    test_isl_prediction_pipeline()
    print("Integration test_isl_pipeline.py passed successfully!")
