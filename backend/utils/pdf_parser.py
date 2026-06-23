"""PDF text extraction utilities."""
import logging

logger = logging.getLogger("finditai")


def extract_text_from_pdf(file_path: str) -> str:
    """Extract plain text from a PDF resume file."""
    from PyPDF2 import PdfReader

    reader = PdfReader(file_path)
    pages = []
    for page in reader.pages:
        text = page.extract_text()
        if text:
            pages.append(text)
    return "\n".join(pages)
