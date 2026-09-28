"""
Sahayak AI — Unit Tests for Camera Intelligence & Frame Processing
Validates image preprocessing, frame quality filtering, duplicate detection,
capability planning, session state tracking, CameraEngine, and CameraService orchestration.
"""

import io
import os
import sys
import builtins
import typing
builtins.Union = typing.Union
import numpy as np
from PIL import Image, ImageDraw


ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)


from shared.schemas.camera_models import (
    CameraMode,
    CameraAnalysisMode,
    FrameQualityMetrics,
    CameraAnalysisResult,
    CameraFrameMetadata,
    CameraObject,
    CameraText,
    CameraObjectTextRelation,
    CameraSceneAnalysis,
    CameraAssistanceResponse,
    CameraError,
    CameraAnalysisResponse,
)
from shared.schemas.models import AccessibilityTwin, LanguagePreference
from ai.camera.image_preprocessor import ImagePreprocessor
from ai.camera.frame_processor import FrameProcessor
from ai.camera.camera_session import CameraSession, CameraSessionManager
from ai.camera.camera_analyzer import CameraAnalyzer
from ai.camera.camera_engine import CameraEngine
from backend.services.camera_service import camera_service
from backend.services.session_service import session_service


def sample_sharp_image():
    """Generates a high-contrast sharp test image with geometry."""
    img = Image.new("RGB", (320, 240), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)
    draw.rectangle([40, 40, 280, 200], outline=(0, 0, 0), width=4)
    draw.line([0, 0, 320, 240], fill=(0, 0, 0), width=3)
    draw.line([0, 240, 320, 0], fill=(0, 0, 0), width=3)
    return img


def sample_blurry_image():
    """Generates an image with zero edge gradients."""
    return Image.new("RGB", (320, 240), color=(128, 128, 128))


def sample_dark_image():
    """Generates an underexposed dark image."""
    return Image.new("RGB", (320, 240), color=(10, 10, 10))


# ----------------------------------------------------
# 1. Image Preprocessor Tests
# ----------------------------------------------------

def test_preprocessor_load_pil():
    img = sample_sharp_image()
    loaded = ImagePreprocessor.load_image(img)
    assert isinstance(loaded, Image.Image)
    assert loaded.size == (320, 240)


def test_preprocessor_load_bytes():
    img = sample_sharp_image()
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    loaded = ImagePreprocessor.load_image(buf.getvalue())
    assert isinstance(loaded, Image.Image)
    assert loaded.size == (320, 240)


def test_preprocessor_to_cv2():
    img = sample_sharp_image()
    cv_img = ImagePreprocessor.to_cv2(img)
    assert isinstance(cv_img, np.ndarray)
    assert cv_img.shape == (240, 320, 3)


def test_preprocessor_resize():
    large_img = Image.new("RGB", (2000, 1000), color=(200, 200, 200))
    resized = ImagePreprocessor.resize_keep_aspect(large_img, max_dim=800)
    assert max(resized.size) <= 800
    assert resized.size == (800, 400)


def test_preprocessor_crop_region():
    img = sample_sharp_image()
    cropped = ImagePreprocessor.crop_region(img, (10, 10, 50, 50))
    assert cropped.size == (40, 40)


# ----------------------------------------------------
# 2. Frame Processor & Quality Tests
# ----------------------------------------------------

def test_frame_quality_sharp():
    img = sample_sharp_image()
    processor = FrameProcessor()
    metrics = processor.assess_quality(img)
    assert isinstance(metrics, FrameQualityMetrics)
    assert metrics.is_valid is True
    assert metrics.blur_score > 50.0
    assert metrics.is_blurry is False


def test_frame_quality_blurry():
    img = sample_blurry_image()
    processor = FrameProcessor()
    metrics = processor.assess_quality(img)
    assert metrics.is_blurry is True
    assert metrics.quality_verdict in ("BLURRY", "BLURRY_AND_POOR_LIGHT")
    assert metrics.recommendation is not None


def test_frame_quality_dark():
    img = sample_dark_image()
    processor = FrameProcessor()
    metrics = processor.assess_quality(img)
    assert metrics.is_underexposed is True


def test_frame_duplicate_detection():
    img = sample_sharp_image()
    processor = FrameProcessor()
    hash1 = processor.compute_perceptual_hash(img)
    hash2 = processor.compute_perceptual_hash(img)
    assert hash1 == hash2
    assert processor.is_duplicate(hash1, hash2) is True


def test_frame_alignment_check():
    img = sample_sharp_image()
    processor = FrameProcessor()
    align = processor.check_alignment(img)
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

def test_camera_engine_see_mode():
    img = sample_sharp_image()
    engine = CameraEngine()
    result = engine.analyze(
        image_input=img,
        mode="see",
        target_object="bottle",
    )
    assert isinstance(result, CameraAnalysisResult)
    assert result.status == "SUCCESS"
    assert result.mode_executed == "see"
    assert len(result.spatial_objects) > 0


def test_camera_engine_navigation_mode():
    img = sample_sharp_image()
    engine = CameraEngine()
    result = engine.analyze(
        image_input=img,
        mode="navigation",
    )
    assert result.mode_executed == "navigation"
    assert len(result.navigation_instructions) > 0


