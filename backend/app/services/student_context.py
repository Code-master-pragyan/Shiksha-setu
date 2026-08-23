from typing import Optional
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.db.models.student import StudentProfile
from app.db.models.mastery import StudentMastery

class StudentLearningContext(BaseModel):
    student_id: Optional[str]
    grade: int
    preferred_language: str
    concept_id: Optional[str] = None
    mastery_score: float = 0.0
    attempts: int = 0
    correct_attempts: int = 0
    consecutive_errors: int = 0
    learning_level: str = "beginner"
    mastery_status: str = "unknown"

class StudentContextService:
    @staticmethod
    def derive_learning_level(mastery_score: float) -> str:
        if mastery_score < 0.40:
            return "beginner"
        elif 0.40 <= mastery_score < 0.70:
            return "intermediate"
        else:
            return "advanced"

    def get_context(
        self, 
        db: Session, 
        student_id: Optional[str], 
        concept_id: Optional[str], 
        default_grade: int, 
        default_language: str
    ) -> StudentLearningContext:
        
        # Base defaults
        context = StudentLearningContext(
            student_id=student_id,
            grade=default_grade,
            preferred_language=default_language,
            concept_id=concept_id
        )

        if not student_id:
            return context

        # 1. Fetch student profile
        student = db.scalar(select(StudentProfile).where(StudentProfile.id == student_id))
        if student:
            context.grade = student.grade
            context.preferred_language = student.preferred_language

        # 2. Fetch mastery if concept is known
        if student and concept_id:
            mastery = db.scalar(
                select(StudentMastery)
                .where(StudentMastery.student_id == student_id)
                .where(StudentMastery.concept_id == concept_id)
            )
            
            if mastery:
                context.mastery_score = mastery.mastery_score
                context.attempts = mastery.attempts
                context.correct_attempts = mastery.correct_attempts
                context.consecutive_errors = mastery.consecutive_errors
                
                context.learning_level = self.derive_learning_level(mastery.mastery_score)
                context.mastery_status = "known"
            else:
                context.learning_level = "beginner"
                context.mastery_status = "unknown"
                
        return context
