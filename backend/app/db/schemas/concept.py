from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID
from datetime import datetime

class ConceptBase(BaseModel):
    subject: str
    grade: int = Field(..., ge=1, le=12)
    name: str
    description: Optional[str] = None
    difficulty: Optional[str] = Field(None, pattern="^(beginner|intermediate|advanced)$")

class ConceptCreate(ConceptBase):
    pass

class ConceptResponse(ConceptBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
