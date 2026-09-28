# Sahayak AI — Team Workflow & Ownership Boundaries

**Project**: Sahayak AI  
**Architecture**: Monorepo with Clean Functional Ownership Boundaries  
**Target Environment**: Linux Ubuntu / Android Mobile / FastAPI Python 3.12 / Flutter 3.24

---

## 1. Team Ownership & Responsibilities

| Area | Owner | Responsibility | Modification Policy |
| :--- | :--- | :--- | :--- |
| `backend/` | Backend Lead | FastAPI orchestrator, modular routes, session management, response normalization, error recovery. | Modify freely within ownership scope |
| `shared/` | Core Team | Shared Pydantic schemas, domain models, evaluation assets, sample forms and notices. | Modify freely within ownership scope |
| `tests/` | QA & Backend | Comprehensive unit and integration test suites, end-to-end regression validation. | Modify freely within ownership scope |
| `docs/` | Core Team | Architectural specs, API references, team contracts, demo workflows. | Modify freely within ownership scope |
| `scripts/` | Devops & Core | Portable launchers, run scripts, automated demo test runners. | Modify freely within ownership scope |
| `ai/` | AI Teammates | Core domain algorithms: MediaPipe gesture recognizers, RapidOCR, Scene Fusion, Intent Classifier. | **STRICTLY PROTECTED** (Do not edit directly; integrate via clean contracts) |
| `mobile/` | Mobile Teammates | Flutter Android application, audio player, haptic motor control, accessible screens. | **STRICTLY PROTECTED** (Do not edit directly; integrate via clean contracts) |
| `frontend/` | Web Teammates | React / TypeScript web interface and Lovable configurations. | **STRICTLY PROTECTED** (Do not edit directly; integrate via clean contracts) |

---

## 2. Team Integration Contracts

### AI Team $\leftrightarrow$ Backend Contract
* AI engines produce raw inference dictionaries or domain objects (`DirectionalFinder.compute_spatial_guidance`, `SceneFusion.fuse`, `DocumentOCREngine.extract_document_info`, `ISLInterpreterService.predict_sign`).
* Backend wraps AI engine invocations inside `backend/services/pipeline_service.py` with automatic error recovery and graceful fallback handling.

### Backend $\leftrightarrow$ Mobile / Frontend Contract
* Mobile and Frontend clients communicate with the 22 normalized REST endpoints under `/api/v1`.
* Every response envelope is normalized via `backend/services/response_service.py` into a consistent structure containing:
  1. `text_content` & `display_summary`
  2. `spoken_content` (localized speech string)
  3. `haptic_cue` / `haptic_pattern`
  4. `visual_card` / bounding box highlights
  5. `priority`
  6. `recovery_info` (if fallback mode engaged)

---

## 3. Development Principles

1. **Depth Over Feature Count**:
   * We do NOT build disconnected demo tools.
   * We build ONE unified 7-stage pipeline that works reliably from voice/image input through barrier compilation to verified completion.
2. **Never Diagnose**:
   * The code and comments must never refer to humans as "disabled", "blind", or "deaf" internally.
   * Use functional interaction terms: `prefers_voice`, `needs_large_text`, `requires_high_contrast`, `prefers_simplified_language`.
3. **Graceful Fallbacks & Zero Crash**:
   * All heavy ML models (YOLO, MediaPipe, BLIP) must have deterministic heuristic fallbacks so that demos NEVER crash during a live judge presentation.
4. **Clean Git Hygiene**:
   * Work strictly within your owned directories.
   * Never overwrite, reset, or force push over teammate contributions.
