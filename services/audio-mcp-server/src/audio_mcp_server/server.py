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

mcp = FastMCP("PodCraft Audio MCP Server")


@mcp.tool(name="generate_audio_from_text")
def generate_audio_from_text_tool(
    podcast_id: str,
    script: str,
    voice: str,
    duration_seconds: int,
    language: str = "en",
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
        "audio_url": result.audio_url,
        "format": result.format,
        "duration_seconds": result.duration_seconds,
    }


@mcp.tool(name="save_audio_file")
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
        "audio_url": audio_url,
        "format": SUPPORTED_FORMAT,
    }


@mcp.tool(name="get_audio_metadata")
def get_audio_metadata_tool(audio_path: str) -> dict[str, Any]:
    """Return basic metadata for an audio file."""
    try:
        result = metadata_tool(audio_path=audio_path)
    except ValueError as exc:
        raise ToolError(str(exc)) from exc

    return {
        "filename": result.filename,
        "format": result.format,
        "size_bytes": result.size_bytes,
    }


def run() -> None:
    mcp.run(transport="stdio")


if __name__ == "__main__":
    run()
