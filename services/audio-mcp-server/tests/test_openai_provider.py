from pathlib import Path

import pytest

import audio_mcp_server.tts.factory as factory_module
from audio_mcp_server.tts.errors import (
    TtsAuthenticationError,
    TtsConfigurationError,
    TtsRateLimitError,
    TtsServiceError,
)
from audio_mcp_server.tts import OpenAiTtsProvider, SynthesisRequest
from podcraft_contracts import AiProvider


def test_openai_tts_provider_streams_audio_to_file(tmp_path: Path) -> None:
    client = FakeOpenAiClient()
    provider = OpenAiTtsProvider(
        client=client,
        model="gpt-4o-mini-tts",
        voice="coral",
        response_format="wav",
        instructions="Speak clearly.",
    )

    result = provider.synthesize(
        SynthesisRequest(
            podcast_id="podcast-openai",
            script="Welcome to the generated episode.",
            voice="default",
            language="en",
            duration_seconds=120,
            output_dir=tmp_path,
        )
    )

    audio_path = tmp_path / "podcast-openai.wav"
    assert result.audio_path == audio_path
    assert result.format == "wav"
    assert result.duration_seconds == 120
    assert audio_path.read_bytes() == b"openai audio"
    assert client.create_kwargs == {
        "model": "gpt-4o-mini-tts",
        "voice": "coral",
        "input": "Welcome to the generated episode.",
        "instructions": "Speak clearly. Speak in English.",
        "response_format": "wav",
    }


def test_openai_tts_provider_uses_requested_voice(tmp_path: Path) -> None:
    client = FakeOpenAiClient()
    provider = OpenAiTtsProvider(client=client, voice="coral")

    provider.synthesize(
        SynthesisRequest(
            podcast_id="podcast-voice",
            script="Voice override test.",
            voice="nova",
            language="en",
            duration_seconds=60,
            output_dir=tmp_path,
        )
    )

    assert client.create_kwargs is not None
    assert client.create_kwargs["voice"] == "nova"


def test_openai_tts_provider_maps_frontend_voice_alias(tmp_path: Path) -> None:
    client = FakeOpenAiClient()
    provider = OpenAiTtsProvider(client=client, voice="coral")

    provider.synthesize(
        SynthesisRequest(
            podcast_id="podcast-alias",
            script="Voice alias test.",
            voice="briefing",
            language="en",
            duration_seconds=60,
            output_dir=tmp_path,
        )
    )

    assert client.create_kwargs is not None
    assert client.create_kwargs["voice"] == "onyx"


def test_openai_tts_provider_rejects_unsupported_voice(tmp_path: Path) -> None:
    provider = OpenAiTtsProvider(client=FakeOpenAiClient())

    with pytest.raises(TtsConfigurationError, match="Unsupported OpenAI TTS voice"):
        provider.synthesize(
            SynthesisRequest(
                podcast_id="podcast-bad-voice",
                script="Bad voice test.",
                voice="robot",
                language="en",
                duration_seconds=60,
                output_dir=tmp_path,
            )
        )


def test_openai_tts_provider_adds_selected_language_to_instructions(tmp_path: Path) -> None:
    client = FakeOpenAiClient()
    provider = OpenAiTtsProvider(client=client, instructions="Narrate naturally.")

    provider.synthesize(
        SynthesisRequest(
            podcast_id="podcast-spanish",
            script="Contenido del episodio.",
            voice="default",
            language="es",
            duration_seconds=60,
            output_dir=tmp_path,
        )
    )

    assert client.create_kwargs is not None
    assert client.create_kwargs["instructions"] == "Narrate naturally. Speak in Spanish."


def test_openai_tts_provider_rejects_unsupported_language(tmp_path: Path) -> None:
    provider = OpenAiTtsProvider(client=FakeOpenAiClient())

    with pytest.raises(TtsConfigurationError, match="Unsupported TTS language"):
        provider.synthesize(
            SynthesisRequest(
                podcast_id="podcast-language",
                script="Language test.",
                voice="default",
                language="fr",
                duration_seconds=60,
                output_dir=tmp_path,
            )
        )


def test_build_tts_provider_selects_openai(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    provider = object()
    monkeypatch.setenv("TTS_PROVIDER", AiProvider.OPENAI)
    monkeypatch.setattr(factory_module, "OpenAiTtsProvider", lambda: provider)

    result = factory_module.build_tts_provider()

    assert result is provider


def test_openai_tts_provider_requires_api_key(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    with pytest.raises(TtsConfigurationError, match="OPENAI_API_KEY is required"):
        OpenAiTtsProvider()


@pytest.mark.parametrize(
    ("status_code", "expected_error", "expected_message"),
    [
        (401, TtsAuthenticationError, "OpenAI TTS authentication failed"),
        (429, TtsRateLimitError, "OpenAI TTS rate limit exceeded"),
        (500, TtsServiceError, "OpenAI TTS is temporarily unavailable"),
        (400, TtsConfigurationError, "OpenAI TTS rejected the request"),
    ],
)
def test_openai_tts_provider_translates_openai_errors(
    tmp_path: Path,
    status_code: int,
    expected_error: type[Exception],
    expected_message: str,
) -> None:
    provider = OpenAiTtsProvider(client=FakeOpenAiClient(error=FakeOpenAiError(status_code)))

    with pytest.raises(expected_error, match=expected_message):
        provider.synthesize(
            SynthesisRequest(
                podcast_id="podcast-error",
                script="Error test.",
                voice="default",
                language="en",
                duration_seconds=60,
                output_dir=tmp_path,
            )
        )


class FakeOpenAiClient:
    def __init__(self, error: Exception | None = None) -> None:
        self.create_kwargs: dict[str, str] | None = None
        self.audio = FakeAudioClient(self, error=error)


class FakeAudioClient:
    def __init__(self, client: FakeOpenAiClient, error: Exception | None = None) -> None:
        self.speech = FakeSpeechClient(client, error=error)


class FakeSpeechClient:
    def __init__(self, client: FakeOpenAiClient, error: Exception | None = None) -> None:
        self.with_streaming_response = FakeStreamingSpeechClient(client, error=error)


class FakeStreamingSpeechClient:
    def __init__(self, client: FakeOpenAiClient, error: Exception | None = None) -> None:
        self._client = client
        self._error = error

    def create(self, **kwargs: str) -> "FakeStreamingSpeechResponse":
        self._client.create_kwargs = kwargs
        if self._error is not None:
            raise self._error
        return FakeStreamingSpeechResponse()


class FakeStreamingSpeechResponse:
    def __enter__(self) -> "FakeStreamingSpeechResponse":
        return self

    def __exit__(self, exc_type: object, exc_value: object, traceback: object) -> None:
        return None

    def stream_to_file(self, file: str | Path) -> None:
        Path(file).write_bytes(b"openai audio")


class FakeOpenAiError(Exception):
    def __init__(self, status_code: int) -> None:
        super().__init__("OpenAI error")
        self.status_code = status_code
