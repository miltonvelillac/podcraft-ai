from pathlib import Path

import pytest

import audio_mcp_server.tts.factory as factory_module
from audio_mcp_server.tts import OpenAiTtsProvider, SynthesisRequest


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
        "instructions": "Speak clearly.",
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
            duration_seconds=60,
            output_dir=tmp_path,
        )
    )

    assert client.create_kwargs is not None
    assert client.create_kwargs["voice"] == "onyx"


def test_openai_tts_provider_rejects_unsupported_voice(tmp_path: Path) -> None:
    provider = OpenAiTtsProvider(client=FakeOpenAiClient())

    with pytest.raises(ValueError, match="Unsupported OpenAI TTS voice"):
        provider.synthesize(
            SynthesisRequest(
                podcast_id="podcast-bad-voice",
                script="Bad voice test.",
                voice="robot",
                duration_seconds=60,
                output_dir=tmp_path,
            )
        )


def test_build_tts_provider_selects_openai(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    provider = object()
    monkeypatch.setenv("TTS_PROVIDER", "openai")
    monkeypatch.setattr(factory_module, "OpenAiTtsProvider", lambda: provider)

    result = factory_module.build_tts_provider()

    assert result is provider


def test_openai_tts_provider_requires_api_key(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    with pytest.raises(ValueError, match="OPENAI_API_KEY is required"):
        OpenAiTtsProvider()


class FakeOpenAiClient:
    def __init__(self) -> None:
        self.create_kwargs: dict[str, str] | None = None
        self.audio = FakeAudioClient(self)


class FakeAudioClient:
    def __init__(self, client: FakeOpenAiClient) -> None:
        self.speech = FakeSpeechClient(client)


class FakeSpeechClient:
    def __init__(self, client: FakeOpenAiClient) -> None:
        self.with_streaming_response = FakeStreamingSpeechClient(client)


class FakeStreamingSpeechClient:
    def __init__(self, client: FakeOpenAiClient) -> None:
        self._client = client

    def create(self, **kwargs: str) -> "FakeStreamingSpeechResponse":
        self._client.create_kwargs = kwargs
        return FakeStreamingSpeechResponse()


class FakeStreamingSpeechResponse:
    def __enter__(self) -> "FakeStreamingSpeechResponse":
        return self

    def __exit__(self, exc_type: object, exc_value: object, traceback: object) -> None:
        return None

    def stream_to_file(self, file: str | Path) -> None:
        Path(file).write_bytes(b"openai audio")
