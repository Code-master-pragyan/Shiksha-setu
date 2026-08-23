# ShikshaSetu API Documentation

This document describes the primary REST endpoints available for the frontend application. The backend is configured to accept CORS requests from the domain specified in the `FRONTEND_URL` environment variable.

All standard API errors are returned in the following JSON structure:
```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human readable message describing the error."
  }
}
```

---

## 1. Doubt Solver API

### Ask a Doubt
Submits a student's question and retrieves a personalized, contextually grounded answer.

- **URL:** `/api/v1/doubt/ask`
- **Method:** `POST`
- **Request Body:**
```json
{
  "student_id": "00000000-0000-4000-a000-00000000000a", 
  "question": "What is a cell?",
  "grade": 8,
  "subject": "Science",
  "preferred_language": "English",
  "top_k": 3
}
```
*(Note: `student_id` is optional but highly recommended for personalization.)*

- **Response Body:**
```json
{
  "question": "What is a cell?",
  "answer": "A cell is the basic structural and functional unit of living organisms...",
  "key_points": ["Cells are fundamental units of life", "They can be single or multicellular"],
  "learning_level": "beginner",
  "confidence": "High",
  "citations": [
    {
      "source_title": "Class 8 Science",
      "chapter": "8 - Cell Structure",
      "section": "Introduction",
      "page_start": 90,
      "page_end": 91,
      "citation_text": "Both bricks in a building and cells in the living organisms..."
    }
  ],
  "follow_up_question": "Can you name an organism made of a single cell?"
}
```

---

## 2. Adaptive Practice API

### Generate Practice Question
Generates a new practice question based on the student's mastery level for a specific concept.

- **URL:** `/api/v1/practice/generate`
- **Method:** `POST`
- **Request Body:**
```json
{
  "student_id": "00000000-0000-4000-a000-00000000000a",
  "concept_id": "123e4567-e89b-12d3-a456-426614174000",
  "subject": "Science"
}
```

- **Response Body:**
```json
{
  "question_id": "987e6543-e21b-12d3-a456-426614174999",
  "question_text": "Which part of the cell controls all its activities?",
  "question_type": "multiple_choice",
  "options": ["Nucleus", "Cytoplasm", "Cell Membrane", "Vacuole"],
  "difficulty": "beginner",
  "concept_id": "123e4567-e89b-12d3-a456-426614174000",
  "citations": [ ... ]
}
```
*(Note: The correct answer is not exposed to the frontend.)*

### Submit Attempt
Evaluates the student's answer and updates their mastery score dynamically.

- **URL:** `/api/v1/practice/attempt`
- **Method:** `POST`
- **Request Body:**
```json
{
  "student_id": "00000000-0000-4000-a000-00000000000a",
  "question_id": "987e6543-e21b-12d3-a456-426614174999",
  "student_answer": "Nucleus",
  "time_taken": 45,
  "hint_used": false
}
```

- **Response Body:**
```json
{
  "correct": true,
  "feedback": "Great job! The nucleus acts as the control center of the cell.",
  "mastery_score": 0.40,
  "learning_level": "intermediate",
  "consecutive_errors": 0,
  "next_action": "practice",
  "next_difficulty": "intermediate",
  "citations": [ ... ]
}
```

---

## 3. Teacher Insights API

### Get Class Summary
Retrieves aggregate statistics and deterministic insights for all students.

- **URL:** `/api/v1/teacher/insights`
- **Method:** `GET`
- **Query Parameters:** `?grade=8&subject=Science&concept_id=...&status=at_risk` (All Optional)

- **Response Body:**
```json
{
  "total_students": 30,
  "at_risk": 5,
  "needs_attention": 10,
  "improving": 5,
  "on_track": 10,
  "insights": [
    {
      "student_id": "00000000-0000-4000-a000-00000000000a",
      "concept_id": "123e4567-e89b-12d3-a456-426614174000",
      "concept_name": "Cell Structure",
      "mastery_score": 0.20,
      "recent_accuracy": 0.25,
      "consecutive_errors": 3,
      "status": "at_risk",
      "trend": "declining",
      "reason": "Three or more consecutive errors detected.",
      "recommended_action": "Provide concept review and beginner-level practice."
    }
  ]
}
```

### Get Student Detail
Retrieves detailed insight history for a specific student across all concepts.

- **URL:** `/api/v1/teacher/students/{student_id}/insights`
- **Method:** `GET`

- **Response Body:**
```json
{
  "student_id": "00000000-0000-4000-a000-00000000000a",
  "grade": 8,
  "preferred_language": "English",
  "insights": [ ... ]
}
```
