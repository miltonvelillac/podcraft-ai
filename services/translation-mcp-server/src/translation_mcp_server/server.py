from typing import Any

from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp.exceptions import ToolError

from podcraft_contracts import McpToolName, PayloadField
from translation_mcp_server.tools.language_detection import detect_language
from translation_mcp_server.tools.translate_text import translate_text as translate_text_tool
from translation_mcp_server.translation.errors import TranslationProviderError

mcp = FastMCP("PodCraft Translation MCP Server")


@mcp.tool(name=McpToolName.DETECT_LANGUAGE)
def detect_language_tool(text: str) -> dict[str, str | None]:
    """Detect the source language for text that may need translation."""
    return {PayloadField.SOURCE_LANGUAGE: detect_language(text)}


@mcp.tool(name=McpToolName.TRANSLATE_TEXT)
def translate_text_mcp_tool(
    source_text: str,
    target_language: str,
    source_language: str | None = None,
) -> dict[str, Any]:
    """Translate text for direct text-to-speech narration."""
    try:
        result = translate_text_tool(
            source_text=source_text,
            target_language=target_language,
            source_language=source_language,
        )
    except (ValueError, TranslationProviderError) as exc:
        raise ToolError(str(exc)) from exc

    return {PayloadField.TRANSLATED_TEXT: result.translated_text}


def run() -> None:
    mcp.run(transport="stdio")


if __name__ == "__main__":
    run()
