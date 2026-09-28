"""
Sahayak AI — Unit Tests for Camera Intelligence
Validates image preprocessing, frame quality filtering, duplicate detection,
capability planning, session state tracking, and CameraEngine routing.
"""

import io
import pytest
from PIL import Image, ImageDraw
import numpy as np

from shared.schemas.camera_models import CameraMode, FrameQualityMetrics, CameraAnalysisResult
from shared.schemas.models import AccessibilityTwin, LanguagePreference
from ai.camera.image_preprocessor import ImagePreprocessor
from ai.camera.frame_processor import FrameProcessor
from ai.camera.camera_session import CameraSession, CameraSessionManager
from ai.camera.camera_analyzer import CameraAnalyzer
from ai.camera.camera_engine import CameraEngine


@pytest.fixture
def sample_sharp_image():
    """Generates a high-contrast sharp test image with geometry."""
    img = Image.new("RGB", (320, 240), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)
    draw.rectangle([40, 40, 280, 200], outline=(0, 0, 0), width=4)
    draw.line([0, 0, 320, 240], fill=(0, 0, 0), width=3)
    draw.line([0, 240, 320, 0], fill=(0, 0, 0), width=3)
    return img


@pytest.fixture
def sample_blurry_image():
    """Generates an image with zero edge gradients."""
    return Image.new("RGB", (320, 240), color=(128, 128, 128))


@pytest.fixture
def sample_dark_image():
    """Generates an underexposed dark image."""
    return Image.new("RGB", (320, 240), color=(10, 10, 10))


# ----------------------------------------------------
# 1. Image Preprocessor Tests
# ----------------------------------------------------

def test_preprocessor_load_pil(sample_sharp_image):
    loaded = ImagePreprocessor.load_image(sample_sharp_image)
    assert isinstance(loaded, Image.Image)
    assert loaded.size == (320, 240)


def test_preprocessor_load_bytes(sample_sharp_image):
    buf = io.BytesIO()
    sample_sharp_image.save(buf, format="JPEG")
    loaded = ImagePreprocessor.load_image(buf.getvalue())
    assert isinstance(loaded, Image.Image)
    assert loaded.size == (320, 240)


def test_preprocessor_to_cv2(sample_sharp_image):
    cv_img = ImagePreprocessor.to_cv2(sample_sharp_image)
    assert isinstance(cv_img, np.ndarray)
    assert cv_img.shape == (240, 320, 3)


def test_preprocessor_resize(sample_sharp_image):
    large_img = Image.new("RGB", (2000, 1000), color=(200, 200, 200))
    resized = ImagePreprocessor.resize_keep_aspect(large_img, max_dim=800)
    assert max(resized.size) <= 800
    assert resized.size == (800, 400)


def test_preprocessor_crop_region(sample_sharp_image):
    cropped = ImagePreprocessor.crop_region(sample_sharp_image, (10, 10, 50, 50))
    assert cropped.size == (40, 40)


# ----------------------------------------------------
# 2. Frame Processor & Quality Tests
# ----------------------------------------------------

def test_frame_quality_sharp(sample_sharp_image):
    processor = FrameProcessor()
    metrics = processor.assess_quality(sample_sharp_image)
    assert isinstance(metrics, FrameQualityMetrics)
    assert metrics.is_valid is True
    assert metrics.blur_score > 50.0
    assert metrics.is_blurry is False


def test_frame_quality_blurry(sample_blurry_image):
    processor = FrameProcessor()
    metrics = processor.assess_quality(sample_blurry_image)
    assert metrics.is_blurry is True
    assert metrics.quality_verdict in ("BLURRY", "BLURRY_AND_POOR_LIGHT")
    assert metrics.recommendation is not None


def test_frame_quality_dark(sample_dark_image):
    processor = FrameProcessor()
    metrics = processor.assess_quality(sample_dark_image)
    assert metrics.is_underexposed is True


