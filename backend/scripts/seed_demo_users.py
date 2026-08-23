import os
import sys
from pathlib import Path

backend_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(backend_dir))

from dotenv import load_dotenv
from sqlalchemy import select
import bcrypt
from app.db.database import SessionLocal, engine, Base
from app.db.models.user import User
from app.db.models.student import StudentProfile

# Hardcoded UUIDs for idempotency
DEMO_STUDENT_ID = "00000000-0000-4000-a000-00000000000a"
DEMO_STUDENT_USER_ID = "11111111-1111-4000-a000-11111111111a"
DEMO_TEACHER_USER_ID = "22222222-2222-4000-b000-22222222222b"

def get_password_hash(password: str) -> str:
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def main():
    load_dotenv()
    db = SessionLocal()
    try:
        # Load env vars
        student_email = os.environ.get("DEMO_STUDENT_EMAIL", "student@demo.com")
        student_password = os.environ.get("DEMO_STUDENT_PASSWORD", "demo123")
        teacher_email = os.environ.get("DEMO_TEACHER_EMAIL", "teacher@demo.com")
        teacher_password = os.environ.get("DEMO_TEACHER_PASSWORD", "demo123")
        
        # 1. Seed Demo Student User
        student_user = db.scalar(select(User).where(User.email == student_email))
        hashed_sp = get_password_hash(student_password)
        if not student_user:
            student_user = User(
                id=DEMO_STUDENT_USER_ID,
                name="Demo Student",
                email=student_email,
                role="student",
                hashed_password=hashed_sp
            )
            db.add(student_user)
            db.commit()
        else:
            student_user.hashed_password = hashed_sp
            db.commit()
            
        # Ensure we capture the actual user ID if it existed
        actual_student_user_id = student_user.id
            
        # 2. Seed Demo Student Profile
        student_profile = db.scalar(select(StudentProfile).where(StudentProfile.user_id == actual_student_user_id))
        if not student_profile:
            student_profile = StudentProfile(
                id=DEMO_STUDENT_ID,
                user_id=actual_student_user_id,
                grade=8,
                preferred_language="English"
            )
            db.add(student_profile)
            db.commit()

        # 3. Seed Demo Teacher User
        teacher_user = db.scalar(select(User).where(User.email == teacher_email))
        hashed_tp = get_password_hash(teacher_password)
        if not teacher_user:
            teacher_user = User(
                id=DEMO_TEACHER_USER_ID,
                name="Demo Teacher",
                email=teacher_email,
                role="teacher",
                hashed_password=hashed_tp
            )
            db.add(teacher_user)
            db.commit()
        else:
            teacher_user.hashed_password = hashed_tp
            db.commit()

        actual_teacher_user_id = teacher_user.id

        print("--- DEMO ACCOUNTS SEEDED ---")
        print(f"Student Email: {student_email}")
        print(f"Student User ID: {actual_student_user_id}")
        print(f"Student Profile ID: {student_profile.id}")
        print(f"Teacher Email: {teacher_email}")
        print(f"Teacher User ID: {actual_teacher_user_id}")

    except Exception as e:
        print(f"Error seeding demo users: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    main()
