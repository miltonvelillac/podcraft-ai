import json
import os
import sys
from pathlib import Path
from typing import Any

from mcp.client.session import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client
from mcp.types import CallToolResult

from api_host.clients.errors import McpExternalServiceError, McpToolInputError
from api_host.schemas.podcast_schemas import PodcastLanguage
from podcraft_contracts import McpToolName, PayloadField


class TranslationMcpClient:
    """Client boundary for the Translation MCP Server.

    This client uses MCP over STDIO to call language and translation tools.
    """

    def __init__(self, project_root: Path | None = None) -> None:
        self._project_root = project_root or _find_project_root(Path(__file__).resolve())
        self._translation_server_script = (
            self._project_root
            / "services"
            / "translation-mcp-server"
            / "src"
            / "translation_mcp_server"
            / "server.py"
        )
        self._translation_server_src = (
            self._project_root / "services" / "translation-mcp-server" / "src"
        )

    async def detect_language(self, text: str) -> PodcastLanguage | None:
        result = await self._call_tool(
            name=McpToolName.DETECT_LANGUAGE,
            arguments={PayloadField.TEXT: text},
        )
        payload = _extract_structured_payload(result)
        language = payload.get(PayloadField.SOURCE_LANGUAGE)
        if language is None:
            return None
        return PodcastLanguage(str(language))

    async def translate_text(
        self,
        source_text: str,
        target_language: PodcastLanguage,
        source_language: PodcastLanguage | None = None,
    ) -> str:
        arguments = {
            PayloadField.SOURCE_TEXT: source_text,
            PayloadField.TARGET_LANGUAGE: target_language.value,
        }
        if source_language is not None:
            arguments[PayloadField.SOURCE_LANGUAGE] = source_language.value

        result = await self._call_tool(
            name=McpToolName.TRANSLATE_TEXT,
            arguments=arguments,
        )
        payload = _extract_structured_payload(result)
        return str(payload[PayloadField.TRANSLATED_TEXT])

    async def _call_tool(self, name: str, arguments: dict[str, Any]) -> CallToolResult:
        server_params = StdioServerParameters(
            command=sys.executable,
            args=[str(self._translation_server_script)],
            cwd=str(self._project_root),
            env={
                **os.environ,
                "PYTHONPATH": str(self._translation_server_src),
            },
        )

        async with stdio_client(server_params) as (read_stream, write_stream):
            async with ClientSession(read_stream, write_stream) as session:
                await session.initialize()
                result = await session.call_tool(name, arguments)

        if result.isError:
            message = _extract_text_payload(result)
            friendly_message = _to_friendly_error_message(message)
            if _is_external_service_error(message):
                raise McpExternalServiceError(friendly_message)
            raise McpToolInputError(friendly_message)

        return result


def _extract_structured_payload(result: CallToolResult) -> dict[str, Any]:
    if isinstance(result.structuredContent, dict):
        return result.structuredContent

    text = _extract_text_payload(result)
    try:
        payload = json.loads(text)
    except json.JSONDecodeError as exc:
        raise ValueError("Translation MCP Server returned invalid JSON.") from exc

    if not isinstance(payload, dict):
        raise ValueError("Translation MCP Server returned an invalid payload.")

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
        "OpenAI translation authentication failed",
        "OpenAI translation rate limit exceeded",
        "OpenAI translation is temporarily unavailable",
        "OpenAI translation failed",
        "OpenAI translation returned empty text",
    )
    return any(marker in message for marker in external_markers)


def _to_friendly_error_message(message: str) -> str:
    if "OPENAI_API_KEY is required" in message:
        return (
            "Translation is not configured. Set OPENAI_API_KEY or use "
            "TRANSLATION_PROVIDER=mock."
        )
    if "Unsupported TRANSLATION_PROVIDER" in message:
        return "Unsupported translation provider. Use mock or openai."
    if "OpenAI translation authentication failed" in message:
        return "Translation provider authentication failed. Check OPENAI_API_KEY."
    if "OpenAI translation rate limit exceeded" in message:
        return "Translation provider rate limit exceeded. Wait a moment and try again."
    if "OpenAI translation is temporarily unavailable" in message:
        return "Translation provider is temporarily unavailable. Try again later."
    if "OpenAI translation returned empty text" in message:
        return "Translation provider returned empty text. Try again with clearer input."
    if "OpenAI translation rejected the request" in message:
        return "Translation provider rejected the request. Check translation model settings."
    if "OpenAI translation failed" in message:
        return "Translation provider failed. Try again."

    return message