def test_frame_duplicate_detection(sample_sharp_image):
    processor = FrameProcessor()
    hash1 = processor.compute_perceptual_hash(sample_sharp_image)
    hash2 = processor.compute_perceptual_hash(sample_sharp_image)
    assert hash1 == hash2
    assert processor.is_duplicate(hash1, hash2) is True


def test_frame_alignment_check(sample_sharp_image):
    processor = FrameProcessor()
    align = processor.check_alignment(sample_sharp_image)
    assert "is_aligned" in align
    assert "recommendation" in align


# ----------------------------------------------------
# 3. Camera Session Tests
# ----------------------------------------------------

def test_camera_session_duplicate_tracking():
    sess = CameraSession("test_session_1")
    sess.record_frame("hash_alpha")
    assert sess.is_duplicate("hash_alpha") is True
    assert sess.is_duplicate("hash_beta") is False


def test_camera_session_reset():
    sess = CameraSession("test_session_2")
    sess.record_frame("hash_alpha")
    sess.update_context("target", "water bottle")
    sess.reset()
    assert sess.is_duplicate("hash_alpha") is False
    assert "target" not in sess.context


def test_camera_session_manager():
    manager = CameraSessionManager()
    s1 = manager.get_or_create("s_123")
    s2 = manager.get_or_create("s_123")
    assert s1.session_id == s2.session_id
    manager.remove_session("s_123")


# ----------------------------------------------------
# 4. Camera Analyzer Capability Planning Tests
# ----------------------------------------------------

def test_camera_analyzer_explicit_document():
    analyzer = CameraAnalyzer()
    plan = analyzer.plan_capabilities(mode="document")
    assert plan["effective_mode"] == "document"
    assert "ocr" in plan["required_capabilities"]


def test_camera_analyzer_explicit_navigation():
    analyzer = CameraAnalyzer()
    plan = analyzer.plan_capabilities(mode="navigation")
    assert plan["effective_mode"] == "navigation"
    assert "obstacle_detection" in plan["required_capabilities"]


def test_camera_analyzer_query_document():
    analyzer = CameraAnalyzer()
    plan = analyzer.plan_capabilities(mode="auto", query="Read this notice for me")
    assert plan["effective_mode"] == "document"


def test_camera_analyzer_query_see():
    analyzer = CameraAnalyzer()
    plan = analyzer.plan_capabilities(mode="auto", query="Where is my bottle?")
    assert plan["effective_mode"] == "see"
    assert "spatial_guidance" in plan["required_capabilities"]


# ----------------------------------------------------
# 5. Central CameraEngine Tests
# ----------------------------------------------------

def test_camera_engine_see_mode(sample_sharp_image):
    engine = CameraEngine()
    result = engine.analyze(
        image_input=sample_sharp_image,
        mode="see",
        target_object="bottle",
    )
    assert isinstance(result, CameraAnalysisResult)
    assert result.status == "SUCCESS"
    assert result.mode_executed == "see"
    assert len(result.spatial_objects) > 0


def test_camera_engine_navigation_mode(sample_sharp_image):
    engine = CameraEngine()
    result = engine.analyze(
        image_input=sample_sharp_image,
        mode="navigation",
    )
    assert result.mode_executed == "navigation"
    assert len(result.navigation_instructions) > 0


def test_camera_engine_isl_mode(sample_sharp_image):
    engine = CameraEngine()
    result = engine.analyze(
        image_input=sample_sharp_image,
        mode="isl",
    )
    assert result.mode_executed == "isl"
    assert result.isl_prediction is not None


def test_camera_engine_scene_mode(sample_sharp_image):
    engine = CameraEngine()
    result = engine.analyze(
        image_input=sample_sharp_image,
        mode="scene",
    )
    assert result.mode_executed == "scene"
    assert result.scene_summary is not None


def test_camera_engine_hindi_twin(sample_sharp_image):
    engine = CameraEngine()
    twin = AccessibilityTwin(id="hindi_user", language=LanguagePreference.HINDI)
    engine.twin_service.update_twin(twin)

    result = engine.analyze(
        image_input=sample_sharp_image,
        mode="navigation",
        twin_id="hindi_user",
    )
    assert result.spoken_feedback is not None
