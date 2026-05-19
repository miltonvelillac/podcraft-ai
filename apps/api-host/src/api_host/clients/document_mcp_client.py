import base64
import json
import sys
from pathlib import Path
from typing import Any

from mcp.client.session import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client
from mcp.types import CallToolResult

from api_host.schemas.podcast_schemas import DocumentExtractionResult
from podcraft_contracts import McpToolName, PayloadField


class DocumentMcpClient:
    """Client boundary for the Document MCP Server.

    This client uses MCP over STDIO to call the document server tools.
    """

    def __init__(self, project_root: Path | None = None) -> None:
        self._project_root = project_root or _find_project_root(Path(__file__).resolve())
        self._document_server_script = (
            self._project_root
            / "services"
            / "document-mcp-server"
            / "src"
            / "document_mcp_server"
            / "server.py"
        )
        self._document_server_src = (
            self._project_root / "services" / "document-mcp-server" / "src"
        )

    async def extract_text_from_pdf(
        self,
        filename: str,
        content: bytes,
    ) -> DocumentExtractionResult:
        content_base64 = base64.b64encode(content).decode("ascii")
        result = await self._call_tool(
            name=McpToolName.EXTRACT_TEXT_FROM_PDF,
            arguments={
                PayloadField.FILENAME: filename,
                PayloadField.CONTENT_BASE64: content_base64,
            },
        )
        payload = _extract_structured_payload(result)

        return DocumentExtractionResult(
            filename=str(payload[PayloadField.FILENAME]),
            pages=int(payload[PayloadField.PAGES]),
            text=str(payload[PayloadField.TEXT]),
        )

    async def clean_extracted_text(self, text: str) -> str:
        result = await self._call_tool(
            name=McpToolName.CLEAN_EXTRACTED_TEXT,
            arguments={PayloadField.TEXT: text},
        )
        return _extract_text_payload(result)

    async def _call_tool(self, name: str, arguments: dict[str, Any]) -> CallToolResult:
        server_params = StdioServerParameters(
            command=sys.executable,
            args=[str(self._document_server_script)],
            cwd=str(self._project_root),
            env={"PYTHONPATH": str(self._document_server_src)},
        )

        async with stdio_client(server_params) as (read_stream, write_stream):
            async with ClientSession(read_stream, write_stream) as session:
                await session.initialize()
                result = await session.call_tool(name, arguments)

        if result.isError:
            raise ValueError(_extract_text_payload(result))

        return result


def _extract_structured_payload(result: CallToolResult) -> dict[str, Any]:
    if isinstance(result.structuredContent, dict):
        return result.structuredContent

    text = _extract_text_payload(result)
    try:
        payload = json.loads(text)
    except json.JSONDecodeError as exc:
        raise ValueError("Document MCP Server returned invalid JSON.") from exc

    if not isinstance(payload, dict):
        raise ValueError("Document MCP Server returned an invalid payload.")

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
