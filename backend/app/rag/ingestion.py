import os
import json
import logging
from datetime import datetime, timezone
from typing import List, Dict, Any

from app.rag.extractor import extract_pdf_pages
from app.rag.cleaner import clean_text
from app.rag.chunker import semantic_chunk_document
from app.rag.citations import generate_chunk_id, build_metadata

logger = logging.getLogger(__name__)

class IngestionPipeline:
    def __init__(
        self,
        raw_dir: str = "data/raw",
        processed_dir: str = "data/processed",
        target_words: int = 500,
        overlap_sentences: int = 3
    ):
        self.raw_dir = raw_dir
        self.processed_dir = processed_dir
        
        os.makedirs(self.raw_dir, exist_ok=True)
        os.makedirs(self.processed_dir, exist_ok=True)
        
        self.target_words = target_words
        self.overlap_sentences = overlap_sentences
        
    def process_document(
        self, 
        filename: str, 
        subject: str = "Science", 
        grade: int = 8, 
        language: str = "English"
    ) -> Dict[str, Any]:
        """Processes a single PDF document into chunks."""
        file_path = os.path.join(self.raw_dir, filename)
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Document {filename} not found.")
            
        document_id = os.path.splitext(filename)[0]
        logger.info(f"Starting processing for {filename} (ID: {document_id})")
        
        pages_processed = 0
        empty_pages = 0
        
        cleaned_pages = []
        
        try:
            for page_data in extract_pdf_pages(file_path):
                pages_processed += 1
                page_num = page_data["page"]
                raw_text = page_data["text"]
                
                cleaned = clean_text(raw_text)
                if not cleaned.strip():
                    empty_pages += 1
                    continue
                    
                cleaned_pages.append({
                    "page": page_num,
                    "text": cleaned
                })
                
            raw_chunks = semantic_chunk_document(cleaned_pages, self.target_words, self.overlap_sentences)
            
            chunks_data = []
            
            # For the document title, we'll use the chapter title of the first chunk if available
            doc_title = None
            doc_chapter_number = None
            doc_chapter = None
            for c in raw_chunks:
                if c["chapter"]:
                    doc_title = c["chapter"]
                    doc_chapter_number = c["chapter_number"]
                    doc_chapter = c["chapter"]
                    break
            
            for i, c_data in enumerate(raw_chunks):
                chunk_id = generate_chunk_id(document_id, c_data["page_start"], c_data["page_end"], i)
                metadata = build_metadata(
                    chunk_id=chunk_id,
                    document_id=document_id,
                    source_file=filename,
                    text=c_data["text"],
                    page_start=c_data["page_start"],
                    page_end=c_data["page_end"],
                    title=doc_title,
                    chapter_number=c_data["chapter_number"],
                    chapter=c_data["chapter"],
                    section=c_data["section"],
                    subject=subject,
                    grade=grade,
                    language=language
                )
                chunks_data.append(metadata)
                
        except Exception as e:
            logger.error(f"Failed to process {filename}: {e}")
            raise
            
        logger.info(f"Completed {filename}: {pages_processed} pages, {len(chunks_data)} chunks.")
        
        return {
            "document_id": document_id,
            "filename": filename,
            "title": doc_title,
            "chapter_number": doc_chapter_number,
            "chapter": doc_chapter,
            "pages_processed": pages_processed,
            "empty_pages": empty_pages,
            "chunks_created": len(chunks_data),
            "chunks_data": chunks_data,
            "subject": subject,
            "grade": grade,
            "language": language
        }
        
    def write_output(self, results: List[Dict[str, Any]]):
        """Writes processed chunks to JSONL and updates the manifest."""
        output_file = os.path.join(self.processed_dir, "knowledge_chunks.jsonl")
        manifest_file = os.path.join(self.processed_dir, "manifest.json")
        
        with open(output_file, 'w', encoding='utf-8') as f:
            for result in results:
                for chunk in result["chunks_data"]:
                    f.write(json.dumps(chunk) + "\n")
                    
        manifest_data = []
        for result in results:
            manifest_data.append({
                "filename": result["filename"],
                "document_id": result["document_id"],
                "title": result["title"],
                "chapter_number": result["chapter_number"],
                "chapter": result["chapter"],
                "processed_at": datetime.now(timezone.utc).isoformat(),
                "pages": result["pages_processed"],
                "chunks": result["chunks_created"],
                "subject": result["subject"],
                "grade": result["grade"],
                "language": result["language"],
                "status": "success"
            })
            
        with open(manifest_file, 'w', encoding='utf-8') as f:
            json.dump(manifest_data, f, indent=2)
