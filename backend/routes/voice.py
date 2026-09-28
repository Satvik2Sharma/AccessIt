"""
Sahayak AI — Voice Assistant & Speech Routes
Endpoints for Voice Command Processing, Multimodal Intent Extraction, and TTS Audio Contracts.
"""

from typing import Optional, Dict, Any
from fastapi import APIRouter, HTTPException
from shared.schemas.models import (
    VoiceCommandRequest,
    VoiceCommandResponse,
    TTSRequest,
    TTSResponse,
)
from backend.services.pipeline_service import pipeline_service

router = APIRouter(tags=["Voice Assistant"])


@router.post("/voice/command", response_model=VoiceCommandResponse)
async def process_voice_command(req: VoiceCommandRequest):
    """
    Processes transcribed voice query or speech input, classifies accessibility task intent,
    and returns localized spoken & display responses with haptic feedback instructions.
    """
    if not req.transcript or not req.transcript.strip():
        raise HTTPException(status_code=400, detail="Voice transcript cannot be empty.")

    result = pipeline_service.process_voice_command(
        transcript=req.transcript,
        twin_id=req.twin_id or "default_user",
        session_id=req.active_session_id,
    )
    return result


@router.post("/voice/tts", response_model=TTSResponse)
async def generate_tts_contract(req: TTSRequest):
    """
    Text-to-Speech contract returning phonetic SSML structure and synthesized audio parameters.
    """
    # Contract response for mobile client audio player / speech synthesizer
    ssml = f"<speak><prosody rate='{req.speed}' pitch='{req.pitch}'>{req.text}</prosody></speak>"
    duration = max(1.0, round(len(req.text.split()) * 0.4 / req.speed, 2))

    return TTSResponse(
        text=req.text,
        language=req.language.value,
        audio_url=None,  # Handled on-device or via local TTS engine
        phonetic_ssml=ssml,
        duration_estimate_sec=duration,
    )
