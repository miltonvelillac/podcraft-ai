from dataclasses import dataclass
from io import BytesIO

from pypdf import PdfReader
from pypdf.errors import PdfReadError


@dataclass(frozen=True)
class DocumentMetadata:
    filename: str
    pages: int


def get_document_metadata(filename: str, content: bytes) -> DocumentMetadata:
    if not filename.lower().endswith(".pdf"):
        raise ValueError("Only PDF files are supported.")
    if not content:
        raise ValueError("PDF file cannot be empty.")

    try:
        reader = PdfReader(BytesIO(content))
    except PdfReadError as exc:
        raise ValueError("Invalid PDF file.") from exc

    return DocumentMetadata(filename=filename, pages=len(reader.pages))
