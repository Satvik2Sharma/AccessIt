"""
Integration Test for Document Reading, Q&A, and Document-to-Task Pipeline
"""

import sys
import os

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from backend.services.pipeline_service import pipeline_service
from backend.services.session_service import session_service


def test_document_reading_and_qa_lifecycle():
    twin = pipeline_service.twin_service.get_twin("default_user")

    # 1. Document scan & understanding
    doc_res = pipeline_service.assistance_engine.assist_understand_document(
        image_bytes=None,
        query="What is the deadline for this notice?",
        twin=twin
    )
    assert "title" in doc_res
    assert "deadlines" in doc_res

    # 2. Session creation
    doc_id = session_service.create_document_session(doc_res)
    assert doc_id is not None

    # 3. Follow-up Q&A
    qa_ans = pipeline_service.answer_document_question(
        document_id=doc_id,
        question="What documents do I need to bring?",
        language="English",
    )
    assert qa_ans.document_id == doc_id
    assert len(qa_ans.supporting_extracted_info) > 0

    # 4. Document-to-Task Conversion
    task_res = pipeline_service.convert_document_to_tasks(document_id=doc_id)
    assert task_res.total_tasks >= 2
    assert len(task_res.tasks) >= 2


if __name__ == "__main__":
    test_document_reading_and_qa_lifecycle()
    print("Integration test_document_reading.py passed successfully!")
