import logging
import uuid
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.api.schemas.doubt import DoubtRequest, DoubtResponse
from app.ai.schemas import Citation, DoubtAnswer
from app.rag.retrieval import RetrievalService
from app.ai.providers.gemini_provider import GeminiProvider
from app.services.student_context import StudentContextService
from app.db.models.concept import Concept
from app.db.models.mastery import StudentMastery

logger = logging.getLogger(__name__)

class DoubtSolverService:
    def __init__(self, retrieval_service: RetrievalService, ai_provider: GeminiProvider, context_service: StudentContextService):
        self.retrieval_service = retrieval_service
        self.ai_provider = ai_provider
        self.context_service = context_service

    def _ensure_mastery_record(self, db: Session, student_id: Optional[str], concept_id) -> None:
        """Auto-create a StudentMastery record (score=0) so the concept
        appears on the Practice page after a student asks a doubt about it."""
        if not student_id or not concept_id:
            return
        try:
            existing = db.scalar(
                select(StudentMastery)
                .where(StudentMastery.student_id == student_id)
                .where(StudentMastery.concept_id == concept_id)
            )
            if not existing:
                mastery = StudentMastery(
                    id=uuid.uuid4(),
                    student_id=student_id,
                    concept_id=concept_id,
                    mastery_score=0.0,
                    attempts=0,
                    correct_attempts=0,
                    consecutive_errors=0,
                )
                db.add(mastery)
                db.commit()
                logger.info(f"Created mastery record for student={student_id}, concept={concept_id}")
        except Exception as e:
            db.rollback()
            logger.warning(f"Could not create mastery record: {e}")

    def solve(self, db: Session, request: DoubtRequest) -> DoubtResponse:
        logger.info(f"Solving doubt: {request.question}")
        
        # 1. Retrieve chunks (without language filter, so AI can translate it)
        chunks = self.retrieval_service.search(
            db=db,
            query=request.question,
            grade=request.grade,
            subject=request.subject,
            language=None, 
            top_k=request.top_k
        )
        
        logger.info(f"Retrieved {len(chunks)} chunks for the question.")

        # 2. Try mapping retrieved chunk to a Concept ID
        concept_id = None
        if chunks:
            # We check the first chunk's chapter or section
            top_chunk = chunks[0]
            stmt = select(Concept).where(
                (Concept.subject == request.subject) &
                (Concept.grade == request.grade) &
                ((Concept.name == top_chunk.chapter) | (Concept.name == top_chunk.section))
            ).limit(1)
            concept = db.scalar(stmt)
            if concept:
                concept_id = concept.id


        # 3. Build student context
        student_context = self.context_service.get_context(
            db=db,
            student_id=request.student_id,
            concept_id=str(concept_id) if concept_id else None,
            default_grade=request.grade,
            default_language=request.preferred_language
        )

        # 4. Determine if evidence is sufficient
        if not chunks:
            return DoubtResponse(
                question=request.question,
                answer=f"I couldn't find enough information about this in the available Class {student_context.grade} {request.subject} learning material.",
                key_points=[],
                learning_level=student_context.learning_level,
                confidence="low",
                citations=[],
                follow_up_question=None,
                concept_id=str(concept_id) if concept_id else None
            )
            
        # 5. Ask AI to generate answer
        ai_answer: DoubtAnswer = self.ai_provider.generate_grounded_answer(
            question=request.question,
            subject=request.subject,
            context=student_context,
            context_chunks=chunks
        )
        
        # 6. Construct authoritative citations from retrieved chunks
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
            
        # 7. Calculate confidence from backend
        avg_score = sum(c.similarity_score for c in chunks) / len(chunks)
        confidence = "low"
        if avg_score > 0.65:
            confidence = "high"
        elif avg_score > 0.55:
            confidence = "medium"
            
        if "couldn't find enough information" in ai_answer.answer or "does not provide enough information" in ai_answer.answer:
            confidence = "low"
            authoritative_citations = []

        # 8. Auto-create mastery record so concept appears on Practice page
        # Done AFTER building the response so db.commit() doesn't expire ORM objects
        self._ensure_mastery_record(db, request.student_id, concept_id)

        return DoubtResponse(
            question=request.question,
            answer=ai_answer.answer,
            key_points=ai_answer.key_points,
            learning_level=student_context.learning_level,
            confidence=confidence,
            citations=authoritative_citations,
            follow_up_question=ai_answer.follow_up_question,
            concept_id=str(concept_id) if concept_id else None
        )
