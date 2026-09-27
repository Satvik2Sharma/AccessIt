# Sahayak AI — Team Workflow & Engineering Guidelines

**Project**: Sahayak AI  
**Role**: Lead Software Architect, Senior Full-Stack Engineer, AI Engineer  
**Target Environment**: Linux Ubuntu / Android Mobile / FastAPI Python 3.12

---

## 1. Development Principles

1. **Depth Over Feature Count**:
   * We do NOT build 20 disconnected demo tools.
   * We build ONE unified 7-stage pipeline that works reliably from voice/image input through barrier compilation to verified completion.
2. **Never Diagnose**:
   * The code and comments must never refer to humans as "disabled", "blind", or "deaf" internally.
   * Use functional interaction terms: `prefers_voice`, `needs_large_text`, `requires_high_contrast`, `prefers_simplified_language`.
3. **Graceful Fallbacks**:
   * All heavy ML models (YOLO, MediaPipe, BLIP) must have fast, deterministic heuristic fallbacks so that demos NEVER crash during a live judge presentation even if GPU memory is tight or weights are downloading.

---

## 2. Directory Layout & Responsibilities

| Directory | Primary Language | Responsibility |
|---|---|---|
| `mobile/` | Dart (Flutter) | Android application with Material 3, Riverpod state management, voice prompts, high contrast UI. |
| `backend/` | Python (FastAPI) | Asynchronous HTTP/WebSocket router, orchestrator pipeline, normalized REST endpoints. |
| `ai/` | Python | Domain engines: Intent, Barrier, Compiler, Assistance, Verification, Learning, Vision, OCR, ISL. |
| `shared/` | Python & Dart / JSON | Shared schemas, sample forms/notices, demo data dictionaries. |
| `docs/` | Markdown | Comprehensive architecture, audit, and demo guidelines. |
| `scripts/` | Bash | Run scripts for local backend and mobile builds. |

---

## 3. Branching & Commit Conventions

* `main`: Protected, production-ready, fully verified demo branch.
* Commit prefix convention:
  * `feat(twin): ...` - Accessibility Twin changes
  * `feat(barrier): ...` - Barrier analysis rules
  * `feat(compiler): ...` - Task flow compilation
  * `feat(verify): ...` - Verification state machine
  * `feat(isl): ...` - Indian Sign Language tracking
  * `feat(mobile): ...` - Flutter UI & audio/haptic cues
  * `docs: ...` - Documentation updates
