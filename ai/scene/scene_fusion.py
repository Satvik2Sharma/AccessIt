"""
Sahayak AI — Scene Fusion Adapter
Adapted from SightAssist (MIT License, Copyright 2023 Arnav Argon).
Geometrically associates detected OCR text entries with physical object bounding boxes.
"""

from typing import List, Dict, Any


class SceneFusion:
    def __init__(self):
        pass

    def fuse(
        self,
        objects: List[Dict[str, Any]],
        texts: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Associates text detections with bounding boxes of objects if contained within.
        Returns a fused scene dictionary:
        {
          'objects': [ {'label': str, 'bbox': [xmin, ymin, xmax, ymax], 'text': Optional[str]} ],
          'texts': [ {'text': str, 'bbox': [...], 'confidence': float} ]
        }
        """
        scene: Dict[str, Any] = {"objects": [], "texts": texts}
        obj_list = []

        for obj in objects:
            obj_copy = dict(obj)
            obj_copy.pop("text", None)
            obj_list.append(obj_copy)

        for text in texts:
            tx_min, ty_min, tx_max, ty_max = text.get("bbox", [0, 0, 0, 0])
            for obj in obj_list:
                ox_min, oy_min, ox_max, oy_max = obj.get("bbox", [0, 0, 0, 0])
                # Spatial containment check
                if tx_min >= ox_min and ty_min >= oy_min and tx_max <= ox_max and ty_max <= oy_max:
                    obj["text"] = text.get("text", "")
                    break

        scene["objects"] = obj_list
        return scene
