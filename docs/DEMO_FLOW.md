# Sahayak AI — Hackathon Live Demonstration Script

**Event**: Hackathon Final Presentation & Live Judging  
**System**: Sahayak AI (Intent-Aware Personal Accessibility Copilot)  
**Author**: Lead Software Architect

---

## Demo Philosophy for Judges

> **"A feature is not complete merely because an AI model produces an output.**  
> **A feature is complete when: USER -> TASK -> BARRIER -> ACCESSIBLE FLOW -> ASSIST -> VERIFY -> COMPLETION."**

Judges will not see isolated buttons for OCR, YOLO, or TTS. They will observe an adaptive copilot that understands the human need and compiles the optimal interaction strategy.

---

---

## 🚦 Feature Capability Classification

In accordance with transparent engineering principles:
* **Demo 1 (Notice Comprehension)**: `IMPLEMENTED` (RapidOCR CPU ONNX engine, entity parsing, Hindi/English summaries).
* **Demo 2 (Form Completion)**: `IMPLEMENTED` (Real OCR field discovery, barrier engine, 7-step linearized voice flow, field-level semantic validation, TaskVerificationService token).
* **Demo 3 (ISL Gesture Recognition)**: `PARTIALLY IMPLEMENTED` (MediaPipe 21-point 3D tracking loaded lazily; verified support for `HELP`, `A`, `ONE`, `TWO`, `YES`, `NO`).
* **Optional Wow Demo (Spatial Guidance)**: `DEMO/MOCK` (Directional math & haptics functional; live YOLO weights disabled by default to stay within 2.5 GB RAM).

---

## 🎯 DEMO 1 — Understand a Document (Notice Comprehension) `[IMPLEMENTED]`

### Scenario
A student holds up a complex official university scholarship notification with fine print, dense government jargon, and multi-paragraph eligibility clauses.

### Execution Steps
1. **User Action**: The judge or presenter points the camera at the notice and taps the voice copilot button.
2. **User Voice Query**:
   > *"What is important in this notice?"*
3. **Sahayak 7-Stage Pipeline**:
   * **Intent**: `UNDERSTAND_DOCUMENT`
   * **Accessibility Twin**: `language = Hindi`, `comprehension = simplified`, `output = voice_and_text`
   * **AI Processing**: Real RapidOCR text extraction + layout entity parsing.
   * **Extracted Entities**:
     * Title: `NATIONAL MERIT SCHOLARSHIP SCHEME 2026`
     * Deadline: `September 30, 2026`
     * Required Documents: Income Certificate (< 2.5 Lakhs), Aadhaar Card, Class 10 Marksheet, Bank Account
     * Application Fee: `NIL (Free of Cost)`
     * Action Required: Candidates must complete and verify application form
   * **Barrier Detected**: 9pt bureaucratic text, complex English legal criteria, confusing date formats.
   * **Accessible Compilation**: Plain-language conversational Hindi/English summary with actionable bullet points.
4. **Sahayak Voice & UI Output**:
   > *"यह NATIONAL MERIT SCHOLARSHIP SCHEME 2026 है। आवेदन जमा करने की अंतिम तिथि September 30, 2026 है। ज़रूरी दस्तावेज़: Valid Income Certificate, Aadhaar Card, Class 10 Marksheet। आवेदन शुल्क: निःशुल्क (NIL) है।"*
5. **Verification**: Task verification logs `NOTICE_DIGEST_DELIVERED`, user comprehension confirmed.

---

## 🏆 DEMO 2 — Complete a Form (The Flagship Demo) `[IMPLEMENTED]`

### Scenario
The judge provides a physical or printed scholarship application form with 7 required fields, fine lines, and small input boxes.

### Execution Steps
1. **User Action**: Presenter holds the form in front of the camera and says:
   > *"Help me fill this form."*
2. **Sahayak 7-Stage Pipeline**:
   * **Task Understood**: `FORM_COMPLETION`
   * **Twin Checked**: `one_step_at_a_time = true`, `voice_input = true`, `large_text = true`, `haptics = true`
   * **Barriers Identified**:
     * Visual Barrier: Dense layout, small 10pt font.
     * Motor Barrier: Tiny paper input boxes, high handwriting burden.
     * Cognitive Barrier: Confusing field names (*"Applicant Patronymic / Guardian"*).
   * **Compilation**: `AccessibleTaskFlowCompiler` converts the 7-field form into a linear, conversational voice flow.
