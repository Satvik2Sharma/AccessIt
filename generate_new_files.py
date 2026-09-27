import os

def append_to_file(path, content):
    with open(path, 'a', encoding='utf-8') as f:
        f.write("\n" + content + "\n")

def write_file(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)

# 1. shared/schemas/models.py
models_ext = """
# ====================================================
# NEW EXTENDED SCHEMAS (Phase 2)
# ====================================================

class SpatialObject(BaseModel):
    \"\"\"A detected physical object with spatial metadata.\"\"\"
    label: str
    confidence: float = Field(ge=0.0, le=1.0)
    bbox: Optional[List[float]] = None  # [xmin, ymin, xmax, ymax] normalized 0-1
    direction: Optional[str] = None  # e.g. "2 o'clock"
    horizontal_zone: Optional[str] = None  # left, center, right
    elevation: Optional[str] = None  # eye_level, table_level, floor_level
    proximity: Optional[str] = None  # very_close, arm_reach, nearby, several_steps
    associated_text: Optional[str] = None
    haptic_cue: Optional[str] = None


class SceneAnalysis(BaseModel):
    \"\"\"Full structured scene representation.\"\"\"
    objects: List[SpatialObject] = Field(default_factory=list)
    text_regions: List[str] = Field(default_factory=list)
    labels: List[str] = Field(default_factory=list)
    spatial_relationships: List[str] = Field(default_factory=list)
    hazards: List[str] = Field(default_factory=list)
    relevant_objects: List[SpatialObject] = Field(default_factory=list)
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    task_context: Optional[str] = None
    summary: Optional[str] = None


class VoiceCommand(BaseModel):
    \"\"\"Represents a parsed voice utterance.\"\"\"
    raw_text: str
    language: str = "English"
    intent: Optional[str] = None
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    entities: Dict[str, Any] = Field(default_factory=dict)
    source: str = "stt"  # stt, text_input, test


class NavigationInstruction(BaseModel):
    \"\"\"A single navigation guidance instruction.\"\"\"
    direction: str  # left, right, forward, stop, slight_left, slight_right
    description: str
    description_hi: Optional[str] = None
    urgency: str = "NORMAL"  # NORMAL, HIGH, EMERGENCY
    haptic_cue: Optional[str] = None
    obstacle_detected: bool = False
    obstacle_label: Optional[str] = None


class AssistanceResponse(BaseModel):
    \"\"\"Multimodal response from the Assistance Engine.\"\"\"
    text: str
    text_hi: Optional[str] = None
    speech: Optional[str] = None
    haptic: Optional[str] = None
    display_data: Dict[str, Any] = Field(default_factory=dict)
    modality_used: str = "text"  # text, voice, haptic, multimodal
    language: str = "English"


class RecoveryAction(BaseModel):
    \"\"\"An error recovery action suggestion.\"\"\"
    failure_type: str
    strategy: str
    description: str
    description_hi: Optional[str] = None
    can_retry: bool = True
    max_retries: int = 3
    user_instruction: str
    user_instruction_hi: Optional[str] = None


class DocumentQuestion(BaseModel):
    \"\"\"A question posed about a document.\"\"\"
    question: str
    document_context: Optional[str] = None  # extracted text or doc title


class DocumentAnswer(BaseModel):
    \"\"\"An answer grounded in extracted document content.\"\"\"
    question: str
    answer: str
    answer_hi: Optional[str] = None
    source_snippet: Optional[str] = None  # snippet from document that supports answer
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    found_in_document: bool = True


class PersonalizationSuggestion(BaseModel):
    \"\"\"A consented personalization adaptation proposal.\"\"\"
    pattern_type: str  # preferred_language, preferred_modality, barrier_type, etc.
    observation: str
    suggested_adaptation: str
    consent_required: bool = True
    dialog_prompt: str
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    task_count: int = 0
"""
append_to_file(r"C:\Users\HP\.gemini\antigravity\scratch\AccessIt\shared\schemas\models.py", models_ext)

# 2. ai/vision/object_detector.py
write_file(r"C:\Users\HP\.gemini\antigravity\scratch\AccessIt\ai\vision\object_detector.py", '''"""
Sahayak AI — Object Detector Adapter
Provider-agnostic adapter for physical object detection from camera frames.
Supports heuristic baseline (no model required) with optional YOLO/MediaPipe backend.
"""
from typing import List, Optional, Dict, Any
from shared.schemas.models import SpatialObject


class ObjectDetectorAdapter:
    """
    Adapter interface for pluggable object detection backends.
    Default: deterministic heuristic baseline.
    Optional: YOLO, MediaPipe, or Gemini Vision (set via provider param).
    """

    def __init__(self, provider: str = "heuristic"):
        """
        Args:
            provider: 'heuristic' (default/offline), 'gemini' (requires GEMINI_API_KEY),
                      'yolo' (requires ultralytics + model file).
        """
        self.provider = provider
        self._yolo_model = None

    def detect(
        self,
        image_bytes: Optional[bytes] = None,
        target_labels: Optional[List[str]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Detects objects in the given image bytes.
        Returns a list of raw detection dicts with keys:
            label, confidence, bbox (xmin, ymin, xmax, ymax normalized 0-1)
        Falls back to heuristic if image_bytes is None or provider unavailable.
        """
        if image_bytes and self.provider == "gemini":
            result = self._detect_gemini(image_bytes, target_labels)
            if result:
                return result
        if image_bytes and self.provider == "yolo":
            result = self._detect_yolo(image_bytes, target_labels)
            if result:
                return result
        return self._heuristic_detections(target_labels)

    def _detect_gemini(self, image_bytes: bytes, target_labels: Optional[List[str]]) -> Optional[List[Dict[str, Any]]]:
        """Gemini Vision object detection."""
        import os, json
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            return None
        try:
            from google import genai
            from google.genai import types
            client = genai.Client(api_key=api_key)
            label_hint = f" Focus on: {', '.join(target_labels)}." if target_labels else ""
            prompt = (
                f"Detect all visible objects in this image.{label_hint} "
                "Return a JSON array. Each element: "
                '{"label": str, "confidence": float 0-1, "bbox": [xmin, ymin, xmax, ymax] normalized 0-1}.'
                " Return ONLY raw JSON array."
            )
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=[prompt, types.Part.from_bytes(data=image_bytes, mime_type="image/jpeg")],
            )
            if response and response.text:
                txt = response.text.strip().lstrip("```json").rstrip("```").strip()
                return json.loads(txt)
        except Exception as e:
            print(f"Gemini object detection error: {e}")
        return None

    def _detect_yolo(self, image_bytes: bytes, target_labels: Optional[List[str]]) -> Optional[List[Dict[str, Any]]]:
        """YOLO object detection (requires ultralytics)."""
        try:
            import io
            from PIL import Image
            from ultralytics import YOLO
            if self._yolo_model is None:
                self._yolo_model = YOLO("yolov8n.pt")
            img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
            results = self._yolo_model(img, verbose=False)
            detections = []
            for r in results:
                for box in r.boxes:
                    label = r.names[int(box.cls[0])]
                    if target_labels and label.lower() not in [t.lower() for t in target_labels]:
                        continue
                    x1, y1, x2, y2 = box.xyxyn[0].tolist()
                    detections.append({
                        "label": label,
                        "confidence": float(box.conf[0]),
                        "bbox": [x1, y1, x2, y2],
                    })
            return detections if detections else None
        except Exception as e:
            print(f"YOLO object detection error: {e}")
            return None

    def _heuristic_detections(self, target_labels: Optional[List[str]]) -> List[Dict[str, Any]]:
        """Returns deterministic demo detections when no model is available."""
        defaults = [
            {"label": "water bottle", "confidence": 0.91, "bbox": [0.52, 0.25, 0.72, 0.87]},
            {"label": "medicine bottle", "confidence": 0.87, "bbox": [0.10, 0.30, 0.28, 0.80]},
            {"label": "document", "confidence": 0.85, "bbox": [0.20, 0.10, 0.80, 0.90]},
        ]
        if not target_labels:
            return defaults
        label_lower = [t.lower() for t in target_labels]
        filtered = [d for d in defaults if any(l in d["label"].lower() for l in label_lower)]
        return filtered if filtered else defaults[:1]
''')

# 3. ai/vision/clock_direction.py
write_file(r"C:\Users\HP\.gemini\antigravity\scratch\AccessIt\ai\vision\clock_direction.py", '''"""
Sahayak AI — Clock-Face Direction Mapper
Converts normalized bounding-box coordinates to 12-hour clock directions
and horizontal zones for intuitive spatial guidance.
"""
import math
from typing import Tuple, Dict, Any, Optional


class ClockDirectionMapper:
    """
    Maps (x_center, y_center) in normalized image space [0,1]
    to clock-face direction (1–12) and horizontal zone.
    """

    CLOCK_LABELS: Dict[int, str] = {
        1: "1 o'clock", 2: "2 o'clock", 3: "3 o'clock",
        4: "4 o'clock", 5: "5 o'clock", 6: "6 o'clock",
        7: "7 o'clock", 8: "8 o'clock", 9: "9 o'clock",
        10: "10 o'clock", 11: "11 o'clock", 12: "12 o'clock",
    }

    CLOCK_LABELS_HI: Dict[int, str] = {
        1: "1 बजे", 2: "2 बजे", 3: "3 बजे",
        4: "4 बजे", 5: "5 बजे", 6: "6 बजे",
        7: "7 बजे", 8: "8 बजे", 9: "9 बजे",
        10: "10 बजे", 11: "11 बजे", 12: "12 बजे",
    }

    def compute(
        self,
        x_center: float,
        y_center: float,
    ) -> Dict[str, Any]:
        """
        Compute clock direction and horizontal zone from normalized center coordinates.

        Args:
            x_center: horizontal center, 0.0 (left) to 1.0 (right)
            y_center: vertical center, 0.0 (top) to 1.0 (bottom)

        Returns:
            dict with clock_hour (int), direction (str), direction_hi (str),
            horizontal_zone (str)
        """
        dx = x_center - 0.5
        dy = 0.5 - y_center  # invert Y so up=positive
        angle_rad = math.atan2(dx, dy)  # angle from top (12 o'clock)
        angle_deg = math.degrees(angle_rad) % 360.0
        clock_hour = max(1, round(angle_deg / 30.0)) % 12 or 12

        if x_center < 0.35:
            horizontal_zone = "left"
        elif x_center > 0.65:
            horizontal_zone = "right"
        else:
            horizontal_zone = "center"

        return {
            "clock_hour": clock_hour,
            "direction": self.CLOCK_LABELS[clock_hour],
            "direction_hi": self.CLOCK_LABELS_HI[clock_hour],
            "horizontal_zone": horizontal_zone,
        }

    def from_bbox(
        self,
        bbox: Tuple[float, float, float, float],
        normalized: bool = True,
        image_width: int = 1,
        image_height: int = 1,
    ) -> Dict[str, Any]:
        """
        Compute direction from bounding box.

        Args:
            bbox: (xmin, ymin, xmax, ymax)
            normalized: True if coordinates are already in [0,1]
            image_width, image_height: used only when normalized=False
        """
        xmin, ymin, xmax, ymax = bbox
        if not normalized:
            xmin /= image_width
            xmax /= image_width
            ymin /= image_height
            ymax /= image_height
        x_center = (xmin + xmax) / 2.0
        y_center = (ymin + ymax) / 2.0
        return self.compute(x_center, y_center)
''')

