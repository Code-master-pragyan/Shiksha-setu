import uuid
from typing import Dict, Any, Optional

def generate_chunk_id(document_id: str, page_start: int, page_end: int, chunk_index: int) -> str:
    """
    Generates a deterministic unique ID for a chunk.
    Example: doc123_p12-13_c0, doc123_p12_c1
    """
    if page_start == page_end:
        return f"{document_id}_p{page_start}_c{chunk_index}"
    return f"{document_id}_p{page_start}-{page_end}_c{chunk_index}"

def build_metadata(
    chunk_id: str,
    document_id: str,
    source_file: str,
    text: str,
    page_start: int,
    page_end: int,
    title: Optional[str] = None,
    chapter_number: Optional[int] = None,
    chapter: Optional[str] = None,
    section: Optional[str] = None,
    subject: Optional[str] = None,
    grade: Optional[int] = None,
    language: str = "English"
) -> Dict[str, Any]:
    """
    Constructs the citation metadata dictionary for a chunk.
    """
    return {
        "chunk_id": chunk_id,
        "document_id": document_id,
        "source_file": source_file,
        "title": title,
        "chapter_number": chapter_number,
        "chapter": chapter,
        "section": section,
        "page_start": page_start,
        "page_end": page_end,
        "subject": subject,
        "grade": grade,
        "language": language,
        "text": text
    }
