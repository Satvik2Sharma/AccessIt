"""
Sahayak AI — Error Recovery Package
Provides failure condition detection and bounded recovery strategy generation.
"""

from ai.recovery.failure_detector import FailureDetector, FAILURE_THRESHOLDS
from ai.recovery.recovery_engine import RecoveryEngine

__all__ = [
    "FailureDetector",
    "FAILURE_THRESHOLDS",
    "RecoveryEngine",
]
