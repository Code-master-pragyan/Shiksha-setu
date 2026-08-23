import os
import json
import pytest
from app.rag.cleaner import clean_text
from app.rag.chunker import semantic_chunk_document, extract_metadata
from app.rag.citations import generate_chunk_id, build_metadata
from app.rag.ingestion import IngestionPipeline

def test_clean_text():
    raw = "This   is \t some text.\n\n\n\nIt has spacing issues."
    cleaned = clean_text(raw)
    assert cleaned == "This is some text.\n\nIt has spacing issues."

def test_extract_metadata():
    line = "Chapter 2 - The Invisible Living World"
    c_num, c_title, c_sec = extract_metadata(line, None, None, None)
    assert c_num == 2
    assert c_title == "The Invisible Living World"
    
    line = "2.1 What Is a Cell?"
    c_num, c_title, c_sec = extract_metadata(line, 2, "Test", None)
    assert c_num == 2
    assert c_title == "Test"
    assert c_sec == "2.1 What Is a Cell?"

def test_semantic_chunk_document():
    # Generate long string of sentences
    text = " ".join([f"This is sentence {i}." for i in range(200)])
    pages = [{"page": 1, "text": text}]
    
    chunks = semantic_chunk_document(pages, target_words=100, overlap_sentences=2)
    
    assert len(chunks) > 1
    # Check if page metadata is preserved
    assert chunks[0]["page_start"] == 1
    assert chunks[0]["page_end"] == 1
    
def test_citation_metadata():
    chunk_id = generate_chunk_id("doc1", 5, 6, 2)
    assert chunk_id == "doc1_p5-6_c2"
    
    chunk_id_same_page = generate_chunk_id("doc1", 5, 5, 2)
    assert chunk_id_same_page == "doc1_p5_c2"
    
    meta = build_metadata(
        chunk_id=chunk_id,
        document_id="doc1",
        source_file="file.pdf",
        text="Sample",
        page_start=5,
        page_end=6,
        subject="Science",
        grade=8
    )
    assert meta["chunk_id"] == chunk_id
    assert meta["page_start"] == 5
    assert meta["page_end"] == 6
    assert meta["subject"] == "Science"

def test_pipeline_idempotency(tmp_path):
    raw_dir = tmp_path / "raw"
    processed_dir = tmp_path / "processed"
    raw_dir.mkdir()
    processed_dir.mkdir()
    
    pipeline = IngestionPipeline(raw_dir=str(raw_dir), processed_dir=str(processed_dir))
    
    results = [{
        "document_id": "test",
        "filename": "test.pdf",
        "title": "Title",
        "chapter_number": 1,
        "chapter": "Title",
        "pages_processed": 1,
        "empty_pages": 0,
        "chunks_created": 1,
        "subject": "Science",
        "grade": 8,
        "language": "English",
        "chunks_data": [{"chunk_id": "test_p1_c0", "text": "hello"}]
    }]
    
    # Run once
    pipeline.write_output(results)
    
    jsonl_path = processed_dir / "knowledge_chunks.jsonl"
    with open(jsonl_path, 'r') as f:
        lines = f.readlines()
    assert len(lines) == 1
    
    # Run twice
    pipeline.write_output(results)
    
    with open(jsonl_path, 'r') as f:
        lines = f.readlines()
    assert len(lines) == 1
