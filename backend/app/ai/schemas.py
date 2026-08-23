from typing import List, Optional
from pydantic import BaseModel, Field

class Citation(BaseModel):
    source_title: str
    chapter: str
    section: Optional[str] = None
    page_start: int
    page_end: int
    citation_text: str

class DoubtAnswer(BaseModel):
    answer: str = Field(description="The detailed answer to the student's question")
    key_points: List[str] = Field(description="List of key points")
    confidence: str = Field(description="high, medium, or low")
    citations: List[Citation] = Field(description="List of citations from the context")
    follow_up_question: Optional[str] = Field(None, description="A follow-up question for the student")

class PracticeQuestion(BaseModel):
    question_text: str = Field(description="The text of the generated question")
    question_type: str = Field(description="'multiple_choice' or 'short_answer'")
    options: Optional[List[str]] = Field(None, description="List of options if multiple choice, exactly 4 options.")
    correct_answer: str = Field(description="The correct answer text or the letter for multiple choice")
    explanation: str = Field(description="Explanation of why the answer is correct")
    difficulty: str = Field(description="'beginner', 'intermediate', or 'advanced'")

class ShortAnswerEvaluation(BaseModel):
    is_correct: bool = Field(description="True if the student's answer is semantically correct, False otherwise")
    confidence: str = Field(description="high, medium, or low")
    brief_feedback: str = Field(description="Brief constructive feedback for the student")