3. **Interactive Step-by-Step Flow**:
   * **Step 1 (Name)**:
     * Sahayak (Voice + 26pt Card): *"आपके फ़ॉर्म में 7 ज़रूरी जानकारियां हैं। मैं एक-एक करके पूछूँगा। आपका पूरा नाम क्या है?"*
     * User (Voice): *"सात्विक शर्मा"* (Satvik Sharma)
     * Sahayak: *"समझ गया। नाम: सात्विक शर्मा। क्या यह सही है?"*
     * User: *"हाँ"* (Yes) -> *Tactile Haptic Pulse*
   * **Step 2 (Date of Birth)**:
     * Sahayak: *"आपकी जन्मतिथि क्या है?"*
     * User: *"15 अगस्त 2003"*
     * Sahayak validates format (`15/08/2003`), auto-advances.
   * **Steps 3–7**: Address, Category, Annual Income, Aadhaar, Bank Details.
4. **Verification & Proof of Completion**:
   * Form completion counter updates live: `1/7 -> 2/7 -> 7/7 (100%)`.
   * `TaskVerificationService` runs consistency checks.
   * Status updates from `IN_PROGRESS` -> `COMPLETED`.
   * Output:
     > *"फ़ॉर्म की सभी 7 आवश्यक जानकारियां सफलतापूर्वक पूरी हो चुकी हैं। आवेदन जमा करने के लिए तैयार है।"*
     > *(All 7 required fields validated and completed. Application ready for submission.)*

---

---

## ✋ DEMO 3 — Sign Communication (ISL Interpreter) `[PARTIALLY IMPLEMENTED]`

### Status
`PARTIALLY IMPLEMENTED` — Supported verified gestures: `HELP` (Open Palm), `A` (Fist), `ONE`, `TWO`, `YES` (Thumbs Up), `NO` (Thumbs Down). Continuous arbitrary sentence translation is `PLANNED`.

### Scenario
A team member or judge communicates using an Indian Sign Language (ISL) gesture.

### Execution Steps
1. **User Action**: The presenter selects the "Talk / Communicate" mode and points the front or back camera at the signer.
2. **Signer Action**: Performs the ISL sign for **"HELP"** or an alphabet sign (**"A"**).
3. **Sahayak 7-Stage Pipeline**:
   * **MediaPipe**: Real-time 21-point 3D hand tracking on key landmarks via lazy-loaded ONNX/Task recognizer.
   * **ISL Engine**: Classifies gesture into verified vocabulary token.
   * **Twin**: Output preferred as clear audio voice for the non-signing listener.
4. **Sahayak Output**:
   * Spoken audio: *"Help"*
   * High-contrast screen caption: **HELP [सहायता]**
   * Tactile confirmation: Double haptic buzz acknowledging sign recognition.

---

## 🌟 OPTIONAL WOW DEMO — Object Finding & Directional Guidance `[DEMO/MOCK]`

### Status
`DEMO/MOCK` — Spatial direction trigonometry and right/left haptic feedback implemented; live YOLOv8 detector weights disabled by default to prevent exceeding the 2.5 GB RAM system limit.

### Scenario
User asks to find an everyday object in the room: *"Find my water bottle."*

### Execution Steps
1. User: *"Find my bottle."*
2. Camera scans room. Directional Finder calculates horizontal offset:
   > *"आपकी बोतल आपके दाईं ओर थोड़ी दूरी पर है।"*  
   > *(Your bottle is slightly to your right, within arm's reach.)*
3. Haptic vibration pulses on the right side of the device, directing user's hand toward the item.

---

## 🧪 Reproducible Automated Demo Test Procedure

Reviewers and hackathon judges can verify all three priority demos end-to-end with a single automated command:

```bash
# Activate environment and run reproducible test suite
backend/venv/bin/python scripts/test_demos.py
```

This automated runner verifies:
1. System Health and lazy model architecture.
2. Demo 2 (Form Completion): Real OCR field extraction -> 7-step sequence -> 4-digit Aadhaar rejection test -> valid answers -> official verification token (`VERIFIED_SAHAYAK_...`).
3. Demo 1 (Document Reading): RapidOCR execution on physical scholarship notice -> Title, deadline, 4 requirements, fee, action required, and localized summaries.
4. Demo 3 (ISL Recognition): MediaPipe 3D gesture recognizer -> `HELP` classification -> Spoken output -> Haptic pulse pattern.
