import pytest
from ai.ocr.document_qa import DocumentQAEngine
from shared.schemas.models import DocumentQuestion, DocumentAnswer

SAMPLE_DOC = {
    "document_title": "National Merit Scholarship 2026",
    "issuing_authority": "Ministry of Education",
    "key_deadlines": ["September 30, 2026"],
    "required_documents": ["Aadhaar Card", "Income Certificate", "Marksheet"],
    "application_fee": "NIL",
    "simplified_summary_en": "Apply for National Merit Scholarship by September 30.",
    "simplified_summary_hi": "राष्ट्रीय योग्यता छात्रवृत्ति के लिए 30 सितंबर तक आवेदन करें।",
}

def test_qa_deadline_question():
    engine = DocumentQAEngine()
    engine.load_document(preloaded_doc=SAMPLE_DOC)
    answer = engine.answer(DocumentQuestion(question="What is the deadline?"))
    assert isinstance(answer, DocumentAnswer)
    assert answer.found_in_document is True
    assert "2026" in answer.answer or "September" in answer.answer

def test_qa_fee_question():
    engine = DocumentQAEngine()
    engine.load_document(preloaded_doc=SAMPLE_DOC)
    answer = engine.answer(DocumentQuestion(question="What is the application fee?"))
    assert answer.found_in_document is True
    assert "NIL" in answer.answer.upper() or "nil" in answer.answer.lower()

def test_qa_required_documents():
    engine = DocumentQAEngine()
    engine.load_document(preloaded_doc=SAMPLE_DOC)
    answer = engine.answer(DocumentQuestion(question="What documents are required?"))
    assert answer.found_in_document is True
    assert len(answer.answer) > 5

def test_qa_not_found():
    engine = DocumentQAEngine()
    engine.load_document(preloaded_doc=SAMPLE_DOC)
    answer = engine.answer(DocumentQuestion(question="Which color is the building?"))
    assert answer.found_in_document is False
    assert "not found" in answer.answer.lower()

def test_qa_no_document_loaded():
    engine = DocumentQAEngine()
    answer = engine.answer(DocumentQuestion(question="What is the deadline?"))
    assert answer.found_in_document is False
    assert "No document" in answer.answer

def test_qa_batch():
    engine = DocumentQAEngine()
    engine.load_document(preloaded_doc=SAMPLE_DOC)
    questions = [
        DocumentQuestion(question="What is the deadline?"),
        DocumentQuestion(question="Who issued this?"),
    ]
    answers = engine.answer_batch(questions)
    assert len(answers) == 2
    assert all(isinstance(a, DocumentAnswer) for a in answers)
