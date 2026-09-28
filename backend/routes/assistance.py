"""
Sahayak AI — Multimodal Assistance Routes
Endpoints for generating unified Voice + Visual + Haptic instructions tailored to the user's Accessibility Twin.
"""

from fastapi import APIRouter
from shared.schemas.models import (
    MultimodalAssistanceRequest,
    AssistanceResponse,
    AssistancePriority,
    LanguagePreference,
)
from backend.services.pipeline_service import pipeline_service
from backend.services.response_service import response_service

router = APIRouter(tags=["Multimodal Assistance"])


@router.post("/assistance/multimodal", response_model=AssistanceResponse)
async def generate_multimodal_assistance(req: MultimodalAssistanceRequest):
    """
    Synthesizes unified multimodal assistance instruction (voice audio text, visual card, haptic pattern, priority)
    adapted to the user's active Accessibility Twin and input context.
    """
    twin = pipeline_service.twin_service.get_twin(req.twin_id or "default_user")
    is_hindi = twin.language == LanguagePreference.HINDI

    spoken_text = (
        f"निर्देश: {req.current_input}। कृपया स्क्रीन पर दिए गए बटन को दबाएं या बोलकर उत्तर दें।"
        if is_hindi else
        f"Instruction: {req.current_input}. Tap the highlighted card or speak your response."
    )

    visual_card = {
        "title": "Sahayak Assistant Guidance",
        "detail": req.current_input,
        "high_contrast": twin.visual.high_contrast,
        "large_text": twin.visual.large_text,
        "accent_color": "#2563EB",
    }

    return response_service.format_multimodal_response(
        text_content=req.current_input,
        spoken_content=spoken_text,
        twin=twin,
        visual_card=visual_card,
        haptic_pattern="DOUBLE_PULSE_CENTER",
        haptic_intensity=twin.haptics.intensity if twin.haptics.enabled else "MEDIUM",
        priority=AssistancePriority.NORMAL,
        next_action="AWAIT_USER_INPUT",
        session_id=req.task_id,
    )
