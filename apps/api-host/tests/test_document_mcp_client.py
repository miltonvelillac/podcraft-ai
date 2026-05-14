import pytest

from api_host.clients.document_mcp_client import DocumentMcpClient


def test_document_client_extracts_mock_pdf_text() -> None:
    client = DocumentMcpClient()

    result = client.extract_text_from_pdf(
        filename="source.pdf",
        content=b"%PDF-1.7 mock content",
    )

    assert result.filename == "source.pdf"
    assert result.pages == 1
    assert result.text == "This is mocked text extracted from the uploaded PDF document."


def test_document_client_rejects_empty_pdf() -> None:
    client = DocumentMcpClient()

    with pytest.raises(ValueError, match="PDF file cannot be empty"):
        client.extract_text_from_pdf(filename="source.pdf", content=b"")


def test_document_client_rejects_unsupported_file_type() -> None:
    client = DocumentMcpClient()

    with pytest.raises(ValueError, match="Only PDF files are supported"):
        client.extract_text_from_pdf(filename="source.txt", content=b"not a pdf")


def test_document_client_cleans_extracted_text() -> None:
    client = DocumentMcpClient()

    result = client.clean_extracted_text("  line one\n\nline two\tline three  ")

    assert result == "line one line two line three"
