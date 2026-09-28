# Sahayak AI — Real ISL (Indian Sign Language) Pipeline

**Status**: `VERIFIED & OPERATIONAL` (MediaPipe 3D Hand Landmarks, Real Camera Stream at 1 FPS, Debouncing, Spoken TTS Output)

---

## 1. Overview & Architecture

The ISL Pipeline enables real-time sign language interpretation for deaf and hard-of-hearing users across mobile and web interfaces.
* **Camera Input**: Front-facing or rear device camera stream sampled at a controlled rate (1 FPS).
* **Perception Engine**: MediaPipe Gesture & Hand Landmark Recognizer (`models/gesture_recognizer.task`) analyzing 21 3D spatial hand landmarks (wrist, thumb, index, middle, ring, pinky).
* **Geometric Landmark Analysis**: Computes finger extension states for numeric and static gestures when direct gesture classification is ambiguous.
* **Temporal Smoothing & Debouncing**: Sliding window queue (5 frames) prevents jitter and eliminates flickering predictions.
* **Defensive Failure Handling**:
  - `NO_HAND_DETECTED`: Gracefully instructs the user to "Move your hand into the camera frame" rather than falsely converting background noise into signs.
  - `UNCERTAIN`: Flags low confidence (< 0.45) gestures and prompts the user to hold steady.
* **Multimodal Feedback**: Visual captions, localized Hindi/English speech synthesis via TTS, and directional haptic pulses.

---

## 2. Supported Vocabulary

| Sign | Category | Spoken Output (EN) | Hindi Translation (HI) | Haptic Feedback |
| :--- | :--- | :--- | :--- | :--- |
| **`HELP`** | Emergency | Help | सहायता / मदद चाहिए | `EMERGENCY_TRIPLE_PULSE` |
| **`DOCTOR`** | Emergency | Need a doctor | डॉक्टर की आवश्यकता है | `EMERGENCY_DOUBLE_PULSE` |
| **`PAIN`** | Emergency | Experiencing pain | दर्द हो रहा है | `HEAVY_PULSE` |
| **`WATER`** | Request | Need drinking water | पीने का पानी चाहिए | `SINGLE_PULSE` |
| **`MEDICINE`** | Request | Need medicine | दवा की आवश्यकता है | `DOUBLE_PULSE` |
| **`YES`** | Communication | Yes | हाँ (स्वीकृत) | `SUCCESS_DOUBLE_PULSE` |
| **`NO`** | Communication | No | नहीं (अस्वीकृत) | `SINGLE_PULSE` |
| **`FRIENDSHIP`** | Communication | Friendship | मित्रता | `SUCCESS_DOUBLE_PULSE` |
| **`ONE` / `1`** | Number | One | एक | `SINGLE_PULSE` |
| **`TWO` / `2`** | Number | Two | दो | `SINGLE_PULSE` |
| **`A`** | Alphabet | A | अक्षर ए | `SINGLE_PULSE` |

---

## 3. API Endpoints

### `POST /api/v1/isl/predict`
Multipart form upload with camera frame image (`image` file or `image_base64` string) and optional `session_id`.

**Response Format**:
```json
{
  "sign": "HELP",
  "confidence": 0.95,
  "sign_type": "DYNAMIC_EMERGENCY",
  "spoken_output": "Help",
  "hindi_translation": "सहायता / मदद",
  "haptic_feedback": "SUCCESS_DOUBLE_PULSE",
  "caption": "HELP [सहायता / मदद]",
  "landmarks_count": 21,
  "method": "MEDIAPIPE_3D"
}
```
