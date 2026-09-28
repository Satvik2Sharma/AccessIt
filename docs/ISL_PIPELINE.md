# Sahayak AI — Real ISL (Indian Sign Language) Pipeline

**Status**: `IMPLEMENTED` (MediaPipe 3D Hand Landmarks, Static & Dynamic Gestures, Spoken TTS Output)

---

## 1. Overview & Pipeline
The ISL Pipeline enables real-time sign language interpretation for deaf and hard-of-hearing users in India.
* Uses MediaPipe Hand Landmark Recognizer with 21 normalized 3D landmarks.
* Translates gestures (e.g. HELP, WATER, MEDICINE, YES, NO) into spoken audio prompts and visual captions.

---

## 2. API Endpoint

### `POST /api/v1/isl/predict`
Multipart form upload with camera frame or landmark data.
* Returns recognized sign, confidence, Hindi/English translations, and haptic feedback pattern.
