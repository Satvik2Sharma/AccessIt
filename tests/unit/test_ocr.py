"""
Unit Tests for Document Reading, Document Q&A, and Document-to-Task Conversion
"""

import sys
import os

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from shared.schemas.models import (
    DocumentQuestion,
    DocumentAnswer,
    DocumentTask,
    DocumentTaskExtractionResponse,
)
from backend.services.session_service import session_service
from backend.services.pipeline_service import pipeline_service


def test_document_session_creation():
    doc_data = {
        "title": "National Merit Scholarship Notice 2026",
        "authority": "Ministry of Education",
        "deadlines": ["15th October 2026", "25th October 2026"],
        "required_documents": ["Aadhaar Card", "Income Certificate", "Marksheet"],
        "application_fee": "NIL",
    }
    doc_id = session_service.create_document_session(doc_data)
    assert doc_id is not None
    sess = session_service.get_document_session(doc_id)
    assert sess["title"] == "National Merit Scholarship Notice 2026"
    assert len(sess["deadlines"]) == 2


def test_document_qa_pipeline():
    doc_data = {
        "title": "National Merit Scholarship Notice 2026",
        "deadlines": ["15th October 2026"],
        "required_documents": ["Aadhaar Card", "Income Certificate"],
    }
    doc_id = session_service.create_document_session(doc_data)

    # Q&A for deadline
    ans = pipeline_service.answer_document_question(
        document_id=doc_id,
        question="What is the deadline for this notice?",
        language="English"
    )
    assert ans.document_id == doc_id
    assert "15th October 2026" in ans.answer
    assert ans.confidence > 0.5


def test_document_to_task_conversion():
    doc_data = {
        "title": "National Merit Scholarship 2026",
        "deadlines": ["15th October 2026", "25th October 2026"],
        "required_documents": ["Aadhaar Card", "Income Certificate"],
    }
    doc_id = session_service.create_document_session(doc_data)

    res = pipeline_service.convert_document_to_tasks(document_id=doc_id)
    assert res.total_tasks >= 2
    assert len(res.tasks) >= 2
    assert any(t.action_type == "DOCUMENT_GATHERING" for t in res.tasks)


if __name__ == "__main__":
    test_document_session_creation()
    test_document_qa_pipeline()
    test_document_to_task_conversion()
    print("All unit/test_ocr.py tests passed!")