# 4. ai/vision/elevation_estimator.py
write_file(r"C:\Users\HP\.gemini\antigravity\scratch\AccessIt\ai\vision\elevation_estimator.py", '''"""
Sahayak AI — Vertical Elevation Estimator
Classifies detected objects into vertical zones:
  eye_level | table_level | floor_level
based on bounding box position in the camera frame.
"""
from typing import Tuple, Dict


class ElevationEstimator:
    """
    Estimates vertical elevation of a detected object.
    Assumes a standard upright camera view (portrait or landscape).
    """

    LABELS = {
        "eye_level": "Eye level",
        "table_level": "Table / waist level",
        "floor_level": "Floor level",
    }

    LABELS_HI = {
        "eye_level": "आँख की सीध में",
        "table_level": "टेबल / कमर के स्तर पर",
        "floor_level": "फर्श के पास",
    }

    def estimate(
        self,
        bbox: Tuple[float, float, float, float],
        normalized: bool = True,
        image_height: int = 1,
    ) -> Dict[str, str]:
        """
        Estimate elevation from bounding box vertical position.

        Args:
            bbox: (xmin, ymin, xmax, ymax)
            normalized: coordinates in [0, 1] if True
            image_height: used when normalized=False

        Returns:
            dict with zone (str), label (str), label_hi (str)
        """
        _, ymin, _, ymax = bbox
        if not normalized:
            ymin /= image_height
            ymax /= image_height
        y_center = (ymin + ymax) / 2.0

        if y_center < 0.35:
            zone = "eye_level"
        elif y_center < 0.70:
            zone = "table_level"
        else:
            zone = "floor_level"

        return {
            "zone": zone,
            "label": self.LABELS[zone],
            "label_hi": self.LABELS_HI[zone],
        }
''')

# 5. ai/vision/proximity_estimator.py
write_file(r"C:\Users\HP\.gemini\antigravity\scratch\AccessIt\ai\vision\proximity_estimator.py", '''"""
Sahayak AI — Proximity Estimator
Estimates coarse distance of a detected object from the camera
based on bounding box area relative to the image.
"""
from typing import Tuple, Dict


class ProximityEstimator:
    """
    Estimates proximity from bounding box area fraction.
    Thresholds are calibrated for standard mobile camera FOV (~60°).
    """

    ZONES = [
        (0.25, "very_close", "Very close", "बहुत पास", "EMERGENCY_PULSE"),
        (0.10, "arm_reach", "Within arm's reach", "हाथ की पहुंच में", "DOUBLE_PULSE"),
        (0.03, "nearby", "Nearby", "पास में", "SINGLE_PULSE"),
        (0.0, "several_steps", "Several steps away", "कुछ कदम दूर", "LIGHT_PULSE"),
    ]

    def estimate(
        self,
        bbox: Tuple[float, float, float, float],
        normalized: bool = True,
        image_width: int = 1,
        image_height: int = 1,
    ) -> Dict[str, str]:
        """
        Estimate coarse proximity.

        Returns:
            dict with zone, label, label_hi, haptic_cue
        """
        xmin, ymin, xmax, ymax = bbox
        if not normalized:
            xmin /= image_width
            xmax /= image_width
            ymin /= image_height
            ymax /= image_height
        area = max(0.0, (xmax - xmin) * (ymax - ymin))
        for threshold, zone, label, label_hi, haptic in self.ZONES:
            if area >= threshold:
                return {"zone": zone, "label": label, "label_hi": label_hi, "haptic_cue": haptic, "bbox_area": round(area, 4)}
        return {"zone": "several_steps", "label": "Several steps away", "label_hi": "कुछ कदम दूर", "haptic_cue": "LIGHT_PULSE", "bbox_area": round(area, 4)}
''')

# 6. ai/scene/scene_understanding.py
write_file(r"C:\Users\HP\.gemini\antigravity\scratch\AccessIt\ai\scene\scene_understanding.py", '''"""
Sahayak AI — Scene Understanding Engine
Combines object detection, OCR, spatial analysis and intent-awareness
to produce a structured, task-relevant scene representation.
"""
from typing import List, Optional, Dict, Any
from shared.schemas.models import (
    SpatialObject, SceneAnalysis, AccessibilityTwin, TaskType, LanguagePreference
)
from ai.vision.object_detector import ObjectDetectorAdapter
from ai.vision.clock_direction import ClockDirectionMapper
from ai.vision.elevation_estimator import ElevationEstimator
from ai.vision.proximity_estimator import ProximityEstimator
from ai.ocr.ocr_engine import DocumentOCREngine


class SceneUnderstandingEngine:
    """
    Orchestrates object detection + OCR + spatial analysis to build
    a structured SceneAnalysis grounded in the user's current task/intent.
    """

    def __init__(self, provider: str = "heuristic"):
        self.detector = ObjectDetectorAdapter(provider=provider)
        self.clock_mapper = ClockDirectionMapper()
        self.elevation_estimator = ElevationEstimator()
        self.proximity_estimator = ProximityEstimator()
        self.ocr_engine = DocumentOCREngine()

    def analyze(
        self,
        image_bytes: Optional[bytes] = None,
        twin: Optional[AccessibilityTwin] = None,
        task_type: Optional[TaskType] = None,
        target_labels: Optional[List[str]] = None,
    ) -> SceneAnalysis:
        """
        Produce a full SceneAnalysis from camera image.

        Args:
            image_bytes: raw JPEG/PNG frame bytes
            twin: user Accessibility Twin for language and preference targeting
            task_type: current task to prioritize relevant objects
            target_labels: optional list of object labels to focus on

        Returns:
            SceneAnalysis with structured objects, text, hazards, and spatial metadata
        """
        is_hindi = twin and twin.language == LanguagePreference.HINDI

        # 1. Detect objects
        raw_detections = self.detector.detect(image_bytes, target_labels=target_labels)

        # 2. Extract text via OCR
        ocr_elements = []
        text_regions: List[str] = []
        if image_bytes:
            try:
                ocr_elements = self.ocr_engine.ocr_image(image_bytes)
                text_regions = [el["text"] for el in ocr_elements if len(el.get("text", "")) > 1]
            except Exception:
                text_regions = []

        # 3. Build SpatialObject for each detection
        spatial_objects: List[SpatialObject] = []
        for det in raw_detections:
            bbox = det.get("bbox", [0.1, 0.1, 0.5, 0.8])
            direction_info = self.clock_mapper.from_bbox(tuple(bbox), normalized=True)
            elevation_info = self.elevation_estimator.estimate(tuple(bbox), normalized=True)
            proximity_info = self.proximity_estimator.estimate(tuple(bbox), normalized=True)

            # Associate nearby text
            associated_text = self._associate_text(det["label"], text_regions)

            obj = SpatialObject(
                label=det["label"],
                confidence=det["confidence"],
                bbox=bbox,
                direction=direction_info["direction"],
                horizontal_zone=direction_info["horizontal_zone"],
                elevation=elevation_info["zone"],
                proximity=proximity_info["zone"],
                associated_text=associated_text,
                haptic_cue=proximity_info["haptic_cue"],
            )
            spatial_objects.append(obj)

        # 4. Detect hazards (objects very close and likely obstacles)
        hazards = [
            f"{obj.label} very close ({obj.direction})"
            for obj in spatial_objects
            if obj.proximity == "very_close"
        ]

        # 5. Prioritize relevant objects by task
        relevant = self._prioritize_by_task(spatial_objects, task_type, target_labels)

        # 6. Build spatial relationship descriptions
        relationships = self._describe_relationships(spatial_objects, is_hindi)

        # 7. Summary
        if spatial_objects:
            top = spatial_objects[0]
            if is_hindi:
                summary = f"{top.label} {top.direction} पर है"
            else:
                summary = f"{top.label} detected at {top.direction}"
        else:
            summary = "हिंदी: कोई वस्तु नहीं मिली" if is_hindi else "No objects detected"

        return SceneAnalysis(
            objects=spatial_objects,
            text_regions=text_regions,
            labels=[o.label for o in spatial_objects],
            spatial_relationships=relationships,
            hazards=hazards,
            relevant_objects=relevant,
            confidence=max((o.confidence for o in spatial_objects), default=0.0),
            task_context=task_type.value if task_type else None,
            summary=summary,
        )

    def _associate_text(self, label: str, text_regions: List[str]) -> Optional[str]:
        """Associate a text region with the object label via keyword matching."""
        label_keywords = label.lower().split()
        for text in text_regions:
            tl = text.lower()
            if any(k in tl for k in label_keywords):
                return text
        return None

    def _prioritize_by_task(self, objects: List[SpatialObject], task_type: Optional[TaskType], target_labels: Optional[List[str]]) -> List[SpatialObject]:
        """Filter objects relevant to the current task."""
        if target_labels:
            target_lower = [t.lower() for t in target_labels]
            return [o for o in objects if any(t in o.label.lower() for t in target_lower)]
        if task_type == TaskType.FIND_OBJECT:
            return objects
        if task_type == TaskType.UNDERSTAND_DOCUMENT:
            return [o for o in objects if "document" in o.label.lower() or "paper" in o.label.lower()]
        return objects

    def _describe_relationships(self, objects: List[SpatialObject], is_hindi: bool) -> List[str]:
        """Generate simple relative position descriptions between pairs of objects."""
        if len(objects) < 2:
            return []
        rels = []
        for i, a in enumerate(objects[:3]):
            for b in objects[i+1:4]:
                if is_hindi:
                    rels.append(f"{a.label} और {b.label} दोनों दिख रहे हैं")
                else:
                    rels.append(f"{a.label} and {b.label} both visible")
        return rels
''')

