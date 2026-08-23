import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import logging
from app.rag.ingestion import IngestionPipeline

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)

def run_ingestion():
    raw_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data', 'raw'))
    os.makedirs(raw_dir, exist_ok=True)
    
    pipeline = IngestionPipeline(
        raw_dir=raw_dir,
        processed_dir=os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data', 'processed')),
        target_words=500,
        overlap_sentences=3
    )
    
    files = [f for f in os.listdir(raw_dir) if f.lower().endswith(".pdf")]
    
    if not files:
        logger.warning(f"No PDF files found in {raw_dir}")
        return
        
    results = []
    
    for file in files:
        try:
            result = pipeline.process_document(file, subject="Science", grade=8, language="English")
            results.append(result)
        except Exception as e:
            logger.error(f"Skipping {file} due to error: {e}")
            
    if results:
        pipeline.write_output(results)
        
        total_docs = len(results)
        total_pages = sum(r["pages_processed"] for r in results)
        total_chunks = sum(r["chunks_created"] for r in results)
        empty_pages = sum(r["empty_pages"] for r in results)
        
        print("\n==================================================")
        print("KNOWLEDGE INGESTION COMPLETE")
        print("==================================================")
        print(f"Documents processed: {total_docs}")
        print(f"Pages processed: {total_pages}")
        print(f"Chunks created: {total_chunks}")
        print(f"Empty pages skipped: {empty_pages}")
        print(f"Output: data/processed/knowledge_chunks.jsonl")
        print("==================================================")

if __name__ == "__main__":
    run_ingestion()
