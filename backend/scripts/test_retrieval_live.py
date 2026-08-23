import os
import sys
import logging
from pathlib import Path
from dotenv import load_dotenv

# Add backend directory to sys.path
backend_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(backend_dir))

from app.core.config import settings
from app.db.database import SessionLocal
from app.rag.retrieval import RetrievalService
from app.services.embeddings.gemini_embedding_provider import GeminiEmbeddingProvider

logging.basicConfig(level=logging.INFO, format="%(message)s")
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
        service = RetrievalService(provider=provider)
    except Exception as e:
        logger.error(f"Failed to initialize embedding service: {e}")
        sys.exit(1)
        
    db = SessionLocal()
    
    queries = [
        "What is a cell?",
        "What are microorganisms?",
        "Why does yeast make dough rise?",
        "What is an electric circuit?",
        "How can diseases spread?"
    ]
    
    print("="*60)
    print("LIVE RETRIEVAL TEST")
    print("="*60)
    
    try:
        for q in queries:
            print(f"\nQuery: {q}")
            results = service.search(db=db, query=q, top_k=3)
            print(f"Top results: {len(results)}")
            
            for i, res in enumerate(results, 1):
                print(f"\n  Result {i}:")
                print(f"  Similarity: {res.similarity_score}")
                print(f"  Title: {res.title}")
                print(f"  Chapter: {res.chapter_number} - {res.chapter}")
                print(f"  Section: {res.section}")
                print(f"  Page: {res.page_start}-{res.page_end}")
                preview = res.text[:200].replace('\n', ' ') + "..."
                preview_safe = preview.encode(sys.stdout.encoding, errors='replace').decode(sys.stdout.encoding)
                print(f"  Text preview: {preview_safe}")
            
            print("-" * 60)
            
    finally:
        db.close()
        
if __name__ == "__main__":
    main()
