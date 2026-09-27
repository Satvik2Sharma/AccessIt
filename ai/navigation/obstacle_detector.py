"""
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
