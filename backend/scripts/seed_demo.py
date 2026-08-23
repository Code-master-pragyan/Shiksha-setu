import sys
from pathlib import Path

backend_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(backend_dir))

from dotenv import load_dotenv
from sqlalchemy import select
from app.db.database import SessionLocal, Base, engine
from app.db.models.student import StudentProfile
from app.db.models.concept import Concept
from app.db.models.mastery import StudentMastery
from app.db.models.attempt import Attempt
from app.db.models.question import Question

from app.db.models.user import User

# Hardcoded UUIDs for idempotency
STUDENT_A_ID = "00000000-0000-4000-a000-00000000000a"
STUDENT_B_ID = "00000000-0000-4000-b000-00000000000b"
STUDENT_C_ID = "00000000-0000-4000-c000-00000000000c"
STUDENT_D_ID = "00000000-0000-4000-d000-00000000000d"

USER_A_ID = "11111111-1111-4000-a000-11111111111a"
USER_B_ID = "11111111-1111-4000-b000-11111111111b"
USER_C_ID = "11111111-1111-4000-c000-11111111111c"
USER_D_ID = "11111111-1111-4000-d000-11111111111d"

def seed_students(db):
    users_data = [
        {"id": USER_A_ID, "name": "Student A", "email": "student@demo.com", "role": "student"},
        {"id": USER_B_ID, "name": "Student B", "email": "b@demo.com", "role": "student"},
        {"id": USER_C_ID, "name": "Student C", "email": "c@demo.com", "role": "student"},
        {"id": USER_D_ID, "name": "Student D", "email": "d@demo.com", "role": "student"},
    ]
    
    students_data = [
        {"id": STUDENT_A_ID, "user_id": USER_A_ID, "grade": 8, "preferred_language": "English"},
        {"id": STUDENT_B_ID, "user_id": USER_B_ID, "grade": 8, "preferred_language": "Assamese"},
        {"id": STUDENT_C_ID, "user_id": USER_C_ID, "grade": 8, "preferred_language": "English"},
        {"id": STUDENT_D_ID, "user_id": USER_D_ID, "grade": 8, "preferred_language": "English"},
    ]
    
    for u_data in users_data:
        user = db.scalar(select(User).where(User.id == u_data["id"]))
        if not user:
            user = User(**u_data)
            db.add(user)
        else:
            for k, v in u_data.items():
                setattr(user, k, v)
    db.commit()
    
    for s_data in students_data:
        student = db.scalar(select(StudentProfile).where(StudentProfile.id == s_data["id"]))
        if not student:
            student = StudentProfile(**s_data)
            db.add(student)
        else:
            for k, v in s_data.items():
                setattr(student, k, v)
    db.commit()

def seed_mastery_and_attempts(db):
    # Find a concept to use
    concept = db.scalar(select(Concept).limit(1))
    if not concept:
        print("No concepts found in DB. Please ingest knowledge first.")
        return
        
    q = db.scalar(select(Question).where(Question.concept_id == concept.id).limit(1))
    if not q:
        q = Question(concept_id=concept.id, question_text="Demo Question", correct_answer="Demo Answer")
        db.add(q)
        db.commit()
        
    # Student A: at_risk (mastery=0.20, cons_errors=3)
    # Student B: needs_attention (mastery=0.40, recent_acc < 0.50)
    # Student C: on_track (mastery=0.70, recent_acc > 0.50)
    # Student D: improving (mastery=0.60, trend=improving)
    scenarios = [
        (STUDENT_A_ID, 0.20, 3, [False, False, False]),
        (STUDENT_B_ID, 0.40, 1, [True, False, False, False, True]),
        (STUDENT_C_ID, 0.70, 0, [True, True, True, False, True]),
        (STUDENT_D_ID, 0.60, 0, [False, False, False, False, False, True, True, True, True, False]),
    ]
    
    for s_id, score, errors, attempts_bools in scenarios:
        # Mastery
        mastery = db.scalar(select(StudentMastery).where(StudentMastery.student_id == s_id, StudentMastery.concept_id == concept.id))
        if not mastery:
            mastery = StudentMastery(
                student_id=s_id,
                concept_id=concept.id,
                mastery_score=score,
                attempts=len(attempts_bools),
                correct_attempts=sum(attempts_bools),
                consecutive_errors=errors
            )
            db.add(mastery)
        else:
            mastery.mastery_score = score
            mastery.attempts = len(attempts_bools)
            mastery.correct_attempts = sum(attempts_bools)
            mastery.consecutive_errors = errors
        db.commit()
        
        # Clear old attempts
        db.query(Attempt).filter(Attempt.student_id == s_id).delete()
        db.commit()
        
        # Seed new attempts
        for is_correct in attempts_bools:
            attempt = Attempt(
                student_id=s_id,
                question_id=q.id,
                concept_id=concept.id,
                student_answer="Demo answer",
                correct=is_correct
            )
            db.add(attempt)
        db.commit()

def main():
    load_dotenv()
    db = SessionLocal()
    try:
        seed_students(db)
        seed_mastery_and_attempts(db)
        print("Demo data seeded successfully.")
    except Exception as e:
        print(f"Error seeding demo data: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    main()
