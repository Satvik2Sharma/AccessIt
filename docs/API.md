# Sahayak AI — Complete REST API Specification

**Base URL**: `/api/v1`  
**Data Exchange**: Normalized JSON & Multipart Image Streams  
**Architecture**: FastAPI 7-Stage Intent-Aware Accessibility Orchestrator

---

## Complete API Endpoint Directory (22 Endpoints)

| Category | Method | Path | Status | Purpose |
| :--- | :--- | :--- | :--- | :--- |
| **System** | `GET` | `/health` | `IMPLEMENTED` | Orchestrator health & engine readiness |
| **Profile** | `GET` | `/accessibility/profile` | `IMPLEMENTED` | Fetch user's Accessibility Twin |
| **Profile** | `POST` | `/accessibility/profile` | `IMPLEMENTED` | Update Accessibility Twin preferences |
| **Intent** | `POST` | `/intent` | `IMPLEMENTED` | Multilingual intent classification |
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

## Detailed Endpoints & Payloads

### 1. Document Q&A (`POST /api/v1/read/qa`)
* **Request**:
```json
{
  "document_id": "doc_842a19c0",
  "question": "What is the application deadline?",
  "twin_id": "default_user",
  "language": "English"
}
```
* **Response (200 OK)**:
```json
{
  "document_id": "doc_842a19c0",
  "question": "What is the application deadline?",
  "answer": "The application deadline is September 30, 2026.",
  "spoken_answer": "The application deadline is September 30, 2026.",
  "supporting_extracted_info": ["September 30, 2026"],
  "confidence": 0.94,
  "source_section": "Key Deadlines",
  "related_actions": ["Set Reminder for Deadline", "Prepare Aadhaar & Income Certificate"],
  "language": "English",
  "haptic_cue": "TOUCH_CONFIRM"
}
```

### 2. Spatial Vision (`POST /api/v1/see/spatial`)
* **Request**:
```json
{
  "target_object": "water bottle",
  "twin_id": "default_user",
  "current_heading_degrees": 0.0
}
```
* **Response (200 OK)**:
```json
{
  "label": "water bottle",
  "relative_direction": "to your right",
  "clock_hour": 4,
  "clock_direction": "at 4 o'clock",
  "elevation": "table/waist level",
  "relative_proximity": "within arm's reach",
  "spoken_guidance": "Your water bottle is at 4 o'clock, table/waist level, within arm's reach.",
  "display_guidance": "Water bottle: at 4 o'clock | table/waist level (within arm's reach)",
  "haptic_cue": "PULSE_RIGHT",
  "haptic_intensity": "MEDIUM",
  "normalized_coordinates": {"x": 0.7, "y": 0.56},
  "area_ratio": 0.137,
  "found": true
}
```

### 3. Voice Assistant Command (`POST /api/v1/voice/command`)
* **Request**:
```json
{
  "transcript": "scholarship form bharna hai",
  "twin_id": "default_user",
  "active_session_id": null
}
```
* **Response (200 OK)**:
```json
{
  "transcript": "scholarship form bharna hai",
  "detected_language": "hi",
  "classified_intent": "FORM_COMPLETION",
  "intent_confidence": 0.95,
  "suggested_action": "START_FORM_COMPLETION",
  "spoken_reply": "मैंने फ़ॉर्म भरने का इरादा पहचाना है। आइए चरण दर चरण फ़ॉर्म पूरा करते हैं।",
  "display_reply": "मैंने फ़ॉर्म भरने का इरादा पहचाना है। आइए चरण दर चरण फ़ॉर्म पूरा करते हैं।",
  "session_id": "voice_3a9f01bc",
  "parameters": {"rationale": "High confidence pattern match for form filling in Hindi"},
  "haptic_cue": "TOUCH_CONFIRM"
}
```

### 4. Smart Navigation (`POST /api/v1/navigation/guide`)
* **Request**:
```json
{
  "session_id": null,
  "target_destination": "exit",
  "detected_labels": ["door", "clear path"],
  "twin_id": "default_user"
}
```
* **Response (200 OK)**:
```json
{
  "session_id": "nav_40bc1829",
  "direction": "Slightly to your left",
  "clock_direction": "11 o'clock",
  "instruction": "Exit door is 5 steps ahead at 11 o'clock. Clear path ahead.",
  "spoken_guidance": "The exit door is ahead at 11 o'clock, about 5 steps away. Path is clear.",
  "urgency": "NORMAL",
  "obstacles_in_path": [],
  "haptic_cue": "DOUBLE_PULSE_CENTER",
  "is_destination_reached": false
}
```
