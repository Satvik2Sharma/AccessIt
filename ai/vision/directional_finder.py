"""
Sahayak AI — Enhanced Directional Guidance & Clock-Face Spatial Engine
Synthesizes 12-hour clock-face spatial guidance, vertical elevations,
proximity estimates, and tactile haptic cues from object bounding boxes.
Adheres strictly to the accessibility design principle: Never claims false exact millimeter depth.
"""

import math
from typing import Dict, Any, Optional, Tuple


class DirectionalFinder:
    def __init__(self, frame_width: int = 640, frame_height: int = 480):
        self.frame_width = max(1, frame_width)
        self.frame_height = max(1, frame_height)

    def _calculate_clock_position(self, norm_x: float, norm_y: float) -> Tuple[int, str, str]:
        """
        Calculates clock-face direction (1 to 12) from normalized (x, y) coordinates [0.0 to 1.0].
        (0.5, 0.5) is dead center.
        """
        # Vector from center (0.5, 0.5)
        # Note: image y grows downward, so dy is positive upwards
        dx = norm_x - 0.5
        dy = 0.5 - norm_y

        dist_from_center = math.sqrt(dx * dx + dy * dy)
        if dist_from_center < 0.12:
            return 12, "straight ahead (12 o'clock)", "बिल्कुल सामने (12 बजे की दिशा)"

        # Angle in degrees where 0 deg is North (12 o'clock), 90 deg is East (3 o'clock)
        angle_rad = math.atan2(dx, dy)
        angle_deg = math.degrees(angle_rad) % 360

        # Map 360 degrees into 12 clock hours
        clock_hour = int(round(angle_deg / 30.0)) % 12
        if clock_hour == 0:
            clock_hour = 12

        en_str = f"at {clock_hour} o'clock"
        hi_str = f"{clock_hour} बजे की दिशा में"
        return clock_hour, en_str, hi_str

    def _determine_elevation(self, norm_y: float) -> Tuple[str, str]:
        """Determines vertical level (eye level, waist/table level, floor)."""
        if norm_y < 0.35:
            return "upper/eye level", "ऊपर की ओर"
        elif norm_y > 0.70:
            return "low/floor level", "नीचे की ओर"
        else:
            return "table/waist level", "मेज के स्तर पर"

    def compute_spatial_guidance(
        self,
        bbox: Tuple[int, int, int, int],
        label: str,
        language: str = "Hindi"
    ) -> Dict[str, Any]:
        """
        Takes [xmin, ymin, xmax, ymax] and computes 12-hour clock direction,
        vertical elevation, proximity heuristic, and specialized haptic cues.
        """
        xmin, ymin, xmax, ymax = bbox if bbox and len(bbox) == 4 else (0, 0, 0, 0)
        center_x = (xmin + xmax) / 2.0
        center_y = (ymin + ymax) / 2.0

        norm_x = center_x / float(self.frame_width)
        norm_y = center_y / float(self.frame_height)

        # 1. Proximity via bounding box area ratio
        box_area = (xmax - xmin) * (ymax - ymin)
        total_area = float(self.frame_width * self.frame_height)
        area_ratio = box_area / total_area

        if area_ratio > 0.25:
            proximity_en = "very close"
            proximity_hi = "बिल्कुल पास"
            haptic_intensity = "HIGH_URGENT"
        elif area_ratio > 0.08:
            proximity_en = "within arm's reach"
            proximity_hi = "हाथ की पहुंच में"
            haptic_intensity = "MEDIUM"
        else:
            proximity_en = "a few steps ahead"
            proximity_hi = "थोड़ी दूरी पर"
            haptic_intensity = "LIGHT"

        # 2. Clock Position & Elevation
        clock_hour, clock_en, clock_hi = self._calculate_clock_position(norm_x, norm_y)
        elev_en, elev_hi = self._determine_elevation(norm_y)

        # 3. Direction and Haptic Cue
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
            spoken = f"आपकी {label} {clock_hi}, {elev_hi}, {proximity_hi} है।"
            display = f"{label.capitalize()}: {clock_hi} | {elev_hi} ({proximity_hi})"
        else:
            spoken = f"Your {label} is {clock_en}, {elev_en}, {proximity_en}."
            display = f"{label.capitalize()}: {clock_en} | {elev_en} ({proximity_en})"

        return {
            "label": label,
            "relative_direction": direction_en,
            "clock_hour": clock_hour,
            "clock_direction": clock_en,
            "elevation": elev_en,
            "relative_proximity": proximity_en,
            "spoken_guidance": spoken,
            "display_guidance": display,
            "haptic_cue": haptic_cue,
            "haptic_intensity": haptic_intensity,
            "normalized_coordinates": {"x": round(norm_x, 2), "y": round(norm_y, 2)},
            "area_ratio": round(area_ratio, 3),
        }
