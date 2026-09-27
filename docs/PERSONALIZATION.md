# Sahayak AI — Advanced Personalization & Telemetry Learning

**Status**: `IMPLEMENTED` (Consented Telemetry Aggregation, Interaction Heatmaps, Preference Updating)

---

## 1. Overview & Principle
Sahayak AI learns how a user interacts over time (voice vs. touch speed, retries, navigation preferences) to proactively simplify future flows. It strictly models **functional preferences** and never infers unsolicited medical conditions.

---

## 2. API Endpoints

### `GET /api/v1/learning/heatmap`
Returns the 3-tier Interaction Heatmap (`RED` = high friction, `YELLOW` = moderate, `GREEN` = smooth) and recommended system adaptations.

### `GET /api/v1/learning/personalization?twin_id=default_user`
Retrieves the user's active interaction settings.

### `POST /api/v1/learning/personalization`
Updates user preferences:
```json
{
  "twin_id": "default_user",
  "updates": {
    "language": "Hindi",
    "high_contrast": true,
    "simplified_language": true,
    "voice_speed": 1.1
  }
}
```

---

## 3. Team Integration Contract

### Mobile Team (`mobile/lib/`)
* On profile screen or settings screen, load `GET /api/v1/learning/personalization` and bind to UI switches (High Contrast, Large Touch Targets, Speech Speed, Language).
