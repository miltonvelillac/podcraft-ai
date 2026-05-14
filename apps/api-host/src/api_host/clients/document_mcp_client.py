from api_host.schemas.podcast_schemas import DocumentExtractionResult
from document_mcp_server.tools.clean_text import clean_extracted_text as clean_text_tool
from document_mcp_server.tools.extract_pdf_text import extract_text_from_pdf as extract_pdf_text_tool


class DocumentMcpClient:
    """Client boundary for the Document MCP Server.

    This currently calls the document tool implementation locally. Later this boundary can
    switch to a real MCP transport without changing the podcast pipeline.
    """

    def extract_text_from_pdf(self, filename: str, content: bytes) -> DocumentExtractionResult:
        extraction_result = extract_pdf_text_tool(filename=filename, content=content)

        return DocumentExtractionResult(
            filename=extraction_result.filename,
            pages=extraction_result.pages,
            text=extraction_result.text,
        )

    def clean_extracted_text(self, text: str) -> str:
        return clean_text_tool(text)
