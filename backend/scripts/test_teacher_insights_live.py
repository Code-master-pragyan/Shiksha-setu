import sys
from pathlib import Path

backend_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(backend_dir))

from sqlalchemy import select
from app.db.database import SessionLocal
from app.db.models.student import StudentProfile
from app.db.models.concept import Concept
from app.db.models.mastery import StudentMastery
from app.db.models.attempt import Attempt
from app.services.teacher_insights import TeacherInsightService

from dotenv import load_dotenv

def main():
    load_dotenv()
    db = SessionLocal()
    
    try:
        # Create some students and a concept or find existing ones
        concept = db.scalar(select(Concept).limit(1))
        students = db.scalars(select(StudentProfile).limit(5)).all()
        
        if not concept or len(students) < 5:
            print("Need at least 1 concept and 5 students in DB for this test.")
            return

        print("Setting up mock data...")
        
        # Clear existing masteries and attempts for these students and this concept
        student_ids = [s.id for s in students]
        
        # We'll just modify the mastery directly to match the test scenarios
        
        # Student A: at_risk (mastery=0.20, cons_errors=3)
        # Student B: needs_attention (mastery=0.40, recent_accuracy < 0.50)
        # Student C: on_track (mastery=0.60, recent_accuracy=0.80)
        # Student D: improving (mastery=0.40, recent_accuracy > older_accuracy + 0.20)
        # Student E: unknown (zero attempts)

        scenarios = [
            (0.20, 3, [False, False, False]), # Student A
            (0.40, 1, [True, False, False, False, True]), # Student B (40% recent)
            (0.60, 0, [True, True, True, False, True]), # Student C (80% recent)
            (0.60, 0, [False, False, False, False, False, True, True, True, True, False]), # Student D (0% older, 80% recent = improving)
            (0.35, 0, []) # Student E
        ]
        
        for i, (student, (score, errors, attempts_bools)) in enumerate(zip(students, scenarios)):
            # Upsert mastery
            mastery = db.scalar(select(StudentMastery).where(StudentMastery.student_id == student.id, StudentMastery.concept_id == concept.id))
            if not mastery:
                mastery = StudentMastery(
                    student_id=student.id,
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
            
            # Delete old mock attempts
            db.query(Attempt).filter(Attempt.student_id == student.id).delete()
            
            # Insert mock attempts
            for is_correct in attempts_bools:
                # we don't care about the question_id for this test, we can just use concept.id as a fake uuid for question_id if it works, or we need a real question
                # Actually attempt model has question_id foreign key, so we need a real question id.
                from app.db.models.question import Question
                q = db.scalar(select(Question).limit(1))
                if not q:
                    # make a dummy question
                    q = Question(concept_id=concept.id, question_text="Q?", correct_answer="A")
                    db.add(q)
                    db.commit()
                
                attempt = Attempt(
                    student_id=student.id,
                    question_id=q.id,
                    concept_id=concept.id,
                    student_answer="X",
                    correct=is_correct
                )
                db.add(attempt)
            db.commit()
            
        print("Setup complete.\n")
        print("="*60)
        print("TEACHER INSIGHT REPORT")
        print("="*60)
        
        service = TeacherInsightService()
        
        for student in students:
            res = service.get_student_detail(db, str(student.id))
            if res.insights:
                insight = res.insights[0]
                print(f"Student: {insight.student_id}")
                print(f"Concept: {insight.concept_name}")
                print(f"Mastery: {insight.mastery_score}")
                print(f"Recent Accuracy: {insight.recent_accuracy}")
                print(f"Consecutive Errors: {insight.consecutive_errors}")
                print(f"Trend: {insight.trend}")
                print(f"Status: {insight.status}")
                print(f"Reason: {insight.reason}")
                print(f"Recommended Action: {insight.recommended_action}")
                print("-" * 60)
            
        print("\nCLASS SUMMARY")
        print("="*60)
        
        summary = service.get_class_summary(db)
        print(f"Total students: {summary.total_students}")
        print(f"At risk: {summary.at_risk}")
        print(f"Needs attention: {summary.needs_attention}")
        print(f"Improving: {summary.improving}")
        print(f"On track: {summary.on_track}")

    finally:
        db.close()
        
if __name__ == "__main__":
    main()
