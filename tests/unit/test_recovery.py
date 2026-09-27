import pytest
from ai.recovery.failure_detector import FailureDetector
from ai.recovery.recovery_engine import RecoveryEngine
from shared.schemas.models import RecoveryAction

def test_ocr_failure_detected():
    detector = FailureDetector()
    result = detector.check_ocr({"confidence": 0.2, "raw_ocr_elements_count": 0})
    assert result is not None
    assert result["type"] == "ocr_low_confidence"

def test_ocr_no_failure():
    detector = FailureDetector()
    result = detector.check_ocr({"confidence": 0.95, "raw_ocr_elements_count": 10})
    assert result is None

def test_isl_failure_detected():
    detector = FailureDetector()
    result = detector.check_isl({"confidence": 0.3, "sign": "SEARCHING"})
    assert result is not None
    assert result["type"] == "isl_unrecognized"

def test_form_retry_failure():
    detector = FailureDetector()
    result = detector.check_form_retries("aadhaar", 3)
    assert result is not None
    assert result["type"] == "form_repeated_failure"

def test_form_no_failure():
    detector = FailureDetector()
    result = detector.check_form_retries("aadhaar", 1)
    assert result is None

def test_speech_failure():
    detector = FailureDetector()
    result = detector.check_speech({"voice_command": {"raw_text": "", "source": "stt_failed"}})
    assert result is not None
    assert result["type"] == "unclear_speech"

def test_recovery_ocr():
    engine = RecoveryEngine()
    action = engine.recover({"type": "ocr_low_confidence", "confidence": 0.2})
    assert isinstance(action, RecoveryAction)
    assert action.strategy == "reposition_camera"
    assert action.can_retry is True

def test_recovery_form():
    engine = RecoveryEngine()
    action = engine.recover({"type": "form_repeated_failure", "field_id": "aadhaar"})
    assert action.strategy == "explain_format"

def test_recovery_unknown():
    engine = RecoveryEngine()
    action = engine.recover({"type": "totally_unknown_error"})
    assert action.strategy == "generic_retry"

def test_recovery_many_prioritized():
    engine = RecoveryEngine()
    failures = [
        {"type": "unclear_speech"},
        {"type": "task_timeout"},
        {"type": "ocr_low_confidence", "confidence": 0.1},
    ]
    actions = engine.recover_many(failures)
    assert len(actions) == 3
    assert actions[0].failure_type == "task_timeout"
