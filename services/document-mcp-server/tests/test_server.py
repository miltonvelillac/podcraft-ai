import base64

import pytest
from mcp.server.fastmcp.exceptions import ToolError

from document_mcp_server.server import (
    clean_extracted_text_tool,
    extract_text_from_pdf_tool,
    get_document_metadata_tool,
)
from pdf_test_utils import build_pdf_with_text


def test_extract_text_from_pdf_tool_returns_document_result() -> None:
    content_base64 = _to_base64(build_pdf_with_text("MCP server PDF text"))

    result = extract_text_from_pdf_tool(filename="source.pdf", content_base64=content_base64)

    assert result["filename"] == "source.pdf"
    assert result["pages"] == 1
    assert "MCP server PDF text" in str(result["text"])


def test_clean_extracted_text_tool_normalizes_text() -> None:
    result = clean_extracted_text_tool("  line one\tline two\n\n\nline three  ")

    assert result == "line one line two\n\nline three"


def test_get_document_metadata_tool_returns_page_count() -> None:
    content_base64 = _to_base64(build_pdf_with_text("Metadata over MCP"))

    result = get_document_metadata_tool(filename="source.pdf", content_base64=content_base64)

    assert result == {"filename": "source.pdf", "pages": 1}


def test_pdf_tools_reject_invalid_base64() -> None:
    with pytest.raises(ToolError, match="PDF content must be valid base64"):
        extract_text_from_pdf_tool(filename="source.pdf", content_base64="not base64")


def _to_base64(content: bytes) -> str:
    return base64.b64encode(content).decode("ascii")
