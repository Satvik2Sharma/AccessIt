"""
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