# 7. ai/scene/object_text_fusion.py
write_file(r"C:\Users\HP\.gemini\antigravity\scratch\AccessIt\ai\scene\object_text_fusion.py", '''"""
Sahayak AI — Object-Text Fusion
Associates OCR text regions with detected physical objects
using bounding-box overlap and semantic label matching.
"""
from typing import List, Dict, Any, Optional, Tuple
from shared.schemas.models import SpatialObject


class ObjectTextFusion:
    """
    Fuses object detection results with OCR text regions
    by spatial proximity (IoA) and semantic matching.
    """

    OVERLAP_THRESHOLD = 0.3

    def fuse(
        self,
        detections: List[Dict[str, Any]],
        ocr_elements: List[Dict[str, Any]],
        image_width: int = 1,
        image_height: int = 1,
    ) -> List[Dict[str, Any]]:
        """
        Fuse object detections with OCR text elements.

        Args:
            detections: list of {label, confidence, bbox: [x1,y1,x2,y2]}
            ocr_elements: list of {text, confidence, bbox: [xmin,ymin,xmax,ymax]} (pixel coords)
            image_width, image_height: image dimensions for normalization

        Returns:
            list of enriched detections with associated_texts list added
        """
        enriched = []
        for det in detections:
            det_copy = dict(det)
            obj_bbox = det_copy.get("bbox", [0, 0, 1, 1])
            # Normalize object bbox if not already
            if max(obj_bbox) > 1.0 and image_width > 1:
                obj_bbox = [obj_bbox[0]/image_width, obj_bbox[1]/image_height,
                            obj_bbox[2]/image_width, obj_bbox[3]/image_height]

            associated = []
            for ocr in ocr_elements:
                text = ocr.get("text", "").strip()
                if not text:
                    continue
                ocr_bbox = ocr.get("bbox", [0, 0, image_width, image_height])
                ocr_norm = [ocr_bbox[0]/image_width, ocr_bbox[1]/image_height,
                            ocr_bbox[2]/image_width, ocr_bbox[3]/image_height]

                if self._overlap_ratio(obj_bbox, ocr_norm) >= self.OVERLAP_THRESHOLD:
                    associated.append(text)
                elif self._semantic_match(det_copy["label"], text):
                    associated.append(text)

            det_copy["associated_texts"] = associated
            det_copy["primary_label"] = associated[0] if associated else det_copy["label"]
            enriched.append(det_copy)
        return enriched

    @staticmethod
    def _overlap_ratio(bbox_a: List[float], bbox_b: List[float]) -> float:
        """Intersection over area of bbox_b."""
        ix1 = max(bbox_a[0], bbox_b[0])
        iy1 = max(bbox_a[1], bbox_b[1])
        ix2 = min(bbox_a[2], bbox_b[2])
        iy2 = min(bbox_a[3], bbox_b[3])
        if ix2 <= ix1 or iy2 <= iy1:
            return 0.0
        inter = (ix2 - ix1) * (iy2 - iy1)
        area_b = max(1e-6, (bbox_b[2] - bbox_b[0]) * (bbox_b[3] - bbox_b[1]))
        return inter / area_b

    @staticmethod
    def _semantic_match(label: str, text: str) -> bool:
        """Check if text is semantically related to the object label."""
        label_words = set(label.lower().split())
        text_words = set(text.lower().split())
        return bool(label_words & text_words)
''')

# 8. ai/voice/speech_to_text.py
write_file(r"C:\Users\HP\.gemini\antigravity\scratch\AccessIt\ai\voice\speech_to_text.py", '''"""
Sahayak AI — Speech-to-Text Abstraction
Provider-agnostic STT adapter supporting English and Hindi.
Default: offline keyword fallback. Optional: Google Speech API.
"""
import re
from typing import Optional, Dict, Any
from shared.schemas.models import VoiceCommand


class STTProvider:
    """Base interface for STT providers."""
    def transcribe(self, audio_bytes: bytes, language: str = "en-IN") -> str:
        raise NotImplementedError


class HeuristicSTTProvider(STTProvider):
    """Offline heuristic STT for testing and fallback."""
    def transcribe(self, audio_bytes: bytes, language: str = "en-IN") -> str:
        # In a real device, this would decode audio. For demo, return a placeholder.
        return "[speech input]"


class SpeechToTextEngine:
    """
    Converts audio bytes to a VoiceCommand.
    Flows through the Intent Engine (not a standalone assistant).
    """

    def __init__(self, provider: Optional[STTProvider] = None):
        self._provider = provider or HeuristicSTTProvider()

    def transcribe(
        self,
        audio_bytes: Optional[bytes] = None,
        text_input: Optional[str] = None,
        language: str = "en-IN",
    ) -> VoiceCommand:
        """
        Convert audio bytes or direct text input to a VoiceCommand.

        Args:
            audio_bytes: raw audio bytes (WAV/OGG)
            text_input: if provided, skip STT and use directly
            language: BCP-47 language tag ('en-IN', 'hi-IN')

        Returns:
            VoiceCommand with raw_text ready for Intent Engine
        """
        if text_input is not None:
            raw_text = text_input.strip()
            source = "text_input"
        elif audio_bytes:
            try:
                raw_text = self._provider.transcribe(audio_bytes, language)
                source = "stt"
            except Exception as e:
                print(f"STT error: {e}")
                raw_text = ""
                source = "stt_failed"
        else:
            raw_text = ""
            source = "empty"

        lang_label = "Hindi" if language.startswith("hi") else "English"
        return VoiceCommand(
            raw_text=raw_text,
            language=lang_label,
            confidence=0.95 if text_input else 0.80,
            source=source,
        )
''')

# 9. ai/voice/text_to_speech.py
write_file(r"C:\Users\HP\.gemini\antigravity\scratch\AccessIt\ai\voice\text_to_speech.py", '''"""
Sahayak AI — Text-to-Speech Abstraction
Provider-agnostic TTS adapter. Returns SSML/text ready for device TTS engine.
Core logic does NOT call device TTS directly — delegates to client layer.
"""
from typing import Optional, Dict, Any
from shared.schemas.models import LanguagePreference


class TextToSpeechEngine:
    """
    Prepares TTS output payload.
    Actual audio rendering is handled by the Flutter/Web client.
    Backend returns structured speech payload.
    """

    SPEED_SETTINGS = {
        "slow": 0.75,
        "normal": 1.0,
        "fast": 1.25,
    }

    def prepare(
        self,
        text: str,
        language: LanguagePreference = LanguagePreference.ENGLISH,
        speed: str = "normal",
        emphasize_words: Optional[list] = None,
    ) -> Dict[str, Any]:
        """
        Prepare a structured TTS payload for the client.
        """
        lang_code = "hi-IN" if language == LanguagePreference.HINDI else "en-IN"
        speed_rate = self.SPEED_SETTINGS.get(speed, 1.0)

        # Build basic SSML
        ssml_text = text
        if emphasize_words:
            for word in emphasize_words:
                ssml_text = ssml_text.replace(word, f'<emphasis level="strong">{word}</emphasis>')

        ssml = (
            f'<speak><prosody rate="{speed_rate}">{ssml_text}</prosody></speak>'
        )

        return {
            "text": text,
            "ssml": ssml,
            "lang_code": lang_code,
            "speed_rate": speed_rate,
            "language": language.value,
        }
''')

# 10. ai/voice/voice_command.py
write_file(r"C:\Users\HP\.gemini\antigravity\scratch\AccessIt\ai\voice\voice_command.py", '''"""
Sahayak AI — Voice Command Processor
Routes voice commands through the existing Intent Engine.
Does NOT bypass the 7-stage pipeline.
"""
from typing import Optional, Dict, Any
from shared.schemas.models import VoiceCommand, AccessibilityTwin
from ai.voice.speech_to_text import SpeechToTextEngine
from ai.voice.text_to_speech import TextToSpeechEngine
from ai.intent.intent_engine import IntentEngine


class VoiceCommandProcessor:
    """
    Ties STT → Intent Engine → TTS into a coherent voice layer.
    Voice commands always flow through the existing Intent Engine.
    """

    def __init__(
        self,
        stt: Optional[SpeechToTextEngine] = None,
        tts: Optional[TextToSpeechEngine] = None,
    ):
        self.stt = stt or SpeechToTextEngine()
        self.tts = tts or TextToSpeechEngine()
        self.intent_engine = IntentEngine()

    def process(
        self,
        audio_bytes: Optional[bytes] = None,
        text_input: Optional[str] = None,
        twin: Optional[AccessibilityTwin] = None,
    ) -> Dict[str, Any]:
        """
        Full voice processing pipeline:
        Audio/Text → STT → Intent Engine → response payload.

        Args:
            audio_bytes: raw audio bytes
            text_input: direct text shortcut (skips STT)
            twin: user Accessibility Twin

        Returns:
            dict with voice_command, intent_analysis, tts_payload
        """
        language = "hi-IN" if (twin and twin.language.value == "Hindi") else "en-IN"

        # Step 1: STT
        voice_cmd = self.stt.transcribe(
            audio_bytes=audio_bytes,
            text_input=text_input,
            language=language,
        )

        if not voice_cmd.raw_text:
            return {
                "voice_command": voice_cmd.model_dump(),
                "intent_analysis": None,
                "error": "No speech or text detected",
            }

        # Step 2: Route through Intent Engine (not a bypass)
        intent_result = self.intent_engine.analyze_intent(
            query=voice_cmd.raw_text,
            twin_id=twin.id if twin else "default_user",
        )

        # Step 3: Prepare TTS acknowledgment
        intent_label = intent_result.get("intent", "UNKNOWN")
        ack_text = f"Processing: {voice_cmd.raw_text}"
        lang_pref = twin.language if twin else None
        from shared.schemas.models import LanguagePreference
        tts_payload = self.tts.prepare(
            text=ack_text,
            language=lang_pref or LanguagePreference.ENGLISH,
        )

        return {
            "voice_command": voice_cmd.model_dump(),
            "intent_analysis": intent_result,
            "tts_payload": tts_payload,
        }
''')

