"""
Sahayak AI — Document Reading, Document Q&A, and Document-to-Task Routes
Endpoints for OCR Notice Understanding, Multi-Turn Q&A, and Actionable Task Generation.
"""

from typing import Optional, Dict, Any
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from shared.schemas.models import (
    TaskType,
    DocumentQuestion,
    DocumentAnswer,
    DocumentTaskExtractionRequest,
    DocumentTaskExtractionResponse,
)
from backend.services.pipeline_service import pipeline_service
from backend.services.session_service import session_service

router = APIRouter(tags=["Document Reading & Q&A"])


@router.post("/read")
async def read_and_understand_document(
    image: Optional[UploadFile] = File(None),
    query: str = Form("What is important in this notice?"),
    twin_id: str = Form("default_user"),
):
    """
    Scans physical document/notice with OCR, extracts key deadlines and required documents,
    detects cognitive/language barriers, and initializes a document session.
    """
    twin = pipeline_service.twin_service.get_twin(twin_id)
    image_bytes = await image.read() if image else None

    # Detect barriers
    barriers = pipeline_service.barrier_engine.detect_barriers(
        task_type=TaskType.UNDERSTAND_DOCUMENT,
        task_context={"document_language": "English"},
        twin=twin,
    )

    # Assist
    result = pipeline_service.assistance_engine.assist_understand_document(image_bytes, query, twin)
    result["barriers_detected"] = barriers

    # Cache document session for follow-up Q&A and Task extraction
    doc_id = session_service.create_document_session(result, twin_id=twin_id)
    result["document_id"] = doc_id

    return result


@router.post("/read/qa", response_model=DocumentAnswer)
async def ask_document_question(req: DocumentQuestion):
    """
    Answers user questions about a previously scanned document (grounded in extracted notice data).
    Preserves document session context for continuous dialogue.
    """
    answer = pipeline_service.answer_document_question(
        document_id=req.document_id,
        question=req.question,
        twin_id=req.twin_id or "default_user",
        language=req.language or "English",
    )
    return answer


@router.post("/read/tasks", response_model=DocumentTaskExtractionResponse)
async def convert_document_to_tasks(req: DocumentTaskExtractionRequest):
    """
    Converts extracted document requirements, eligibility, and deadlines into structured actionable tasks.
    """
    response = pipeline_service.convert_document_to_tasks(
        document_id=req.document_id,
        raw_text=req.raw_text,
        twin_id=req.twin_id or "default_user",
    )
    return response
