"""
Sahayak AI — Document & Reading Schema Models
Defines structured data contracts for Real Document Understanding,
Document Q&A, and Document-to-Task Conversion.
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime


class DocumentSummary(BaseModel):
    title: str
    authority: Optional[str] = "Authority"
    deadlines: List[str] = Field(default_factory=list)
    required_documents: List[str] = Field(default_factory=list)
    application_fee: Optional[str] = "NIL"
    action_required: Optional[str] = "Review and apply"
    spoken_summary: str
    display_summary: str
    summary_en: str
    summary_hi: str
    language: str = "English"
    raw_ocr_elements_count: int = 0
    haptic_cue: Optional[str] = None
    document_id: Optional[str] = None


class DocumentQuestion(BaseModel):
    question: str = Field(description="User question in natural language (Hindi, English, Hinglish)")
    document_id: Optional[str] = Field(default="default_doc", description="Active document or session ID")
    document_context: Optional[str] = Field(default=None, description="Extracted text or document context")
    twin_id: Optional[str] = "default_user"
    language: Optional[str] = "English"


class DocumentAnswer(BaseModel):
    question: str
    answer: str
    document_id: Optional[str] = "default_doc"
    spoken_answer: Optional[str] = None
    supporting_extracted_info: List[str] = Field(default_factory=list)
    confidence: float = Field(default=0.92, ge=0.0, le=1.0)
    source_section: Optional[str] = Field(default=None, description="e.g. 'Eligibility', 'Deadlines', 'Fee'")
    related_actions: List[str] = Field(default_factory=list)
    language: str = "English"
    answer_hi: Optional[str] = None
    source_snippet: Optional[str] = None
    found_in_document: bool = True


class DocumentTask(BaseModel):
    task_id: str
    title: str
    description: str
    deadline: Optional[str] = None
    required_documents: List[str] = Field(default_factory=list)
    status: str = Field(default="PENDING", description="'PENDING', 'IN_PROGRESS', 'COMPLETED', 'BLOCKED'")
    priority: str = Field(default="HIGH", description="'HIGH', 'MEDIUM', 'LOW'")
    action_type: str = Field(default="SUBMISSION", description="'SUBMISSION', 'VERIFICATION', 'DOCUMENT_GATHERING', 'PAYMENT'")
    source_document_id: Optional[str] = None
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())


class DocumentTaskExtractionRequest(BaseModel):
    document_id: Optional[str] = None
    raw_text: Optional[str] = None
    twin_id: Optional[str] = "default_user"


class DocumentTaskExtractionResponse(BaseModel):
    document_id: str
    document_title: str
    tasks: List[DocumentTask] = Field(default_factory=list)
    total_tasks: int = 0
    primary_deadline: Optional[str] = None
    spoken_summary: str = ""
