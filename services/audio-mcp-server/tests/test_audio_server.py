import pytest
from mcp.server.fastmcp.exceptions import ToolError

import audio_mcp_server.server as server_module
from audio_mcp_server.tts.errors import TtsAuthenticationError
from audio_mcp_server.server import (
    generate_audio_from_text_tool,
    get_audio_metadata_tool,
    save_audio_file_mcp_tool,
)
from podcraft_contracts import AiProvider, GeneratedAssetName, PayloadField


def test_generate_audio_from_text_tool_returns_audio_result(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("TTS_PROVIDER", AiProvider.MOCK)

    result = generate_audio_from_text_tool(
        podcast_id="podcast-server-test",
        script="Welcome to today's episode.",
        voice="default",
        duration_seconds=120,
    )

    assert result == {
        "audio_url": "/generated/audio/podcast-server-test.wav",
        "format": "wav",
        "duration_seconds": 120,
    }


def test_save_audio_file_tool_returns_audio_url() -> None:
    result = save_audio_file_mcp_tool(
        podcast_id="podcast-server-saved",
        content_base64="YWJj",
    )

    assert result == {
        "audio_url": "/generated/audio/podcast-server-saved.wav",
        "format": "wav",
    }


def test_get_audio_metadata_tool_returns_file_details(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("TTS_PROVIDER", AiProvider.MOCK)

    generate_audio_from_text_tool(
        podcast_id="podcast-server-metadata",
        script="Welcome to today's episode.",
        voice="default",
        duration_seconds=120,
    )

    metadata_audio = GeneratedAssetName.PODCAST_SERVER_METADATA_AUDIO
    result = get_audio_metadata_tool(f"generated/audio/{metadata_audio}")

    assert result[PayloadField.FILENAME] == metadata_audio
    assert result[PayloadField.FORMAT] == "wav"
    assert result[PayloadField.SIZE_BYTES] > 0


def test_audio_tools_reject_invalid_base64() -> None:
    with pytest.raises(ToolError, match="Audio content must be valid base64"):
        save_audio_file_mcp_tool(
            podcast_id="podcast-invalid",
            content_base64="not base64",
        )


def test_generate_audio_tool_returns_clean_tts_error(monkeypatch: pytest.MonkeyPatch) -> None:
    def raise_tts_error(**_kwargs):
        raise TtsAuthenticationError("OpenAI TTS authentication failed.")

    monkeypatch.setattr(server_module, "generate_audio_tool", raise_tts_error)

    with pytest.raises(ToolError, match="OpenAI TTS authentication failed"):
        generate_audio_from_text_tool(
            podcast_id="podcast-error",
            script="Welcome to today's episode.",
            voice="default",
            duration_seconds=120,
        )
