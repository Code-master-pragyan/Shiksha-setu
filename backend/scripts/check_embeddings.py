import os
import sys
import json
import logging
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy import text

# Add backend directory to sys.path
backend_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(backend_dir))

from app.core.config import settings
from app.db.database import SessionLocal
from app.db.models.knowledge import KnowledgeChunk

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

def main():
    load_dotenv()
    
    logger.info("Connecting to database...")
    try:
        db = SessionLocal()
    except Exception as e:
        logger.error(f"Failed to connect to DB: {e}")
        sys.exit(1)
        
    try:
        # Check pgvector extension
        res = db.execute(text("SELECT extname FROM pg_extension WHERE extname = 'vector';")).fetchone()
        if res:
            logger.info("pgvector is enabled: PASS")
        else:
            logger.error("pgvector is enabled: FAIL")
            
        # Total rows
        total_rows = db.query(KnowledgeChunk).count()
        logger.info(f"Total rows in knowledge_chunks: {total_rows}")
        
        # Unique chunk IDs
        unique_ids = db.query(KnowledgeChunk.chunk_id).distinct().count()
        logger.info(f"Unique chunk IDs: {unique_ids}")
        if total_rows == unique_ids:
            logger.info("Unique chunk IDs match total rows: PASS")
        else:
            logger.error("Unique chunk IDs match total rows: FAIL")
            
        # Null embeddings
        null_embeddings = db.query(KnowledgeChunk).filter(KnowledgeChunk.embedding == None).count()
        if null_embeddings == 0:
            logger.info("Null embeddings check (should be 0): PASS")
        else:
            logger.error(f"Null embeddings check: FAIL ({null_embeddings} found)")
            
        # Load JSONL and check against DB
        chunks_path = backend_dir / "data" / "processed" / "knowledge_chunks.jsonl"
        source_count = 0
        if chunks_path.exists():
            with open(chunks_path, 'r', encoding='utf-8') as f:
                source_count = sum(1 for line in f if line.strip())
        logger.info(f"Source chunks in JSONL: {source_count}")
        
        if total_rows == source_count:
            logger.info("Database chunks match source chunks: PASS")
        else:
            logger.error("Database chunks match source chunks: FAIL")
            
    except Exception as e:
        logger.error(f"Validation failed: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    main()
