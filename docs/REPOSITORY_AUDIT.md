# Sahayak AI — Repository Audit & Open-Source Foundation Analysis

**Lead Software Architect & AI Integration Report**  
**Project**: Sahayak AI — Intent-Aware Personal Accessibility Copilot  
**Date**: September 2026  
**Status**: Completed Analysis & Selective Architectural Integration

---

## 1. Executive Summary

Sahayak AI is built around a unified **7-Stage Intent-Aware Accessibility Pipeline**:
```
UNDERSTAND USER (Accessibility Twin) 
  → UNDERSTAND TASK 
  → DETECT BARRIERS 
  → COMPILE ACCESSIBLE TASK FLOW 
  → ASSIST 
  → VERIFY 
  → LEARN
```

Traditional accessibility tools expose fragmented, standalone features (OCR button, TTS toggle, YOLO viewer, ISL detector). Sahayak AI rejects this fragmentation. Instead of blindly pasting disparate open-source repositories into subfolders, this audit evaluates four candidate open-source repositories to extract battle-tested algorithms, UI interactions, and inference patterns while establishing a unified, cohesive, high-performance monorepo.

---

## 2. Comprehensive Repository Audit

### Repository 1: Full-Stack AI VisualAid (Flutter + Python)
* **Upstream URL**: `https://github.com/Eng-M-Abdrabbou/Full-Stack_AI-VisualAid_Flutter_Python`
* **Author / Copyright**: Mahmoud Abdrabbou (2023)
* **License**: **MIT License** (Fully permissive, commercial & non-commercial reuse with attribution)
* **Tech Stack**:
  * **Frontend**: Flutter (Dart), Camera plugin, Speech-to-Text (`speech_to_text: ^7.0.0`), WebSocket client, TTS audio player.
  * **Backend**: Python (Flask + Flask-SocketIO + Flask-SQLAlchemy), PyTorch, TorchVision (Places365 ResNet-50 scene classifier: 97.2 MB weight file), YOLOv5n / YOLOv8n (Ultralytics), EasyOCR / Tesseract OCR.
* **Architecture Review**:
  * Employs real-time streaming over WebSockets and HTTP for object and text detection.
  * Backend tightly couples Flask endpoints with local MySQL database initialization (`mysql+pymysql://root:@127.0.0.1:3306/visualaiddb`) which fails immediately if MySQL is not running.
  * Includes local weights inside repository (`resnet50_places365.pth.tar` @ 97.2MB, `yolov5n.pt` @ 4.0MB, `yolov8n.pt` @ 6.5MB).
* **Reusable Modules**:
  * Flutter camera frame capture patterns & UI action buttons (`camera_view_widget.dart`, `action_button.dart`).
  * Text detection & OCR coordinate mapping logic.
  * Places365 scene categories dictionary (`categories_places365.txt`).
* **Liabilities & Deprecations**:
  * Hardcoded MySQL database dependency; backend crashes on startup without local DB.
  * Heavy monolithic Flask script (`App.py` ~600 lines) with unhandled exceptions.
  * SocketIO frame delivery lacks backpressure handling on constrained network links.
* **Verdict**: **Selectively Integrated Adapter**. Reused camera capture interface paradigms and scene classification concept; discarded MySQL and monolithic Flask server in favor of FastAPI async pipeline.

---

### Repository 2: ISL-Interpreter (Indian Sign Language)
* **Upstream URL**: `https://github.com/Dev-2604/ISL-Interpreter`
* **Author / Copyright**: Dev Patel (2024)
* **License**: **MIT License** (Fully permissive with attribution)
* **Tech Stack**:
  * **Frontend**: Flutter (Dart), `camera: ^0.10.5+5`, `flutter_tts`, HTTP client.
  * **Backend**: Python (Flask + Flask-CORS), TensorFlow / Keras, OpenCV, MediaPipe Hands.
* **Architecture Review**:
  * Extracts 21 3D hand landmarks per hand (up to 2 hands = 42 landmarks / 126 coordinate values) via Google MediaPipe.
  * Static gesture classification: MobileViT / CNN on normalized landmark coordinates (A–Z, 1–9).
  * Dynamic gesture classification: LSTM sequence model over 30-frame sequence (84 coordinates/frame) for gestures: *"Doctor"*, *"Help"*, *"Hot"*, *"Lose"*, *"Pain"*, *"Thief"*.
