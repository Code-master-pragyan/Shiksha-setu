import os
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.core.config import settings
from app.api.schemas.doubt import DoubtRequest, DoubtResponse
from app.ai.doubt_solver import DoubtSolverService
from app.ai.providers.gemini_provider import GeminiProvider
from app.rag.retrieval import RetrievalService
from app.services.embeddings.gemini_embedding_provider import GeminiEmbeddingProvider
from app.services.student_context import StudentContextService
from app.api.deps import get_current_user_optional, CurrentUser
from typing import Optional

router = APIRouter()

def get_doubt_solver_service() -> DoubtSolverService:
    api_key = settings.GEMINI_API_KEY or os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Server misconfiguration: missing API key."
        )
        
    embedding_model = settings.GEMINI_EMBEDDING_MODEL or os.environ.get("GEMINI_EMBEDDING_MODEL", "text-embedding-004")
    generation_model = settings.GEMINI_GENERATION_MODEL or os.environ.get("GEMINI_GENERATION_MODEL", "gemini-3.6-flash")
    
    try:
        embedding_provider = GeminiEmbeddingProvider(api_key=api_key, model=embedding_model)
        retrieval_service = RetrievalService(provider=embedding_provider)
        ai_provider = GeminiProvider(api_key=api_key, model=generation_model)
        context_service = StudentContextService()
        
        return DoubtSolverService(
            retrieval_service=retrieval_service, 
            ai_provider=ai_provider,
            context_service=context_service
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to initialize AI services."
        )

@router.post("/ask", response_model=DoubtResponse)
def ask_doubt(
    request: DoubtRequest,
    db: Session = Depends(get_db),
    solver: DoubtSolverService = Depends(get_doubt_solver_service),
    current_user: Optional[CurrentUser] = Depends(get_current_user_optional)
):
    # Override/validate student_id if authenticated
    if current_user and current_user.role == "student" and current_user.student_id:
        if request.student_id and request.student_id != current_user.student_id:
            raise HTTPException(status_code=403, detail="Not authorized to ask doubt for this student")
        request.student_id = current_user.student_id

    try:
        return solver.solve(db=db, request=request)
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process doubt."
        )
