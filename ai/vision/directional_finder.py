"""
Sahayak AI — Directional Guidance & Object Finding Engine
Synthesizes spatial directional instructions and haptic cues from object bounding boxes.
Adheres to design principle: Never claims false exact millimeter depth without hardware depth sensors.
"""

from typing import Dict, Any, Optional, Tuple


class DirectionalFinder:
    def __init__(self, frame_width: int = 640, frame_height: int = 480):
        self.frame_width = frame_width
        self.frame_height = frame_height

    def compute_spatial_guidance(
        self,
        bbox: Tuple[int, int, int, int],
        label: str,
        language: str = "Hindi"
    ) -> Dict[str, Any]:
        """
        Takes [xmin, ymin, xmax, ymax] and computes direction relative to camera center.
        """
        xmin, ymin, xmax, ymax = bbox
        center_x = (xmin + xmax) / 2.0
        norm_x = center_x / float(self.frame_width)

        # Estimate relative size to approximate proximity
        box_area = (xmax - xmin) * (ymax - ymin)
        total_area = self.frame_width * self.frame_height
        area_ratio = box_area / float(total_area)

        if area_ratio > 0.25:
            proximity_en = "very close"
            proximity_hi = "बिल्कुल पास"
        elif area_ratio > 0.08:
            proximity_en = "within arm's reach"
            proximity_hi = "हाथ की पहुंच में"
        else:
            proximity_en = "a few steps ahead"
            proximity_hi = "थोड़ी दूरी पर"

        if norm_x < 0.35:
            direction_en = "to your left"
            direction_hi = "आपके बाईं ओर"
            haptic_cue = "PULSE_LEFT"
        elif norm_x > 0.65:
            direction_en = "to your right"
            direction_hi = "आपके दाईं ओर"
            haptic_cue = "PULSE_RIGHT"
        else:
            direction_en = "straight ahead"
            direction_hi = "बिल्कुल सामने"
            haptic_cue = "DOUBLE_PULSE_CENTER"

        if language == "Hindi":
            spoken = f"आपकी {label} {direction_hi} {proximity_hi} है।"
            display = f"{label.capitalize()}: {direction_hi} ({proximity_hi})"
        else:
            spoken = f"Your {label} is {direction_en}, {proximity_en}."
            display = f"{label.capitalize()}: {direction_en} ({proximity_en})"

        return {
            "label": label,
            "relative_direction": direction_en,
            "relative_proximity": proximity_en,
            "spoken_guidance": spoken,
            "display_guidance": display,
            "haptic_cue": haptic_cue,
            "normalized_x": round(norm_x, 2),
        }
