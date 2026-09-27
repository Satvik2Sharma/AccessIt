"""
Integration Test for 7-Stage Pipeline Orchestration, Navigation, and Error Recovery
"""

import sys
import os

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from shared.schemas.models import PipelineStage, RecoveryStatus
from backend.services.pipeline_service import pipeline_service
from backend.services.session_service import session_service


def test_full_navigation_orchestration():
    nav_res = pipeline_service.guide_navigation(
        target_destination="exit",
        detected_labels=["door", "clear path"],
        twin_id="default_user",
    )
    assert nav_res.session_id is not None
    assert "o'clock" in nav_res.clock_direction
    assert nav_res.haptic_cue is not None

    # Verify session update
    sess = session_service.get_navigation_session(nav_res.session_id)
    assert sess is not None
    assert sess["steps_guided"] >= 1


def test_pipeline_error_recovery_graceful_handling():
    recovery = pipeline_service.build_recovery_result(
        stage=PipelineStage.AI_INFERENCE,
        error_message="Camera frame timeout",
        fallback_used=True,
        strategy="AUDIO_AND_TACTILE_SAFE_MODE",
    )
    assert recovery.failed_stage == PipelineStage.AI_INFERENCE
    assert recovery.fallback_used is True
    assert recovery.recovery_status == RecoveryStatus.RECOVERED_WITH_FALLBACK
    assert recovery.spoken_recovery_guidance is not None


if __name__ == "__main__":
    test_full_navigation_orchestration()
    test_pipeline_error_recovery_graceful_handling()
    print("Integration test_task_pipeline.py passed successfully!")