# 11. ai/navigation/obstacle_detector.py
write_file(r"C:\Users\HP\.gemini\antigravity\scratch\AccessIt\ai\navigation\obstacle_detector.py", '''"""
Sahayak AI — Obstacle Detector
Identifies potential obstacles from spatial scene analysis.
Based on proximity and position - NOT GPS/map-based navigation.
"""
from typing import List, Dict, Any
from shared.schemas.models import SpatialObject

# Labels considered navigation obstacles
OBSTACLE_LABELS = {
    "person", "chair", "table", "wall", "door", "step", "stair",
    "pole", "car", "bicycle", "motorcycle", "box", "suitcase",
}


class ObstacleDetector:
    """
    Determines which detected objects are navigation obstacles
    based on proximity and object category.
    """

    def detect_obstacles(
        self,
        objects: List[SpatialObject],
    ) -> List[Dict[str, Any]]:
        """
        Identify obstacles from a list of SpatialObjects.

        Returns:
            list of obstacle dicts with label, severity, direction
        """
        obstacles = []
        for obj in objects:
            is_obstacle = any(kw in obj.label.lower() for kw in OBSTACLE_LABELS)
            is_close = obj.proximity in ("very_close", "arm_reach")
            if is_obstacle or is_close:
                severity = "HIGH" if obj.proximity == "very_close" else "MEDIUM"
                obstacles.append({
                    "label": obj.label,
                    "direction": obj.direction,
                    "horizontal_zone": obj.horizontal_zone,
                    "proximity": obj.proximity,
                    "severity": severity,
                })
        return obstacles
''')

# 12. ai/navigation/guidance_engine.py
write_file(r"C:\Users\HP\.gemini\antigravity\scratch\AccessIt\ai\navigation\guidance_engine.py", '''"""
Sahayak AI — Navigation Guidance Engine
Generates simple camera-based local navigation instructions.
Does NOT claim GPS or map-level accuracy — strictly local scene guidance.
"""
from typing import List, Dict, Any, Optional
from shared.schemas.models import NavigationInstruction, SpatialObject, AccessibilityTwin, LanguagePreference
from ai.navigation.obstacle_detector import ObstacleDetector


class GuidanceEngine:
    """
    Produces NavigationInstruction from scene objects.
    Integrates with voice and haptic layers for multimodal output.
    """

    def __init__(self):
        self.obstacle_detector = ObstacleDetector()

    def guide(
        self,
        objects: List[SpatialObject],
        target_label: Optional[str] = None,
        twin: Optional[AccessibilityTwin] = None,
    ) -> List[NavigationInstruction]:
        """
        Generate navigation instructions from scene objects.

        Args:
            objects: list of SpatialObjects from scene analysis
            target_label: optional label of the object to navigate toward
            twin: Accessibility Twin for language preference

        Returns:
            list of NavigationInstruction (ordered by priority)
        """
        is_hindi = twin and twin.language == LanguagePreference.HINDI
        instructions: List[NavigationInstruction] = []

        # 1. Check for obstacles
        obstacles = self.obstacle_detector.detect_obstacles(objects)
        for obs in obstacles:
            zone = obs["horizontal_zone"]
            if zone == "center":
                direction = "stop"
                desc = f"Obstacle ahead: {obs['label']}. Stop."
                desc_hi = f"आगे बाधा: {obs['label']}। रुकें।"
            elif zone == "right":
                direction = "slight_left"
                desc = f"{obs['label']} on your right. Move slightly left."
                desc_hi = f"{obs['label']} दाईं ओर है। थोड़ा बाईं ओर जाएं।"
            else:
                direction = "slight_right"
                desc = f"{obs['label']} on your left. Move slightly right."
                desc_hi = f"{obs['label']} बाईं ओर है। थोड़ा दाईं ओर जाएं।"

            instructions.append(NavigationInstruction(
                direction=direction,
                description=desc,
                description_hi=desc_hi,
                urgency="HIGH" if obs["severity"] == "HIGH" else "NORMAL",
                haptic_cue=f"PULSE_{direction.upper().replace('SLIGHT_', '')}",
                obstacle_detected=True,
                obstacle_label=obs["label"],
            ))

        # 2. Guide toward target object if specified
        if target_label:
            target_objs = [o for o in objects if target_label.lower() in o.label.lower()]
            if target_objs:
                target = target_objs[0]
                zone = target.horizontal_zone
                if zone == "left":
                    direction = "left"
                    desc = f"{target.label} is to your {target.direction}. Turn left."
                    desc_hi = f"{target.label} {target.direction} पर है। बाईं ओर मुड़ें।"
                    haptic = "PULSE_LEFT"
                elif zone == "right":
                    direction = "right"
                    desc = f"{target.label} is to your {target.direction}. Turn right."
                    desc_hi = f"{target.label} {target.direction} पर है। दाईं ओर मुड़ें।"
                    haptic = "PULSE_RIGHT"
                else:
                    direction = "forward"
                    desc = f"{target.label} is directly ahead at {target.direction}."
                    desc_hi = f"{target.label} सीधे आगे {target.direction} पर है।"
                    haptic = "DOUBLE_PULSE_CENTER"
                instructions.append(NavigationInstruction(
                    direction=direction,
                    description=desc,
                    description_hi=desc_hi,
                    urgency="NORMAL",
                    haptic_cue=haptic,
                    obstacle_detected=False,
                ))

        # 3. Default: no obstacles, path clear
        if not instructions:
            instructions.append(NavigationInstruction(
                direction="forward",
                description="Path appears clear. Move forward carefully.",
                description_hi="रास्ता साफ दिखता है। सावधानी से आगे बढ़ें।",
                urgency="NORMAL",
                haptic_cue="LIGHT_PULSE",
                obstacle_detected=False,
            ))

        return instructions
''')

# 13. ai/navigation/navigation_engine.py
write_file(r"C:\Users\HP\.gemini\antigravity\scratch\AccessIt\ai\navigation\navigation_engine.py", '''"""
Sahayak AI — Navigation Engine
Orchestrates scene analysis → obstacle detection → guidance generation.
Provides camera-based LOCAL navigation only (not GPS/map).
"""
from typing import Optional, List, Dict, Any
from shared.schemas.models import (
    NavigationInstruction, SceneAnalysis, AccessibilityTwin, TaskType
)
from ai.scene.scene_understanding import SceneUnderstandingEngine
from ai.navigation.guidance_engine import GuidanceEngine


class NavigationEngine:
    """
    Full local navigation pipeline:
    Camera Frame → Scene Analysis → Obstacle Detection → Guidance Instructions.

    IMPORTANT: Provides camera-based local scene guidance only.
    Does NOT claim GPS, map accuracy, or outdoor route navigation.
    """

    def __init__(self, vision_provider: str = "heuristic"):
        self.scene_engine = SceneUnderstandingEngine(provider=vision_provider)
        self.guidance_engine = GuidanceEngine()

    def navigate(
        self,
        image_bytes: Optional[bytes] = None,
        target_label: Optional[str] = None,
        twin: Optional[AccessibilityTwin] = None,
    ) -> Dict[str, Any]:
        """
        Generate navigation guidance from a camera frame.

        Args:
            image_bytes: raw camera frame bytes
            target_label: object to navigate toward (optional)
            twin: Accessibility Twin

        Returns:
            dict with scene_summary, instructions, and obstacle_count
        """
        target_list = [target_label] if target_label else None
        scene = self.scene_engine.analyze(
            image_bytes=image_bytes,
            twin=twin,
            task_type=TaskType.FIND_OBJECT,
            target_labels=target_list,
        )

        instructions = self.guidance_engine.guide(
            objects=scene.objects,
            target_label=target_label,
            twin=twin,
        )

        return {
            "scene_summary": scene.summary,
            "objects_detected": len(scene.objects),
            "instructions": [i.model_dump() for i in instructions],
            "obstacle_count": len(scene.hazards),
            "hazards": scene.hazards,
            "disclaimer": "Local camera-based guidance only. Not GPS navigation.",
        }
''')

# 14. ai/recovery/failure_detector.py
write_file(r"C:\Users\HP\.gemini\antigravity\scratch\AccessIt\ai\recovery\failure_detector.py", '''"""
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

    def check_ocr(self, ocr_result: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Detect low-confidence or empty OCR results."""
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

    def check_isl(self, isl_result: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Detect unrecognized or low-confidence ISL gestures."""
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

    def check_speech(self, voice_cmd_result: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Detect unclear or empty speech input."""
        raw_text = voice_cmd_result.get("voice_command", {}).get("raw_text", "")
        source = voice_cmd_result.get("voice_command", {}).get("source", "")
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
''')

# 15. ai/recovery/recovery_engine.py
write_file(r"C:\Users\HP\.gemini\antigravity\scratch\AccessIt\ai\recovery\recovery_engine.py", '''"""
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
''')

