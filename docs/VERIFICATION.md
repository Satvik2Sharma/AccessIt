# Sahayak AI — First-Class Task & Form Verification

**Status**: `IMPLEMENTED` (Multi-Field Constraint Validation, Progress Auditing & Verification Token Issuance)

---

## 1. Overview & Purpose
Verification guarantees that no form is submitted or official document processed with missing, erroneous, or unconfirmed fields. When all required fields are validated and confirmed by the user, the Verification Service issues a cryptographic/audit verification token (e.g., `VERIFIED_SAHAYAK_FC21E713`).

---

## 2. API Endpoints

### `POST /api/v1/task/verify?task_id=task_form_123`
Returns the current verification status of an active task.

### `POST /api/v1/verification/check`
Executes an explicit audit across completed fields:
```json
{
  "task_id": "task_form_123",
  "total_fields": 7,
  "completed_fields": {
    "full_name": {"value": "Satvik Sharma", "confirmed": true},
    "aadhaar": {"value": "982455101289", "confirmed": true}
  },
  "required_field_ids": ["full_name", "dob", "address", "category", "annual_income", "aadhaar", "bank_account"]
}
```

* **Response**:
```json
{
  "task_id": "task_form_123",
  "status": "IN_PROGRESS",
  "completion_percentage": 28.6,
  "completed_fields": 2,
  "total_fields": 7,
  "missing_fields": ["dob", "address", "category", "annual_income", "bank_account"],
  "verification_token": null,
  "summary_message": "2 of 7 fields completed (29%). 5 remaining."
}
```
