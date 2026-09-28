"""
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
    ) -> Dict[str, Any]:
        """
        Estimate coarse proximity.

        Returns:
            dict with zone, label, label_hi, haptic_cue, bbox_area
        """
        xmin, ymin, xmax, ymax = bbox
        if not normalized:
            w = max(1, image_width)
            h = max(1, image_height)
            xmin /= w
            xmax /= w
            ymin /= h
            ymax /= h
        area = max(0.0, min(1.0, (xmax - xmin) * (ymax - ymin)))
        for threshold, zone, label, label_hi, haptic in self.ZONES:
            if area >= threshold:
                return {"zone": zone, "label": label, "label_hi": label_hi, "haptic_cue": haptic, "bbox_area": round(area, 4)}
        return {"zone": "several_steps", "label": "Several steps away", "label_hi": "कुछ कदम दूर", "haptic_cue": "LIGHT_PULSE", "bbox_area": round(area, 4)}