# 16. ai/ocr/document_qa.py
write_file(r"C:\Users\HP\.gemini\antigravity\scratch\AccessIt\ai\ocr\document_qa.py", '''"""
Sahayak AI — Document Question Answering
Grounded QA over extracted document content.
Does NOT invent information not present in the document.
Reuses the existing OCR/document parser pipeline.
"""
import re
from typing import Optional, Dict, Any, List
from shared.schemas.models import DocumentQuestion, DocumentAnswer
from ai.ocr.ocr_engine import DocumentOCREngine


# Map of question keywords to document field keys
QUESTION_FIELD_MAP = [
    (["deadline", "last date", "closing date", "submit by", "due date", "अंतिम"],
     "key_deadlines", "deadline"),
    (["fee", "application fee", "charge", "cost", "शुल्क"],
     "application_fee", "application fee"),
    (["document", "required", "proof", "certificate", "दस्तावेज"],
     "required_documents", "required documents"),
    (["eligible", "eligibility", "who can", "criteria", "पात्रता"],
     "eligibility_criteria", "eligibility criteria"),
    (["authority", "issued by", "ministry", "department", "जारीकर्ता"],
     "issuing_authority", "issuing authority"),
    (["title", "name", "scheme", "subject", "शीर्षक"],
     "document_title", "document title"),
    (["summary", "briefly", "what is", "tell me", "सारांश"],
     "simplified_summary_en", "summary"),
]


class DocumentQAEngine:
    """
    Answers natural-language questions about extracted document content.
    All answers are grounded in document data — fabrication is explicitly forbidden.
    """

    def __init__(self):
        self.ocr_engine = DocumentOCREngine()
        self._cached_doc: Optional[Dict[str, Any]] = None

    def load_document(
        self,
        image_bytes: Optional[bytes] = None,
        raw_text: Optional[str] = None,
        preloaded_doc: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Extract and cache document information.
        Accepts image bytes, raw text, or a preloaded document dict.
        """
        if preloaded_doc:
            self._cached_doc = preloaded_doc
        else:
            self._cached_doc = self.ocr_engine.extract_document_info(
                image_bytes=image_bytes,
                raw_text=raw_text,
            )
        return self._cached_doc

    def answer(self, question: DocumentQuestion) -> DocumentAnswer:
        """
        Answer a question grounded in the loaded document.

        Args:
            question: DocumentQuestion with question text

        Returns:
            DocumentAnswer - always grounded, never fabricated
        """
        if not self._cached_doc:
            return DocumentAnswer(
                question=question.question,
                answer="No document has been loaded. Please provide a document first.",
                confidence=0.0,
                found_in_document=False,
            )

        q_lower = question.question.lower()

        # First: try Gemini QA if API key is available
        gemini_answer = self._gemini_qa(question.question, self._cached_doc)
        if gemini_answer:
            return gemini_answer

        # Fallback: keyword-based field lookup
        for keywords, field_key, field_name in QUESTION_FIELD_MAP:
            if any(kw in q_lower for kw in keywords):
                value = self._cached_doc.get(field_key)
                if value:
                    if isinstance(value, list):
                        answer_text = ", ".join(str(v) for v in value)
                    else:
                        answer_text = str(value)
                    return DocumentAnswer(
                        question=question.question,
                        answer=answer_text,
                        source_snippet=answer_text[:200],
                        confidence=0.88,
                        found_in_document=True,
                    )

        return DocumentAnswer(
            question=question.question,
            answer="Information not found in document.",
            confidence=0.0,
            found_in_document=False,
        )

    def answer_batch(self, questions: List[DocumentQuestion]) -> List[DocumentAnswer]:
        """Answer multiple questions about the same document."""
        return [self.answer(q) for q in questions]

    def _gemini_qa(
        self, question: str, doc: Dict[str, Any]
    ) -> Optional[DocumentAnswer]:
        """Use Gemini to answer with document context as grounding."""
        import os, json
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            return None
        try:
            from google import genai
            client = genai.Client(api_key=api_key)
            doc_context = json.dumps(doc, ensure_ascii=False, indent=2)
            prompt = (
                f"You are answering a question strictly based on this document data:\\n\\n"
                f"{doc_context}\\n\\n"
                f"Question: {question}\\n\\n"
                "Rules:\\n"
                "1. Answer ONLY based on the document data above.\\n"
                "2. If the answer is not in the document, say 'Information not found in document.'\\n"
                "3. Return JSON: {\\"answer\\": str, \\"answer_hi\\": str, \\"source_snippet\\": str, \\"confidence\\": float, \\"found_in_document\\": bool}\\n"
                "4. Return ONLY raw JSON."
            )
            response = client.models.generate_content(model="gemini-2.5-flash", contents=[prompt])
            if response and response.text:
                txt = response.text.strip().lstrip("```json").rstrip("```").strip()
                parsed = json.loads(txt)
                return DocumentAnswer(
                    question=question,
                    answer=parsed.get("answer", "Information not found in document."),
                    answer_hi=parsed.get("answer_hi"),
                    source_snippet=parsed.get("source_snippet"),
                    confidence=float(parsed.get("confidence", 0.9)),
                    found_in_document=parsed.get("found_in_document", True),
                )
        except Exception as e:
            print(f"Gemini QA error: {e}")
        return None
''')

# 17. ai/task/document_task_generator.py
write_file(r"C:\Users\HP\.gemini\antigravity\scratch\AccessIt\ai\task\document_task_generator.py", '''"""
Sahayak AI — Document-to-Task Generator
Converts extracted document information into actionable TaskEngine tasks.
Integrates with the existing TaskEngine — does NOT create a second task system.
"""
from typing import Dict, Any, Optional, List
from ai.task.task_engine import TaskEngine
from shared.schemas.models import TaskType


class DocumentTaskGenerator:
    """
    Converts extracted document data (from OCR engine) into structured tasks
    by delegating to the existing TaskEngine.
    """

    def __init__(self, task_engine: Optional[TaskEngine] = None):
        self.task_engine = task_engine or TaskEngine()

    def generate_from_document(
        self,
        doc_info: Dict[str, Any],
        twin_id: str = "default_user",
    ) -> Dict[str, Any]:
        """
        Convert extracted document data into a structured task.

        Args:
            doc_info: result from DocumentOCREngine.extract_document_info()
            twin_id: user twin identifier

        Returns:
            dict with task_id, title, deadlines, required_actions, milestones
        """
        title = doc_info.get("document_title", "Document Task")
        deadlines = doc_info.get("key_deadlines", [])
        required_docs = doc_info.get("required_documents", [])
        action_items = doc_info.get("action_items", [])

        # Create a generic task via the existing TaskEngine
        task = self.task_engine.create_generic_task(
            task_type=TaskType.UNDERSTAND_DOCUMENT,
            description=f"Complete requirements for: {title}",
            context={
                "document_title": title,
                "deadlines": deadlines,
                "required_documents": required_docs,
            },
        )

        # Decompose into milestones via existing TaskEngine
        milestones = self.task_engine.decompose_task(
            task_type=TaskType.UNDERSTAND_DOCUMENT,
            context={"document_title": title, "deadline": deadlines[0] if deadlines else "Unknown"},
        )

        return {
            "task_id": task["task_id"],
            "title": title,
            "deadlines": deadlines,
            "required_documents": required_docs,
            "action_items": action_items,
            "milestones": milestones,
            "source": "document",
            "task_type": TaskType.UNDERSTAND_DOCUMENT.value,
            "status": task["status"],
        }

    def generate_submission_task(
        self,
        doc_info: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Create a form submission task from a document with application fields.
        Delegates to the existing TaskEngine form flow.
        """
        title = doc_info.get("document_title", "Application Form")
        deadlines = doc_info.get("key_deadlines", [])

        task = self.task_engine.create_form_task(
            description=f"Submit application: {title}",
        )
        return {
            "task_id": task["task_id"],
            "title": f"Submit: {title}",
            "deadline": deadlines[0] if deadlines else "Check document",
            "required_action": "application_submission",
            "source": "document",
            "task_type": TaskType.FORM_COMPLETION.value,
            "status": task["status"],
        }
''')

# 18. Append to ai/learning/learning_service.py
learning_ext = """    def get_pattern_suggestions(self) -> List[Dict[str, Any]]:
        \"\"\"
        Analyze interaction patterns and generate consented PersonalizationSuggestion list.
        Uses real telemetry if available; otherwise returns calibrated defaults.
        Strictly requires user consent before applying any change.
        \"\"\"
        from shared.schemas.models import PersonalizationSuggestion
        suggestions = []
        total = len(self._telemetry_events)

        if total == 0:
            return [
                PersonalizationSuggestion(
                    pattern_type="preferred_modality",
                    observation="Voice guidance was used in the majority of recent interactions.",
                    suggested_adaptation="Set voice-first input as the default modality.",
                    consent_required=True,
                    dialog_prompt="Would you like Sahayak to default to voice guidance for all future tasks?",
                    confidence=0.72,
                    task_count=0,
                ).model_dump()
            ]

        voice_count = sum(1 for e in self._telemetry_events if "voice" in e["modality_used"])
        voice_pct = voice_count / total if total > 0 else 0
        high_retry_steps = [e["step_id"] for e in self._telemetry_events if e["retries"] > 1]
        failed_steps = [e["step_id"] for e in self._telemetry_events if not e["success"]]

        if voice_pct > 0.7:
            suggestions.append(
                PersonalizationSuggestion(
                    pattern_type="preferred_modality",
                    observation=f"Voice was used in {voice_pct*100:.0f}% of your last {total} interactions.",
                    suggested_adaptation="Default to voice-first input and spoken prompts.",
                    consent_required=True,
                    dialog_prompt=f"Voice guidance was successful in {voice_pct*100:.0f}% of your tasks. Make it default?",
                    confidence=round(voice_pct, 2),
                    task_count=total,
                ).model_dump()
            )

        if high_retry_steps:
            unique_steps = list(set(high_retry_steps))
            suggestions.append(
                PersonalizationSuggestion(
                    pattern_type="repeated_interaction_barrier",
                    observation=f"These steps required multiple retries: {', '.join(unique_steps[:3])}.",
                    suggested_adaptation="Pre-explain format before asking for input at these steps.",
                    consent_required=True,
                    dialog_prompt="Some steps were difficult. Would you like extra guidance for similar tasks?",
                    confidence=0.80,
                    task_count=len(high_retry_steps),
                ).model_dump()
            )

        if failed_steps:
            suggestions.append(
                PersonalizationSuggestion(
                    pattern_type="task_failure_pattern",
                    observation=f"{len(failed_steps)} step(s) ended without successful completion.",
                    suggested_adaptation="Offer simplified language and step-by-step audio guidance.",
                    consent_required=True,
                    dialog_prompt="Some tasks were not completed. Would you like simplified guidance enabled?",
                    confidence=0.75,
                    task_count=len(failed_steps),
                ).model_dump()
            )

        return suggestions"""
