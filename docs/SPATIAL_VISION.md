# Sahayak AI — Spatial Vision & Directional Guidance

**Status**: `IMPLEMENTED` (Full Spatial Direction, Object Detection Adapters & Camera Pipeline Integration)

---

## 1. Overview & Purpose
Spatial Vision allows visually impaired users to locate physical objects in their immediate environment without needing fine manual sight. Rather than returning dry millimeter estimates, the system models spatial positions as **12-Hour Clock Directions** relative to the user's forward heading, combined with **Vertical Elevation** and **Relative Proximity**.
This is integrated directly into the `ai/vision/` modules and orchestrated through `ai/camera/camera_engine.py`.

---

## 2. Spatial Mapping Mechanics
* **12-Hour Clock Direction**:
  * Normalized image space $(x, y) \in [0.0, 1.0]$. Center $(0.5, 0.5)$ is 12 o'clock.
  * Angle $\theta = \text{atan2}(dx, dy)$ mapped to hours $1 \dots 12$.
  * Left: 9 to 11 o'clock. Straight ahead: 12 o'clock. Right: 1 to 3 o'clock.
* **Vertical Elevation**:
  * $y < 0.35$: Upper / Eye level.
  * $0.35 \le y \le 0.70$: Table / Waist level.
  * $y > 0.70$: Low / Floor level.
* **Relative Proximity** (Derived from bounding box area ratio):
  * $\text{Area} > 0.25$: Very close.
  * $0.08 \le \text{Area} \le 0.25$: Within arm's reach.
  * $\text{Area} < 0.08$: A few steps ahead.
* **Tactile Haptic Cues**:
  * Left: `PULSE_LEFT`
  * Right: `PULSE_RIGHT`
  * Center / Target Acquired: `DOUBLE_PULSE_CENTER`
  * Proximity Alert: `HIGH_URGENT`

---

## 3. API Contract

### Endpoint: `POST /api/v1/see/spatial`

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
  "normalized_coordinates": {
    "x": 0.7,
    "y": 0.56
  },
  "area_ratio": 0.137,
  "found": true
}
```

---

## 4. Team Integration Contract

### AI Team (`ai/vision/directional_finder.py`)
* **Produces**: `compute_spatial_guidance(bbox, label, language)` returning normalized coordinates, clock hour, elevation, and proximity strings.

### Mobile Team (`mobile/lib/`)
* **Consumes**: `POST /api/v1/see/spatial`
* **Actions**:
  1. Play spoken guidance audio string (`spoken_guidance`).
  2. Trigger vibration according to `haptic_cue` (`PULSE_LEFT`, `PULSE_RIGHT`, `DOUBLE_PULSE_CENTER`).
  3. Render directional overlay arrow on screen pointing to `clock_hour`.
