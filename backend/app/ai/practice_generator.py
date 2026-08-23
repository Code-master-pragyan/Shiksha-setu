import logging
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.db.models.concept import Concept
from app.db.models.question import Question
from app.api.schemas.practice import PracticeGenerateRequest, PracticeGenerateResponse
from app.api.schemas.retrieval import RetrievalResult
from app.ai.schemas import Citation, PracticeQuestion
from app.services.student_context import StudentContextService
from app.rag.retrieval import RetrievalService
from app.ai.providers.gemini_provider import GeminiProvider

logger = logging.getLogger(__name__)

class PracticeGeneratorService:
    def __init__(self, retrieval_service: RetrievalService, ai_provider: GeminiProvider, context_service: StudentContextService):
        self.retrieval_service = retrieval_service
        self.ai_provider = ai_provider
        self.context_service = context_service

    def generate(self, db: Session, request: PracticeGenerateRequest) -> PracticeGenerateResponse:
        # 1. Look up concept to get a name for retrieval
        concept = db.scalar(select(Concept).where(Concept.id == request.concept_id))
        if not concept:
            raise ValueError("Concept not found")
            
        # 2. Get student context
        student_context = self.context_service.get_context(
            db=db,
            student_id=request.student_id,
            concept_id=str(concept.id),
            default_grade=concept.grade,
            default_language="English"
        )
        
        chunks = self.retrieval_service.search(
            db=db,
            query=concept.name,
            grade=student_context.grade,
            subject=request.subject,
            language=None,
            top_k=3
        )
        
        if not chunks:
            raise ValueError("No context found for the concept to generate a question.")
            
        # 4. Determine difficulty
        difficulty = student_context.learning_level
        
        # 5. Generate question
        gen_q: PracticeQuestion = self.ai_provider.generate_practice_question(
            context=student_context,
            subject=request.subject,
            difficulty=difficulty,
            context_chunks=chunks
        )
        
        # 6. Save question to DB
        new_q = Question(
            concept_id=concept.id,
            question_text=gen_q.question_text,
            difficulty=gen_q.difficulty,
            question_type=gen_q.question_type,
            options=gen_q.options,
            correct_answer=gen_q.correct_answer,
            explanation=gen_q.explanation
        )
        db.add(new_q)
        db.commit()
        db.refresh(new_q)
        
        # 7. Build citations
        authoritative_citations = []
        for chunk in chunks:
            authoritative_citations.append(
                Citation(
                    source_title=chunk.title,
                    chapter=f"{chunk.chapter_number} - {chunk.chapter}" if chunk.chapter_number else (chunk.chapter or "N/A"),
                    section=chunk.section,
                    page_start=chunk.page_start,
                    page_end=chunk.page_end,
                    citation_text=chunk.text[:200] + "..."
                )
            )
            
        return PracticeGenerateResponse(
            question_id=str(new_q.id),
            question_text=new_q.question_text,
            question_type=new_q.question_type,
            options=new_q.options,
            difficulty=new_q.difficulty,
            concept_id=str(concept.id),
            citations=authoritative_citations
        )
