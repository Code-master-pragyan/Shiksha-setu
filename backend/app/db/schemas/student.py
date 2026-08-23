from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID
from datetime import datetime

class StudentProfileBase(BaseModel):
    grade: int = Field(..., ge=1, le=12)
    preferred_language: str = "English"

class StudentProfileCreate(StudentProfileBase):
    user_id: UUID

class StudentProfileResponse(StudentProfileBase):
    id: UUID
    user_id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
