# Sahayak AI — Error Recovery & Graceful Degradation

**Status**: `IMPLEMENTED` (Backend Recovery Middleware & Structured Machine-Readable Results)

---

## 1. Overview & Principle
An accessibility copilot must **never crash or display raw stack traces** to a user with visual, motor, or cognitive impairments. If an AI service, camera feed, or OCR parsing fails, Sahayak AI initiates deterministic, safe fallbacks and returns structured recovery instructions.

---

## 2. Recovery Strategies by Pipeline Stage

| Pipeline Stage | Potential Failure | Automatic Recovery Strategy | Fallback State |
| :--- | :--- | :--- | :--- |
| **UNDERSTAND_USER** | Ambiguous voice query | Keyword fuzzy match & default to form or document flow | Conversational clarification prompt |
| **AI_INFERENCE (OCR)** | Blurred image / low lighting | Heuristic text parser with cached template matching | Guidance to hold document steady |
| **AI_INFERENCE (ISL)** | No hand detected / low confidence | Landmark tracker fallback + emergency gesture catalogue | Prompt to center hand in frame |
| **AI_INFERENCE (Vision)** | Object bounding box out of range | Fallback center coordinate $(0.5, 0.5)$ | "Object straight ahead at 12 o'clock" |
| **COMPILE_FLOW** | Unknown form structure | Standard 7-field sequential accessibility workflow | Safe universal form template |
| **VERIFY** | Validation timeout | Local regex and constraint validation | Manual user confirmation step |

---

## 3. Schema: `RecoveryResult`

```json
{
  "failed_stage": "AI_INFERENCE",
  "failure_type": "NON_BLOCKING_FALLBACK",
  "error_message": "Low OCR contrast detected",
  "retry_attempted": true,
  "fallback_used": true,
  "fallback_strategy": "TEMPLATE_HEURISTIC_MATCH",
  "recovery_status": "RECOVERED_WITH_FALLBACK",
  "actionable_user_message": "Notice: An operation required a fallback. Continuing safely with standard assistance.",
  "spoken_recovery_guidance": "We encountered a minor hiccup, but we have adjusted and are ready to proceed."
}
```

---

## 4. Team Integration Contract

### Mobile Team (`mobile/lib/`)
* **Behavior**:
  * Check for `recovery_info` in response envelopes.
  * If present, announce `spoken_recovery_guidance` to the user so they are always aware of adjustments without panic.
