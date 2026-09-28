"""
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
            h = max(1, image_height)
            ymin /= h
            ymax /= h
        y_center = max(0.0, min(1.0, (ymin + ymax) / 2.0))

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
