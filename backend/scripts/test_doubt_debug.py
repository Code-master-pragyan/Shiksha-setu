import sys, os, traceback
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.db.database import SessionLocal
from app.api.schemas.doubt import DoubtRequest
from app.ai.doubt_solver import DoubtSolverService
from app.core.config import settings
from app.services.embeddings.gemini_embedding_provider import GeminiEmbeddingProvider
from app.rag.retrieval import RetrievalService
from app.ai.providers.gemini_provider import GeminiProvider
from app.services.student_context import StudentContextService

api_key = settings.GEMINI_API_KEY
embedding_provider = GeminiEmbeddingProvider(api_key=api_key)
retrieval_service = RetrievalService(provider=embedding_provider)
ai_provider = GeminiProvider(api_key=api_key, model=settings.GEMINI_GENERATION_MODEL or "gemini-3.6-flash")
context_service = StudentContextService()
solver = DoubtSolverService(retrieval_service=retrieval_service, ai_provider=ai_provider, context_service=context_service)

db = SessionLocal()
req = DoubtRequest(question="what is a cell", grade=8, subject="Science", preferred_language="English", top_k=3, student_id="00000000-0000-4000-a000-00000000000a")

try:
    result = solver.solve(db=db, request=req)
    print("SUCCESS:", result.answer[:200])
except Exception as e:
    traceback.print_exc()
finally:
    db.close()