* **Reusable Modules**:
  * MediaPipe landmark extraction pipeline (`static_features` with gamma correction lookup table and `video_features` sequence generator).
  * Static sign label mapping (digits 1–9, letters A–Z) and dynamic sign dictionary (`['Doctor', 'Help', 'Hot', 'Lose', 'Pain', 'Thief']`).
  * Real-time camera streaming with red recording indicator from Flutter.
* **Liabilities & Deprecations**:
  * Upstream repository does *not* bundle the trained `.h5` model files (`CNN_landmarks_mode_71.h5` and `dynamic_sign_language_model.h5` must be supplied or downloaded; fallback needed for offline development).
  * MediaPipe `mp.solutions.hands` has breaking API changes in newer `mediapipe >= 0.10.14` (transition to MediaPipe Tasks API).
* **Verdict**: **Selectively Integrated Adapter**. Extracted landmark extraction and sign classification adapter into `ai/isl/`. Created resilient fallback/heuristic landmark analyzer for hackathon demo stability when heavy weights are unavailable.

---

### Repository 3: SightBuddy (Android Accessibility App)
* **Upstream URL**: `https://github.com/DrophouseLtd/SightBuddy`
* **Author / Copyright**: Drophouse Ltd (2024)
* **License**: **MIT License** (Includes Apache-2.0 notices for TensorFlow/EfficientDet models)
* **Tech Stack**:
  * **Platform**: Native Android (Kotlin + Jetpack Compose), CameraX, Android Haptics API (`Vibrator` / `VibratorManager`), Android TTS, Firebase/Google Services.
* **Architecture Review**:
  * Pure native Kotlin Android application — **NOT Flutter**.
  * Highly polished accessibility UX: high-contrast tactile action buttons, sound effects on state changes (`sfx_listening.mp3`, `sfx_camera_click.mp3`, `sfx_stop_listening.mp3`), granular haptic feedback patterns (success, error, direction pulses).
  * Object picker & COCO target finding routines.
* **Reusable Modules**:
  * Haptic feedback design patterns: tick feedback for scanning, double pulse on object acquisition, warning buzz on obstacle.
  * Audio UX feedback assets (earcons / sound cues) and accessible contrast color tokens.
  * Directional object guidance heuristics ("Object slightly to your right", "Move camera forward").
* **Liabilities & Deprecations**:
  * Cannot be directly compiled inside a Flutter project without writing a custom native Android platform channel or porting to Dart.
* **Verdict**: **UX & Architectural Reference**. Ported the haptic cues, audio feedback scheme, and directional finding heuristics into Flutter Material 3 widgets and Dart services.

---

### Repository 4: SightAssist (Vision-Language Scene Assistance)
* **Upstream URL**: `https://github.com/ArgonArnav/SightAssist`
* **Author / Copyright**: Arnav Argon (2023)
* **License**: **MIT License** (Fully permissive with attribution)
* **Tech Stack**:
  * **Backend**: Python (Flask + Gunicorn), Ultralytics (YOLO11n / YOLOv5), EasyOCR / PyTesseract, HuggingFace Transformers (BLIP Image Captioning), Coqui TTS / gTTS.
* **Architecture Review**:
  * Outstanding modular design with clean single-responsibility files:
    * `object_detection.py` (YOLO inference with bounding boxes and labels)
    * `ocr_reader.py` (EasyOCR bounding box + text extraction)
    * `scene_fusion.py` (Geometric fusion algorithm associating detected text within object bounding boxes)
    * `caption_generator.py` (BLIP vision-to-text narrative generation)
    * `speech_synthesizer.py` (TTS audio file generator)
* **Reusable Modules**:
  * `SceneFusion` class: Geometric bounding-box spatial containment algorithm matching text to objects.
  * Clean object detection & OCR wrapper interfaces.
* **Liabilities & Deprecations**:
  * BLIP image captioning (`Salesforce/blip-image-captioning-base`) requires ~1 GB RAM download and GPU for sub-second inference.
  * Hardcoded file-based audio generation writes MP3 files to disk on every request without cache cleanup.
* **Verdict**: **Directly Integrated & Refactored**. Modernized `SceneFusion`, `ObjectDetector`, and `OCRReader` into asynchronous FastAPI services under `ai/vision/`, `ai/ocr/`, and `ai/scene/`.

---

## 3. License Compatibility Matrix

