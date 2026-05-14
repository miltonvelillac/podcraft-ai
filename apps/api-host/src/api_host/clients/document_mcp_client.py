from api_host.schemas.podcast_schemas import DocumentExtractionResult


class DocumentMcpClient:
    """Client boundary for the Document MCP Server.

    The current implementation is mocked. The real implementation will call document tools
    exposed by the Document MCP Server.
    """

    def extract_text_from_pdf(self, filename: str, content: bytes) -> DocumentExtractionResult:
        if not filename.lower().endswith(".pdf"):
            raise ValueError("Only PDF files are supported.")
        if not content:
            raise ValueError("PDF file cannot be empty.")

        extracted_text = self.clean_extracted_text(
            "This is mocked text extracted from the uploaded PDF document."
        )

        return DocumentExtractionResult(
            filename=filename,
            pages=1,
            text=extracted_text,
        )

    def clean_extracted_text(self, text: str) -> str:
        return " ".join(text.split())
