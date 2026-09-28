"""
Sahayak AI — Failure Detector
Detects failure conditions across OCR, ISL, navigation, voice, and form completion.
"""
from typing import Dict, Any, Optional, List


FAILURE_THRESHOLDS = {
    "ocr_min_confidence": 0.40,
    "isl_min_confidence": 0.50,
    "max_form_retries": 3,
    "task_timeout_seconds": 120.0,
}


class FailureDetector:
    """
    Identifies failure conditions from AI component outputs.
    Returns structured failure dicts for the RecoveryEngine.
    """

    def check_ocr(self, ocr_result: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Detect low-confidence or empty OCR results."""
        if not ocr_result:
            return {
                "type": "ocr_low_confidence",
                "confidence": 0.0,
                "elements_found": 0,
                "message": "OCR could not extract sufficient text from the image.",
            }
        confidence = ocr_result.get("confidence", 1.0)
        element_count = ocr_result.get("raw_ocr_elements_count", -1)
        if element_count == 0 or confidence < FAILURE_THRESHOLDS["ocr_min_confidence"]:
            return {
                "type": "ocr_low_confidence",
                "confidence": confidence,
                "elements_found": element_count,
                "message": "OCR could not extract sufficient text from the image.",
            }
        return None

    def check_isl(self, isl_result: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Detect unrecognized or low-confidence ISL gestures."""
        if not isl_result:
            return {
                "type": "isl_unrecognized",
                "confidence": 0.0,
                "sign": "",
                "message": "Hand gesture could not be recognized.",
            }
        confidence = isl_result.get("confidence", 1.0)
        sign = isl_result.get("sign", "")
        if confidence < FAILURE_THRESHOLDS["isl_min_confidence"] or sign == "SEARCHING":
            return {
                "type": "isl_unrecognized",
                "confidence": confidence,
                "sign": sign,
                "message": "Hand gesture could not be recognized.",
            }
        return None

    def check_form_retries(
        self,
        field_id: str,
        retry_count: int,
        last_error: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        """Detect repeated form validation failures."""
        if retry_count >= FAILURE_THRESHOLDS["max_form_retries"]:
            return {
                "type": "form_repeated_failure",
                "field_id": field_id,
                "retry_count": retry_count,
                "last_error": last_error or "Invalid input",
                "message": f"Field '{field_id}' failed validation {retry_count} times.",
            }
        return None

    def check_speech(self, voice_cmd_result: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Detect unclear or empty speech input."""
        if not voice_cmd_result:
            return {
                "type": "unclear_speech",
                "raw_text": "",
                "message": "Speech was not recognized clearly.",
            }
        voice_cmd = voice_cmd_result.get("voice_command") or {}
        raw_text = voice_cmd.get("raw_text", "")
        source = voice_cmd.get("source", "")
        if not raw_text or source == "stt_failed" or raw_text == "[speech input]":
            return {
                "type": "unclear_speech",
                "raw_text": raw_text,
                "message": "Speech was not recognized clearly.",
            }
        return None

    def check_task_timeout(
        self,
        elapsed_seconds: float,
        task_id: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        """Detect task timeout."""
        if elapsed_seconds > FAILURE_THRESHOLDS["task_timeout_seconds"]:
            return {
                "type": "task_timeout",
                "task_id": task_id,
                "elapsed_seconds": elapsed_seconds,
                "message": f"Task exceeded {FAILURE_THRESHOLDS['task_timeout_seconds']}s.",
            }
        return None
