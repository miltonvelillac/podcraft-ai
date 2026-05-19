import os
from pathlib import Path
from typing import Protocol

from audio_mcp_server.tts.errors import (
    TtsAuthenticationError,
    TtsConfigurationError,
    TtsProviderError,
    TtsRateLimitError,
    TtsServiceError,
)
from audio_mcp_server.tts.provider import SynthesisRequest, SynthesisResult
from podcraft_contracts import AUDIO_VOICE_ALIASES, AudioFormat, EnvVar, LANGUAGE_NAMES


DEFAULT_OPENAI_TTS_MODEL = "gpt-4o-mini-tts"
DEFAULT_OPENAI_TTS_VOICE = "coral"
DEFAULT_OPENAI_TTS_RESPONSE_FORMAT = AudioFormat.WAV
DEFAULT_OPENAI_TTS_INSTRUCTIONS = "Speak clearly in a warm podcast narration style."
OPENAI_VOICES = {
    "alloy",
    "ash",
    "ballad",
    "cedar",
    "coral",
    "echo",
    "fable",
    "marin",
    "nova",
    "onyx",
    "sage",
    "shimmer",
    "verse",
}


class StreamingSpeechResponse(Protocol):
    def __enter__(self) -> "StreamingSpeechResponse": ...

    def __exit__(self, exc_type: object, exc_value: object, traceback: object) -> None: ...

    def stream_to_file(self, file: str | Path) -> None: ...


class SpeechCreateClient(Protocol):
    def create(
        self,
        *,
        model: str,
        voice: str,
        input: str,
        instructions: str,
        response_format: str,
    ) -> StreamingSpeechResponse: ...


class SpeechClient(Protocol):
    with_streaming_response: SpeechCreateClient


class AudioClient(Protocol):
    speech: SpeechClient


class OpenAiClient(Protocol):
    audio: AudioClient


class OpenAiTtsProvider:
    def __init__(
        self,
        client: OpenAiClient | None = None,
        model: str | None = None,
        voice: str | None = None,
        response_format: str | None = None,
        instructions: str | None = None,
    ) -> None:
        self._client = client or _build_openai_client()
        self._model = model or os.getenv(EnvVar.OPENAI_TTS_MODEL, DEFAULT_OPENAI_TTS_MODEL)
        self._voice = voice or os.getenv(EnvVar.OPENAI_TTS_VOICE, DEFAULT_OPENAI_TTS_VOICE)
        self._response_format = response_format or os.getenv(
            EnvVar.OPENAI_TTS_RESPONSE_FORMAT,
            DEFAULT_OPENAI_TTS_RESPONSE_FORMAT.value,
        )
        self._instructions = instructions or os.getenv(
            EnvVar.OPENAI_TTS_INSTRUCTIONS,
            DEFAULT_OPENAI_TTS_INSTRUCTIONS,
        )

    def synthesize(self, request: SynthesisRequest) -> SynthesisResult:
        request.output_dir.mkdir(parents=True, exist_ok=True)
        audio_path = request.output_dir / f"{request.podcast_id}.{self._response_format}"

        try:
            with self._client.audio.speech.with_streaming_response.create(
                model=self._model,
                voice=self._resolve_voice(request.voice),
                input=request.script,
                instructions=self._build_instructions(request.language),
                response_format=self._response_format,
            ) as response:
                response.stream_to_file(audio_path)
        except TtsProviderError:
            raise
        except Exception as exc:
            raise _to_tts_error(exc) from exc

        return SynthesisResult(
            audio_path=audio_path,
            format=self._response_format,
            duration_seconds=request.duration_seconds,
        )

    def _resolve_voice(self, requested_voice: str) -> str:
        normalized = requested_voice.strip().lower()
        if not normalized:
            return self._voice
        if normalized in AUDIO_VOICE_ALIASES:
            return self._voice if normalized == "default" else AUDIO_VOICE_ALIASES[normalized]
        if normalized in OPENAI_VOICES:
            return normalized

        raise TtsConfigurationError(f"Unsupported OpenAI TTS voice: {requested_voice}.")

    def _build_instructions(self, language: str) -> str:
        normalized = language.strip().lower()
        language_name = LANGUAGE_NAMES.get(normalized)
        if language_name is None:
            raise TtsConfigurationError(f"Unsupported TTS language: {language}.")

        return f"{self._instructions} Speak in {language_name}."


def _build_openai_client() -> OpenAiClient:
    if not os.getenv(EnvVar.OPENAI_API_KEY):
        raise TtsConfigurationError(
            f"{EnvVar.OPENAI_API_KEY} is required when {EnvVar.TTS_PROVIDER}=openai."
        )

    try:
        from openai import OpenAI
    except ImportError as exc:
        raise TtsConfigurationError(
            f"The openai package is required when {EnvVar.TTS_PROVIDER}=openai."
        ) from exc

    return OpenAI()


def _to_tts_error(exc: Exception) -> Exception:
    status_code = getattr(exc, "status_code", None)

    if status_code == 401:
        return TtsAuthenticationError(
            f"OpenAI TTS authentication failed. Check {EnvVar.OPENAI_API_KEY} in your .env file."
        )
    if status_code == 429:
        return TtsRateLimitError(
            "OpenAI TTS rate limit exceeded. Wait a moment and try again."
        )
    if isinstance(status_code, int) and status_code >= 500:
        return TtsServiceError("OpenAI TTS is temporarily unavailable. Try again later.")
    if isinstance(status_code, int) and 400 <= status_code < 500:
        return TtsConfigurationError(
            "OpenAI TTS rejected the request. Check model, voice, and audio settings."
        )

    return TtsServiceError("OpenAI TTS failed while generating audio.")
