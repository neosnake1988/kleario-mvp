from pathlib import Path

import fitz


class PdfTextExtractionError(Exception):
    """Raised when a PDF cannot be opened or read as a text PDF."""


def extract_text_from_pdf(file_path: Path) -> str:
    """Extract text from a readable PDF without OCR.

    The MVP only supports PDFs that already contain text. Scanned documents
    may return an empty string until OCR is introduced later.
    """
    try:
        parts: list[str] = []
        with fitz.open(file_path) as document:
            for page in document:
                parts.append(page.get_text())
        extracted_text = "\n".join(parts).strip()
        if not extracted_text:
            raise PdfTextExtractionError("No readable text found in PDF.")
        return extracted_text
    except Exception as exc:
        if isinstance(exc, PdfTextExtractionError):
            raise
        raise PdfTextExtractionError("The PDF could not be read.") from exc
