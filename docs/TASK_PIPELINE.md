# Sahayak AI — The 7-Stage Intent-Aware Task Pipeline

**Pipeline Blueprint**: End-to-End Task Transformation & Execution  
**Author**: Lead Software Architect  
**Version**: 1.0.0

---

## 1. Pipeline Overview

Traditional accessibility tools execute isolated actions:
```
User -> Clicks "OCR" -> Gets unstructured text dump -> Struggles with next steps
```

Sahayak AI compiles intent into completed tasks:
```
User -> "Help me fill this form" -> Sahayak analyzes barriers -> Compiles accessible sequence -> Guides user field-by-field -> Validates inputs -> Confirms completion
```

---

## 2. Stage-by-Stage Specification

### Stage 1: UNDERSTAND USER (Accessibility Twin)
* **Input**: User interaction profile (explicit preferences + consented session signals).
* **Output**: Normalized `AccessibilityTwin` object.
* **Fields Evaluated**:
  * Language preference (`Hindi`, `English`, etc.)
  * Preferred interaction modality (`voice`, `touch`, `hybrid`)
  * Presentation requirements (`large_text`, `high_contrast`, `screen_reader`)
  * Cognitive support needs (`simplified_language`, `one_step_at_a_time`)
  * Physical support (`haptic_feedback`, `large_touch_targets`)

---

### Stage 2: UNDERSTAND TASK
* **Input**: User multimodal input (audio voice query, captured image, direct tap).
* **Engine**: `IntentEngine`
* **Output**: Normalized `Task` specification.
* **Core Task Types**:
  1. `FORM_COMPLETION`: User needs to complete a digital or physical application.
  2. `UNDERSTAND_DOCUMENT`: User needs key highlights, deadlines, and requirements from an official document/notice.
  3. `COMMUNICATE`: User needs two-way communication (e.g., ISL sign-to-speech or speech-to-captions).
  4. `SEE`: User needs scene understanding, physical layout awareness, and obstacle detection.
  5. `READ`: User needs targeted OCR reading of signs, menus, or labels.
  6. `FIND_OBJECT`: User needs directional guidance to locate a specific item.

---

### Stage 3: DETECT BARRIERS
* **Input**: `Task` structure + `AccessibilityTwin` + Document/Scene metadata.
* **Engine**: `BarrierEngine`
* **Output**: List of identified `Barrier` descriptors.
* **Barrier Categories**:
  * **Visual Barriers**: Tiny fonts (<12pt), low color contrast (<4.5:1), dense layouts, purely graphical data without alt-text.
  * **Motor Barriers**: Multiple tiny interactive controls, dense form fields, mandatory typing on touchscreens.
  * **Cognitive Barriers**: Complex legal/bureaucratic jargon, more than 4 concurrent choices, ambiguous field labels.
  * **Language Barriers**: Information presented in formal English when user prefers conversational Hindi.
  * **Digital Literacy Barriers**: Hidden action buttons, multi-page file upload hurdles, confusing nested menus.
  * **Interaction Complexity Barriers**: Complex dependencies between fields (e.g., IFSC required after bank account).

---

### Stage 4: COMPILE ACCESSIBLE TASK FLOW
* **Input**: `Task` + `AccessibilityTwin` + Detected `Barriers` + Available AI Capabilities.
* **Engine**: `AccessibleTaskFlowCompiler`
* **Output**: `AccessibleTaskFlow` (a linearized execution plan with custom UI instructions and prompts).
* **Compilation Rules**:
  * *Rule 1*: If `one_step_at_a_time == True`, flatten multi-column forms into a strictly sequential card flow.
  * *Rule 2*: If `voice_input == True`, generate clear conversational spoken prompts for each step.
  * *Rule 3*: If `simplified_language == True`, translate bureaucratic terms (e.g., *"Matriculation roll code"*) into plain language (*"Your 10th standard roll number"*).
  * *Rule 4*: If `language == "Hindi"`, provide localized text and Hindi voice synthesis.

---

### Stage 5: ASSIST
* **Input**: Current step of `AccessibleTaskFlow` + active inputs.
* **Engine**: `AccessibilityAssistanceEngine`
* **Capabilities Coordinated**:
  * **Vision & Object Detection**: Identifies physical objects and bounding coordinates.
  * **OCR & Document Engine**: Extracts structured key-value pairs from documents.
  * **Scene Fusion**: Associates text with corresponding physical objects.
  * **ISL Engine**: MediaPipe 3D hand tracking and gesture recognition.
  * **Speech (STT / TTS)**: Bidirectional voice communication.
  * **Tactile Haptics**: Directional vibration cues and confirmation pulses.

---

### Stage 6: VERIFY
* **Input**: User responses + Task completion criteria.
* **Engine**: `TaskVerificationService`
* **States**:
  * `IN_PROGRESS`: Active step processing, incomplete fields remain.
  * `NEEDS_CONFIRMATION`: User response captured, awaiting user confirmation before committing.
  * `BLOCKED`: Missing critical document or validation error (e.g., invalid Aadhaar length).
  * `COMPLETED`: All mandatory criteria satisfied and confirmed.
  * `FAILED`: Task aborted or irrecoverable barrier encountered.
* **Output**: Verification certificate with completion percentage and verification summary.

---

### Stage 7: LEARN & HEATMAP
* **Input**: Task execution telemetry (completion status, step delays, repeated retries, modality switches).
* **Engine**: `AccessibilityLearningService`
* **Outputs**:
  * **Interaction Heatmap**:
    * <span style="color:red">**RED**</span>: High interaction complexity (e.g., multi-step document upload).
    * <span style="color:goldenrod">**YELLOW**</span>: Moderate complexity (e.g., long address input).
    * <span style="color:green">**GREEN**</span>: Low complexity (e.g., single-word voice confirmation).
  * **Proactive Adaptation Proposal**: Recommends personalized adjustments for upcoming workflows.
