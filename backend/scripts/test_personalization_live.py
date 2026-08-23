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
from app.services.student_context import StudentContextService, StudentLearningContext

logging.basicConfig(level=logging.WARNING, format="%(message)s")
logger = logging.getLogger(__name__)

class FixtureContextService(StudentContextService):
    def __init__(self, fixture_contexts):
        self.fixture_contexts = fixture_contexts

    def get_context(self, db, student_id, concept_id, default_grade, default_language):
        # Return the fixture for the given student_id, fallback to default
        if student_id in self.fixture_contexts:
            return self.fixture_contexts[student_id]
        return super().get_context(db, student_id, concept_id, default_grade, default_language)

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
        
        # Setup fixtures
        fixtures = {
            "student_beginner": StudentLearningContext(
                student_id="student_beginner", grade=8, preferred_language="English",
                learning_level="beginner", mastery_status="unknown"
            ),
            "student_intermediate": StudentLearningContext(
                student_id="student_intermediate", grade=8, preferred_language="English",
                learning_level="intermediate", mastery_status="known", mastery_score=0.5
            ),
            "student_advanced": StudentLearningContext(
                student_id="student_advanced", grade=8, preferred_language="English",
                learning_level="advanced", mastery_status="known", mastery_score=0.9
            ),
            "student_assamese": StudentLearningContext(
                student_id="student_assamese", grade=8, preferred_language="Assamese",
                learning_level="beginner", mastery_status="unknown"
            )
        }
        
        context_service = FixtureContextService(fixture_contexts=fixtures)
        solver = DoubtSolverService(retrieval_service=retrieval_service, ai_provider=ai_provider, context_service=context_service)
        
    except Exception as e:
        print(f"Failed to initialize services: {e}")
        sys.exit(1)
        
    db = SessionLocal()
    
    test_cases = [
        ("What is a cell?", "student_beginner"),
        ("What is a cell?", "student_intermediate"),
        ("What is a cell?", "student_advanced"),
        ("What is a cell?", "student_assamese"),
    ]
    
    print("="*60)
    print("LIVE PERSONALIZATION TEST")
    print("="*60)
    
    try:
        for q, sid in test_cases:
            req = DoubtRequest(
                student_id=sid,
                question=q,
                grade=8,
                subject="Science",
                preferred_language="English", # Will be overridden by context service fixture if applicable
                top_k=3
            )
            
            q_safe = q.encode(sys.stdout.encoding, errors='replace').decode(sys.stdout.encoding)
            
            print(f"\nStudent Profile: {sid}")
            print(f"Question: {q_safe}")
            
            res = solver.solve(db=db, request=req)
            
            ans_safe = res.answer.encode(sys.stdout.encoding, errors='replace').decode(sys.stdout.encoding)
            print(f"Learning Level used: {res.learning_level}")
            print(f"Answer:\n{ans_safe}\n")
            print(f"Confidence: {res.confidence}")
            print(f"Citations: {len(res.citations)}")
                
            print("-" * 60)
            
    finally:
        db.close()
        
if __name__ == "__main__":
    main()
