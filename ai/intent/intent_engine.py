"""
Sahayak AI — Enhanced Intent Engine
Hybrid natural language understanding engine for intent classification, entity extraction,
and ambiguity resolution across English, Hindi, and Hinglish.
Supports optional Gemini LLM acceleration with zero-dependency offline fallback.
"""

import os
import re
from typing import Dict, Any, Tuple, Optional, List
from shared.schemas.models import TaskType, AccessibilityTwin, LanguagePreference


class IntentEngine:
    def __init__(self):
        # Multilingual keyword taxonomy with weighted scoring
        self._intent_patterns = {
            TaskType.FORM_COMPLETION: {
                "keywords": [
                    "fill", "form", "apply", "application", "scholarship form",
                    "register", "registration", "submit", "admission",
                    "भरने", "आवेदन", "फॉर्म", "रजिस्ट्रेशन", "दाखिला", "जमा",
                    "bharna", "form bharo", "apply karna"
                ],
                "weight": 1.2,
            },
            TaskType.UNDERSTAND_DOCUMENT: {
                "keywords": [
                    "notice", "document", "important", "deadline", "circular",
                    "announcement", "guidelines", "last date", "explain notice",
                    "नोटिस", "दस्तावेज़", "ज़रूरी", "तारीख", "लास्ट डेट", "सूचना", "नियम",
                    "kya likha hai", "samjha do", "notice padho"
                ],
                "weight": 1.1,
            },
            TaskType.COMMUNICATE: {
                "keywords": [
                    "saying", "communicate", "talk", "sign", "isl", "gesture",
                    "caption", "speech", "deaf", "interpreter",
                    "बात", "इशारा", "सांकेतिक", "बोल", "सुनना", "इशारे",
                    "ishara", "sign language", "baat karni hai"
                ],
                "weight": 1.1,
            },
            TaskType.FIND_OBJECT: {
                "keywords": [
                    "find", "locate", "where is", "where's", "bottle", "keys", "wallet",
                    "spectacles", "glasses", "medicine", "search object",
                    "ढूंढो", "कहाँ है", "बोतल", "चाबी", "चश्मा", "दवा", "सर्च",
                    "kahan hai", "dhundo", "chashma", "dawai", "paani"
                ],
                "weight": 1.2,
            },
            TaskType.SEE: {
                "keywords": [
                    "see", "look", "describe", "surroundings", "in front", "obstacle",
                    "what is ahead", "environment", "room description",
                    "देखो", "सामने", "क्या है", "रास्ता", "रुकावट", "चारों तरफ",
                    "aage kya hai", "dekho", "kya dikh raha hai"
                ],
                "weight": 1.0,
            },
            TaskType.READ: {
                "keywords": [
                    "read", "ocr", "text on", "board", "signboard", "menu", "label",
                    "heading", "reading", "read aloud",
                    "पढ़ो", "बोर्ड", "लिखा", "लेबल", "पढ़कर सुनाओ",
                    "padh kar sunao", "board par kya hai"
                ],
                "weight": 1.0,
            },
        }

        # Common object keywords for entity extraction
        self._object_catalog = [
            "bottle", "water bottle", "keys", "wallet", "glasses", "spectacles",
            "medicine", "phone", "pen", "bag", "cup", "plate", "door", "chair",
            "बोतल", "चाबी", "बटुआ", "चश्मा", "दवा", "दवाई", "फ़ोन", "कुर्सी", "दरवाज़ा"
        ]

    def _extract_entities(self, query: str) -> Dict[str, Any]:
        """Extracts contextual entities (target objects, dates, document references)."""
        q_lower = query.lower()
        entities: Dict[str, Any] = {
            "target_object": None,
            "detected_language": "en",
        }

        # Check for Hindi/Devanagari characters
        if re.search(r'[\u0900-\u097F]', query):
            entities["detected_language"] = "hi"

        # Extract target object if present
        for obj in self._object_catalog:
            if obj in q_lower:
                entities["target_object"] = obj
                break

        return entities

    def _call_gemini_intent(self, query: str) -> Optional[Tuple[TaskType, float, str]]:
        """Optional Gemini LLM classifier if API key is configured."""
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            return None

        try:
            from google import genai
            client = genai.Client(api_key=api_key)
            prompt = (
                f"You are an intent classification engine for an accessibility assistant. "
                f"User query: '{query}'. "
                f"Classify into exactly one of: FORM_COMPLETION, UNDERSTAND_DOCUMENT, COMMUNICATE, "
                f"FIND_OBJECT, SEE, READ. "
                f"Return in format: TASK_TYPE|CONFIDENCE|REASON"
            )
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
            )
            if response and response.text:
                parts = response.text.strip().split("|")
                if len(parts) >= 2:
                    tt_name = parts[0].strip()
                    conf = float(parts[1].strip())
                    reason = parts[2].strip() if len(parts) > 2 else "Classified by Gemini 2.5 Flash"
                    for tt in TaskType:
                        if tt.value == tt_name:
                            return tt, conf, reason
        except Exception:
            # Gracefully degrade to offline heuristic on any network/API issue
            pass
        return None

    def analyze_intent(
        self,
        query: str,
        twin: Optional[AccessibilityTwin] = None,
        twin_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Deep analysis returning candidate scores, extracted entities, and ambiguity status.
        """
        if not query or not str(query).strip():
            return {
                "task_type": TaskType.SEE,
                "intent": TaskType.SEE.value,
                "confidence": 0.50,
                "rationale": "Empty query defaulted to SEE",
                "entities": {"target_object": None, "detected_language": "en"},
                "is_ambiguous": False,
                "disambiguation_options": [],
                "source": "empty_fallback",
            }

        # Check LLM first if available
        llm_result = self._call_gemini_intent(query)
        if llm_result:
            tt, conf, reason = llm_result
            return {
                "task_type": tt,
                "intent": tt.value,
                "confidence": conf,
                "rationale": reason,
                "entities": self._extract_entities(query),
                "is_ambiguous": False,
                "disambiguation_options": [],
                "source": "gemini_llm",
            }

        q = str(query).lower().strip()
        scores: Dict[TaskType, float] = {}

        for task_type, config in self._intent_patterns.items():
            kw_list = config["keywords"]
            weight = config["weight"]
            match_count = sum(1 for kw in kw_list if kw in q)
            scores[task_type] = match_count * weight

        # Sort tasks by score descending
        sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        top_task, top_score = sorted_scores[0]
        second_task, second_score = sorted_scores[1]

        # Check for ambiguity
        is_ambiguous = (top_score > 0 and (top_score - second_score) < 0.3 and second_score > 0)
        confidence = min(0.95, 0.60 + (top_score * 0.15)) if top_score > 0 else 0.50

        rationale = (
            f"Matched score {top_score:.1f} for {top_task.value} from query '{query}'"
            if top_score > 0
            else f"No dominant pattern matched in '{query}', defaulted to {top_task.value}"
        )

        options = []
        if is_ambiguous:
            options = [
                {"task_type": top_task.value, "label": f"Proceed with {top_task.value}"},
                {"task_type": second_task.value, "label": f"Switch to {second_task.value}"},
            ]

        return {
            "task_type": top_task,
            "intent": top_task.value,
            "confidence": round(confidence, 2),
            "rationale": rationale,
            "entities": self._extract_entities(query),
            "is_ambiguous": is_ambiguous,
            "disambiguation_options": options,
            "source": "semantic_rules",
        }

    def classify_intent(
        self,
        query: str,
        twin: Optional[AccessibilityTwin] = None,
        twin_id: Optional[str] = None,
    ) -> Tuple[TaskType, float, str]:
        """
        Backwards-compatible interface returning (TaskType, confidence, rationale).
        """
        analysis = self.analyze_intent(query, twin=twin, twin_id=twin_id)
        return analysis["task_type"], analysis["confidence"], analysis["rationale"]
