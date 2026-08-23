from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID
from datetime import datetime

class AttemptBase(BaseModel):
    student_id: UUID
    question_id: UUID
    concept_id: UUID
    student_answer: str
    correct: bool
    time_taken: Optional[int] = Field(None, ge=0)
    hint_used: bool = False

class AttemptCreate(AttemptBase):
    pass

class AttemptResponse(AttemptBase):
    id: UUID
    created_at: datetime

    model_config = {"from_attributes": True}
