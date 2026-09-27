# Sahayak AI — Real Document Reading, Q&A & Task Extraction

**Status**: `IMPLEMENTED` (RapidOCR Image Extraction, Hindi/English Simplification, Multi-Turn Q&A, and Actionable Task Generation)

---

## 1. Overview & Pipeline
Document Reading enables users to photograph complex administrative notices, circulars, or medical prescriptions. The engine extracts:
1. Document Title & Issuing Authority
2. Key Deadlines (with date regex and NLP parsing)
3. Required Documents & Eligibility Criteria
4. Application Fees & Immediate Action Items
5. Multi-turn Q&A for follow-up inquiries
6. Automatic creation of structured calendar tasks

---

## 2. API Endpoints

### `POST /api/v1/read`
Upload notice image for OCR and accessibility analysis.

### `POST /api/v1/read/qa`
Ask natural language questions about the scanned document:
```json
{
  "document_id": "doc_842a19c0",
  "question": "What is the deadline for this notice?",
  "language": "English"
}
```

### `POST /api/v1/read/tasks`
Converts document requirements into actionable tasks:
```json
{
  "document_id": "doc_842a19c0"
}
```
* **Response**:
```json
{
  "document_id": "doc_842a19c0",
  "document_title": "National Merit Scholarship Notice 2026",
  "tasks": [
    {
      "task_id": "task_doc_1",
      "title": "Collect Required Documents",
      "description": "Gather and scan: Aadhaar Card, Income Certificate, Marksheet",
      "deadline": "September 30, 2026",
      "action_type": "DOCUMENT_GATHERING"
    }
  ],
  "total_tasks": 3,
  "primary_deadline": "September 30, 2026"
}
```
