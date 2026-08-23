from typing import List, Optional
from pydantic import BaseModel, Field
from app.ai.schemas import Citation

class DoubtRequest(BaseModel):
    student_id: Optional[str] = Field(None, description="Optional student ID for personalization")
    question: str = Field(..., min_length=1, max_length=1000)
    grade: int = Field(..., ge=1, le=12)
    subject: str = Field(...)
    preferred_language: str = Field("English")
    top_k: int = Field(3, ge=1, le=5)

class DoubtResponse(BaseModel):
    question: str = Field(description="The original question asked by the student")
    answer: str = Field(description="The generated personalized answer")
    key_points: List[str] = Field(description="Key takeaways from the answer")
    learning_level: Optional[str] = Field(None, description="The evaluated learning level used to generate the answer")
    confidence: str = Field(description="High, Medium, or Low confidence based on available context")
    citations: List[Citation] = Field(description="List of textbook citations used to ground the answer")
    follow_up_question: Optional[str] = Field(None, description="A suggested follow-up question to check understanding")
    concept_id: Optional[str] = Field(None, description="The ID of the concept matched to this doubt")
