"""
Sahayak AI — Text-to-Speech Abstraction
Provider-agnostic TTS adapter. Returns SSML/text ready for device TTS engine.
Core logic does NOT call device TTS directly — delegates to client layer.
"""
from typing import Optional, Dict, Any
from shared.schemas.models import LanguagePreference


class TextToSpeechEngine:
    """
    Prepares TTS output payload.
    Actual audio rendering is handled by the Flutter/Web client.
    Backend returns structured speech payload.
    """

    SPEED_SETTINGS = {
        "slow": 0.75,
        "normal": 1.0,
        "fast": 1.25,
    }

    def prepare(
        self,
        text: str,
        language: LanguagePreference = LanguagePreference.ENGLISH,
        speed: str = "normal",
        emphasize_words: Optional[list] = None,
    ) -> Dict[str, Any]:
        """
        Prepare a structured TTS payload for the client.
        """
        lang_code = "hi-IN" if language == LanguagePreference.HINDI else "en-IN"
        speed_rate = self.SPEED_SETTINGS.get(speed, 1.0)

        # Build basic SSML
        ssml_text = text
        if emphasize_words:
            for word in emphasize_words:
                ssml_text = ssml_text.replace(word, f'<emphasis level="strong">{word}</emphasis>')

        ssml = (
            f'<speak><prosody rate="{speed_rate}">{ssml_text}</prosody></speak>'
        )

        return {
            "text": text,
            "ssml": ssml,
            "lang_code": lang_code,
            "speed_rate": speed_rate,
            "language": language.value,
        }
