import logging
from typing import Callable, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import select
from datetime import datetime, timezone

from app.db.models.student import StudentProfile
from app.db.models.question import Question
from app.db.models.attempt import Attempt
from app.db.models.mastery import StudentMastery
from app.api.schemas.practice import PracticeAttemptRequest, PracticeAttemptResponse
from app.ai.schemas import ShortAnswerEvaluation
from app.api.schemas.retrieval import RetrievalResult
from app.services.student_context import StudentContextService
from app.ai.providers.gemini_provider import GeminiProvider

logger = logging.getLogger(__name__)

class MasteryService:
    def __init__(self, context_service: StudentContextService, ai_provider: GeminiProvider):
        self.context_service = context_service
        self.ai_provider = ai_provider

    def record_attempt(
        self, 
        db: Session, 
        request: PracticeAttemptRequest, 
        context_chunks: list[RetrievalResult]
    ) -> PracticeAttemptResponse:
        
        # 1. Fetch Question
        question = db.scalar(select(Question).where(Question.id == request.question_id))
        if not question:
            raise ValueError("Question not found")
            
        # 2. Evaluate
        is_correct = False
        feedback = ""
        
        if question.question_type == "multiple_choice":
            # Deterministic check
            # For simplicity, we just check if answer strings match or the option letters match
            expected = question.correct_answer.strip().lower()
            provided = request.student_answer.strip().lower()
            is_correct = (expected == provided)
            feedback = question.explanation if question.explanation else ("Correct!" if is_correct else "Incorrect.")
        else:
            # Short answer evaluation via Gemini
            eval_result: ShortAnswerEvaluation = self.ai_provider.evaluate_short_answer(
                question=question.question_text,
                expected_answer=question.correct_answer,
                student_answer=request.student_answer,
                context_chunks=context_chunks
            )
            is_correct = eval_result.is_correct
            feedback = eval_result.brief_feedback
            
        # 3. Transactional update for Attempt and Mastery
        try:
            with db.begin_nested():
                # Fetch mastery record
                mastery = db.scalar(
                    select(StudentMastery)
                    .where(StudentMastery.student_id == request.student_id)
                    .where(StudentMastery.concept_id == question.concept_id)
                    .with_for_update() # lock for update
                )
                
                if not mastery:
                    # Create one if doesn't exist starting at 0.0
                    mastery = StudentMastery(
                        student_id=request.student_id,
                        concept_id=question.concept_id,
                        mastery_score=0.0,
                        attempts=0,
                        correct_attempts=0,
                        consecutive_errors=0
                    )
                    db.add(mastery)
                    db.flush() # flush to get mastery in session
                
                # Update attempt counts
                mastery.attempts += 1
                mastery.last_attempt_at = datetime.now(timezone.utc)
                
                if is_correct:
                    mastery.correct_attempts += 1
                    mastery.consecutive_errors = 0
                    new_score = mastery.mastery_score + 0.10
                else:
                    mastery.consecutive_errors += 1
                    new_score = mastery.mastery_score - 0.08
                    
                # Clamp score
                mastery.mastery_score = max(0.0, min(1.0, new_score))
                
                # Record the Attempt
                attempt = Attempt(
                    student_id=request.student_id,
                    question_id=question.id,
                    concept_id=question.concept_id,
                    student_answer=request.student_answer,
                    correct=is_correct,
                    time_taken=request.time_taken,
                    hint_used=request.hint_used
                )
                db.add(attempt)
            db.commit()
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to record attempt: {e}")
            raise e

        # 4. Determine next step
        new_learning_level = self.context_service.derive_learning_level(mastery.mastery_score)
        
        next_action = "practice"
        next_difficulty = new_learning_level
        
        if not is_correct and mastery.consecutive_errors >= 2:
            next_action = "review"
            next_difficulty = "beginner"
        elif is_correct and mastery.mastery_score >= 0.70:
            next_difficulty = "advanced"

        # Note: Citations will be attached by the router which has context chunks
        return PracticeAttemptResponse(
            correct=is_correct,
            feedback=feedback,
            mastery_score=round(mastery.mastery_score, 2),
            learning_level=new_learning_level,
            consecutive_errors=mastery.consecutive_errors,
            next_action=next_action,
            next_difficulty=next_difficulty,
            citations=[] # Router to fill
        )