def test_camera_engine_isl_mode():
    img = sample_sharp_image()
    engine = CameraEngine()
    result = engine.analyze(
        image_input=img,
        mode="isl",
    )
    assert result.mode_executed == "isl"
    assert result.isl_prediction is not None


def test_camera_engine_scene_mode():
    img = sample_sharp_image()
    engine = CameraEngine()
    result = engine.analyze(
        image_input=img,
        mode="scene",
    )
    assert result.mode_executed == "scene"
    assert result.scene_summary is not None


# ----------------------------------------------------
# 6. Backend Camera Service & Validation Tests
# ----------------------------------------------------

def _create_synthetic_image_bytes(width: int = 320, height: int = 240, color: str = "red") -> bytes:
    img = Image.new("RGB", (width, height), color=color)
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    return buf.getvalue()


def test_frame_validation_valid():
    valid_bytes = _create_synthetic_image_bytes(400, 300)
    is_valid, err, dims = camera_service.validate_image_frame(valid_bytes, "frame.jpg", "image/jpeg")
    assert is_valid is True
    assert err is None
    assert dims == (400, 300)


def test_frame_validation_empty_and_corrupt():
    is_valid, err, _ = camera_service.validate_image_frame(b"", "empty.jpg", "image/jpeg")
    assert is_valid is False
    assert "empty" in err.lower()

    is_valid, err, _ = camera_service.validate_image_frame(b"NOT_AN_IMAGE_DATA", "corrupt.jpg", "image/jpeg")
    assert is_valid is False
    assert "could not be decoded" in err.lower() or "corrupted" in err.lower()


def test_frame_validation_unsupported_mime():
    valid_bytes = _create_synthetic_image_bytes()
    is_valid, err, _ = camera_service.validate_image_frame(valid_bytes, "doc.pdf", "application/pdf")
    assert is_valid is False
    assert "unsupported" in err.lower()


def test_frame_preprocessing():
    large_bytes = _create_synthetic_image_bytes(1600, 1200)
    processed_bytes, meta = camera_service.preprocess_frame(large_bytes, max_dimension=1000)
    assert meta.width <= 1000
    assert meta.height <= 1000
    assert len(processed_bytes) > 0


def test_mode_and_intent_resolution():
    m1, _ = camera_service.resolve_mode_and_intent(requested_mode=CameraAnalysisMode.READ)
    assert m1 == CameraAnalysisMode.READ

    m2, _ = camera_service.resolve_mode_and_intent(target_object="water bottle")
    assert m2 == CameraAnalysisMode.FIND

    m3, _ = camera_service.resolve_mode_and_intent(intent="What is written here?")
    assert m3 == CameraAnalysisMode.READ

    m4, _ = camera_service.resolve_mode_and_intent(intent="Navigate to the exit")
    assert m4 == CameraAnalysisMode.NAVIGATE


def test_camera_session_lifecycle():
    sid = session_service.create_camera_session(twin_id="user_test", initial_mode="FIND", target_object="door")
    assert sid.startswith("cam_")

    sess = session_service.get_camera_session(sid)
    assert sess is not None
    assert sess["target_object"] == "door"
    assert sess["total_frames_processed"] == 0

    session_service.update_camera_session(
        session_id=sid,
        frame_id="frame_001",
        objects=[{"label": "door", "clock_hour": 11}],
        texts=[{"text": "EXIT"}],
        fused_relations=[{"combined": "EXIT door"}],
        hazards=[],
    )
    updated = session_service.get_camera_session(sid)
    assert updated["total_frames_processed"] == 1
    assert len(updated["analysis_history"]) == 1


def test_camera_analysis_multimodal_synthesis():
    img_bytes = _create_synthetic_image_bytes()
    resp = camera_service.analyze_frame(
        image_bytes=img_bytes,
        requested_mode=CameraAnalysisMode.FIND,
        target_object="water bottle",
        twin_id="default_user",
    )
    assert resp.success is True
    assert resp.session_id is not None
    assert resp.assistance.spoken_response is not None
    assert resp.assistance.haptic_cue is not None
    assert resp.analysis.target_found is True


if __name__ == "__main__":
    # AI tests
    test_preprocessor_load_pil()
    test_preprocessor_load_bytes()
    test_preprocessor_to_cv2()
    test_preprocessor_resize()
    test_preprocessor_crop_region()
    test_frame_quality_sharp()
    test_frame_quality_blurry()
    test_frame_quality_dark()
    test_frame_duplicate_detection()
    test_frame_alignment_check()
    test_camera_session_duplicate_tracking()
    test_camera_session_reset()
    test_camera_session_manager()
    test_camera_analyzer_explicit_document()
    test_camera_analyzer_explicit_navigation()
    test_camera_analyzer_query_document()
    test_camera_analyzer_query_see()
    test_camera_engine_see_mode()
    test_camera_engine_navigation_mode()
    test_camera_engine_isl_mode()
    test_camera_engine_scene_mode()
    # Backend tests
    test_frame_validation_valid()
    test_frame_validation_empty_and_corrupt()
    test_frame_validation_unsupported_mime()
    test_frame_preprocessing()
    test_mode_and_intent_resolution()
    test_camera_session_lifecycle()
    test_camera_analysis_multimodal_synthesis()
    print("All unit/test_camera.py tests passed successfully!")
