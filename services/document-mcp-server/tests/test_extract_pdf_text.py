import pytest

from document_mcp_server.tools.document_metadata import get_document_metadata
from document_mcp_server.tools.extract_pdf_text import extract_text_from_pdf


def test_extract_text_from_pdf_returns_clean_text() -> None:
    content = _build_pdf_with_text("Hello from PodCraft PDF")

    result = extract_text_from_pdf(filename="source.pdf", content=content)

    assert result.filename == "source.pdf"
    assert result.pages == 1
    assert "Hello from PodCraft PDF" in result.text


def test_extract_text_from_pdf_rejects_invalid_pdf() -> None:
    with pytest.raises(ValueError, match="Invalid PDF file"):
        extract_text_from_pdf(filename="source.pdf", content=b"not a pdf")


def test_extract_text_from_pdf_rejects_empty_pdf() -> None:
    with pytest.raises(ValueError, match="PDF file cannot be empty"):
        extract_text_from_pdf(filename="source.pdf", content=b"")


def test_extract_text_from_pdf_rejects_unsupported_file_type() -> None:
    with pytest.raises(ValueError, match="Only PDF files are supported"):
        extract_text_from_pdf(filename="source.txt", content=b"not a pdf")


def test_get_document_metadata_returns_page_count() -> None:
    content = _build_pdf_with_text("Metadata test")

    result = get_document_metadata(filename="source.pdf", content=content)

    assert result.filename == "source.pdf"
    assert result.pages == 1


def _build_pdf_with_text(text: str) -> bytes:
    escaped_text = text.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
    stream = f"BT /F1 24 Tf 72 720 Td ({escaped_text}) Tj ET".encode()
    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        (
            b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
            b"/Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>"
        ),
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
        b"<< /Length " + str(len(stream)).encode() + b" >>\nstream\n" + stream + b"\nendstream",
    ]

    pdf = b"%PDF-1.4\n"
    offsets = [0]
    for index, obj in enumerate(objects, start=1):
        offsets.append(len(pdf))
        pdf += f"{index} 0 obj\n".encode() + obj + b"\nendobj\n"

    xref_offset = len(pdf)
    pdf += f"xref\n0 {len(objects) + 1}\n".encode()
    pdf += b"0000000000 65535 f \n"
    for offset in offsets[1:]:
        pdf += f"{offset:010d} 00000 n \n".encode()

    pdf += (
        b"trailer\n"
        + f"<< /Size {len(objects) + 1} /Root 1 0 R >>\n".encode()
        + b"startxref\n"
        + str(xref_offset).encode()
        + b"\n%%EOF\n"
    )
    return pdf
