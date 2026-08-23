from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID
from datetime import datetime

class UserBase(BaseModel):
    name: str
    email: str
    role: str = Field(..., pattern="^(student|teacher)$")

class UserCreate(UserBase):
    pass

class UserResponse(UserBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
