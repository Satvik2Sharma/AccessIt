"""
Sahayak AI — Intent Engine
Classifies user intent from natural language voice/text queries into standard Task types.
"""

from typing import Dict, Any, Tuple
from shared.schemas.models import TaskType, AccessibilityTwin


class IntentEngine:
    def __init__(self):
        # Keyword & pattern taxonomy for zero-latency, reliable hackathon inference
        self._intent_patterns = {
            TaskType.FORM_COMPLETION: [
                "fill", "form", "apply", "application", "scholarship form",
                "भरने", "आवेदन", "फॉर्म", "रजिस्ट्रेशन", "register", "submit"
            ],
            TaskType.UNDERSTAND_DOCUMENT: [
                "notice", "document", "important", "deadline", "circular",
                "नोटिस", "दस्तावेज़", "ज़रूरी", "तारीख", "लास्ट डेट", "explain notice"
            ],
            TaskType.COMMUNICATE: [
                "saying", "communicate", "talk", "sign", "isl", "gesture",
                "बात", "इशारा", "सांकेतिक", "बोल", "सुनना", "caption"
            ],
            TaskType.FIND_OBJECT: [
                "find", "locate", "where is", "bottle", "keys", "wallet",
                "ढूंढो", "कहाँ है", "बोतल", "चाबी", "सर्च"
            ],
            TaskType.SEE: [
                "see", "look", "describe", "surroundings", "in front", "obstacle",
                "देखो", "सामने", "क्या है", "रास्ता"
            ],
            TaskType.READ: [
                "read", "ocr", "text on", "board", "signboard",
                "पढ़ो", "बोर्ड", "लिखा"
            ],
        }

    def classify_intent(self, query: str, twin: AccessibilityTwin) -> Tuple[TaskType, float, str]:
        """
        Classifies user query into (TaskType, confidence, rationale).
        """
        q = query.lower().strip()
        best_match = TaskType.UNDERSTAND_DOCUMENT
        max_score = 0

        for task_type, keywords in self._intent_patterns.items():
            matches = sum(1 for kw in keywords if kw in q)
            if matches > max_score:
                max_score = matches
                best_match = task_type

        confidence = 0.95 if max_score >= 1 else 0.60
        rationale = f"Matched {max_score} intent keyword(s) in query '{query}'"
        return best_match, confidence, rationale
