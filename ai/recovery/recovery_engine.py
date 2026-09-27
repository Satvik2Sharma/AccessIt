"""
Sahayak AI — Recovery Engine
Context-aware error recovery strategy generator.
Does NOT create infinite retry loops.
"""
from typing import Dict, Any, Optional, List
from shared.schemas.models import RecoveryAction


class RecoveryEngine:
    """
    Generates RecoveryAction strategies for different failure types.
    All strategies have bounded retry limits.
    Integrates with the existing Task Engine and Verification Service
    to preserve already-valid form fields.
    """

    STRATEGIES: Dict[str, Dict[str, Any]] = {
        "ocr_low_confidence": {
            "strategy": "reposition_camera",
            "description": "OCR confidence too low — image may be blurry or poorly lit.",
            "description_hi": "OCR सटीकता कम है — छवि धुंधली या खराब रोशनी में हो सकती है।",
            "user_instruction": "Please reposition the camera closer to the document and ensure good lighting.",
            "user_instruction_hi": "कृपया कैमरे को दस्तावेज़ के नजदीक रखें और अच्छी रोशनी सुनिश्चित करें।",
            "can_retry": True,
            "max_retries": 3,
        },
        "isl_unrecognized": {
            "strategy": "gesture_retry",
            "description": "Hand gesture was not recognized. Please hold the gesture steady.",
            "description_hi": "हाथ का संकेत पहचाना नहीं गया। कृपया संकेत को स्थिर रखें।",
            "user_instruction": "Hold your hand steady in front of the camera with fingers clearly visible.",
            "user_instruction_hi": "अपना हाथ कैमरे के सामने स्थिर रखें, उंगलियाँ स्पष्ट दिखनी चाहिए।",
            "can_retry": True,
            "max_retries": 3,
        },
        "form_repeated_failure": {
            "strategy": "explain_format",
            "description": "Field validation failed multiple times.",
            "description_hi": "फ़ील्ड सत्यापन कई बार विफल हुआ।",
            "user_instruction": "The input format is incorrect. Please check the expected format and try again.",
            "user_instruction_hi": "इनपुट प्रारूप गलत है। कृपया अपेक्षित प्रारूप जांचें और पुनः प्रयास करें।",
            "can_retry": True,
            "max_retries": 2,
        },
        "unclear_speech": {
            "strategy": "repeat_prompt",
            "description": "Speech was not recognized. Please speak clearly.",
            "description_hi": "भाषण पहचाना नहीं गया। कृपया स्पष्ट बोलें।",
            "user_instruction": "Please speak clearly and try again, or type your answer.",
            "user_instruction_hi": "कृपया स्पष्ट बोलें और पुनः प्रयास करें, या अपना उत्तर टाइप करें।",
            "can_retry": True,
            "max_retries": 3,
        },
        "task_timeout": {
            "strategy": "save_and_resume",
            "description": "Task took too long. Progress has been saved.",
            "description_hi": "कार्य में बहुत समय लगा। प्रगति सहेजी गई है।",
            "user_instruction": "Your progress has been saved. You can resume this task anytime.",
            "user_instruction_hi": "आपकी प्रगति सहेजी गई है। आप इस कार्य को कभी भी जारी रख सकते हैं।",
            "can_retry": False,
            "max_retries": 0,
        },
        "unknown": {
            "strategy": "generic_retry",
            "description": "An unexpected error occurred.",
            "description_hi": "एक अप्रत्याशित त्रुटि हुई।",
            "user_instruction": "Something went wrong. Please try again.",
            "user_instruction_hi": "कुछ गलत हुआ। कृपया पुनः प्रयास करें।",
            "can_retry": True,
            "max_retries": 2,
        },
    }

    def recover(self, failure: Dict[str, Any]) -> RecoveryAction:
        """
        Generate a RecoveryAction for a given failure dict.

        Args:
            failure: failure dict from FailureDetector (must have 'type' key)

        Returns:
            RecoveryAction with strategy and user instructions
        """
        failure_type = failure.get("type", "unknown")
        strategy = self.STRATEGIES.get(failure_type, self.STRATEGIES["unknown"])
        return RecoveryAction(
            failure_type=failure_type,
            strategy=strategy["strategy"],
            description=strategy["description"],
            description_hi=strategy.get("description_hi"),
            can_retry=strategy["can_retry"],
            max_retries=strategy["max_retries"],
            user_instruction=strategy["user_instruction"],
            user_instruction_hi=strategy.get("user_instruction_hi"),
        )

    def recover_many(self, failures: List[Dict[str, Any]]) -> List[RecoveryAction]:
        """Recover from multiple failures, prioritized by severity."""
        priority_order = [
            "task_timeout", "form_repeated_failure", "ocr_low_confidence",
            "isl_unrecognized", "unclear_speech", "unknown"
        ]
        sorted_failures = sorted(
            failures,
            key=lambda f: priority_order.index(f.get("type", "unknown"))
            if f.get("type") in priority_order else len(priority_order)
        )
        return [self.recover(f) for f in sorted_failures]
