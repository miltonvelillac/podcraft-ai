from typing import Any

from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp.exceptions import ToolError

from audio_mcp_server.tts.errors import TtsProviderError
from audio_mcp_server.tools.audio_metadata import get_audio_metadata as metadata_tool
from audio_mcp_server.tools.generate_audio import (
    SUPPORTED_FORMAT,
    generate_audio_from_text as generate_audio_tool,
)
from audio_mcp_server.tools.save_audio_file import save_audio_file as save_audio_file_tool
from podcraft_contracts import DEFAULT_LANGUAGE, McpToolName, PayloadField

mcp = FastMCP("PodCraft Audio MCP Server")


@mcp.tool(name=McpToolName.GENERATE_AUDIO_FROM_TEXT)
def generate_audio_from_text_tool(
    podcast_id: str,
    script: str,
    voice: str,
    duration_seconds: int,
    language: str = DEFAULT_LANGUAGE,
) -> dict[str, Any]:
    """Generate a mocked audio file from podcast script text."""
    try:
        result = generate_audio_tool(
            podcast_id=podcast_id,
            script=script,
            voice=voice,
            language=language,
            duration_seconds=duration_seconds,
        )
    except (ValueError, TtsProviderError) as exc:
        raise ToolError(str(exc)) from exc

    return {
        PayloadField.AUDIO_URL: result.audio_url,
        PayloadField.FORMAT: result.format,
        PayloadField.DURATION_SECONDS: result.duration_seconds,
    }


@mcp.tool(name=McpToolName.SAVE_AUDIO_FILE)
def save_audio_file_mcp_tool(podcast_id: str, content_base64: str) -> dict[str, str]:
    """Save base64-encoded audio content to the generated audio directory."""
    try:
        audio_url = save_audio_file_tool(
            podcast_id=podcast_id,
            content_base64=content_base64,
        )
    except ValueError as exc:
        raise ToolError(str(exc)) from exc

    return {
        PayloadField.AUDIO_URL: audio_url,
        PayloadField.FORMAT: SUPPORTED_FORMAT,
    }


@mcp.tool(name=McpToolName.GET_AUDIO_METADATA)
def get_audio_metadata_tool(audio_path: str) -> dict[str, Any]:
    """Return basic metadata for an audio file."""
    try:
        result = metadata_tool(audio_path=audio_path)
    except ValueError as exc:
        raise ToolError(str(exc)) from exc

    return {
        PayloadField.FILENAME: result.filename,
        PayloadField.FORMAT: result.format,
        PayloadField.SIZE_BYTES: result.size_bytes,
    }


def run() -> None:
    mcp.run(transport="stdio")


if __name__ == "__main__":
    run()
