"""
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
        x_norm = max(0.0, min(1.0, float(x_center)))
        y_norm = max(0.0, min(1.0, float(y_center)))

        dx = x_norm - 0.5
        dy = 0.5 - y_norm  # invert Y so up=positive
        angle_rad = math.atan2(dx, dy)  # angle from top (12 o'clock)
        angle_deg = math.degrees(angle_rad) % 360.0
        clock_hour = max(1, round(angle_deg / 30.0)) % 12 or 12

        if x_norm < 0.35:
            horizontal_zone = "left"
        elif x_norm > 0.65:
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
            w = max(1, image_width)
            h = max(1, image_height)
            xmin /= w
            xmax /= w
            ymin /= h
            ymax /= h
        x_center = (xmin + xmax) / 2.0
        y_center = (ymin + ymax) / 2.0
        return self.compute(x_center, y_center)
