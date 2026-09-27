# Sahayak AI — Scene Understanding & Object + OCR Fusion

**Status**: `IMPLEMENTED` (Geometric Bounding Box & OCR Text Fusion Adapter) / `PARTIAL` (Live Multi-Object Video Feed)

---

## 1. Overview & Purpose
In complex real-world environments (corridors, clinics, administrative offices), detecting objects in isolation is not enough. A user needs to know **which** door or **which** bottle is in front of them. Scene Understanding fuses physical object bounding boxes with nearby recognized OCR text signage to create meaningful semantic associations (e.g., `door` + `EMERGENCY EXIT` $\rightarrow$ `EMERGENCY EXIT door`).

---

## 2. Fusion Mechanics
* **Containment & High-Overlap Intersection**:
  * Intersection-over-Text-Area (IoA) metric measures whether recognized text is inscribed on or positioned directly adjacent to an object bounding box.
  * Threshold: $\text{Overlap} > 0.40$.
* **Geometric Spatial Attribution**:
  * Associates text annotations to the best-matching object entity.
  * Assigns clock-face direction and elevation to the composite object.

---

## 3. API Contract

### `POST /api/v1/scene/analyze`

* **Request**:
```json
{
  "scene_description": null,
  "objects": [
    {"label": "door", "bbox": [100, 50, 280, 420]},
    {"label": "water dispenser", "bbox": [350, 150, 500, 400]}
  ],
  "texts": [
    {"text": "EMERGENCY EXIT", "bbox": [120, 80, 260, 130], "confidence": 0.96},
    {"text": "DRINKING WATER", "bbox": [360, 170, 490, 210], "confidence": 0.94}
  ],
  "twin_id": "default_user"
}
```

* **Response (200 OK)**:
```json
{
  "scene_description": "Corridor area with an Emergency Exit door on the left and Drinking Water ahead.",
  "scene_type": "corridor",
  "detected_objects": [
    {
      "label": "door",
      "confidence": 0.92,
      "bbox": [100, 50, 280, 420],
      "clock_direction": "at 10 o'clock",
      "clock_hour": 10,
      "relative_direction": "to your left",
      "relative_proximity": "within arm's reach",
      "elevation": "table/waist level",
      "associated_texts": ["EMERGENCY EXIT"],
      "text": "EMERGENCY EXIT",
      "haptic_cue": "PULSE_LEFT",
      "haptic_intensity": "MEDIUM"
    }
  ],
  "fused_relations": [
    {
      "object_label": "door",
      "associated_text": "EMERGENCY EXIT",
      "spatial_relationship": "contained_within",
      "combined_interpretation": "EMERGENCY EXIT (door)",
      "confidence": 0.95
    }
  ],
  "hazards": [],
  "navigable_path_clear": true,
  "suggested_action": "Walk forward towards the clear walkway",
  "spoken_scene_summary": "There is an EMERGENCY EXIT door on your left at 10 o'clock, and drinking water ahead at 1 o'clock.",
  "language": "English"
}
```

---

## 4. Team Integration Contract

### AI Team (`ai/scene/scene_fusion.py`)
* **Produces**: `SceneFusion.fuse(objects, texts)` returning combined object bounding boxes with associated signage text.

### Mobile Team (`mobile/lib/`)
* **Consumes**: `POST /api/v1/scene/analyze`
* **Actions**:
  1. Render camera preview with highlighted fused bounding boxes.
  2. Display combined labels (e.g., "EMERGENCY EXIT (door)").
  3. Announce `spoken_scene_summary` aloud.
