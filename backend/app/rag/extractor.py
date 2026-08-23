import logging
from typing import Generator, Dict, Any
from pypdf import PdfReader

logger = logging.getLogger(__name__)

def extract_pdf_pages(file_path: str) -> Generator[Dict[str, Any], None, None]:
    """
    Yields extracted text page by page from a PDF file.
    Returns dictionaries containing the page number and text.
    """
    try:
        reader = PdfReader(file_path)
        for i, page in enumerate(reader.pages):
            text = page.extract_text()
            if text:
                yield {
                    "page": i + 1,
                    "text": text
                }
            else:
                yield {
                    "page": i + 1,
                    "text": ""
                }
    except Exception as e:
        logger.error(f"Failed to extract text from {file_path}: {e}")
        raise
