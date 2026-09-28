# Sahayak AI — Camera Intelligence & Frame Processing Architecture

## 1. Overview

The **Camera Intelligence** subsystem (`ai/camera/`) serves as the high-throughput, adaptive visual perception gateway for Sahayak AI. It interfaces directly with camera hardware streams (mobile front/back cameras, webcams, wearable visual devices) and selectively routes high-quality frames to downstream perception models without overloading client batteries or server inference pipelines.

```
Camera Frame Stream (Mobile / Web)
             │
             ▼
    ┌──────────────────┐
    │ ImagePreprocessor│  (Format conversion, rotation, perspective normalization)
    └────────┬─────────┘
             │
             ▼
    ┌──────────────────┐
    │  FrameProcessor  │  (Blur detection, luminance checks, perceptual dHash duplicate check)
    └────────┬─────────┘
             │
       Pass Quality?
      /             \
    No               Yes
    │                 │
    ▼                 ▼
[Recovery Action]  ┌──────────────────┐
(User guidance:    │  CameraAnalyzer  │  (Determine minimal capability: OCR vs Object vs ISL vs Nav)
 "Hold steady",    └────────┬─────────┘
 "Add light")               │
                            ▼
                   ┌──────────────────┐
                   │   CameraEngine   │  (Routes to OCR, Vision, ISL, Scene, Navigation)
                   └────────┬─────────┘
                            │
                            ▼
                  [CameraAnalysisResult]
          (Spoken feedback, display text, haptic cue)
```

---

## 2. Directory Structure

```text
ai/camera/
├── __init__.py               # Package exports
├── camera_engine.py          # Central multimodal camera intelligence coordinator
├── frame_processor.py        # Blur, brightness, alignment, and duplicate frame detection
├── image_preprocessor.py     # Resizing, color transforms, rotation, perspective warping
├── camera_analyzer.py        # Task/mode capability planner to minimize model execution
└── camera_session.py         # Ephemeral session tracking and duplicate frame suppression
```

---

## 3. Core Modules & Responsibilities

### `ImagePreprocessor` (`ai/camera/image_preprocessor.py`)
- **Universal Input Ingestion**: Supports raw bytes, base64 data URLs, PIL `Image.Image`, and OpenCV NumPy `ndarray`.
- **EXIF Rotation Normalization**: Corrects portrait/landscape orientations before feature extraction.
- **Aspect-Preserving Downscaling**: Restricts max dimension to 1280px for optimal speed without OCR degradation.
- **Document Perspective Correction**: Applies OpenCV contour detection and 4-point perspective warping on quadrilateral document boundaries.

### `FrameProcessor` (`ai/camera/frame_processor.py`)
- **Laplacian Variance Blur Metric**: Measures high-frequency gradient variance. Frames with variance $< 50.0$ are tagged as blurry.
- **Luminance Histogram Estimation**: Evaluates mean pixel intensity ($35 \le Y \le 225$). Flags underexposed (dark) and overexposed (glare) images.
- **Perceptual Difference Hashing (dHash)**: Computes horizontal gradient hashes. Stationary camera frames are identified and served from ephemeral session cache without redundant inference.
- **Content Alignment Verification**: Samples frame boundary variance to verify documents or objects are centered rather than cropped.

### `CameraSession` (`ai/camera/camera_session.py`)
- **Privacy First**: Raw visual frames are strictly held in volatile memory; images are never persisted to disk.
- **Sliding Hash Window**: Maintains a FIFO deque of recent perceptual hashes to prevent re-processing stationary scenes.
- **State Continuity**: Preserves task context (e.g., active document ID, target object query) across multi-turn interactions.

### `CameraAnalyzer` (`ai/camera/camera_analyzer.py`)
- Evaluates incoming request parameters (`mode`, natural language `query`, and `AccessibilityTwin`).
- Determines the exact set of required perception models:
  - `mode="document"`: Activates `DocumentOCREngine` and `DocumentQAEngine`.
  - `mode="see"`: Activates `ObjectDetectorAdapter` and `ClockDirectionMapper`.
  - `mode="navigation"`: Activates `ObstacleDetector` and `GuidanceEngine`.
  - `mode="isl"`: Activates `ISLInterpreterService`.
  - `mode="scene"`: Activates `SceneUnderstandingEngine` and `ObjectTextFusion`.

### `CameraEngine` (`ai/camera/camera_engine.py`)
- The unified entry point accepting images and delivering normalized `CameraAnalysisResult` responses.
- Generates localized spoken text (English / Hindi), display cards, and directional haptic cues based on the user's `AccessibilityTwin`.

---

## 4. API Endpoints

### `POST /api/v1/camera/analyze`
**Request Parameters (Multipart Form or JSON):**
- `image`: Binary file upload (JPEG/PNG)
- `mode`: `"auto" | "document" | "see" | "scene" | "isl" | "navigation" | "form"`
- `query`: Optional voice/text intent (e.g., `"Where is my medicine bottle?"`)
- `twin_id`: Identifier for user accessibility profile (default: `"default_user"`)
- `session_id`: Optional continuous session tracking identifier
- `skip_duplicate_check`: Boolean to bypass duplicate suppression

**Sample Response (`CameraAnalysisResult`):**
```json
{
  "mode_executed": "see",
  "status": "SUCCESS",
  "quality": {
    "is_valid": true,
    "blur_score": 142.8,
    "is_blurry": false,
    "brightness": 128.5,
    "is_underexposed": false,
    "is_overexposed": false,
    "resolution": [640, 480],
    "quality_verdict": "GOOD"
  },
  "primary_interpretation": "water bottle is at 2 o'clock, within arm's reach",
  "spoken_feedback": "water bottle is at 2 o'clock, within arm's reach",
  "display_feedback": "water bottle detected at 2 o'clock",
  "haptic_cue": "PULSE_RIGHT",
  "spatial_objects": [
    {
      "label": "water bottle",
      "clock_direction": "2 o'clock",
      "elevation": "table/waist level",
      "relative_proximity": "within arm's reach"
    }
  ],
  "processing_time_ms": 38.4
}
```

### `POST /api/v1/camera/session/reset`
Clears session history, duplicate hashes, and cached results.

---

## 5. Performance & Safety Measures

1. **Lightweight Pre-Flight Filtering**: Quality and duplicate checks run in under 4ms using optimized NumPy/OpenCV routines before any neural models are invoked.
2. **Graceful Quality Recovery**: If a frame is blurry or dark, bounded instructions (e.g. `"Please hold camera steady and move to better lighting"`) guide the user immediately without executing expensive models.
3. **Hardware Independence**: Operates seamlessly on mobile phone camera sensors, webcams, and synthetic test frames.