with open(r"C:\Users\HP\.gemini\antigravity\scratch\AccessIt\ai\learning\learning_service.py", "r", encoding="utf-8") as f:
    content = f.read()

append_to_file(r"C:\Users\HP\.gemini\antigravity\scratch\AccessIt\ai\learning\learning_service.py", learning_ext)


# 19. ai/orchestrator/ai_pipeline.py
write_file(r"C:\Users\HP\.gemini\antigravity\scratch\AccessIt\ai\orchestrator\ai_pipeline.py", '''"""
Sahayak AI — AI Pipeline Orchestrator
Single entry point that coordinates all 7-stage pipeline stages
and selects the appropriate AI capabilities per task/intent.
Does NOT bypass existing engines.
"""
from typing import Optional, Dict, Any, List
from shared.schemas.models import (
    AccessibilityTwin, TaskType, LanguagePreference
)
from ai.accessibility.twin import AccessibilityTwinService
from ai.intent.intent_engine import IntentEngine
from ai.barrier.barrier_engine import BarrierEngine
from ai.task.task_engine import TaskEngine
from ai.compiler.flow_compiler import AccessibleTaskFlowCompiler
from ai.assistance.assistance_engine import AccessibilityAssistanceEngine
from ai.verification.verification_service import TaskVerificationService
from ai.learning.learning_service import AccessibilityLearningService
from ai.voice.voice_command import VoiceCommandProcessor
from ai.scene.scene_understanding import SceneUnderstandingEngine
from ai.navigation.navigation_engine import NavigationEngine
from ai.recovery.failure_detector import FailureDetector
from ai.recovery.recovery_engine import RecoveryEngine
from ai.ocr.document_qa import DocumentQAEngine


class AIPipeline:
    """
    Orchestrates the full Sahayak AI pipeline:

    Input
     → Accessibility Twin
     → Intent Detection
     → Barrier Analysis
     → Task Engine
     → Flow Compiler
     → Capability Selection (OCR / Vision / ISL / Voice / Scene / Navigation)
     → Assistance
     → Verification
     → Learning

    All existing engines are reused — no bypassing.
    """

    def __init__(self):
        # Existing 7-stage engines
        self.twin_service = AccessibilityTwinService()
        self.intent_engine = IntentEngine()
        self.barrier_engine = BarrierEngine()
        self.task_engine = TaskEngine()
        self.flow_compiler = AccessibleTaskFlowCompiler()
        self.assistance_engine = AccessibilityAssistanceEngine()
        self.verification_service = TaskVerificationService()
        self.learning_service = AccessibilityLearningService()

        # New capability engines
        self.voice_processor = VoiceCommandProcessor()
        self.scene_engine = SceneUnderstandingEngine()
        self.navigation_engine = NavigationEngine()
        self.failure_detector = FailureDetector()
        self.recovery_engine = RecoveryEngine()
        self.doc_qa_engine = DocumentQAEngine()

    def run(
        self,
        query: Optional[str] = None,
        audio_bytes: Optional[bytes] = None,
        image_bytes: Optional[bytes] = None,
        twin_id: str = "default_user",
        task_type_override: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Execute the full AI pipeline for an arbitrary user request.

        Args:
            query: text query (shortcut for voice)
            audio_bytes: raw audio for STT
            image_bytes: camera frame or document scan
            twin_id: user identifier
            task_type_override: force a specific TaskType (for testing)

        Returns:
            structured pipeline result with all stage outputs
        """
        result: Dict[str, Any] = {"twin_id": twin_id, "pipeline_stages": []}

        # Stage 1: Accessibility Twin
        twin = self.twin_service.get_twin(twin_id)
        result["twin"] = {"language": twin.language.value, "input_modality": twin.preferred_input.value}
        result["pipeline_stages"].append("twin")

        # Stage 2: Intent (via Voice layer if audio, else direct)
        if audio_bytes or query:
            voice_result = self.voice_processor.process(
                audio_bytes=audio_bytes,
                text_input=query,
                twin=twin,
            )
            intent_data = voice_result.get("intent_analysis", {})
            result["voice"] = voice_result.get("voice_command", {})
        else:
            intent_data = {"intent": "SEE", "confidence": 0.80}
            result["voice"] = None
        result["intent"] = intent_data
        result["pipeline_stages"].append("intent")

        # Resolve task type
        intent_label = intent_data.get("intent", "SEE")
        if task_type_override:
            intent_label = task_type_override
        try:
            task_type = TaskType(intent_label)
        except ValueError:
            task_type = TaskType.SEE

        # Stage 3: Barrier Detection
        barriers = self.barrier_engine.detect_barriers(
            task_type=task_type,
            task_context={},
            twin=twin,
        )
        result["barriers"] = [{"category": b.category.value, "severity": b.severity.value} for b in barriers]
        result["pipeline_stages"].append("barriers")

        # Stage 4+5: Task Engine + Flow Compiler
        task = self.task_engine.create_generic_task(task_type=task_type, description=query or "")
        flow = self.flow_compiler.compile_form_flow(task["task_id"], twin, barriers)
        result["task_id"] = task["task_id"]
        result["pipeline_stages"].extend(["task_engine", "flow_compiler"])

        # Stage 6: Capability Selection based on TaskType
        capability_output: Dict[str, Any] = {}
        failures: List[Dict[str, Any]] = []

        if task_type == TaskType.UNDERSTAND_DOCUMENT:
            doc_result = self.assistance_engine.assist_understand_document(image_bytes, query or "", twin)
            capability_output["document"] = doc_result
            failure = self.failure_detector.check_ocr(doc_result)
            if failure:
                failures.append(failure)

        elif task_type == TaskType.FIND_OBJECT:
            nav_result = self.navigation_engine.navigate(image_bytes=image_bytes, target_label=query, twin=twin)
            capability_output["navigation"] = nav_result

        elif task_type == TaskType.COMMUNICATE:
            isl_result = self.assistance_engine.assist_sign_communication(image_bytes, twin)
            capability_output["isl"] = isl_result
            failure = self.failure_detector.check_isl(isl_result)
            if failure:
                failures.append(failure)

        elif task_type == TaskType.SEE:
            scene = self.scene_engine.analyze(image_bytes=image_bytes, twin=twin, task_type=task_type)
            capability_output["scene"] = {
                "summary": scene.summary,
                "objects": len(scene.objects),
                "hazards": scene.hazards,
            }

        result["capabilities"] = capability_output
        result["pipeline_stages"].append("capabilities")

        # Stage 7: Recovery if failures detected
        if failures:
            recovery_actions = self.recovery_engine.recover_many(failures)
            result["recovery"] = [a.model_dump() for a in recovery_actions]
        else:
            result["recovery"] = []
        result["pipeline_stages"].append("recovery")

        # Stage 8: Learning
        self.learning_service.record_interaction(
            step_id=task_type.value,
            modality_used=twin.preferred_input.value,
            duration_seconds=1.0,
            retries=len(failures),
            success=len(failures) == 0,
        )
        result["learning_recorded"] = True
        result["pipeline_stages"].append("learning")

        return result
''')

# 20. __init__.py files
for d in ['ai/voice', 'ai/navigation', 'ai/recovery', 'ai/orchestrator']:
    write_file(f"C:\\Users\\HP\\.gemini\\antigravity\\scratch\\AccessIt\\{d}\\__init__.py", "")

# 21. Tests
tests_spatial = '''import pytest
from ai.vision.object_detector import ObjectDetectorAdapter
from ai.vision.clock_direction import ClockDirectionMapper
from ai.vision.elevation_estimator import ElevationEstimator
from ai.vision.proximity_estimator import ProximityEstimator

def test_clock_direction_right():
    mapper = ClockDirectionMapper()
    result = mapper.compute(0.8, 0.5)
    assert result["horizontal_zone"] == "right"
    assert "clock_hour" in result
    assert 1 <= result["clock_hour"] <= 12

def test_clock_direction_left():
    mapper = ClockDirectionMapper()
    result = mapper.compute(0.1, 0.5)
    assert result["horizontal_zone"] == "left"

def test_clock_direction_center():
    mapper = ClockDirectionMapper()
    result = mapper.compute(0.5, 0.5)
    assert result["horizontal_zone"] == "center"

def test_clock_from_bbox():
    mapper = ClockDirectionMapper()
    result = mapper.from_bbox((0.6, 0.2, 0.9, 0.7), normalized=True)
    assert "direction" in result
    assert "clock_hour" in result

def test_elevation_eye_level():
    estimator = ElevationEstimator()
    result = estimator.estimate((0.1, 0.0, 0.9, 0.3), normalized=True)
    assert result["zone"] == "eye_level"

def test_elevation_table_level():
    estimator = ElevationEstimator()
    result = estimator.estimate((0.1, 0.3, 0.9, 0.7), normalized=True)
    assert result["zone"] == "table_level"

def test_elevation_floor_level():
    estimator = ElevationEstimator()
    result = estimator.estimate((0.1, 0.75, 0.9, 1.0), normalized=True)
    assert result["zone"] == "floor_level"

def test_proximity_very_close():
    estimator = ProximityEstimator()
    result = estimator.estimate((0.1, 0.1, 0.7, 0.9), normalized=True)
    assert result["zone"] == "very_close"

def test_proximity_several_steps():
    estimator = ProximityEstimator()
    result = estimator.estimate((0.45, 0.45, 0.55, 0.55), normalized=True)
    assert result["zone"] == "several_steps"

def test_object_detector_heuristic():
    detector = ObjectDetectorAdapter(provider="heuristic")
    results = detector.detect(image_bytes=None)
    assert len(results) > 0
    assert "label" in results[0]
    assert "confidence" in results[0]

def test_object_detector_target_filter():
    detector = ObjectDetectorAdapter(provider="heuristic")
    results = detector.detect(image_bytes=None, target_labels=["water bottle"])
    assert any("water" in r["label"].lower() for r in results)
'''
write_file(r"C:\Users\HP\.gemini\antigravity\scratch\AccessIt\tests\unit\test_spatial_vision.py", tests_spatial)

