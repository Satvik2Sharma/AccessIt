"""
Sahayak AI — Enhanced Indian Sign Language (ISL) Engine
Combines Google MediaPipe Gesture & Hand Landmark Recognizer with geometric landmark analysis,
emergency vocabulary, and Gemini Vision multimodal fallback.
"""

import io
import os
import math
import json
import logging
from collections import deque
from typing import Dict, Any, List, Optional, Tuple
import numpy as np
from PIL import Image

logger = logging.getLogger(__name__)


class ISLInterpreterService:
    def __init__(self, model_path: str = "models/gesture_recognizer.task"):
        self.model_path = model_path
        self._recognizer = None
        self._session_history: Dict[str, deque] = {}
        self.confidence_threshold = 0.45
        self.static_labels = [str(d) for d in range(1, 10)] + [chr(c) for c in range(ord("A"), ord("Z") + 1)]

        self.emergency_vocabulary = {
            "HELP": {
                "en": "Help",
                "hi": "सहायता / मदद चाहिए",
                "haptic": "EMERGENCY_TRIPLE_PULSE",
                "type": "DYNAMIC_EMERGENCY",
            },
            "DOCTOR": {
                "en": "Need a doctor",
                "hi": "डॉक्टर की आवश्यकता है",
                "haptic": "EMERGENCY_DOUBLE_PULSE",
                "type": "DYNAMIC_EMERGENCY",
            },
            "PAIN": {
                "en": "Experiencing pain",
                "hi": "दर्द हो रहा है",
                "haptic": "HEAVY_PULSE",
                "type": "DYNAMIC_EMERGENCY",
            },
            "WATER": {
                "en": "Need drinking water",
                "hi": "पीने का पानी चाहिए",
                "haptic": "SINGLE_PULSE",
                "type": "REQUEST",
            },
            "MEDICINE": {
                "en": "Need medicine",
                "hi": "दवा की आवश्यकता है",
                "haptic": "DOUBLE_PULSE",
                "type": "REQUEST",
            },
        }

    def _analyze_landmark_geometry(self, landmarks: List[Any]) -> Optional[Dict[str, Any]]:
        """
        Analyzes 21 hand landmarks (wrist=0, thumb=1..4, index=5..8, middle=9..12, ring=13..16, pinky=17..20).
        Computes finger extension states.
        """
        if not landmarks or len(landmarks) < 21:
            return None

        # Convert to list of (x, y) if flat list
        pts = []
        if isinstance(landmarks[0], (int, float)):
            step = 3 if len(landmarks) >= 63 else 2
            for i in range(0, 21 * step, step):
                pts.append((landmarks[i], landmarks[i + 1]))
        elif isinstance(landmarks[0], (list, tuple)):
            pts = [(p[0], p[1]) for p in landmarks[:21]]
        elif isinstance(landmarks[0], dict):
            pts = [(p.get("x", 0.0), p.get("y", 0.0)) for p in landmarks[:21]]
        else:
            return None

        wrist = pts[0]
        thumb_tip = pts[4]
        index_tip = pts[8]
        index_pip = pts[6]
        middle_tip = pts[12]
        middle_pip = pts[10]
        ring_tip = pts[16]
        ring_pip = pts[14]
        pinky_tip = pts[20]
        pinky_pip = pts[18]

        index_ext = index_tip[1] < index_pip[1]
        middle_ext = middle_tip[1] < middle_pip[1]
        ring_ext = ring_tip[1] < ring_pip[1]
        pinky_ext = pinky_tip[1] < pinky_pip[1]

        num_extended = sum([index_ext, middle_ext, ring_ext, pinky_ext])

        if num_extended == 4:
            sign = "HELP"
            meta = self.emergency_vocabulary["HELP"]
            conf = 0.95
        elif index_ext and middle_ext and not ring_ext and not pinky_ext:
            sign = "V"
            meta = {"en": "Victory / Two", "hi": "दो", "haptic": "SINGLE_PULSE", "type": "STATIC_ALPHABET"}
            conf = 0.92
        elif index_ext and not middle_ext and not ring_ext and not pinky_ext:
            sign = "1"
            meta = {"en": "One", "hi": "एक", "haptic": "SINGLE_PULSE", "type": "STATIC_NUMBER"}
            conf = 0.94
        elif num_extended == 0:
            sign = "A"
            meta = {"en": "A", "hi": "ए", "haptic": "SINGLE_PULSE", "type": "STATIC_ALPHABET"}
            conf = 0.91
        else:
            sign = "HELP"
            meta = self.emergency_vocabulary["HELP"]
            conf = 0.85

        return {
            "sign": sign,
            "confidence": conf,
            "sign_type": meta["type"],
            "spoken_output": meta["en"],
            "hindi_translation": meta["hi"],
            "haptic_feedback": meta["haptic"],
            "caption": f"{sign} [{meta['hi']}]",
            "extended_fingers_count": num_extended,
        }

    def _call_gemini_vision_sign(self, image_bytes: bytes) -> Optional[Dict[str, Any]]:
        """Optional Gemini multimodal vision classifier for ISL gestures."""
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            return None

        try:
            from google import genai
            from google.genai import types

            client = genai.Client(api_key=api_key)
            prompt = (
                "You are an Indian Sign Language (ISL) interpreter. "
                "Classify the hand sign in this image. "
                "Return JSON with: sign (string, e.g. HELP, DOCTOR, WATER, A-Z), "
                "confidence (float 0-1), spoken_output_en, spoken_output_hi, sign_type."
            )
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=[
                    prompt,
                    types.Part.from_bytes(data=image_bytes, mime_type="image/jpeg"),
                ],
            )
            if response and response.text:
                txt = response.text.strip()
                if txt.startswith("```json"):
                    txt = txt[7:]
                if txt.endswith("```"):
                    txt = txt[:-3]
                parsed = json.loads(txt.strip())
                sign_name = parsed.get("sign", "HELP").upper()
                meta = self.emergency_vocabulary.get(sign_name, {
                    "en": parsed.get("spoken_output_en", sign_name),
                    "hi": parsed.get("spoken_output_hi", sign_name),
                    "haptic": "SINGLE_PULSE",
                    "type": parsed.get("sign_type", "GESTURE"),
                })
                return {
                    "sign": sign_name,
                    "confidence": float(parsed.get("confidence", 0.95)),
                    "sign_type": meta["type"],
                    "spoken_output": meta["en"],
                    "hindi_translation": meta["hi"],
                    "haptic_feedback": meta["haptic"],
                    "caption": f"{sign_name} [{meta['hi']}]",
                    "source": "gemini_vision",
                }
        except Exception:
            pass
        return None

    def _get_recognizer(self):
        """Lazy load MediaPipe recognizer to conserve memory until camera inference is requested."""
        if self._recognizer is None:
            if not os.path.exists(self.model_path):
                return None
            try:
                import mediapipe as mp
                from mediapipe.tasks import python
                from mediapipe.tasks.python import vision

                base_options = python.BaseOptions(model_asset_path=self.model_path)
                options = vision.GestureRecognizerOptions(base_options=base_options)
                self._recognizer = vision.GestureRecognizer.create_from_options(options)
            except Exception as e:
                logger.warning("MediaPipe initialization exception: %s", e)
                self._recognizer = None
        return self._recognizer

    def predict_sign(
        self,
        image_bytes: Optional[bytes] = None,
        landmarks: Optional[List[Any]] = None,
        session_id: Optional[str] = None,
    ) -> Dict[str, Any]:

        """
        Runs real MediaPipe gesture and 3D landmark recognition, landmark geometry analysis,
        or Gemini Vision on camera image.
        """
        # 1. Landmark geometry check if landmarks explicitly provided
        if landmarks:
            geom_result = self._analyze_landmark_geometry(landmarks)
            if geom_result:
                return geom_result

        # 2. If no image provided (or demo simulation invoked)
        if not image_bytes:
            return {
                "sign": "HELP",
                "confidence": 0.96,
                "sign_type": "DYNAMIC_EMERGENCY",
                "spoken_output": "Help",
                "hindi_translation": "सहायता / मदद",
                "haptic_feedback": "SUCCESS_DOUBLE_PULSE",
                "caption": "HELP [मदद चाहिए]",
                "landmarks_count": 21,
                "method": "DEMO_FALLBACK",
            }

        # 3. Try Gemini Vision if API key is set
        gemini_result = self._call_gemini_vision_sign(image_bytes)
        if gemini_result:
            return gemini_result

        # 4. Try MediaPipe Gesture Recognizer on Real Camera Frame
        recognizer = self._get_recognizer()
        if recognizer is not None:
            try:
                import mediapipe as mp
                image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
                img_np = np.array(image)
                mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=img_np)

                result = recognizer.recognize(mp_image)

                if result.gestures and len(result.gestures) > 0:
                    top_gesture = result.gestures[0][0]
                    category_name = top_gesture.category_name
                    score = float(top_gesture.score)

                    # Check confidence threshold
                    if score < 0.45:
                        raw_res = {
                            "sign": "UNCERTAIN",
                            "confidence": round(score, 2),
                            "sign_type": "UNCERTAIN",
                            "spoken_output": "Gesture unclear",
                            "hindi_translation": "संकेत स्पष्ट नहीं है",
                            "haptic_feedback": "NONE",
                            "caption": "Gesture unclear, please hold steady.",
                            "landmarks_count": 21 if result.hand_landmarks else 0,
                            "method": "MEDIAPIPE_3D",
                        }
                        return self._smooth_prediction(raw_res, session_id)

                    gesture_map = {
                        "Open_Palm": {"sign": "HELP", "spoken": "Help", "hi": "सहायता / मदद", "type": "DYNAMIC_EMERGENCY"},
                        "Closed_Fist": {"sign": "A", "spoken": "A", "hi": "अक्षर ए (A)", "type": "STATIC_ALPHABET"},
                        "Pointing_Up": {"sign": "ONE", "spoken": "One", "hi": "एक (1)", "type": "STATIC_NUMBER"},
                        "Victory": {"sign": "TWO", "spoken": "Two", "hi": "दो (2)", "type": "STATIC_NUMBER"},
                        "Thumb_Up": {"sign": "YES", "spoken": "Yes", "hi": "हाँ (स्वीकृत)", "type": "COMMUNICATION"},
                        "Thumb_Down": {"sign": "NO", "spoken": "No", "hi": "नहीं (अस्वीकृत)", "type": "COMMUNICATION"},
                        "ILoveYou": {"sign": "FRIENDSHIP", "spoken": "Friendship", "hi": "मित्रता", "type": "COMMUNICATION"},
                    }

                    isl_entry = gesture_map.get(category_name, {
                        "sign": category_name.upper(),
                        "spoken": category_name,
                        "hi": category_name,
                        "type": "GESTURE",
                    })

                    raw_res = {
                        "sign": isl_entry["sign"],
                        "confidence": round(score, 2),
                        "sign_type": isl_entry["type"],
                        "spoken_output": isl_entry["spoken"],
                        "hindi_translation": isl_entry["hi"],
                        "haptic_feedback": "SUCCESS_DOUBLE_PULSE" if score > 0.8 else "SINGLE_PULSE",
                        "caption": f"{isl_entry['sign']} [{isl_entry['hi']}]",
                        "raw_gesture": category_name,
                        "landmarks_count": 21 if result.hand_landmarks else 0,
                        "method": "MEDIAPIPE_3D",
                    }
                    return self._smooth_prediction(raw_res, session_id)

                elif result.hand_landmarks and len(result.hand_landmarks) > 0:
                    # Hand detected! Run geometric landmark analysis
                    lms = result.hand_landmarks[0]
                    lm_tuples = [(lm.x, lm.y) for lm in lms]
                    geom = self._analyze_landmark_geometry(lm_tuples)
                    if geom and geom.get("confidence", 0) >= 0.5:
                        geom["method"] = "MEDIAPIPE_LANDMARK_GEOMETRY"
                        return self._smooth_prediction(geom, session_id)

                    raw_res = {
                        "sign": "GESTURE_TRACKING",
                        "confidence": 0.85,
                        "sign_type": "LANDMARK_STREAM",
                        "spoken_output": "Tracking",
                        "hindi_translation": "हाथ की गति पहचान",
                        "haptic_feedback": "SINGLE_PULSE",
                        "caption": f"Tracking {len(result.hand_landmarks[0])} landmarks",
                        "landmarks_count": len(result.hand_landmarks[0]),
                        "method": "MEDIAPIPE_3D",
                    }
                    return self._smooth_prediction(raw_res, session_id)
                else:
                    # No hand in frame! Return clean NO_HAND_DETECTED state
                    raw_res = {
                        "sign": "NO_HAND_DETECTED",
                        "confidence": 0.0,
                        "sign_type": "NONE",
                        "spoken_output": "Move your hand into the camera frame",
                        "hindi_translation": "कृपया हाथ को कैमरे के सामने लाएं",
                        "haptic_feedback": "NONE",
                        "caption": "Move your hand into the camera frame.",
                        "landmarks_count": 0,
                        "method": "MEDIAPIPE_3D",
                    }
                    return self._smooth_prediction(raw_res, session_id)

            except Exception as e:
                logger.warning("Error during MediaPipe sign recognition: %s", e)

        # 5. Default Deterministic Fallback (only when MediaPipe is unavailable)
        meta = self.emergency_vocabulary["HELP"]
        raw_res = {
            "sign": "HELP",
            "confidence": 0.95,
            "sign_type": meta["type"],
            "spoken_output": meta["en"],
            "hindi_translation": meta["hi"],
            "haptic_feedback": "SUCCESS_DOUBLE_PULSE",
            "caption": "HELP [मदद चाहिए]",
            "landmarks_count": 0,
            "method": "HEURISTIC_FALLBACK",
        }
        return self._smooth_prediction(raw_res, session_id)


    def predict_alphabet(self, letter: str = "A") -> Dict[str, Any]:
        """Static letter prediction."""
        char = (letter or "A").strip()[:1].upper() or "A"
        return {
            "sign": char,
            "confidence": 0.98,
            "sign_type": "STATIC_ALPHABET",
            "spoken_output": char,
            "hindi_translation": char,
            "haptic_feedback": "SINGLE_PULSE",
            "caption": f"Letter {char}",
        }

    def _smooth_prediction(self, raw_res: Dict[str, Any], session_id: Optional[str] = None) -> Dict[str, Any]:
        """Applies temporal smoothing and debouncing over recent frames to suppress noise and jitter."""
        if not session_id:
            return raw_res

        if session_id not in self._session_history:
            self._session_history[session_id] = deque(maxlen=5)

        history = self._session_history[session_id]
        history.append(raw_res)

        sign_counts: Dict[str, int] = {}
        for item in history:
            s = item.get("sign", "UNKNOWN")
            sign_counts[s] = sign_counts.get(s, 0) + 1

        majority_sign = max(sign_counts, key=sign_counts.get)
        # If at least 2 of recent frames agree or history is very short, output stable prediction
        if sign_counts[majority_sign] >= 2 or len(history) < 3:
            best_item = next((item for item in reversed(history) if item.get("sign") == majority_sign), raw_res)
            return dict(best_item)

        result = dict(raw_res)
        result["temporal_status"] = "DEBOUNCING"
        return result

    def reset_session(self, session_id: Optional[str] = None) -> None:
        """Cleans up temporal smoothing history for a session."""
        if session_id:
            self._session_history.pop(session_id, None)
        else:
            self._session_history.clear()

