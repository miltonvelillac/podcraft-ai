from typing import Any

from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp.exceptions import ToolError

from document_mcp_server.tools.clean_text import clean_extracted_text as clean_text_tool
from document_mcp_server.tools.document_metadata import get_document_metadata as metadata_tool
from document_mcp_server.tools.extract_pdf_text import extract_text_from_pdf as extract_pdf_text_tool
from document_mcp_server.utils.payload_encoding import decode_base64_content

mcp = FastMCP("PodCraft Document MCP Server")


@mcp.tool(name="extract_text_from_pdf")
def extract_text_from_pdf_tool(filename: str, content_base64: str) -> dict[str, Any]:
    """Extract clean text from a base64-encoded PDF document."""
    content = _decode_base64_pdf(content_base64)

    try:
        result = extract_pdf_text_tool(filename=filename, content=content)
    except ValueError as exc:
        raise ToolError(str(exc)) from exc

    return {
        "filename": result.filename,
        "pages": result.pages,
        "text": result.text,
    }


@mcp.tool(name="clean_extracted_text")
def clean_extracted_text_tool(text: str) -> str:
    """Normalize whitespace in extracted document text."""
    return clean_text_tool(text)


@mcp.tool(name="get_document_metadata")
def get_document_metadata_tool(filename: str, content_base64: str) -> dict[str, Any]:
    """Return basic metadata for a base64-encoded PDF document."""
    content = _decode_base64_pdf(content_base64)

    try:
        result = metadata_tool(filename=filename, content=content)
    except ValueError as exc:
        raise ToolError(str(exc)) from exc

    return {
        "filename": result.filename,
        "pages": result.pages,
    }


def run() -> None:
    mcp.run(transport="stdio")


def _decode_base64_pdf(content_base64: str) -> bytes:
    try:
        return decode_base64_content(content_base64)
    except ValueError as exc:
        raise ToolError("PDF content must be valid base64.") from exc


if __name__ == "__main__":
    run()
