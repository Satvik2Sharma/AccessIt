# Sahayak AI — Voice Assistant & Speech Processing

**Status**: `VERIFIED & OPERATIONAL` (Multilingual Voice Command & Intent Mapping, Flutter `speech_to_text` STT, `flutter_tts` Speech Synthesis, and Text Input Fallback Modal)


---

## 1. Overview & Purpose
The Voice Assistant allows hands-free, motor-accessible control of the entire Sahayak AI copilot. Users can speak naturally in Hindi, English, or mixed Hinglish. The pipeline maps speech transcripts into actionable tasks, triggers corresponding workflows (form filling, document scanning, object finding, sign translation), and returns localized spoken audio guidance.

---

## 2. API Specifications

### `POST /api/v1/voice/command`
Processes user speech queries, classifies intent, initiates sessions, and returns spoken prompts.

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
  "session_id": "voice_4a2c19e8",
  "parameters": {
    "rationale": "High confidence pattern match for form filling in Hindi"
  },
  "haptic_cue": "TOUCH_CONFIRM"
}
```

### `POST /api/v1/voice/tts`
Text-to-Speech contract returning speech parameters and SSML markup.

* **Request**:
```json
{
  "text": "Please state your full name",
  "language": "English",
  "speed": 1.0,
  "pitch": 1.0
}
```

* **Response (200 OK)**:
```json
{
  "text": "Please state your full name",
  "language": "English",
  "audio_url": null,
  "phonetic_ssml": "<speak><prosody rate='1.0' pitch='1.0'>Please state your full name</prosody></speak>",
  "duration_estimate_sec": 2.0
}
```

---

## 3. Team Integration Contract

### AI Team (`ai/intent/intent_engine.py`)
* **Produces**: `classify_intent(query, twin)` and entity decomposition with Hindi/English language identification.

### Mobile Team (`mobile/lib/`)
* **Consumes**: `POST /api/v1/voice/command`
* **Actions**:
  1. Record speech using on-device STT (`speech_to_text` Flutter package).
  2. Send transcript to backend.
  3. Route mobile screen to the view corresponding to `suggested_action` (`START_FORM_COMPLETION` -> Form Screen, `SCAN_DOCUMENT` -> Read Screen).
  4. Speak `spoken_reply` using device TTS (`flutter_tts`).
