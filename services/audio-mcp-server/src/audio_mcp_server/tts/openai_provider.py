import os
from pathlib import Path
from typing import Protocol

from audio_mcp_server.tts.provider import SynthesisRequest, SynthesisResult


DEFAULT_OPENAI_TTS_MODEL = "gpt-4o-mini-tts"
DEFAULT_OPENAI_TTS_VOICE = "coral"
DEFAULT_OPENAI_TTS_RESPONSE_FORMAT = "wav"
DEFAULT_OPENAI_TTS_INSTRUCTIONS = "Speak clearly in a warm podcast narration style."
OPENAI_VOICE_ALIASES = {
    "default": DEFAULT_OPENAI_TTS_VOICE,
    "studio": "nova",
    "briefing": "onyx",
}
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
        self._model = model or os.getenv("OPENAI_TTS_MODEL", DEFAULT_OPENAI_TTS_MODEL)
        self._voice = voice or os.getenv("OPENAI_TTS_VOICE", DEFAULT_OPENAI_TTS_VOICE)
        self._response_format = response_format or os.getenv(
            "OPENAI_TTS_RESPONSE_FORMAT",
            DEFAULT_OPENAI_TTS_RESPONSE_FORMAT,
        )
        self._instructions = instructions or os.getenv(
            "OPENAI_TTS_INSTRUCTIONS",
            DEFAULT_OPENAI_TTS_INSTRUCTIONS,
        )

    def synthesize(self, request: SynthesisRequest) -> SynthesisResult:
        request.output_dir.mkdir(parents=True, exist_ok=True)
        audio_path = request.output_dir / f"{request.podcast_id}.{self._response_format}"

        with self._client.audio.speech.with_streaming_response.create(
            model=self._model,
            voice=self._resolve_voice(request.voice),
            input=request.script,
            instructions=self._instructions,
            response_format=self._response_format,
        ) as response:
            response.stream_to_file(audio_path)

        return SynthesisResult(
            audio_path=audio_path,
            format=self._response_format,
            duration_seconds=request.duration_seconds,
        )

    def _resolve_voice(self, requested_voice: str) -> str:
        normalized = requested_voice.strip().lower()
        if not normalized:
            return self._voice
        if normalized in OPENAI_VOICE_ALIASES:
            return self._voice if normalized == "default" else OPENAI_VOICE_ALIASES[normalized]
        if normalized in OPENAI_VOICES:
            return normalized

        raise ValueError(f"Unsupported OpenAI TTS voice: {requested_voice}.")


def _build_openai_client() -> OpenAiClient:
    if not os.getenv("OPENAI_API_KEY"):
        raise ValueError("OPENAI_API_KEY is required when TTS_PROVIDER=openai.")

    try:
        from openai import OpenAI
    except ImportError as exc:
        raise RuntimeError("The openai package is required when TTS_PROVIDER=openai.") from exc

    return OpenAI()
