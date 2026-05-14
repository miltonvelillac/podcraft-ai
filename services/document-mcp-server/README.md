# Document MCP Server

MCP server responsible for document tools such as PDF text extraction, text cleaning, and document metadata.

## Current Tools

- `extract_text_from_pdf`
- `clean_extracted_text`
- `get_document_metadata`

The current implementation uses `pypdf` for PDF parsing and raises explicit `ValueError`
messages for invalid files, empty files, unsupported file types, and PDFs without extractable
text.

## MCP Server

The server exposes document tools through the MCP Python SDK using STDIO transport:

```bash
uv run python services/document-mcp-server/src/document_mcp_server/server.py
```

Tool inputs that include PDF content use base64 strings because MCP messages are JSON-RPC
payloads and should not carry raw bytes directly.
