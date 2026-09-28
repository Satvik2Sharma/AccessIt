# Adapt-X (formerly Sahayak AI) — Complete REST API Specification

**Product**: Adapt-X — Intent-Aware Personal Accessibility Copilot  
**Base URL**: `/api/v1`  
**Data Exchange**: Normalized JSON & Multipart Image Streams  
**Architecture**: FastAPI 7-Stage Intent-Aware Accessibility Orchestrator

---

## Complete API Endpoint Directory (30 Endpoints)

| Category | Method | Path | Status | Purpose |
| :--- | :--- | :--- | :--- | :--- |
| **Auth** | `POST` | `/auth/login` | `IMPLEMENTED` | Authenticate user via password, PIN, or voice token |
| **Auth** | `POST` | `/auth/register` | `IMPLEMENTED` | Register user & initialize custom Accessibility Twin |
| **Auth** | `POST` | `/auth/guest` | `IMPLEMENTED` | 1-Click Judge Guest login with preset personas |
| **Auth** | `GET` | `/auth/me` | `IMPLEMENTED` | Retrieve active authenticated session & profile |
| **Auth** | `POST` | `/auth/logout` | `IMPLEMENTED` | Terminate session & clear tokens |
| **Auth** | `GET` | `/auth/personas` | `IMPLEMENTED` | List preset accessibility personas for judges |
| **System** | `GET` | `/health` | `IMPLEMENTED` | Orchestrator health & engine readiness |
| **Profile** | `GET` | `/accessibility/profile` | `IMPLEMENTED` | Fetch user's Accessibility Twin |
| **Profile** | `POST` | `/accessibility/profile` | `IMPLEMENTED` | Update Accessibility Twin preferences |
| **Intent** | `POST` | `/intent` | `IMPLEMENTED` | Multilingual intent classification |
| **Camera** | `POST` | `/camera/analyze` | `IMPLEMENTED` | Intent-aware camera frame intelligence & fusion |
| **Camera** | `POST` | `/camera/session` | `IMPLEMENTED` | Initialize continuous camera session |
| **Camera** | `GET` | `/camera/session` | `IMPLEMENTED` | Retrieve active camera session state & history |
| **Camera** | `POST` | `/camera/session/reset` | `IMPLEMENTED` | Reset frame history & duplicate suppression |
| **Form** | `POST` | `/complete/analyze` | `IMPLEMENTED` | Real OCR form scan & flow compilation |
| **Form** | `POST` | `/complete/respond` | `IMPLEMENTED` | Submit field response with validation |
| **Document** | `POST` | `/read` | `IMPLEMENTED` | OCR document notice extraction |
| **Document** | `POST` | `/read/qa` | `IMPLEMENTED` | Multi-turn Document Q&A |
| **Document** | `POST` | `/read/tasks` | `IMPLEMENTED` | Convert document info into actionable tasks |
| **ISL** | `POST` | `/isl/predict` | `IMPLEMENTED` | ISL gesture classification & spoken output |
| **Vision** | `POST` | `/see` | `IMPLEMENTED` | Object finder & directional guidance |
| **Vision** | `POST` | `/see/spatial` | `IMPLEMENTED` | 12-hour clock spatial guidance & proximity |
| **Scene** | `POST` | `/scene/analyze` | `IMPLEMENTED` | Comprehensive scene understanding |
| **Scene** | `POST` | `/scene/fusion` | `IMPLEMENTED` | Fuses detected objects with OCR signage |
| **Voice** | `POST` | `/voice/command` | `IMPLEMENTED` | Voice command parsing & multimodal response |
| **Voice** | `POST` | `/voice/tts` | `INTERFACE/CONTRACT ONLY` | TTS audio SSML contract |
| **Assistance**| `POST` | `/assistance/multimodal` | `IMPLEMENTED` | Unified voice + visual + haptic guidance |
| **Navigation**| `POST` | `/navigation/guide` | `IMPLEMENTED` | Step-by-step navigation & obstacle alert |
| **Navigation**| `GET` | `/navigation/session` | `IMPLEMENTED` | Navigation session state & obstacle history |
| **Verification**| `POST` | `/task/verify` | `IMPLEMENTED` | Task verification status & certificate token |
| **Verification**| `POST` | `/verification/check` | `IMPLEMENTED` | Detailed multi-field schema verification |
| **Learning** | `GET` | `/learning/heatmap` | `IMPLEMENTED` | Interaction friction heatmap & telemetry |
| **Learning** | `GET` | `/learning/personalization` | `IMPLEMENTED` | Fetch personalization settings |
| **Learning** | `POST` | `/learning/personalization` | `IMPLEMENTED` | Update personalization settings |

---

## Key Authentication & Judge Endpoints

### 1. Judge 1-Click Guest Login (`POST /api/v1/auth/guest`)
* **Request**:
```json
{
  "persona": "low_vision",
  "preferred_language": "English",
  "custom_name": "Lead Hackathon Judge"
}
```
* **Response (200 OK)**:
```json
{
  "success": true,
  "token": "adaptx_token_9f83a0bc819241d7",
  "token_type": "Bearer",
  "user": {
    "user_id": "usr_guest_38f2910a",
    "username": "judge_low_vision",
    "full_name": "Lead Hackathon Judge",
    "twin_id": "twin_usr_guest_38f2910a",
    "is_guest": true,
    "active_persona": "low_vision"
  },
  "twin": {
    "id": "twin_usr_guest_38f2910a",
    "language": "English",
    "visual": {
      "large_text": true,
      "high_contrast": true,
      "magnification_level": 1.75
    },
    "haptics": {
      "enabled": true,
      "intensity": "strong"
    },
    "preferred_input": "voice",
    "preferred_output": "voice_and_text"
  },
  "message": "Welcome! Logged in as Lead Hackathon Judge with 'low_vision' accessibility persona."
}
```

### 2. Standard Login (`POST /api/v1/auth/login`)
* **Request**:
```json
{
  "username": "judge",
  "password": "demo",
  "auth_modality": "password"
}
```
