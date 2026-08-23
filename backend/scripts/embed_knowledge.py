import os
import sys
import json
import logging
from pathlib import Path
from dotenv import load_dotenv

# Add backend directory to sys.path
backend_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(backend_dir))

from app.core.config import settings
from app.db.database import SessionLocal, get_db
from app.services.embeddings.gemini_embedding_provider import GeminiEmbeddingProvider
from app.services.embeddings.embedding_service import EmbeddingService

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

def main():
    load_dotenv()
    
    api_key = settings.GEMINI_API_KEY or os.environ.get("GEMINI_API_KEY")
    if not api_key:
        logger.error("GEMINI_API_KEY is not set. Exiting.")
        sys.exit(1)

    db_url = settings.DATABASE_URL or os.environ.get("DATABASE_URL")
    if not db_url:
        logger.error("DATABASE_URL is not set. Exiting.")
        sys.exit(1)
        
    model_name = settings.GEMINI_EMBEDDING_MODEL or os.environ.get("GEMINI_EMBEDDING_MODEL", "text-embedding-004")
    
    try:
        provider = GeminiEmbeddingProvider(api_key=api_key, model=model_name)
        service = EmbeddingService(provider=provider)
    except Exception as e:
        logger.error(f"Failed to initialize embedding service: {e}")
        sys.exit(1)

    # Initialize DB
    logger.info("Ensuring database schema and pgvector extension...")
    try:
        db = SessionLocal()
        service.ensure_schema(db)
    except Exception as e:
        logger.error(f"Failed to ensure database schema: {e}")
        sys.exit(1)
        
    chunks_path = backend_dir / "data" / "processed" / "knowledge_chunks.jsonl"
    if not chunks_path.exists():
        logger.error(f"Chunks file not found at {chunks_path}")
        sys.exit(1)
        
    # Read chunks
    chunks = []
    with open(chunks_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line:
                chunks.append(json.loads(line))
                
    total_chunks = len(chunks)
    logger.info(f"Loaded {total_chunks} chunks for processing.")
    
    metrics = {
        "documents": set(),
        "pages": set(),
        "chunks_total": total_chunks,
        "new": 0,
        "updated": 0,
        "skipped": 0,
        "failures": 0
    }
    
    for i, chunk in enumerate(chunks, 1):
        chunk_id = chunk.get("chunk_id")
        doc_id = chunk.get("document_id")
        logger.info(f"Embedding {i}/{total_chunks}: {chunk_id}")
        
        metrics["documents"].add(doc_id)
        # Using a tuple of (doc_id, page_start) to count roughly unique pages processed
        metrics["pages"].add((doc_id, chunk.get("page_start")))
        
        try:
            status = service.process_chunk(db, chunk)
            if status == "inserted":
                metrics["new"] += 1
            elif status == "skipped":
                metrics["skipped"] += 1
            elif status == "updated":
                metrics["updated"] += 1
        except Exception as e:
            logger.error(f"Failed to process chunk {chunk_id}: {e}")
            metrics["failures"] += 1
            
    # Final summary
    db.close()
    
    print("\n" + "="*50)
    print("FINAL SUMMARY")
    print("="*50)
    print(f"Documents: {len(metrics['documents'])}")
    print(f"Pages (unique starts): {len(metrics['pages'])}")
    print(f"Chunks: {metrics['chunks_total']}")
    print(f"New embeddings: {metrics['new']}")
    print(f"Updated embeddings: {metrics['updated']}")
    print(f"Skipped embeddings: {metrics['skipped']}")
    print(f"Failures: {metrics['failures']}")
    print("="*50)

if __name__ == "__main__":
    main()
