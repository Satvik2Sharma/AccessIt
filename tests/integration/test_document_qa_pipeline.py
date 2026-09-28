import pytest
from ai.ocr.document_qa import DocumentQAEngine
from ai.task.document_task_generator import DocumentTaskGenerator
from shared.schemas.models import DocumentQuestion, TaskType

SAMPLE_DOC = {
    "document_title": "National Scholarship 2026",
    "issuing_authority": "Ministry of Education",
    "key_deadlines": ["October 15, 2026"],
    "required_documents": ["Aadhaar Card", "Income Certificate"],
    "application_fee": "NIL",
    "simplified_summary_en": "Apply before October 15 with Aadhaar and income certificate.",
    "simplified_summary_hi": "15 अक्टूबर से पहले आवेदन करें।",
    "action_items": ["Gather documents", "Fill form", "Submit online"],
}

def test_qa_pipeline_full():
    engine = DocumentQAEngine()
    engine.load_document(preloaded_doc=SAMPLE_DOC)
    questions = [
        DocumentQuestion(question="What is the deadline?"),
        DocumentQuestion(question="What is the application fee?"),
        DocumentQuestion(question="What documents do I need?"),
    ]
    answers = engine.answer_batch(questions)
    assert len(answers) == 3
    assert answers[0].found_in_document is True
    assert "October" in answers[0].answer or "15" in answers[0].answer

def test_document_task_generator():
    generator = DocumentTaskGenerator()
    result = generator.generate_from_document(SAMPLE_DOC)
    assert "task_id" in result
    assert result["title"] == "National Scholarship 2026"
    assert result["task_type"] == TaskType.UNDERSTAND_DOCUMENT.value
    assert len(result["milestones"]) > 0

def test_document_submission_task():
    generator = DocumentTaskGenerator()
    result = generator.generate_submission_task(SAMPLE_DOC)
    assert "task_id" in result
    assert result["task_type"] == TaskType.FORM_COMPLETION.value
    assert result["source"] == "document"
