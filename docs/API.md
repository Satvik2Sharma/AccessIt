# Sahayak AI — REST & WebSocket API Specification

**API Engine**: FastAPI Asynchronous Core  
**Base URL**: `/api/v1`  
**Data Exchange**: Normalized JSON & Multipart Image Streams

---

## 1. System Endpoints

### `GET /api/v1/health`
Health check endpoint reporting orchestrator status and loaded model states.
* **Response (200 OK)**:
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "system": "Sahayak AI Orchestrator",
  "engines": {
    "intent": true,
    "barrier": true,
    "compiler": true,
    "verification": true,
    "learning": true,
    "vision": "ready (heuristic/YOLO)",
    "ocr": "ready (EasyOCR/Tesseract)",
    "isl": "ready (MediaPipe)"
  }
}
```

---

## 2. Intent & Pipeline Endpoints

### `POST /api/v1/intent`
Classifies raw user query into task intent and identifies initial parameters.
* **Request**:
```json
{
  "query": "Help me fill this scholarship form",
  "twin": {
    "language": "Hindi",
    "visual": { "large_text": true }
  }
}
```
* **Response (200 OK)**:
```json
{
  "intent": "FORM_COMPLETION",
  "confidence": 0.95,
  "suggested_pipeline_stage": "DETECT_BARRIERS",
  "task_summary": "Guide user step-by-step through form completion"
}
```

---

## 3. Core Task Workflows

### `POST /api/v1/complete/analyze`
Extracts fields from a form image, performs barrier analysis, and compiles the first step of an `AccessibleTaskFlow`.
* **Request**: Multipart Form Data
  * `image`: Binary file (form image / camera frame)
  * `twin_json`: JSON string of `AccessibilityTwin`
* **Response (200 OK)**:
```json
{
  "task_id": "task_form_84712",
  "task_type": "FORM_COMPLETION",
  "total_fields": 7,
  "barriers_detected": [
    {
      "category": "VISUAL",
      "severity": "HIGH",
      "description": "Dense multi-column layout with 9pt font size"
    },
    {
      "category": "MOTOR",
      "severity": "MEDIUM",
      "description": "Requires manual handwriting or precise capacitive typing"
    }
  ],
  "accessible_flow": {
    "strategy": "ONE_STEP_AT_A_TIME_VOICE",
    "total_steps": 7,
    "current_step_index": 0,
    "current_step": {
      "field_id": "full_name",
      "label": "Full Name",
      "spoken_prompt": "आपकी फ़ॉर्म में 7 ज़रूरी जानकारियां हैं। पहला सवाल: आपका पूरा नाम क्या है?",
      "display_prompt": "चरण 1/7: अपना पूरा नाम बताएं",
      "input_type": "VOICE_OR_TEXT",
      "is_required": true
    }
  }
}
```

### `POST /api/v1/complete/respond`
Submits an answer to the current step, validates input, updates verification state, and returns the next step.
* **Request**:
```json
{
  "task_id": "task_form_84712",
  "field_id": "full_name",
  "value": "Satvik Sharma",
  "confirmation_received": true
}
```
* **Response (200 OK)**:
```json
{
  "task_id": "task_form_84712",
  "field_completed": "full_name",
  "fields_remaining": 6,
  "verification_status": "IN_PROGRESS",
  "completion_percentage": 14.3,
  "next_step": {
    "field_id": "dob",
    "label": "Date of Birth",
    "spoken_prompt": "धन्यवाद सात्विक। आपकी जन्मतिथि क्या है?",
    "display_prompt": "चरण 2/7: जन्मतिथि बताएं (दिन, महीना, साल)",
    "input_type": "VOICE_OR_TEXT"
  }
}
```

---

## 4. Document & Scene Understanding

### `POST /api/v1/read`
Analyzes a document image, detects deadlines, certificates required, and produces a simplified summary.
* **Request**: Multipart Form Data (`image`, `query`, `twin_json`)
* **Response (200 OK)**:
```json
{
  "document_title": "National Merit Scholarship Notice 2026",
  "key_deadlines": ["September 30, 2026"],
  "required_documents": ["Income Certificate", "Aadhaar Card", "Class 10 Marksheet"],
  "simplified_summary": "यह छात्रवृत्ति सूचना है। अंतिम तिथि 30 सितंबर है। आपको आय प्रमाण पत्र और आधार कार्ड की आवश्यकता होगी।",
  "audio_summary_url": "/api/v1/speech/synthesize?id=notice_sum_01"
}
```

### `POST /api/v1/see`
Performs object detection, scene fusion, and directional spatial guidance.
* **Request**: Multipart Form Data (`image`, `target_object` [optional])
* **Response (200 OK)**:
```json
{
  "scene_summary": "A table with a water bottle on the right and paperwork in the center.",
  "objects": [
    {
      "label": "bottle",
      "confidence": 0.92,
      "relative_position": "slightly to your right",
      "distance_estimate": "near",
      "bbox": [280, 150, 420, 600]
    }
  ],
  "haptic_cue": "PULSE_RIGHT"
}
```

---

## 5. Indian Sign Language (ISL) Recognition

### `POST /api/v1/isl/predict`
Takes an image frame or landmark tensor, extracts hand coordinates via MediaPipe, and classifies static/dynamic sign.
* **Request**: Multipart image or JSON landmark sequence
* **Response (200 OK)**:
```json
{
  "sign_detected": "HELP",
  "confidence": 0.94,
  "sign_type": "DYNAMIC_EMERGENCY",
  "spoken_output": "Help",
  "haptic_feedback": "SUCCESS_DOUBLE_PULSE"
}
```

---

## 6. Verification & Learning

### `POST /api/v1/task/verify`
Evaluates complete state of an active task and returns an official verification status.
* **Response (200 OK)**:
```json
{
  "task_id": "task_form_84712",
  "status": "COMPLETED",
  "completion_rate": 1.0,
  "missing_fields": [],
  "verification_token": "VERIFIED_SAHAYAK_9824",
  "message": "All required fields completed and validated."
}
```

### `GET /api/v1/learning/heatmap`
Returns local interaction complexity heatmap aggregated across user steps.
* **Response (200 OK)**:
```json
{
  "total_tasks_completed": 5,
  "preferred_modality": "voice",
  "complexity_heatmap": [
    { "interaction": "document_upload", "complexity": "HIGH", "color": "RED", "avg_retries": 2.4 },
    { "interaction": "address_input", "complexity": "MEDIUM", "color": "YELLOW", "avg_retries": 1.1 },
    { "interaction": "name_input", "complexity": "LOW", "color": "GREEN", "avg_retries": 0.0 }
  ],
  "adaptation_recommendation": "Default to voice input and single-field auto-advance."
}
```