tests_scene = '''import pytest
from ai.scene.scene_understanding import SceneUnderstandingEngine
from ai.scene.object_text_fusion import ObjectTextFusion
from shared.schemas.models import SceneAnalysis, SpatialObject, TaskType

def test_scene_analyze_no_image():
    engine = SceneUnderstandingEngine(provider="heuristic")
    scene = engine.analyze(image_bytes=None)
    assert isinstance(scene, SceneAnalysis)
    assert len(scene.objects) > 0
    assert scene.confidence > 0

def test_scene_analyze_with_target():
    engine = SceneUnderstandingEngine(provider="heuristic")
    scene = engine.analyze(image_bytes=None, target_labels=["water bottle"])
    assert any("water" in o.label.lower() for o in scene.relevant_objects)

def test_scene_spatial_object_has_direction():
    engine = SceneUnderstandingEngine(provider="heuristic")
    scene = engine.analyze(image_bytes=None)
    for obj in scene.objects:
        assert obj.direction is not None
        assert obj.elevation is not None
        assert obj.proximity is not None

def test_object_text_fusion():
    fusion = ObjectTextFusion()
    detections = [{"label": "medicine bottle", "confidence": 0.9, "bbox": [0.1, 0.3, 0.3, 0.8]}]
    ocr = [{"text": "Paracetamol 500mg", "confidence": 0.95, "bbox": [110, 300, 300, 800]}]
    result = fusion.fuse(detections, ocr, image_width=1000, image_height=1000)
    assert len(result) == 1
    assert result[0]["label"] == "medicine bottle"

def test_scene_task_type_filter():
    engine = SceneUnderstandingEngine(provider="heuristic")
    scene = engine.analyze(image_bytes=None, task_type=TaskType.UNDERSTAND_DOCUMENT, target_labels=["document"])
    assert scene.task_context == TaskType.UNDERSTAND_DOCUMENT.value
'''
write_file(r"C:\Users\HP\.gemini\antigravity\scratch\AccessIt\tests\unit\test_scene_understanding.py", tests_scene)

tests_voice = '''import pytest
from ai.voice.speech_to_text import SpeechToTextEngine
from ai.voice.text_to_speech import TextToSpeechEngine
from ai.voice.voice_command import VoiceCommandProcessor
from shared.schemas.models import LanguagePreference, VoiceCommand

def test_stt_text_input():
    engine = SpeechToTextEngine()
    result = engine.transcribe(text_input="Read this document")
    assert isinstance(result, VoiceCommand)
    assert result.raw_text == "Read this document"
    assert result.source == "text_input"
    assert result.confidence > 0.9

def test_stt_empty_input():
    engine = SpeechToTextEngine()
    result = engine.transcribe()
    assert result.raw_text == ""
    assert result.source == "empty"

def test_tts_english():
    engine = TextToSpeechEngine()
    payload = engine.prepare("Hello", language=LanguagePreference.ENGLISH)
    assert payload["lang_code"] == "en-IN"
    assert "ssml" in payload
    assert "speed_rate" in payload

def test_tts_hindi():
    engine = TextToSpeechEngine()
    payload = engine.prepare("नमस्ते", language=LanguagePreference.HINDI)
    assert payload["lang_code"] == "hi-IN"

def test_voice_command_processor_routes_intent():
    processor = VoiceCommandProcessor()
    result = processor.process(text_input="Help me fill this form")
    assert "voice_command" in result
    assert "intent_analysis" in result
    intent = result["intent_analysis"]
    assert "intent" in intent
    assert intent["intent"] == "FORM_COMPLETION"

def test_voice_command_empty():
    processor = VoiceCommandProcessor()
    result = processor.process()
    assert "error" in result
'''
write_file(r"C:\Users\HP\.gemini\antigravity\scratch\AccessIt\tests\unit\test_voice.py", tests_voice)

tests_nav = '''import pytest
from ai.navigation.navigation_engine import NavigationEngine
from ai.navigation.obstacle_detector import ObstacleDetector
from ai.navigation.guidance_engine import GuidanceEngine
from shared.schemas.models import SpatialObject, NavigationInstruction

def test_navigation_no_image():
    engine = NavigationEngine()
    result = engine.navigate(image_bytes=None, target_label="water bottle")
    assert "instructions" in result
    assert len(result["instructions"]) > 0
    assert "scene_summary" in result
    assert "disclaimer" in result

def test_obstacle_detector_close_object():
    detector = ObstacleDetector()
    obj = SpatialObject(
        label="chair", confidence=0.9,
        bbox=[0.3, 0.2, 0.7, 0.8],
        proximity="very_close", horizontal_zone="center",
        direction="12 o'clock"
    )
    obstacles = detector.detect_obstacles([obj])
    assert len(obstacles) == 1
    assert obstacles[0]["severity"] == "HIGH"

def test_guidance_engine_target():
    engine = GuidanceEngine()
    obj = SpatialObject(
        label="water bottle", confidence=0.9,
        bbox=[0.6, 0.2, 0.9, 0.8],
        proximity="arm_reach", horizontal_zone="right",
        direction="3 o'clock"
    )
    instructions = engine.guide([obj], target_label="water bottle")
    assert len(instructions) > 0
    directions = [i.direction for i in instructions]
    assert any(d in ["right", "forward", "slight_right"] for d in directions)

def test_guidance_engine_no_obstacles():
    engine = GuidanceEngine()
    instructions = engine.guide([])
    assert len(instructions) == 1
    assert instructions[0].direction == "forward"
'''
write_file(r"C:\Users\HP\.gemini\antigravity\scratch\AccessIt\tests\unit\test_navigation.py", tests_nav)

tests_rec = '''import pytest
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
'''
write_file(r"C:\Users\HP\.gemini\antigravity\scratch\AccessIt\tests\unit\test_recovery.py", tests_rec)

tests_qa = '''import pytest
from ai.ocr.document_qa import DocumentQAEngine
from shared.schemas.models import DocumentQuestion, DocumentAnswer

SAMPLE_DOC = {
    "document_title": "National Merit Scholarship 2026",
    "issuing_authority": "Ministry of Education",
    "key_deadlines": ["September 30, 2026"],
    "required_documents": ["Aadhaar Card", "Income Certificate", "Marksheet"],
    "application_fee": "NIL",
    "simplified_summary_en": "Apply for National Merit Scholarship by September 30.",
    "simplified_summary_hi": "राष्ट्रीय योग्यता छात्रवृत्ति के लिए 30 सितंबर तक आवेदन करें।",
}

def test_qa_deadline_question():
    engine = DocumentQAEngine()
    engine.load_document(preloaded_doc=SAMPLE_DOC)
    answer = engine.answer(DocumentQuestion(question="What is the deadline?"))
    assert isinstance(answer, DocumentAnswer)
    assert answer.found_in_document is True
    assert "2026" in answer.answer or "September" in answer.answer

def test_qa_fee_question():
    engine = DocumentQAEngine()
    engine.load_document(preloaded_doc=SAMPLE_DOC)
    answer = engine.answer(DocumentQuestion(question="What is the application fee?"))
    assert answer.found_in_document is True
    assert "NIL" in answer.answer.upper() or "nil" in answer.answer.lower()

def test_qa_required_documents():
    engine = DocumentQAEngine()
    engine.load_document(preloaded_doc=SAMPLE_DOC)
    answer = engine.answer(DocumentQuestion(question="What documents are required?"))
    assert answer.found_in_document is True
    assert len(answer.answer) > 5

def test_qa_not_found():
    engine = DocumentQAEngine()
    engine.load_document(preloaded_doc=SAMPLE_DOC)
    answer = engine.answer(DocumentQuestion(question="What is the color of the building?"))
    assert answer.found_in_document is False
    assert "not found" in answer.answer.lower()

def test_qa_no_document_loaded():
    engine = DocumentQAEngine()
    answer = engine.answer(DocumentQuestion(question="What is the deadline?"))
    assert answer.found_in_document is False
    assert "No document" in answer.answer

def test_qa_batch():
    engine = DocumentQAEngine()
    engine.load_document(preloaded_doc=SAMPLE_DOC)
    questions = [
        DocumentQuestion(question="What is the deadline?"),
        DocumentQuestion(question="Who issued this?"),
    ]
    answers = engine.answer_batch(questions)
    assert len(answers) == 2
    assert all(isinstance(a, DocumentAnswer) for a in answers)
'''
write_file(r"C:\Users\HP\.gemini\antigravity\scratch\AccessIt\tests\unit\test_document_qa.py", tests_qa)

