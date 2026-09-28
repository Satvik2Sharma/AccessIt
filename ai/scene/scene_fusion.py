"""
Sahayak AI — Enhanced Scene Fusion Adapter
Adapted from SightAssist (MIT License, Copyright 2023 Arnav Argon).
Geometrically and semantically associates detected OCR text entries with physical object bounding boxes.
"""

from typing import List, Dict, Any, Optional, Tuple


class SceneFusion:
    def __init__(self, proximity_threshold_px: float = 50.0):
        self.proximity_threshold_px = proximity_threshold_px

    def _compute_overlap_ratio(
        self,
        box_a: Tuple[int, int, int, int],
        box_b: Tuple[int, int, int, int]
    ) -> float:
        """Computes intersection over text box area."""
        ax_min, ay_min, ax_max, ay_max = box_a
        bx_min, by_min, bx_max, by_max = box_b

        ix_min = max(ax_min, bx_min)
        iy_min = max(ay_min, by_min)
        ix_max = min(ax_max, bx_max)
        iy_max = min(ay_max, by_max)

        if ix_max <= ix_min or iy_max <= iy_min:
            return 0.0

        intersection_area = (ix_max - ix_min) * (iy_max - iy_min)
        text_area = max(1, (ax_max - ax_min) * (ay_max - ay_min))
        return float(intersection_area) / float(text_area)

    def fuse(
        self,
        objects: List[Dict[str, Any]],
        texts: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Associates text detections with bounding boxes of objects using
        both containment and high-overlap intersection.
        """
        if not objects and not texts:
            return {"objects": [], "texts": []}

        scene: Dict[str, Any] = {"objects": [], "texts": texts or []}
        obj_list = []

        for obj in (objects or []):
            obj_copy = dict(obj)
            obj_copy.setdefault("associated_texts", [])
            obj_copy.setdefault("text", None)
            obj_list.append(obj_copy)

        for text_item in texts:
            t_bbox = text_item.get("bbox", (0, 0, 0, 0))
            t_str = text_item.get("text", "")
            best_obj = None
            best_overlap = 0.0

            for obj in obj_list:
                o_bbox = obj.get("bbox", (0, 0, 0, 0))
                overlap = self._compute_overlap_ratio(t_bbox, o_bbox)
                if overlap > 0.40 and overlap > best_overlap:
                    best_overlap = overlap
                    best_obj = obj

            if best_obj:
                best_obj["associated_texts"].append(t_str)
                best_obj["text"] = " ".join(best_obj["associated_texts"])

        scene["objects"] = obj_list
        return scene

    def search_fused_scene(
        self,
        scene: Dict[str, Any],
        target_label: Optional[str] = None,
        target_text: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Finds matching objects in the fused scene matching label and/or contained text."""
        matches = []
        for obj in scene.get("objects", []):
            label_match = True
            text_match = True

            if target_label:
                label_match = target_label.lower() in obj.get("label", "").lower()
            if target_text:
                associated = " ".join(obj.get("associated_texts", [])).lower()
                text_match = target_text.lower() in associated

            if label_match and text_match:
                matches.append(obj)

        return matches
