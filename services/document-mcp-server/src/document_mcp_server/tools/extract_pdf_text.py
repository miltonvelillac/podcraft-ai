from dataclasses import dataclass
from io import BytesIO

from pypdf import PdfReader
from pypdf.errors import PdfReadError

from document_mcp_server.tools.clean_text import clean_extracted_text


@dataclass(frozen=True)
class PdfExtractionResult:
    filename: str
    pages: int
    text: str


def extract_text_from_pdf(filename: str, content: bytes) -> PdfExtractionResult:
    if not filename.lower().endswith(".pdf"):
        raise ValueError("Only PDF files are supported.")
    if not content:
        raise ValueError("PDF file cannot be empty.")

    try:
        reader = PdfReader(BytesIO(content))
    except PdfReadError as exc:
        raise ValueError("Invalid PDF file.") from exc

    page_text = [page.extract_text() or "" for page in reader.pages]
    text = clean_extracted_text("\n\n".join(page_text))
    if not text:
        raise ValueError("PDF has no extractable text.")

    return PdfExtractionResult(
        filename=filename,
        pages=len(reader.pages),
        text=text,
    )
