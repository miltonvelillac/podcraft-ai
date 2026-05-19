from pathlib import Path

import pytest

from audio_mcp_server.tts import (
    MockTtsProvider,
    SynthesisRequest,
    SynthesisResult,
    build_tts_provider,
)
from audio_mcp_server.tools.audio_metadata import get_audio_metadata
from audio_mcp_server.tools.generate_audio import generate_audio_from_text
from audio_mcp_server.tools.save_audio_file import save_audio_file
from podcraft_contracts import AiProvider


def test_generate_audio_from_text_writes_mock_audio_file(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("TTS_PROVIDER", AiProvider.MOCK)
    result = generate_audio_from_text(
        podcast_id="podcast-test",
        script="Welcome to today's episode.",
        voice="default",
        duration_seconds=120,
        output_dir=tmp_path,
    )

    audio_path = tmp_path / "podcast-test.wav"
    assert result.audio_url == "/generated/audio/podcast-test.wav"
    assert result.format == "wav"
    assert result.duration_seconds == 120
    assert audio_path.exists()
    assert audio_path.read_bytes().startswith(b"RIFF")


def test_generate_audio_from_text_uses_injected_tts_provider(tmp_path: Path) -> None:
    provider = FakeTtsProvider()

    result = generate_audio_from_text(
        podcast_id="podcast-provider",
        script="Provider generated audio.",
        voice="default",
        language="es",
        duration_seconds=30,
        output_dir=tmp_path,
        provider=provider,
    )

    assert provider.request is not None
    assert provider.request.podcast_id == "podcast-provider"
    assert provider.request.script == "Provider generated audio."
    assert provider.request.language == "es"
    assert result.audio_url == "/generated/audio/podcast-provider.fake"
    assert result.format == "fake"
    assert result.duration_seconds == 7


def test_generate_audio_from_text_rejects_empty_script(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="Script cannot be empty"):
        generate_audio_from_text(
            podcast_id="podcast-test",
            script=" ",
            voice="default",
            duration_seconds=120,
            output_dir=tmp_path,
        )


def test_save_audio_file_writes_base64_content(tmp_path: Path) -> None:
    result = save_audio_file(
        podcast_id="podcast-saved",
        content_base64="YWJj",
        output_dir=tmp_path,
    )

    assert result == "/generated/audio/podcast-saved.wav"
    assert (tmp_path / "podcast-saved.wav").read_bytes() == b"abc"


def test_get_audio_metadata_returns_file_details(tmp_path: Path) -> None:
    audio_path = tmp_path / "podcast-test.wav"
    audio_path.write_bytes(b"abc")

    result = get_audio_metadata(str(audio_path))

    assert result.filename == "podcast-test.wav"
    assert result.format == "wav"
    assert result.size_bytes == 3


def test_build_tts_provider_defaults_to_mock(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("TTS_PROVIDER", AiProvider.MOCK)

    result = build_tts_provider()

    assert isinstance(result, MockTtsProvider)


def test_build_tts_provider_rejects_unsupported_provider(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("TTS_PROVIDER", "unknown")

    with pytest.raises(ValueError, match="Unsupported TTS_PROVIDER: unknown"):
        build_tts_provider()


class FakeTtsProvider:
    def __init__(self) -> None:
        self.request: SynthesisRequest | None = None

    def synthesize(self, request: SynthesisRequest) -> SynthesisResult:
        self.request = request
        audio_path = request.output_dir / f"{request.podcast_id}.fake"
        audio_path.write_bytes(b"fake audio")
        return SynthesisResult(
            audio_path=audio_path,
            format="fake",
            duration_seconds=7,
        )
