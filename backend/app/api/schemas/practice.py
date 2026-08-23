from typing import Optional, List
from pydantic import BaseModel, Field
from app.ai.schemas import Citation

class PracticeGenerateRequest(BaseModel):
    student_id: str = Field(..., description="The unique ID of the student")
    concept_id: str = Field(..., description="The unique ID of the concept to practice")
    subject: str = Field(..., description="The subject name (e.g. Science)")

class PracticeGenerateResponse(BaseModel):
    question_id: str = Field(description="The unique ID of the generated question")
    question_text: str = Field(description="The text of the practice question")
    question_type: str = Field(description="Type of question (e.g. multiple_choice, short_answer)")
    options: Optional[List[str]] = Field(None, description="List of options for multiple choice questions")
    difficulty: str = Field(description="The difficulty level (beginner, intermediate, advanced)")
    concept_id: str = Field(description="The associated concept ID")
    citations: List[Citation] = Field(description="Citations from the textbook")

class PracticeAttemptRequest(BaseModel):
    student_id: str = Field(..., description="The unique ID of the student")
    question_id: str = Field(..., description="The ID of the question being answered")
    student_answer: str = Field(..., description="The student's answer text")
    time_taken: Optional[int] = Field(None, description="Time taken to answer in seconds")
    hint_used: bool = Field(False, description="Whether a hint was used")

class PracticeAttemptResponse(BaseModel):
    correct: bool = Field(description="Whether the answer was correct")
    feedback: str = Field(description="Constructive feedback explaining the answer")
    mastery_score: float = Field(description="The new mastery score for this concept (0.0 to 1.0)")
    learning_level: str = Field(description="The updated learning level of the student")
    consecutive_errors: int = Field(description="Current streak of incorrect answers")
    next_action: str = Field(description="The next recommended action (practice or review)")
    next_difficulty: str = Field(description="The recommended difficulty for the next question")
    citations: List[Citation] = Field(description="Citations from the textbook grounding the feedback")
