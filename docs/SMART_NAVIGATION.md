# Sahayak AI — Smart Navigation & Obstacle Guidance

**Status**: `IMPLEMENTED` (Session-Aware Direction & Obstacle Guidance) / `PARTIAL` (Continuous Visual Odometry)

---

## 1. Overview & Purpose
Smart Navigation assists visually impaired or motor-restricted users in navigating indoor and campus environments safely. It combines landmark detection, destination targeting, obstacle avoidance warnings, and directional tactile pulses.

---

## 2. Navigation State & Mechanics
* **Directional Cues**:
  * Step-by-step instructions (e.g., "5 steps ahead at 11 o'clock").
  * 12-hour clock directions for intuitive angular orientation.
* **Obstacle Warnings**:
  * Identifies pillars, stairs (up/down), doors, furniture, and persons in path.
  * Assigns severity levels: `LOW`, `MEDIUM`, `HIGH_URGENT`.
* **Tactile Haptic Feedback**:
  * Straight path: `DOUBLE_PULSE_CENTER`.
  * Obstacle on right: `PULSE_LEFT` (nudges user leftwards).
  * Imminent obstacle: `HIGH_URGENT` / heavy pulse.

---

## 3. API Contract

### `POST /api/v1/navigation/guide`

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
  "session_id": "nav_81f20a9e",
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

### `GET /api/v1/navigation/session?session_id=nav_81f20a9e`
Returns stateful path history, obstacles encountered, and current heading.

---

## 4. Team Integration Contract

### AI Team (`ai/vision/directional_finder.py`)
* **Produces**: Spatial vectors and proximity classification for navigation landmarks.

### Mobile Team (`mobile/lib/`)
* **Consumes**: `POST /api/v1/navigation/guide`
* **Actions**:
  1. Poll navigation guide periodically or on camera frame change.
  2. Speak `spoken_guidance` via TTS.
  3. Execute tactile vibration pattern according to `haptic_cue`.
