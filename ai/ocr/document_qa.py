"""
Sahayak AI — Document Question Answering
Grounded QA over extracted document content.
Does NOT invent information not present in the document.
Reuses the existing OCR/document parser pipeline.
"""
import re
from typing import Optional, Dict, Any, List
from shared.schemas.models import DocumentQuestion, DocumentAnswer
from ai.ocr.ocr_engine import DocumentOCREngine


# Map of question keywords to document field keys
QUESTION_FIELD_MAP = [
    (["deadline", "last date", "closing date", "submit by", "due date", "अंतिम"],
     "key_deadlines", "deadline"),
    (["fee", "application fee", "charge", "cost", "शुल्क"],
     "application_fee", "application fee"),
    (["document", "required", "proof", "certificate", "दस्तावेज"],
     "required_documents", "required documents"),
    (["eligible", "eligibility", "who can", "criteria", "पात्रता"],
     "eligibility_criteria", "eligibility criteria"),
    (["authority", "issued by", "ministry", "department", "जारीकर्ता"],
     "issuing_authority", "issuing authority"),
    (["title", "name", "scheme", "subject", "शीर्षक"],
     "document_title", "document title"),
    (["summary", "briefly", "what is", "tell me", "सारांश"],
     "simplified_summary_en", "summary"),
]


class DocumentQAEngine:
    """
    Answers natural-language questions about extracted document content.
    All answers are grounded in document data — fabrication is explicitly forbidden.
    """

    def __init__(self):
        self.ocr_engine = DocumentOCREngine()
        self._cached_doc: Optional[Dict[str, Any]] = None

    def load_document(
        self,
        image_bytes: Optional[bytes] = None,
        raw_text: Optional[str] = None,
        preloaded_doc: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Extract and cache document information.
        Accepts image bytes, raw text, or a preloaded document dict.
        """
        if preloaded_doc:
            self._cached_doc = preloaded_doc
        else:
            self._cached_doc = self.ocr_engine.extract_document_info(
                image_bytes=image_bytes,
                raw_text=raw_text,
            )
        return self._cached_doc

    def answer(self, question: DocumentQuestion) -> DocumentAnswer:
        """
        Answer a question grounded in the loaded document.

        Args:
            question: DocumentQuestion with question text

        Returns:
            DocumentAnswer - always grounded, never fabricated
        """
        if not self._cached_doc:
            return DocumentAnswer(
                question=question.question,
                answer="No document has been loaded. Please provide a document first.",
                confidence=0.0,
                found_in_document=False,
            )

        q_lower = question.question.lower()

        # First: try Gemini QA if API key is available
        gemini_answer = self._gemini_qa(question.question, self._cached_doc)
        if gemini_answer:
            return gemini_answer

        # Fallback: keyword-based field lookup
        for keywords, field_key, field_name in QUESTION_FIELD_MAP:
            if any(kw in q_lower for kw in keywords):
                value = self._cached_doc.get(field_key)
                if value:
                    if isinstance(value, list):
                        answer_text = ", ".join(str(v) for v in value)
                    else:
                        answer_text = str(value)
                    return DocumentAnswer(
                        question=question.question,
                        answer=answer_text,
                        source_snippet=answer_text[:200],
                        confidence=0.88,
                        found_in_document=True,
                    )

        return DocumentAnswer(
            question=question.question,
            answer="Information not found in document.",
            confidence=0.0,
            found_in_document=False,
        )

    def answer_batch(self, questions: List[DocumentQuestion]) -> List[DocumentAnswer]:
        """Answer multiple questions about the same document."""
        return [self.answer(q) for q in questions]

    def _gemini_qa(
        self, question: str, doc: Dict[str, Any]
    ) -> Optional[DocumentAnswer]:
        """Use Gemini to answer with document context as grounding."""
        import os, json
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            return None
        try:
            from google import genai
            client = genai.Client(api_key=api_key)
            doc_context = json.dumps(doc, ensure_ascii=False, indent=2)
            prompt = (
                f"You are answering a question strictly based on this document data:\n\n"
                f"{doc_context}\n\n"
                f"Question: {question}\n\n"
                "Rules:\n"
                "1. Answer ONLY based on the document data above.\n"
                "2. If the answer is not in the document, say 'Information not found in document.'\n"
                "3. Return JSON: {\"answer\": str, \"answer_hi\": str, \"source_snippet\": str, \"confidence\": float, \"found_in_document\": bool}\n"
                "4. Return ONLY raw JSON."
            )
            response = client.models.generate_content(model="gemini-2.5-flash", contents=[prompt])
            if response and response.text:
                txt = response.text.strip().lstrip("```json").rstrip("```").strip()
                parsed = json.loads(txt)
                return DocumentAnswer(
                    question=question,
                    answer=parsed.get("answer", "Information not found in document."),
                    answer_hi=parsed.get("answer_hi"),
                    source_snippet=parsed.get("source_snippet"),
                    confidence=float(parsed.get("confidence", 0.9)),
                    found_in_document=parsed.get("found_in_document", True),
                )
        except Exception as e:
            print(f"Gemini QA error: {e}")
        return None
