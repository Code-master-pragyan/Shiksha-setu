from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from uuid import UUID
from datetime import datetime

class QuestionBase(BaseModel):
    concept_id: UUID
    source_id: Optional[UUID] = None
    question_text: str
    difficulty: Optional[str] = Field(None, pattern="^(beginner|intermediate|advanced)$")
    question_type: Optional[str] = None
    options: Optional[Dict[str, Any]] = None
    correct_answer: str
    explanation: Optional[str] = None

class QuestionCreate(QuestionBase):
    pass

class QuestionResponse(QuestionBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
