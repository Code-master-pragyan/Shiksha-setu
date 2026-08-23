import sys
import os
from pathlib import Path
from dotenv import load_dotenv

backend_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(backend_dir))

load_dotenv()

from fastapi.testclient import TestClient
from app.main import app
from app.db.database import SessionLocal
from app.db.models.concept import Concept
from sqlalchemy import select

client = TestClient(app)

# Hardcoded from seed_demo.py
STUDENT_A_ID = "00000000-0000-4000-a000-00000000000a"

def test_end_to_end():
    db = SessionLocal()
    concept = db.scalar(select(Concept).limit(1))
    db.close()
    
    if not concept:
        print("No concepts found in DB. Please ingest knowledge first.")
        return

    print("--- 0. Login as Student ---")
    login_res = client.post("/api/v1/auth/login", json={
        "email": "student@demo.com",
        "password": "demo123",
        "role": "student"
    })
    assert login_res.status_code == 200, login_res.text
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    print("--- 1. Ask a Doubt ---")
    doubt_res = client.post("/api/v1/doubt/ask", json={
        "student_id": STUDENT_A_ID,
        "question": "What is a cell?",
        "subject": "Science",
        "grade": 8,
        "top_k": 3
    }, headers=headers)
    
    assert doubt_res.status_code == 200, doubt_res.text
    doubt_data = doubt_res.json()
    assert "answer" in doubt_data
    assert "citations" in doubt_data
    print("Doubt answered successfully.")

    print("\n--- 2. Generate Practice Question ---")
    prac_gen_res = client.post("/api/v1/practice/generate", json={
        "student_id": STUDENT_A_ID,
        "concept_id": str(concept.id),
        "subject": "Science"
    }, headers=headers)
    
    assert prac_gen_res.status_code == 200, prac_gen_res.text
    prac_gen_data = prac_gen_res.json()
    assert "question_id" in prac_gen_data
    assert "correct_answer" not in prac_gen_data
    question_id = prac_gen_data["question_id"]
    print(f"Practice generated. Difficulty: {prac_gen_data['difficulty']}")

    print("\n--- 3. Attempt Practice Question ---")
    attempt_res = client.post("/api/v1/practice/attempt", json={
        "student_id": STUDENT_A_ID,
        "question_id": question_id,
        "student_answer": "I don't know the answer.",
        "time_taken": 30,
        "hint_used": False
    }, headers=headers)
    
    assert attempt_res.status_code == 200, attempt_res.text
    attempt_data = attempt_res.json()
    assert "mastery_score" in attempt_data
    assert "feedback" in attempt_data
    print(f"Attempt recorded. Correct: {attempt_data['correct']}, New Mastery: {attempt_data['mastery_score']}")

    print("\n--- 4. Generate Next Practice Question ---")
    prac_gen_res2 = client.post("/api/v1/practice/generate", json={
        "student_id": STUDENT_A_ID,
        "concept_id": str(concept.id),
        "subject": "Science"
    }, headers=headers)
    assert prac_gen_res2.status_code == 200, prac_gen_res2.text
    prac_gen_data2 = prac_gen_res2.json()
    print(f"Next Practice generated. Difficulty: {prac_gen_data2['difficulty']}")

    print("\n--- 4.5 Login as Teacher ---")
    teacher_login = client.post("/api/v1/auth/login", json={
        "email": "teacher@demo.com",
        "password": "demo123",
        "role": "teacher"
    })
    assert teacher_login.status_code == 200, teacher_login.text
    teacher_token = teacher_login.json()["access_token"]
    teacher_headers = {"Authorization": f"Bearer {teacher_token}"}

    print("\n--- 5. Teacher Insights ---")
    insights_res = client.get("/api/v1/teacher/insights", headers=teacher_headers)
    assert insights_res.status_code == 200, insights_res.text
    insights_data = insights_res.json()
    assert "total_students" in insights_data
    
    # Check specific student
    student_res = client.get(f"/api/v1/teacher/students/{STUDENT_A_ID}/insights", headers=teacher_headers)
    assert student_res.status_code == 200, student_res.text
    student_data = student_res.json()
    
    # Assert proper standardized error handling by requesting a missing student
    error_res = client.get("/api/v1/teacher/students/123e4567-e89b-12d3-a456-426614174000/insights", headers=teacher_headers)
    assert error_res.status_code == 404
    error_data = error_res.json()
    assert "error" in error_data
    assert error_data["error"]["code"] == "NOT_FOUND"

    print("\nEnd-to-End Test Passed!")

if __name__ == "__main__":
    test_end_to_end()
