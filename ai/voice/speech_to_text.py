"""
Sahayak AI — Speech-to-Text Abstraction
Provider-agnostic STT adapter supporting English and Hindi.
Default: offline keyword fallback. Optional: Google Speech API.
"""
import re
import logging
from typing import Optional, Dict, Any
from shared.schemas.models import VoiceCommand

logger = logging.getLogger(__name__)


class STTProvider:
    """Base interface for STT providers."""
    def transcribe(self, audio_bytes: bytes, language: str = "en-IN") -> str:
        raise NotImplementedError


class HeuristicSTTProvider(STTProvider):
    """Offline heuristic STT for testing and fallback."""
    def transcribe(self, audio_bytes: bytes, language: str = "en-IN") -> str:
        # In a real device, this would decode audio. For demo, return a placeholder.
        return "[speech input]"


class SpeechToTextEngine:
    """
    Converts audio bytes to a VoiceCommand.
    Flows through the Intent Engine (not a standalone assistant).
    """

    def __init__(self, provider: Optional[STTProvider] = None):
        self._provider = provider or HeuristicSTTProvider()

    def transcribe(
        self,
        audio_bytes: Optional[bytes] = None,
        text_input: Optional[str] = None,
        language: str = "en-IN",
    ) -> VoiceCommand:
        """
        Convert audio bytes or direct text input to a VoiceCommand.

        Args:
            audio_bytes: raw audio bytes (WAV/OGG)
            text_input: if provided, skip STT and use directly
            language: BCP-47 language tag ('en-IN', 'hi-IN')

        Returns:
            VoiceCommand with raw_text ready for Intent Engine
        """
        if text_input is not None:
            raw_text = text_input.strip()
            source = "text_input"
        elif audio_bytes:
            try:
                raw_text = self._provider.transcribe(audio_bytes, language)
                source = "stt"
            except Exception as e:
                logger.warning(f"STT transcription failed: {e}")
                raw_text = ""
                source = "stt_failed"
        else:
            raw_text = ""
            source = "empty"

        lang_label = "Hindi" if language.startswith("hi") else "English"
        return VoiceCommand(
            raw_text=raw_text,
            language=lang_label,
            confidence=0.95 if text_input else 0.80,
            source=source,
        )
