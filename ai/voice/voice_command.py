"""
Sahayak AI — Voice Command Processor
Routes voice commands through the existing Intent Engine.
Does NOT bypass the 7-stage pipeline.
"""
import logging
from typing import Optional, Dict, Any
from shared.schemas.models import VoiceCommand, AccessibilityTwin, LanguagePreference
from ai.voice.speech_to_text import SpeechToTextEngine
from ai.voice.text_to_speech import TextToSpeechEngine
from ai.intent.intent_engine import IntentEngine

logger = logging.getLogger(__name__)


class VoiceCommandProcessor:
    """
    Ties STT → Intent Engine → TTS into a coherent voice layer.
    Voice commands always flow through the existing Intent Engine.
    """

    def __init__(
        self,
        stt: Optional[SpeechToTextEngine] = None,
        tts: Optional[TextToSpeechEngine] = None,
    ):
        self.stt = stt or SpeechToTextEngine()
        self.tts = tts or TextToSpeechEngine()
        self.intent_engine = IntentEngine()

    def process(
        self,
        audio_bytes: Optional[bytes] = None,
        text_input: Optional[str] = None,
        twin: Optional[AccessibilityTwin] = None,
    ) -> Dict[str, Any]:
        """
        Full voice processing pipeline:
        Audio/Text → STT → Intent Engine → response payload.

        Args:
            audio_bytes: raw audio bytes
            text_input: direct text shortcut (skips STT)
            twin: user Accessibility Twin

        Returns:
            dict with voice_command, intent_analysis, tts_payload
        """
        language = "hi-IN" if (twin and twin.language.value == "Hindi") else "en-IN"

        # Step 1: STT
        voice_cmd = self.stt.transcribe(
            audio_bytes=audio_bytes,
            text_input=text_input,
            language=language,
        )

        if not voice_cmd.raw_text:
            return {
                "voice_command": voice_cmd.model_dump(),
                "intent_analysis": None,
                "error": "No speech or text detected",
            }

        # Step 2: Route through Intent Engine (not a bypass)
        intent_result = self.intent_engine.analyze_intent(
            query=voice_cmd.raw_text,
            twin=twin,
        )

        # Step 3: Prepare TTS acknowledgment
        task_type_obj = intent_result.get("task_type")
        intent_label = task_type_obj.value if task_type_obj else "UNKNOWN"
        intent_result["intent"] = intent_label
        
        ack_text = f"Processing: {voice_cmd.raw_text}"
        lang_pref = twin.language if twin else None
        tts_payload = self.tts.prepare(
            text=ack_text,
            language=lang_pref or LanguagePreference.ENGLISH,
        )

        return {
            "voice_command": voice_cmd.model_dump(),
            "intent_analysis": intent_result,
            "tts_payload": tts_payload,
        }
