from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID
from datetime import datetime

class StudentMasteryBase(BaseModel):
    student_id: UUID
    concept_id: UUID
    mastery_score: float = Field(0.0, ge=0.0, le=1.0)
    attempts: int = Field(0, ge=0)
    correct_attempts: int = Field(0, ge=0)
    consecutive_errors: int = Field(0, ge=0)
    last_attempt_at: Optional[datetime] = None

class StudentMasteryResponse(StudentMasteryBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
