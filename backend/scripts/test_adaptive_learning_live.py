import os
import sys
import logging
import time
from pathlib import Path
from dotenv import load_dotenv

backend_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(backend_dir))

from sqlalchemy import select
from app.core.config import settings
from app.db.database import SessionLocal
from app.db.models.student import StudentProfile
from app.db.models.concept import Concept
from app.db.models.mastery import StudentMastery
from app.api.schemas.practice import PracticeGenerateRequest, PracticeAttemptRequest
from app.ai.practice_generator import PracticeGeneratorService
from app.services.mastery import MasteryService
from app.rag.retrieval import RetrievalService
from app.ai.providers.gemini_provider import GeminiProvider
from app.services.embeddings.gemini_embedding_provider import GeminiEmbeddingProvider
from app.services.student_context import StudentContextService

logging.basicConfig(level=logging.WARNING, format="%(message)s")
logger = logging.getLogger(__name__)

class FixtureContextService(StudentContextService):
    def get_context(self, db, student_id, concept_id, default_grade, default_language):
        ctx = super().get_context(db, student_id, concept_id, default_grade, default_language)
        ctx.grade = 8
        return ctx

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
        context_service = FixtureContextService()
        
        practice_generator = PracticeGeneratorService(retrieval_service, ai_provider, context_service)
        mastery_service = MasteryService(context_service, ai_provider)

    except Exception as e:
        print(f"Failed to initialize services: {e}")
        sys.exit(1)
        
    db = SessionLocal()
    
    try:
        # Get a student and a concept
        student = db.scalar(select(StudentProfile).limit(1))
        concept = db.scalar(select(Concept).where(Concept.name.ilike("%Circuit%")).limit(1))
        if not concept:
            concept = db.scalar(select(Concept).limit(1))
            
        if not student or not concept:
            print("Need at least 1 student and 1 concept in DB.")
            return

        print("="*60)
        print("LIVE ADAPTIVE LEARNING TEST")
        print("="*60)
        print(f"Student ID: {student.id}")
        print(f"Concept: {concept.name}")
        
        # Reset mastery for testing
        mastery = db.scalar(select(StudentMastery).where(StudentMastery.student_id == student.id).where(StudentMastery.concept_id == concept.id))
        if mastery:
            mastery.mastery_score = 0.20
            mastery.attempts = 0
            mastery.correct_attempts = 0
            mastery.consecutive_errors = 0
            db.commit()
            print("Reset mastery score to 0.20")
        else:
            print("No existing mastery. It will start at 0.0")

        # helper function
        def run_cycle(attempt_correct: bool):
            # 1. Generate
            print(f"\n--- GENERATING QUESTION ---")
            gen_req = PracticeGenerateRequest(student_id=str(student.id), concept_id=str(concept.id), subject="Science")
            gen_res = practice_generator.generate(db, gen_req)
            
            print(f"Generated ({gen_res.difficulty}): {gen_res.question_text}")
            if gen_res.options:
                for o in gen_res.options:
                    print(f"  - {o}")
            print(f"Citations attached: {len(gen_res.citations)}")
            
            # Fetch the actual correct answer from DB to simulate the student
            from app.db.models.question import Question
            q = db.scalar(select(Question).where(Question.id == gen_res.question_id))
            
            ans = q.correct_answer if attempt_correct else "Some completely wrong answer"
            print(f"\nSubmitting Answer: {ans}")
            
            # 2. Attempt
            chunks = retrieval_service.search(db=db, query=concept.name, grade=8, subject="Science", language=None, top_k=3)
            att_req = PracticeAttemptRequest(
                student_id=str(student.id),
                question_id=gen_res.question_id,
                student_answer=ans
            )
            att_res = mastery_service.record_attempt(db, att_req, chunks)
            
            print(f"Result: {'CORRECT' if att_res.correct else 'INCORRECT'}")
            print(f"Feedback: {att_res.feedback}")
            print(f"New Mastery Score: {att_res.mastery_score}")
            print(f"Consecutive Errors: {att_res.consecutive_errors}")
            print(f"Next Action: {att_res.next_action}, Difficulty: {att_res.next_difficulty}")

        # Simulate:
        # 1. Correct Answer
        run_cycle(attempt_correct=True)
        
        # 2. Incorrect Answer
        run_cycle(attempt_correct=False)
        
        # 3. Incorrect Answer (consecutive)
        run_cycle(attempt_correct=False)
        
        # 4. Set mastery very high to test advanced
        mastery = db.scalar(select(StudentMastery).where(StudentMastery.student_id == student.id).where(StudentMastery.concept_id == concept.id))
        mastery.mastery_score = 0.85
        db.commit()
        print("\n--- FORCING MASTERY TO 0.85 (ADVANCED) ---")
        run_cycle(attempt_correct=True)

    finally:
        db.close()
        
if __name__ == "__main__":
    main()
