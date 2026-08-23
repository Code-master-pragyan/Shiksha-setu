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
from app.services.embeddings.gemini_embedding_provider import GeminiEmbeddingProvider

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

def main():
    load_dotenv()
    
    api_key = settings.GEMINI_API_KEY or os.environ.get("GEMINI_API_KEY")
    if not api_key:
        logger.error("GEMINI_API_KEY is not set. Exiting.")
        sys.exit(1)

    model_name = settings.GEMINI_EMBEDDING_MODEL or os.environ.get("GEMINI_EMBEDDING_MODEL", "text-embedding-004")
    
    try:
        provider = GeminiEmbeddingProvider(api_key=api_key, model=model_name)
    except Exception as e:
        logger.error(f"Failed to initialize embedding provider: {e}")
        sys.exit(1)

    # Load one chunk from the JSONL
    chunks_path = backend_dir / "data" / "processed" / "knowledge_chunks.jsonl"
    if not chunks_path.exists():
        logger.error(f"Chunks file not found at {chunks_path}")
        sys.exit(1)
        
    logger.info(f"Using model: {model_name}")
    logger.info("Reading first chunk...")
    
    first_chunk = None
    with open(chunks_path, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                first_chunk = json.loads(line)
                break
                
    if not first_chunk:
        logger.error("No chunks found in the file.")
        sys.exit(1)
        
    text_to_embed = first_chunk.get("text")
    if not text_to_embed:
        logger.error("First chunk does not contain 'text'.")
        sys.exit(1)
        
    logger.info(f"Extracted text of length {len(text_to_embed)}. Generating embedding...")
    
    try:
        embedding = provider.embed_text(text_to_embed)
        logger.info(f"Successfully generated embedding.")
        logger.info(f"Actual Dimension: {len(embedding)}")
        logger.info("Live smoke test passed!")
    except Exception as e:
        logger.error(f"Failed to generate embedding: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
