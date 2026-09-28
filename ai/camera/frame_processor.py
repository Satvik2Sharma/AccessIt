"""
Sahayak AI — Camera Frame Processor
Validates frames, estimates blur/lighting metrics, checks camera alignment,
detects duplicate frames via perceptual hashing, and throttles expensive AI pipelines.
"""

import time
import hashlib
from typing import Tuple, Optional, Dict, Any
from PIL import Image
import numpy as np
try:
    import cv2
    HAS_CV2 = True
except ImportError:
    cv2 = None
    HAS_CV2 = False

from shared.schemas.camera_models import FrameQualityMetrics
from ai.camera.image_preprocessor import ImagePreprocessor


class FrameProcessor:
    """
    Evaluates raw camera frames to ensure only high-quality, non-duplicate
    frames trigger heavy downstream AI models.
    """

    BLUR_THRESHOLD = 50.0  # Laplacian variance threshold
    MIN_BRIGHTNESS = 35.0   # 0-255 scale
    MAX_BRIGHTNESS = 225.0  # 0-255 scale
    MIN_DIMENSION = 120     # Minimum width/height in px

    def __init__(
        self,
        blur_threshold: float = BLUR_THRESHOLD,
        min_brightness: float = MIN_BRIGHTNESS,
        max_brightness: float = MAX_BRIGHTNESS,
    ):
        self.blur_threshold = blur_threshold
        self.min_brightness = min_brightness
        self.max_brightness = max_brightness
        self._last_processed_timestamp: float = 0.0

    def assess_quality(self, image: Image.Image) -> FrameQualityMetrics:
        """
        Calculates blur variance, luminance, and resolution quality metrics.
        Returns a structured FrameQualityMetrics object.
        """
        w, h = image.size

        # 1. Check minimum resolution
        if w < self.MIN_DIMENSION or h < self.MIN_DIMENSION:
            return FrameQualityMetrics(
                is_valid=False,
                blur_score=0.0,
                is_blurry=True,
                brightness=0.0,
                resolution=[w, h],
                quality_verdict="LOW_RES",
                recommendation="Camera resolution is too low. Please increase video quality.",
            )

        # 2. Convert to grayscale array for quality metrics
        if HAS_CV2 and cv2 is not None:
            cv_img = ImagePreprocessor.to_cv2(image)
            gray = cv2.cvtColor(cv_img, cv2.COLOR_BGR2GRAY)
            blur_variance = float(cv2.Laplacian(gray, cv2.CV_64F).var())
            mean_brightness = float(np.mean(gray))
        else:
            gray_img = image.convert("L")
            gray = np.array(gray_img, dtype=np.float64)
            # Standard variance of gradients as blur proxy
            gy, gx = np.gradient(gray)
            blur_variance = float(np.var(gx) + np.var(gy))
            mean_brightness = float(np.mean(gray))

        is_blurry = blur_variance < self.blur_threshold
        is_underexposed = mean_brightness < self.min_brightness
        is_overexposed = mean_brightness > self.max_brightness

        # Verdict assignment
        if is_blurry and (is_underexposed or is_overexposed):
            verdict = "BLURRY_AND_POOR_LIGHT"
            rec = "Hold the camera steady and move to better lighting."
        elif is_blurry:
            verdict = "BLURRY"
            rec = "Image is blurry. Please hold your camera steady."
        elif is_underexposed:
            verdict = "DARK"
            rec = "Lighting is too dark. Please turn on a light or move closer."
        elif is_overexposed:
            verdict = "OVEREXPOSED"
            rec = "Too much glare or brightness. Adjust angle to reduce reflection."
        else:
            verdict = "GOOD"
            rec = None

        return FrameQualityMetrics(
            is_valid=True,
            blur_score=round(blur_variance, 2),
            is_blurry=is_blurry,
            brightness=round(mean_brightness, 2),
            is_underexposed=is_underexposed,
            is_overexposed=is_overexposed,
            resolution=[w, h],
            quality_verdict=verdict,
            recommendation=rec,
        )

    def compute_perceptual_hash(self, image: Image.Image, hash_size: int = 8) -> str:
        """
        Computes difference hash (dHash) to detect duplicate or stationary frames.
        """
        # Resize to (hash_size + 1, hash_size)
        resized = image.convert("L").resize((hash_size + 1, hash_size), Image.Resampling.LANCZOS)
        pixels = np.array(resized)
        # Compute horizontal differences
        diff = pixels[:, 1:] > pixels[:, :-1]
        # Pack into hex string
        return hashlib.md5(diff.tobytes()).hexdigest()

    def is_duplicate(self, current_hash: str, previous_hash: Optional[str]) -> bool:
        """Returns True if current frame hash matches previous frame hash."""
        if not previous_hash:
            return False
        return current_hash == previous_hash

    def check_alignment(self, image: Image.Image) -> Dict[str, Any]:
        """
        Checks whether prominent content appears centered or clipped at the borders.
        """
        if HAS_CV2 and cv2 is not None:
            cv_img = ImagePreprocessor.to_cv2(image)
            gray = cv2.cvtColor(cv_img, cv2.COLOR_BGR2GRAY)
        else:
            gray = np.array(image.convert("L"))
        h, w = gray.shape

        # Sample border margins (5% on each edge)
        margin_x = max(1, int(w * 0.05))
        margin_y = max(1, int(h * 0.05))

        if h <= 2 * margin_y or w <= 2 * margin_x:
            return {
                "is_aligned": True,
                "border_variance": 0.0,
                "recommendation": "Well aligned",
            }

        border_pixels = np.concatenate([
            gray[:margin_y, :].flatten(),
            gray[-margin_y:, :].flatten(),
            gray[:, :margin_x].flatten(),
            gray[:, -margin_x:].flatten()
        ])
        center_pixels = gray[margin_y:-margin_y, margin_x:-margin_x]

        border_std = float(np.std(border_pixels))
        center_std = float(np.std(center_pixels))

        is_clipped = border_std > (center_std * 1.3)
        return {
            "is_aligned": not is_clipped,
            "border_variance": round(border_std, 2),
            "recommendation": "Center the object or document within the camera frame." if is_clipped else "Well aligned",
        }

    def should_sample_frame(self, min_interval_seconds: float = 0.25) -> bool:
        """
        Frame-rate throttling helper. Returns True if enough time
        has passed since the last processed frame.
        """
        now = time.time()
        if (now - self._last_processed_timestamp) >= min_interval_seconds:
            self._last_processed_timestamp = now
            return True
        return False