All four evaluated upstream repositories are licensed under the **MIT License**, with third-party model weights utilizing **Apache-2.0** (MediaPipe, TensorFlow, EfficientDet) or **GPL/AGPL/Proprietary** (Ultralytics YOLO requires commercial license or AGPL-3.0 compliance).

| Repository | Declared License | Compatibility with Sahayak AI | Usage in Sahayak AI | Attribution Required? |
|---|---|---|---|---|
| **VisualAid** | MIT | Compatible | Camera flow, scene categorizer | Yes (Added to `THIRD_PARTY_LICENSES.md`) |
| **ISL-Interpreter** | MIT | Compatible | MediaPipe hand landmark extraction | Yes (Added to `THIRD_PARTY_LICENSES.md`) |
| **SightBuddy** | MIT | Compatible | Haptic design patterns, accessibility UI | Yes (Added to `THIRD_PARTY_LICENSES.md`) |
| **SightAssist** | MIT | Compatible | Scene fusion, OCR bounding box fusion | Yes (Added to `THIRD_PARTY_LICENSES.md`) |

---

## 4. Reusable Modules Discovered & Integrated

| Module | Origin | Target Location in Sahayak AI | Architectural Benefit |
|---|---|---|---|
| **Scene Fusion Engine** | SightAssist | `ai/scene/scene_fusion.py` | Associates OCR text with detected physical objects (e.g., medicine bottle + label text). |
| **Hand Landmark Extractor** | ISL-Interpreter | `ai/isl/hand_tracker.py` | Extracts normalized 21-point 3D hand coordinates for sign language detection. |
| **ISL Sign Classifier** | ISL-Interpreter | `ai/isl/sign_classifier.py` | Maps hand landmarks to Indian Sign Language alphabet and dynamic emergency words. |
| **Document OCR Engine** | SightAssist / VisualAid | `ai/ocr/ocr_engine.py` | High-confidence bounding box text extraction and layout understanding. |
| **Haptic Accessibility Service** | SightBuddy (concept) | `mobile/lib/core/services/haptics_service.dart` | Directional vibrations and tactile task progress confirmation. |
| **Directional Guidance Engine** | SightBuddy / SightAssist | `ai/vision/directional_finder.py` | Converts object bounding boxes into camera-relative spatial guidance ("to your right"). |

---

## 5. Dependency Conflicts & Resolution Strategy

1. **Flask vs. FastAPI**:
   * *Conflict*: VisualAid, ISL-Interpreter, and SightAssist all use synchronous Flask servers with blocking I/O and disparate port bindings (`5000`, `8000`, `5001`).
   * *Resolution*: Standardized on **FastAPI with async Pydantic endpoints** under a single unified orchestrator. All sub-engines are asynchronous services.
2. **TensorFlow vs. PyTorch**:
   * *Conflict*: ISL-Interpreter relies on TensorFlow/Keras (`tf.keras`), whereas SightAssist and VisualAid rely on PyTorch and Ultralytics. Running both in the same runtime creates massive memory footprints (>2.5 GB RAM) and potential CUDA library collisions.
   * *Resolution*: Decoupled heavy neural networks behind light runtime interfaces with fallback rule-based / MediaPipe standalone inference. Hand landmarks use pure NumPy / MediaPipe without requiring full TensorFlow if weights are absent.
3. **Flutter Plugin Compatibility**:
   * *Conflict*: VisualAid pubspec targeted legacy Flutter 3.1, while ISL-Interpreter targeted Flutter 3.7 with older camera plugins.
   * *Resolution*: Modernized to modern Flutter 3.24+ with Dart 3 null-safety, Material 3 theming, Riverpod state management, and modern camera/TTS plugins.

---

## 6. Monorepo Integration Verdict

| Repository | Decision | Rationale |
|---|---|---|
| **Full-Stack AI VisualAid** | **Selectively Integrated** | Reused camera interaction patterns and scene detection concepts; removed Flask/MySQL. |
| **ISL-Interpreter** | **Selectively Integrated** | Integrated MediaPipe landmark processing and ISL gesture vocabulary into `ai/isl/`. |
| **SightBuddy** | **Reference & Ported** | Ported Kotlin haptics and accessibility cues into Flutter Dart services. |
| **SightAssist** | **Integrated & Refactored** | Modernized SceneFusion and OCR pipelines into asynchronous FastAPI architecture. |

**Final Architecture**: ONE cohesive system with clean domain boundaries, zero code duplication, and strict adherence to the 7-stage Sahayak pipeline.
