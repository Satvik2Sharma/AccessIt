"""
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
        if not detections:
            return []
        ocr_elements = ocr_elements or []
        width = max(1, image_width)
        height = max(1, image_height)

        enriched = []
        for det in detections:
            det_copy = dict(det)
            obj_bbox = det_copy.get("bbox") or [0, 0, 1, 1]
            # Normalize object bbox if not already
            if max(obj_bbox) > 1.0 and width > 1:
                obj_bbox = [obj_bbox[0]/width, obj_bbox[1]/height,
                            obj_bbox[2]/width, obj_bbox[3]/height]

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
