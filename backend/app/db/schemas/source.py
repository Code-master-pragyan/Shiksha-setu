from pydantic import BaseModel, Field, AnyHttpUrl
from typing import Optional
from uuid import UUID
from datetime import datetime

class SourceBase(BaseModel):
    title: str
    publisher: Optional[str] = None
    chapter: Optional[str] = None
    section: Optional[str] = None
    page: Optional[int] = Field(None, ge=1)
    url: Optional[AnyHttpUrl] = None
    language: str = "English"
    source_type: str

class SourceCreate(SourceBase):
    pass

class SourceResponse(SourceBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
