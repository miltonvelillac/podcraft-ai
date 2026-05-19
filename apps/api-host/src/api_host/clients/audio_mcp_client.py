import json
import os
import sys
from pathlib import Path
from typing import Any

from mcp.client.session import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client
from mcp.types import CallToolResult

from api_host.clients.errors import McpExternalServiceError, McpToolInputError
from api_host.schemas.podcast_schemas import AudioGenerationResult


class AudioMcpClient:
    """Client boundary for the Audio MCP Server.

    This client uses MCP over STDIO to call the audio server tools.
    """

    def __init__(self, project_root: Path | None = None) -> None:
        self._project_root = project_root or _find_project_root(Path(__file__).resolve())
        self._audio_server_script = (
            self._project_root
            / "services"
            / "audio-mcp-server"
            / "src"
            / "audio_mcp_server"
            / "server.py"
        )
        self._audio_server_src = self._project_root / "services" / "audio-mcp-server" / "src"

    async def generate_audio_from_text(
        self,
        podcast_id: str,
        script: str,
        voice: str,
        language: str,
        duration_seconds: int,
    ) -> AudioGenerationResult:
        result = await self._call_tool(
            name="generate_audio_from_text",
            arguments={
                "podcast_id": podcast_id,
                "script": script,
                "voice": voice,
                "language": language,
                "duration_seconds": duration_seconds,
            },
        )
        payload = _extract_structured_payload(result)

        return AudioGenerationResult(
            audio_url=str(payload["audio_url"]),
            format=str(payload["format"]),
            duration_seconds=int(payload["duration_seconds"]),
        )

    async def _call_tool(self, name: str, arguments: dict[str, Any]) -> CallToolResult:
        server_params = StdioServerParameters(
            command=sys.executable,
            args=[str(self._audio_server_script)],
            cwd=str(self._project_root),
            env={
                **os.environ,
                "PYTHONPATH": str(self._audio_server_src),
            },
        )

        async with stdio_client(server_params) as (read_stream, write_stream):
            async with ClientSession(read_stream, write_stream) as session:
                await session.initialize()
                result = await session.call_tool(name, arguments)

        if result.isError:
            message = _extract_text_payload(result)
            if _is_external_service_error(message):
                raise McpExternalServiceError(message)
            raise McpToolInputError(message)

        return result


def _extract_structured_payload(result: CallToolResult) -> dict[str, Any]:
    if isinstance(result.structuredContent, dict):
        return result.structuredContent

    text = _extract_text_payload(result)
    try:
        payload = json.loads(text)
    except json.JSONDecodeError as exc:
        raise ValueError("Audio MCP Server returned invalid JSON.") from exc

    if not isinstance(payload, dict):
        raise ValueError("Audio MCP Server returned an invalid payload.")

    return payload


def _extract_text_payload(result: CallToolResult) -> str:
    text_parts = [
        text
        for content in result.content
        if (text := getattr(content, "text", None)) is not None
    ]
    return "\n".join(text_parts).strip()


def _find_project_root(start: Path) -> Path:
    for path in (start, *start.parents):
        if (path / "pyproject.toml").exists():
            return path

    raise RuntimeError("Could not locate project root.")


def _is_external_service_error(message: str) -> bool:
    external_markers = (
        "OpenAI TTS authentication failed",
        "OpenAI TTS rate limit exceeded",
        "OpenAI TTS is temporarily unavailable",
        "OpenAI TTS failed",
    )
    return any(marker in message for marker in external_markers)
