import pytest
from mcp.server.fastmcp.exceptions import ToolError

from audio_mcp_server.server import (
    generate_audio_from_text_tool,
    get_audio_metadata_tool,
    save_audio_file_mcp_tool,
)


def test_generate_audio_from_text_tool_returns_audio_result() -> None:
    result = generate_audio_from_text_tool(
        podcast_id="podcast-server-test",
        script="Welcome to today's episode.",
        voice="default",
        duration_seconds=120,
    )

    assert result == {
        "audio_url": "/generated/audio/podcast-server-test.mp3",
        "format": "mp3",
        "duration_seconds": 120,
    }


def test_save_audio_file_tool_returns_audio_url() -> None:
    result = save_audio_file_mcp_tool(
        podcast_id="podcast-server-saved",
        content_base64="YWJj",
    )

    assert result == {
        "audio_url": "/generated/audio/podcast-server-saved.mp3",
        "format": "mp3",
    }


def test_get_audio_metadata_tool_returns_file_details() -> None:
    generate_audio_from_text_tool(
        podcast_id="podcast-server-metadata",
        script="Welcome to today's episode.",
        voice="default",
        duration_seconds=120,
    )

    result = get_audio_metadata_tool("generated/audio/podcast-server-metadata.mp3")

    assert result["filename"] == "podcast-server-metadata.mp3"
    assert result["format"] == "mp3"
    assert result["size_bytes"] > 0


def test_audio_tools_reject_invalid_base64() -> None:
    with pytest.raises(ToolError, match="Audio content must be valid base64"):
        save_audio_file_mcp_tool(
            podcast_id="podcast-invalid",
            content_base64="not base64",
        )
