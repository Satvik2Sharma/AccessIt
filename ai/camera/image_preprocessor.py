"""
Sahayak AI — Image Preprocessor
Modular image transformations, color space conversions, rotation normalization,
document perspective correction, and image quality estimation.
Used across OCR, Vision, ISL, and Camera pipelines.
"""

import io
import base64
from typing import Union, Tuple, Optional, Dict, Any
from PIL import Image, ImageOps, ImageEnhance
import numpy as np
try:
    import cv2
    HAS_CV2 = True
except ImportError:
    cv2 = None
    HAS_CV2 = False


class ImagePreprocessor:
    """
    Utility class for standardizing camera frames and document images
    before sending to AI perception modules.
    """

    @staticmethod
    def load_image(image_input: Union[bytes, str, Image.Image, np.ndarray]) -> Image.Image:
        """
        Universal image loader supporting raw bytes, base64 string, PIL Image,
        numpy ndarray, or file path.
        """
        if isinstance(image_input, Image.Image):
            return image_input.convert("RGB")

        if isinstance(image_input, np.ndarray):
            # Check if OpenCV BGR or RGB
            if len(image_input.shape) == 3 and image_input.shape[2] == 3:
                return Image.fromarray(cv2.cvtColor(image_input, cv2.COLOR_BGR2RGB))
            return Image.fromarray(image_input).convert("RGB")

        if isinstance(image_input, str):
            # Base64 data URL
            if image_input.startswith("data:image"):
                base64_data = image_input.split(",")[1]
                image_bytes = base64.b64decode(base64_data)
                return Image.open(io.BytesIO(image_bytes)).convert("RGB")
            # Raw base64 string or file path
            try:
                if len(image_input) > 260 and not image_input.endswith((".jpg", ".png", ".jpeg")):
                    image_bytes = base64.b64decode(image_input)
                    return Image.open(io.BytesIO(image_bytes)).convert("RGB")
                return Image.open(image_input).convert("RGB")
            except Exception:
                return Image.open(image_input).convert("RGB")

        if isinstance(image_input, (bytes, bytearray)):
            return Image.open(io.BytesIO(image_input)).convert("RGB")

        raise ValueError(f"Unsupported image input type: {type(image_input)}")

    @staticmethod
    def to_bytes(image: Image.Image, format: str = "JPEG", quality: int = 90) -> bytes:
        """Converts PIL Image to bytes."""
        buf = io.BytesIO()
        image.save(buf, format=format, quality=quality)
        return buf.getvalue()

    @staticmethod
    def to_cv2(image: Image.Image) -> np.ndarray:
        """Converts PIL Image (RGB) to OpenCV format (BGR) or numpy array."""
        np_arr = np.array(image.convert("RGB"))
        if HAS_CV2 and cv2 is not None:
            return cv2.cvtColor(np_arr, cv2.COLOR_RGB2BGR)
        return np_arr

    @staticmethod
    def from_cv2(cv_img: np.ndarray) -> Image.Image:
        """Converts OpenCV format (BGR) to PIL Image (RGB)."""
        if HAS_CV2 and cv2 is not None:
            rgb = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
            return Image.fromarray(rgb)
        return Image.fromarray(cv_img)

    @staticmethod
    def normalize_rotation(image: Image.Image) -> Image.Image:
        """Corrects orientation based on EXIF tags."""
        try:
            return ImageOps.exif_transpose(image)
        except Exception:
            return image

    @staticmethod
    def resize_keep_aspect(image: Image.Image, max_dim: int = 1280) -> Image.Image:
        """
        Resizes image so that neither width nor height exceeds max_dim,
        preserving aspect ratio.
        """
        limit = max(1, max_dim)
        width, height = image.size
        if width <= limit and height <= limit:
            return image

        if width > height:
            new_w = limit
            new_h = max(1, int(height * (limit / max(1, width))))
        else:
            new_h = limit
            new_w = max(1, int(width * (limit / max(1, height))))

        return image.resize((new_w, new_h), Image.Resampling.LANCZOS)

    @staticmethod
    def adjust_brightness_contrast(
        image: Image.Image,
        brightness_factor: float = 1.0,
        contrast_factor: float = 1.0
    ) -> Image.Image:
        """Adjusts brightness and contrast via PIL enhancers."""
        out = image
        if brightness_factor != 1.0:
            enhancer = ImageEnhance.Brightness(out)
            out = enhancer.enhance(brightness_factor)
        if contrast_factor != 1.0:
            enhancer = ImageEnhance.Contrast(out)
            out = enhancer.enhance(contrast_factor)
        return out

    @staticmethod
    def crop_region(
        image: Image.Image,
        bbox: Union[Tuple[int, int, int, int], Tuple[float, float, float, float]],
        normalized: bool = False
    ) -> Image.Image:
        """
        Crops bounding box (xmin, ymin, xmax, ymax).
        If normalized is True, coordinates are between 0.0 and 1.0.
        """
        w, h = image.size
        x1, y1, x2, y2 = bbox
        if normalized:
            x1, y1, x2, y2 = int(x1 * w), int(y1 * h), int(x2 * w), int(y2 * h)

        # Clamp boundaries
        x1 = max(0, min(w - 1, int(x1)))
        y1 = max(0, min(h - 1, int(y1)))
        x2 = max(x1 + 1, min(w, int(x2)))
        y2 = max(y1 + 1, min(h, int(y2)))

        return image.crop((x1, y1, x2, y2))

    @staticmethod
    def correct_document_perspective(image: Image.Image) -> Image.Image:
        """
        Finds document contours and performs 4-point perspective warp.
        If no clear document quad is found, returns original image.
        """
        if not HAS_CV2 or cv2 is None:
            return image
        cv_img = ImagePreprocessor.to_cv2(image)
        gray = cv2.cvtColor(cv_img, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        edged = cv2.Canny(blurred, 75, 200)

        contours, _ = cv2.findContours(edged.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
        contours = sorted(contours, key=cv2.contourArea, reverse=True)[:5]

        doc_contour = None
        for c in contours:
            peri = cv2.arcLength(c, True)
            approx = cv2.approxPolyDP(c, 0.02 * peri, True)
            if len(approx) == 4 and cv2.contourArea(c) > (image.width * image.height * 0.15):
                doc_contour = approx
                break

        if doc_contour is None:
            return image

        # 4-point warp
        pts = doc_contour.reshape(4, 2)
        rect = np.zeros((4, 2), dtype="float32")
        s = pts.sum(axis=1)
        rect[0] = pts[np.argmin(s)]
        rect[2] = pts[np.argmax(s)]

        diff = np.diff(pts, axis=1)
        rect[1] = pts[np.argmin(diff)]
        rect[3] = pts[np.argmax(diff)]

        (tl, tr, br, bl) = rect
        width_a = np.sqrt(((br[0] - bl[0]) ** 2) + ((br[1] - bl[1]) ** 2))
        width_b = np.sqrt(((tr[0] - tl[0]) ** 2) + ((tr[1] - tl[1]) ** 2))
        max_w = max(int(width_a), int(width_b))

        height_a = np.sqrt(((tr[0] - br[0]) ** 2) + ((tr[1] - br[1]) ** 2))
        height_b = np.sqrt(((tl[0] - bl[0]) ** 2) + ((tl[1] - bl[1]) ** 2))
        max_h = max(int(height_a), int(height_b))

        if max_w < 50 or max_h < 50:
            return image

        dst = np.array([
            [0, 0],
            [max_w - 1, 0],
            [max_w - 1, max_h - 1],
            [0, max_h - 1]
        ], dtype="float32")

        transform_matrix = cv2.getPerspectiveTransform(rect, dst)
        warped = cv2.warpPerspective(cv_img, transform_matrix, (max_w, max_h))
        return ImagePreprocessor.from_cv2(warped)
