# Document MCP Server

MCP server responsible for document tools such as PDF text extraction, text cleaning, and document metadata.

## Current Tools

- `extract_text_from_pdf`
- `clean_extracted_text`
- `get_document_metadata`

The current implementation uses `pypdf` for PDF parsing and raises explicit `ValueError`
messages for invalid files, empty files, unsupported file types, and PDFs without extractable
text.
