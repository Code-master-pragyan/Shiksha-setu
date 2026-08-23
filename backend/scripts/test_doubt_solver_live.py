import os
import sys
import logging
from pathlib import Path
from dotenv import load_dotenv

backend_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(backend_dir))

from app.core.config import settings
from app.db.database import SessionLocal
from app.rag.retrieval import RetrievalService
from app.services.embeddings.gemini_embedding_provider import GeminiEmbeddingProvider
from app.ai.providers.gemini_provider import GeminiProvider
from app.ai.doubt_solver import DoubtSolverService
from app.api.schemas.doubt import DoubtRequest

logging.basicConfig(level=logging.WARNING, format="%(message)s")
logger = logging.getLogger(__name__)

def main():
    load_dotenv()
    
    api_key = settings.GEMINI_API_KEY or os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("GEMINI_API_KEY is not set. Exiting.")
        sys.exit(1)

    emb_model = settings.GEMINI_EMBEDDING_MODEL or os.environ.get("GEMINI_EMBEDDING_MODEL", "text-embedding-004")
    gen_model = settings.GEMINI_GENERATION_MODEL or os.environ.get("GEMINI_GENERATION_MODEL", "gemini-3.6-flash")
    
    try:
        embedding_provider = GeminiEmbeddingProvider(api_key=api_key, model=emb_model)
        retrieval_service = RetrievalService(provider=embedding_provider)
        ai_provider = GeminiProvider(api_key=api_key, model=gen_model)
        solver = DoubtSolverService(retrieval_service=retrieval_service, ai_provider=ai_provider)
    except Exception as e:
        print(f"Failed to initialize services: {e}")
        sys.exit(1)
        
    db = SessionLocal()
    
    test_cases = [
        {"question": "What is a cell?", "language": "English"},
        {"question": "Why does yeast make dough rise?", "language": "English"},
        {"question": "What are microorganisms?", "language": "English"},
        {"question": "What is an electric circuit?", "language": "English"},
        {"question": "How can diseases spread?", "language": "English"},
        {"question": "কোষ কি?", "language": "Assamese"}, # What is a cell in Assamese
        {"question": "What is the capital of Brazil?", "language": "English"} # Out of context
    ]
    
    print("="*60)
    print("LIVE DOUBT SOLVER TEST")
    print("="*60)
    
    try:
        for tc in test_cases:
            q = tc["question"]
            lang = tc["language"]
            
            req = DoubtRequest(
                question=q,
                grade=8,
                subject="Science",
                preferred_language=lang,
                top_k=3
            )
            
            q_safe = q.encode(sys.stdout.encoding, errors='replace').decode(sys.stdout.encoding)
            print(f"\nQuestion ({lang}): {q_safe}")
            
            res = solver.solve(db=db, request=req)
            
            ans_safe = res.answer.encode(sys.stdout.encoding, errors='replace').decode(sys.stdout.encoding)
            print(f"Answer:\n{ans_safe}\n")
            print(f"Confidence: {res.confidence}")
            print(f"Citations ({len(res.citations)}):")
            for i, c in enumerate(res.citations, 1):
                print(f"  {i}. {c.source_title}, {c.chapter} (Pages {c.page_start}-{c.page_end})")
                
            print("-" * 60)
            
    finally:
        db.close()
        
if __name__ == "__main__":
    main()