tests_pers = '''import pytest
from ai.learning.learning_service import AccessibilityLearningService
from shared.schemas.models import PersonalizationSuggestion

def test_pattern_suggestions_empty_baseline():
    service = AccessibilityLearningService()
    suggestions = service.get_pattern_suggestions()
    assert len(suggestions) >= 1
    assert "pattern_type" in suggestions[0]
    assert suggestions[0]["consent_required"] is True

def test_pattern_suggestions_voice_dominant():
    service = AccessibilityLearningService()
    for i in range(10):
        service.record_interaction(f"step_{i}", "voice", 3.0, 0, True)
    suggestions = service.get_pattern_suggestions()
    types = [s["pattern_type"] for s in suggestions]
    assert "preferred_modality" in types

def test_pattern_suggestions_high_retries():
    service = AccessibilityLearningService()
    for i in range(5):
        service.record_interaction("aadhaar_input", "voice", 20.0, 3, False)
    suggestions = service.get_pattern_suggestions()
    types = [s["pattern_type"] for s in suggestions]
    assert any(t in ("repeated_interaction_barrier", "task_failure_pattern") for t in types)

def test_pattern_suggestion_consent_required():
    service = AccessibilityLearningService()
    service.record_interaction("form_step", "voice", 2.0, 0, True)
    suggestions = service.get_pattern_suggestions()
    for s in suggestions:
        assert s["consent_required"] is True
'''
write_file(r"C:\Users\HP\.gemini\antigravity\scratch\AccessIt\tests\unit\test_personalization.py", tests_pers)

tests_ast = '''import pytest
from ai.assistance.assistance_engine import AccessibilityAssistanceEngine
from shared.schemas.models import AccessibilityTwin, LanguagePreference

def test_assist_document_english():
    engine = AccessibilityAssistanceEngine()
    twin = AccessibilityTwin(id="t1", language=LanguagePreference.ENGLISH)
    result = engine.assist_understand_document(None, "What is the deadline?", twin)
    assert "title" in result
    assert "deadlines" in result
    assert "spoken_summary" in result
    assert result["language"] == "English"

def test_assist_document_hindi():
    engine = AccessibilityAssistanceEngine()
    twin = AccessibilityTwin(id="t1", language=LanguagePreference.HINDI)
    result = engine.assist_understand_document(None, "क्या है?", twin)
    assert result["language"] == "Hindi"

def test_assist_find_object():
    engine = AccessibilityAssistanceEngine()
    twin = AccessibilityTwin(id="t1")
    result = engine.assist_find_object("water bottle", twin)
    assert "direction" in result or "clock_hour" in result or "spoken_direction" in result

def test_assist_sign_communication():
    engine = AccessibilityAssistanceEngine()
    twin = AccessibilityTwin(id="t1")
    result = engine.assist_sign_communication(None, twin)
    assert "sign" in result
    assert result["sign"] == "HELP"
'''
write_file(r"C:\Users\HP\.gemini\antigravity\scratch\AccessIt\tests\unit\test_assistance.py", tests_ast)

tests_mm = '''import pytest
from ai.orchestrator.ai_pipeline import AIPipeline

def test_pipeline_form_completion():
    pipeline = AIPipeline()
    result = pipeline.run(query="Help me fill this form", twin_id="default_user")
    assert "intent" in result
    assert result["intent"]["intent"] == "FORM_COMPLETION"
    assert "barriers" in result
    assert "learning_recorded" in result
    assert result["learning_recorded"] is True

def test_pipeline_document_reading():
    pipeline = AIPipeline()
    result = pipeline.run(query="What is important in this notice?", twin_id="default_user")
    assert result["intent"]["intent"] == "UNDERSTAND_DOCUMENT"
    assert "capabilities" in result
    assert "document" in result["capabilities"]

def test_pipeline_no_query_defaults_to_see():
    pipeline = AIPipeline()
    result = pipeline.run(twin_id="default_user")
    assert "intent" in result
    assert "pipeline_stages" in result
    assert "twin" in result

def test_pipeline_recovery_on_failure():
    pipeline = AIPipeline()
    result = pipeline.run(query="Read this notice", twin_id="default_user")
    assert "recovery" in result
    # May have 0 or more recovery actions depending on OCR confidence
    assert isinstance(result["recovery"], list)

def test_pipeline_all_stages_recorded():
    pipeline = AIPipeline()
    result = pipeline.run(query="Help me fill this form", twin_id="default_user")
    stages = result["pipeline_stages"]
    for expected in ["twin", "intent", "barriers", "task_engine", "flow_compiler"]:
        assert expected in stages
'''
write_file(r"C:\Users\HP\.gemini\antigravity\scratch\AccessIt\tests\integration\test_multimodal_pipeline.py", tests_mm)

tests_vis = '''import pytest
from ai.scene.scene_understanding import SceneUnderstandingEngine
from ai.navigation.navigation_engine import NavigationEngine
from shared.schemas.models import AccessibilityTwin, TaskType, LanguagePreference

def test_vision_pipeline_no_image():
    engine = SceneUnderstandingEngine()
    twin = AccessibilityTwin(id="t1")
    scene = engine.analyze(image_bytes=None, twin=twin, task_type=TaskType.SEE)
    assert len(scene.objects) > 0
    assert scene.summary is not None

def test_vision_pipeline_hindi_twin():
    engine = SceneUnderstandingEngine()
    twin = AccessibilityTwin(id="t1", language=LanguagePreference.HINDI)
    scene = engine.analyze(image_bytes=None, twin=twin)
    assert scene.summary is not None

def test_navigation_pipeline_no_image():
    engine = NavigationEngine()
    result = engine.navigate(image_bytes=None, target_label="medicine bottle")
    assert "instructions" in result
    assert len(result["instructions"]) > 0
    assert result["disclaimer"] is not None

def test_navigation_pipeline_obstacle_handling():
    engine = NavigationEngine()
    result = engine.navigate(image_bytes=None)
    assert "instructions" in result
    instr = result["instructions"]
    assert all("direction" in i for i in instr)
'''
write_file(r"C:\Users\HP\.gemini\antigravity\scratch\AccessIt\tests\integration\test_vision_pipeline.py", tests_vis)

tests_qap = '''import pytest
from ai.ocr.document_qa import DocumentQAEngine
from ai.task.document_task_generator import DocumentTaskGenerator
from shared.schemas.models import DocumentQuestion, TaskType

SAMPLE_DOC = {
    "document_title": "National Scholarship 2026",
    "issuing_authority": "Ministry of Education",
    "key_deadlines": ["October 15, 2026"],
    "required_documents": ["Aadhaar Card", "Income Certificate"],
    "application_fee": "NIL",
    "simplified_summary_en": "Apply before October 15 with Aadhaar and income certificate.",
    "simplified_summary_hi": "15 अक्टूबर से पहले आवेदन करें।",
    "action_items": ["Gather documents", "Fill form", "Submit online"],
}

def test_qa_pipeline_full():
    engine = DocumentQAEngine()
    engine.load_document(preloaded_doc=SAMPLE_DOC)
    questions = [
        DocumentQuestion(question="What is the deadline?"),
        DocumentQuestion(question="What is the application fee?"),
        DocumentQuestion(question="What documents do I need?"),
    ]
    answers = engine.answer_batch(questions)
    assert len(answers) == 3
    assert answers[0].found_in_document is True
    assert "October" in answers[0].answer or "15" in answers[0].answer

def test_document_task_generator():
    generator = DocumentTaskGenerator()
    result = generator.generate_from_document(SAMPLE_DOC)
    assert "task_id" in result
    assert result["title"] == "National Scholarship 2026"
    assert result["task_type"] == TaskType.UNDERSTAND_DOCUMENT.value
    assert len(result["milestones"]) > 0

def test_document_submission_task():
    generator = DocumentTaskGenerator()
    result = generator.generate_submission_task(SAMPLE_DOC)
    assert "task_id" in result
    assert result["task_type"] == TaskType.FORM_COMPLETION.value
    assert result["source"] == "document"
'''
write_file(r"C:\Users\HP\.gemini\antigravity\scratch\AccessIt\tests\integration\test_document_qa_pipeline.py", tests_qap)

tests_vcp = '''import pytest
from ai.voice.voice_command import VoiceCommandProcessor
from shared.schemas.models import AccessibilityTwin, LanguagePreference

def test_voice_pipeline_english():
    processor = VoiceCommandProcessor()
    twin = AccessibilityTwin(id="t1", language=LanguagePreference.ENGLISH)
    result = processor.process(text_input="What is the deadline in this notice?", twin=twin)
    assert result["voice_command"]["raw_text"] == "What is the deadline in this notice?"
    assert "intent_analysis" in result
    assert result["intent_analysis"]["intent"] == "UNDERSTAND_DOCUMENT"

def test_voice_pipeline_hindi_twin():
    processor = VoiceCommandProcessor()
    twin = AccessibilityTwin(id="t1", language=LanguagePreference.HINDI)
    result = processor.process(text_input="Form भरने में मदद करो", twin=twin)
    assert "intent_analysis" in result

def test_voice_pipeline_no_input():
    processor = VoiceCommandProcessor()
    result = processor.process()
    assert "error" in result
'''
write_file(r"C:\Users\HP\.gemini\antigravity\scratch\AccessIt\tests\integration\test_voice_pipeline.py", tests_vcp)

tests_navp = '''import pytest
from ai.navigation.navigation_engine import NavigationEngine
from shared.schemas.models import AccessibilityTwin, LanguagePreference

def test_navigation_full_pipeline():
    engine = NavigationEngine()
    twin = AccessibilityTwin(id="t1", language=LanguagePreference.ENGLISH)
    result = engine.navigate(image_bytes=None, target_label="water bottle", twin=twin)
    assert "instructions" in result
    assert "hazards" in result
    assert result["disclaimer"] is not None
    for instr in result["instructions"]:
        assert "direction" in instr
        assert "description" in instr

def test_navigation_hindi_instructions():
    engine = NavigationEngine()
    twin = AccessibilityTwin(id="t1", language=LanguagePreference.HINDI)
    result = engine.navigate(image_bytes=None, target_label="medicine bottle", twin=twin)
    assert len(result["instructions"]) > 0
    for instr in result["instructions"]:
        # Hindi instructions have description_hi
        assert "description_hi" in instr
'''
write_file(r"C:\Users\HP\.gemini\antigravity\scratch\AccessIt\tests\integration\test_navigation_pipeline.py", tests_navp)
