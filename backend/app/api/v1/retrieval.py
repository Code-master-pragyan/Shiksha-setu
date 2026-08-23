import os
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.core.config import settings
from app.api.schemas.retrieval import RetrievalRequest, RetrievalResponse
from app.rag.retrieval import RetrievalService
from app.services.embeddings.gemini_embedding_provider import GeminiEmbeddingProvider

router = APIRouter()

# Dependency for retrieval service
def get_retrieval_service() -> RetrievalService:
    api_key = settings.GEMINI_API_KEY or os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Server misconfiguration: missing API key."
        )
    model = settings.GEMINI_EMBEDDING_MODEL or os.environ.get("GEMINI_EMBEDDING_MODEL", "text-embedding-004")
    
    try:
        provider = GeminiEmbeddingProvider(api_key=api_key, model=model)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to initialize embedding provider."
        )
    return RetrievalService(provider=provider)

@router.post("/search", response_model=RetrievalResponse)
def search_knowledge(
    request: RetrievalRequest,
    db: Session = Depends(get_db),
    retrieval_service: RetrievalService = Depends(get_retrieval_service)
):
    try:
        results = retrieval_service.search(
            db=db,
            query=request.query,
            grade=request.grade,
            subject=request.subject,
            language=request.language,
            chapter=request.chapter,
            top_k=request.top_k
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Retrieval process failed.")
        
    return RetrievalResponse(
        query=request.query,
        results=results
    )
