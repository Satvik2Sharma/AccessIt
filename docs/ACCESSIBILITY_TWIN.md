# Sahayak AI — The Accessibility Twin Specification

**Concept**: The Accessibility Twin  
**Philosophy**: Modeling Functional Interaction Requirements, Not Medical Conditions  
**Author**: Lead Software Architect

---

## 1. What is an Accessibility Twin?

An **Accessibility Twin** is a dynamic, software-defined profile describing how a user prefers and needs to interact with digital information and physical surroundings.

### Fundamental Ethical Distinction
* **Medical Profile**: Labels a person with clinical diagnoses (*"patient has 80% bilateral sensorineural hearing loss"*, *"user is legally blind"*).
* **Accessibility Twin**: Defines functional interaction capabilities (*"prefers spoken feedback"*, *"needs large 24pt high-contrast text"*, *"benefits from one-step-at-a-time task decomposition"*).

Sahayak AI **strictly avoids medical labeling**. The system adapts technology to human needs without making unsolicited diagnostic claims.

---

## 2. Accessibility Twin Data Model Schema

```json
{
  "id": "twin_default_satvik",
  "language": "Hindi",
  "secondary_language": "English",
  "visual": {
    "large_text": true,
    "high_contrast": true,
    "screen_reader": false,
    "magnification_level": 1.5,
    "color_inversion": false
  },
  "hearing": {
    "captions": true,
    "visual_alerts": true,
    "sign_language": false,
    "audio_frequency_boost": "none"
  },
  "motor": {
    "voice_input": true,
    "large_touch_targets": true,
    "reduce_scrolling": true,
    "dwell_time_ms": 300
  },
  "comprehension": {
    "simplified_language": true,
    "one_step_at_a_time": true,
    "read_instructions_aloud": true,
    "show_task_progress": true,
    "summarize_documents": true
  },
  "communication": {
    "preferred_input": "voice",
    "preferred_output": "voice_and_text",
    "sign_to_text": false,
    "text_to_sign": false
  },
  "haptics": {
    "enabled": true,
    "intensity": "strong",
    "tactile_confirmation": true
  }
}
```

---

## 3. Interaction Adaptation Matrix

The same underlying task generates fundamentally different interaction flows depending on the Accessibility Twin:

| Dimension | User A (Voice + Simplified Hindi) | User B (Visual Captions + English) | User C (High Contrast + Large Text) |
|---|---|---|---|
| **Form Filling** | Reads each field aloud in simple Hindi; records voice response. | Displays one large input card with visual hint; accepts typing. | Displays 24pt bold yellow-on-black text fields with tactile ticks. |
| **Notice Summary** | Spoken bullet points in conversational Hindi. | Formatted textual summary with keyword highlights. | High-contrast high-legibility card with 2-sentence key takeaway. |
| **Sign Language** | Speaks out detected signs in real-time. | Displays large on-screen caption overlays. | Displays prominent high-contrast text banner. |

---

## 4. Personalization & The Learning Stage

The Accessibility Twin evolves through **interaction feedback signals**, never guesswork:
1. **Completion rate**: Did user successfully complete the compiled steps?
2. **Abandoned fields**: Did user skip a complex file upload or dense field?
3. **Repeated input errors**: Did user struggle with small on-screen buttons?
4. **Modality switches**: Did user press the microphone icon repeatedly instead of typing?

When persistent signals are detected over local sessions, Sahayak respectfully proposes:
> *"Would you like Sahayak to default to voice input and simplified step-by-step guidance for future forms?"*

Consent is mandatory before updating the profile.
