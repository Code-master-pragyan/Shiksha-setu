import os
import sys

# Add the parent directory to sys.path to allow imports from app
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.db.database import SessionLocal
from app.db.models.student import StudentProfile
from app.api.v1.student import get_student_dashboard

def main():
    db = SessionLocal()
    
    # Get the first student
    student = db.query(StudentProfile).first()
    
    if not student:
        print("No student found in DB")
        return
        
    print(f"Testing dashboard for student ID: {student.id}")
    
    try:
        dashboard = get_student_dashboard(student_id=str(student.id), db=db)
        
        print("\n==============================")
        print("STUDENT DASHBOARD")
        print("==============================\n")
        print(f"Student: {dashboard.student.name}")
        print(f"Grade: {dashboard.student.grade}")
        print(f"Language: {dashboard.student.preferred_language}")
        print(f"Overall mastery: {dashboard.overall_mastery:.2f}")
        print(f"Accuracy Rate: {dashboard.accuracy_rate:.2f}")
        
        print("\nConcepts:")
        for c in dashboard.concepts:
            print(f"- {c.concept_name}: {c.score:.2f} (Attempts: {c.attempts})")
            
        print("\n(Note: Recent Doubts is NOT backed by real data because there is no Doubt table in DB)")
        
    except Exception as e:
        print(f"Failed to fetch dashboard: {e}")

if __name__ == "__main__":
    main()
