from pydantic import BaseModel, Field, constr
from typing import Optional, List

class RetrievalRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=2000, description="The student's question")
    grade: Optional[int] = Field(None, description="Optional grade filter")
    subject: Optional[str] = Field(None, description="Optional subject filter")
    language: Optional[str] = Field(None, description="Optional language filter")
    chapter: Optional[str] = Field(None, description="Optional chapter filter")
    top_k: int = Field(5, ge=1, le=20, description="Number of results to return")

class RetrievalResult(BaseModel):
    chunk_id: str
    text: str
    title: str
    chapter_number: Optional[int] = None
    chapter: Optional[str] = None
    section: Optional[str] = None
    page_start: int
    page_end: int
    subject: str
    grade: int
    language: str
    similarity_score: float

class RetrievalResponse(BaseModel):
    query: str
    results: List[RetrievalResult]
