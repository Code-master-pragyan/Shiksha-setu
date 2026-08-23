import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import logging
from app.db.database import SessionLocal
from app.db.models import User, StudentProfile, Concept, Source, Question
from sqlalchemy.orm import Session

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def seed_users(db: Session):
    teacher = db.query(User).filter_by(email="teacher@demo.com").first()
    if not teacher:
        teacher = User(name="Demo Teacher", email="teacher@demo.com", role="teacher")
        db.add(teacher)

    student1 = db.query(User).filter_by(email="student1@demo.com").first()
    if not student1:
        student1 = User(name="Alice", email="student1@demo.com", role="student")
        db.add(student1)
    
    student2 = db.query(User).filter_by(email="student2@demo.com").first()
    if not student2:
        student2 = User(name="Bob", email="student2@demo.com", role="student")
        db.add(student2)
        
    db.commit()
    return teacher, student1, student2

def seed_profiles(db: Session, student1: User, student2: User):
    p1 = db.query(StudentProfile).filter_by(user_id=student1.id).first()
    if not p1:
        p1 = StudentProfile(user_id=student1.id, grade=8, preferred_language="English")
        db.add(p1)
        
    p2 = db.query(StudentProfile).filter_by(user_id=student2.id).first()
    if not p2:
        p2 = StudentProfile(user_id=student2.id, grade=8, preferred_language="Assamese")
        db.add(p2)
        
    db.commit()

def seed_concepts(db: Session):
    concepts = [
        {"subject": "Science", "grade": 8, "name": "The Electric Circuit", "difficulty": "intermediate"},
        {"subject": "Science", "grade": 8, "name": "2.1 What Is a Cell?", "difficulty": "beginner"},
        {"subject": "Science", "grade": 8, "name": "3.1 Health: Is It More Than Not Falling Sick?", "difficulty": "beginner"},
        {"subject": "Math", "grade": 8, "name": "Fractions", "difficulty": "beginner"},
        {"subject": "Math", "grade": 8, "name": "Equivalent Fractions", "difficulty": "intermediate"}
    ]
    
    for c_data in concepts:
        c = db.query(Concept).filter_by(subject=c_data["subject"], grade=c_data["grade"], name=c_data["name"]).first()
        if not c:
            c = Concept(**c_data)
            db.add(c)
            
    db.commit()

def seed_sources(db: Session):
    s1 = db.query(Source).filter_by(title="Demo Science Textbook").first()
    if not s1:
        s1 = Source(title="Demo Science Textbook", source_type="book", publisher="Demo Pub")
        db.add(s1)
        
    db.commit()

def seed_questions(db: Session):
    concept_circuit = db.query(Concept).filter_by(name="The Electric Circuit").first()
    concept_cell = db.query(Concept).filter_by(name="2.1 What Is a Cell?").first()
    source_book = db.query(Source).filter_by(title="Demo Science Textbook").first()
    
    if concept_circuit and source_book:
        q1 = db.query(Question).filter_by(question_text="What is required for current to flow?").first()
        if not q1:
            q1 = Question(
                concept_id=concept_circuit.id,
                source_id=source_book.id,
                question_text="What is required for current to flow?",
                question_type="multiple_choice",
                options={"A": "A closed path", "B": "An open path"},
                correct_answer="A",
                difficulty="beginner"
            )
            db.add(q1)
            
    if concept_cell and source_book:
        q2 = db.query(Question).filter_by(question_text="What is a cell?").first()
        if not q2:
            q2 = Question(
                concept_id=concept_cell.id,
                source_id=source_book.id,
                question_text="What is a cell?",
                question_type="multiple_choice",
                options={"A": "The basic structural and functional unit of life", "B": "A small room", "C": "A battery", "D": "A type of virus"},
                correct_answer="A",
                difficulty="beginner"
            )
            db.add(q2)
            db.commit()

def seed_db():
    if not SessionLocal:
        logger.error("Database session not configured.")
        return
        
    db = SessionLocal()
    try:
        logger.info("Seeding users...")
        t, s1, s2 = seed_users(db)
        logger.info("Seeding profiles...")
        seed_profiles(db, s1, s2)
        logger.info("Seeding concepts...")
        seed_concepts(db)
        logger.info("Seeding sources...")
        seed_sources(db)
        logger.info("Seeding questions...")
        seed_questions(db)
        logger.info("Seeding complete.")
    except Exception as e:
        logger.error(f"Error seeding database: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_db()
