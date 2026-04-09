"""Audio service for speech-to-text (Groq Whisper) and text-to-speech (OpenAI)."""

import io
import base64
from typing import Optional
from pathlib import Path
import aiohttp
from groq import Groq
from openai import AsyncOpenAI

from app.core.config import settings


class AudioService:
    """Service for handling audio transcription and synthesis."""

    def __init__(self):
        """Initialize audio clients."""
        self.groq_client = Groq(api_key=settings.GROQ_API_KEY)
        self.openai_client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

    async def speech_to_text(
        self,
        audio_file,
        language: str = "en",
        prompt: Optional[str] = None
    ) -> dict:
        """
        Convert audio to text using Groq Whisper API.
        
        Args:
            audio_file: Audio file object (bytes or file-like)
            language: Language code (e.g., 'en', 'es', 'fr')
            prompt: Optional prompt to guide transcription
            
        Returns:
            dict with 'text', 'language', 'duration'
        """
        try:
            # Groq Whisper transcription
            if isinstance(audio_file, bytes):
                audio_bytes = io.BytesIO(audio_file)
            else:
                audio_bytes = audio_file

            # Convert to tuple format for Groq API
            transcript_data = (
                "audio.wav",
                audio_bytes,
                "audio/wav"
            )

            transcript = self.groq_client.audio.transcriptions.create(
                file=transcript_data,
                model="whisper-large-v3-turbo",
                language=language,
                prompt=prompt,
            )

            return {
                "text": transcript.text,
                "language": language,
                "success": True
            }
        except Exception as e:
            return {
                "text": "",
                "success": False,
                "error": str(e)
            }

    async def text_to_speech(
        self,
        text: str,
        voice: str = "alloy",
        speed: float = 1.0,
        language: str = "en"
    ) -> dict:
        """
        Convert text to speech using OpenAI TTS API.
        
        Args:
            text: Text to synthesize
            voice: Voice preset (alloy, echo, fable, onyx, nova, shimmer)
            speed: Playback speed (0.25-4.0, default 1.0)
            language: Language code (for reference, OpenAI uses voice presets)
            
        Returns:
            dict with 'audio_base64', 'voice', 'speed'
        """
        try:
            # Validate speed
            speed = max(0.25, min(4.0, speed))

            # Generate speech using OpenAI
            response = await self.openai_client.audio.speech.create(
                model="tts-1-hd",  # High quality
                voice=voice,
                input=text,
                speed=speed,
                response_format="mp3"
            )

            # Convert to bytes and then base64
            audio_bytes = await response.aread() if hasattr(response, 'aread') else response.content
            audio_base64 = base64.b64encode(audio_bytes).decode('utf-8')

            return {
                "audio_base64": audio_base64,
                "voice": voice,
                "speed": speed,
                "success": True
            }
        except Exception as e:
            return {
                "audio_base64": "",
                "success": False,
                "error": str(e)
            }

    def get_available_voices(self) -> list:
        """Get list of available TTS voices."""
        return [
            {"id": "alloy", "name": "Alloy (Neutral)", "lang": "en"},
            {"id": "echo", "name": "Echo (Male)", "lang": "en"},
            {"id": "fable", "name": "Fable (Storyteller)", "lang": "en"},
            {"id": "onyx", "name": "Onyx (Deep Male)", "lang": "en"},
            {"id": "nova", "name": "Nova (Female)", "lang": "en"},
            {"id": "shimmer", "name": "Shimmer (Bright Female)", "lang": "en"},
        ]

    def get_available_languages(self) -> list:
        """Get list of supported languages for STT."""
        return [
            {"code": "en", "name": "English"},
            {"code": "es", "name": "Spanish"},
            {"code": "fr", "name": "French"},
            {"code":"hi", "name": "Hindi"},
            {"code": "de", "name": "German"},
            {"code": "it", "name": "Italian"},
            {"code": "pt", "name": "Portuguese"},
            {"code": "ja", "name": "Japanese"},
            {"code": "zh", "name": "Chinese"},
            {"code": "ru", "name": "Russian"},
            {"code": "ar", "name": "Arabic"},
            {"code": "hi", "name": "Hindi"},
            {"code": "ko", "name": "Korean"},
        ]


# Singleton instance
audio_service: Optional[AudioService] = None


def get_audio_service() -> AudioService:
    """Get or create audio service singleton."""
    global audio_service
    if audio_service is None:
        audio_service = AudioService()
    return audio_service
