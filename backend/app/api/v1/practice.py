import os
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.db.database import get_db
from app.core.config import settings

from app.api.schemas.practice import PracticeGenerateRequest, PracticeGenerateResponse, PracticeAttemptRequest, PracticeAttemptResponse
from app.ai.schemas import Citation
from app.ai.practice_generator import PracticeGeneratorService
from app.services.mastery import MasteryService
from app.ai.providers.gemini_provider import GeminiProvider
from app.rag.retrieval import RetrievalService
from app.services.embeddings.gemini_embedding_provider import GeminiEmbeddingProvider
from app.services.student_context import StudentContextService
from app.db.models.concept import Concept
from app.db.models.question import Question
from app.api.deps import get_current_student, CurrentUser

router = APIRouter()

def get_services():
    api_key = settings.GEMINI_API_KEY or os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="Missing API key.")
        
    embedding_model = settings.GEMINI_EMBEDDING_MODEL or os.environ.get("GEMINI_EMBEDDING_MODEL", "text-embedding-004")
    generation_model = settings.GEMINI_GENERATION_MODEL or os.environ.get("GEMINI_GENERATION_MODEL", "gemini-3.6-flash")
    
    emb_provider = GeminiEmbeddingProvider(api_key=api_key, model=embedding_model)
    retrieval_service = RetrievalService(provider=emb_provider)
    ai_provider = GeminiProvider(api_key=api_key, model=generation_model)
    context_service = StudentContextService()
    
    practice_generator = PracticeGeneratorService(retrieval_service, ai_provider, context_service)
    mastery_service = MasteryService(context_service, ai_provider)
    
    return practice_generator, mastery_service, retrieval_service

@router.post("/generate", response_model=PracticeGenerateResponse)
def generate_practice(
    request: PracticeGenerateRequest,
    db: Session = Depends(get_db),
    current_student: CurrentUser = Depends(get_current_student)
):
    if current_student.student_id != request.student_id:
        raise HTTPException(status_code=403, detail="Not authorized to practice for this student")
    try:
        services = get_services()
        practice_generator = services[0]
        return practice_generator.generate(db, request)
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to generate practice question.")

@router.post("/attempt", response_model=PracticeAttemptResponse)
def attempt_practice(
    request: PracticeAttemptRequest,
    db: Session = Depends(get_db),
    current_student: CurrentUser = Depends(get_current_student)
):
    if current_student.student_id != request.student_id:
        raise HTTPException(status_code=403, detail="Not authorized to record attempt for this student")
    try:
        services = get_services()
        mastery_service = services[1]
        retrieval_service = services[2]
        
        # We need context chunks for short answer evaluation and citations
        question = db.scalar(select(Question).where(Question.id == request.question_id))
        if not question:
            raise HTTPException(status_code=404, detail="Question not found")
            
        concept = db.scalar(select(Concept).where(Concept.id == question.concept_id))
        
        chunks = retrieval_service.search(
            db=db, query=concept.name, grade=concept.grade, subject=concept.subject, language=None, top_k=3
        )
        
        response = mastery_service.record_attempt(db, request, chunks)
        
        # Attach citations
        citations = []
        for chunk in chunks:
            citations.append(
                Citation(
                    source_title=chunk.title,
                    chapter=f"{chunk.chapter_number} - {chunk.chapter}" if chunk.chapter_number else (chunk.chapter or "N/A"),
                    section=chunk.section,
                    page_start=chunk.page_start,
                    page_end=chunk.page_end,
                    citation_text=chunk.text[:200] + "..."
                )
            )
        response.citations = citations
        
        return response
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to record attempt.")
