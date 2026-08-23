from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field

class StudentInfo(BaseModel):
    id: str
    name: str
    grade: int
    preferred_language: str

class ConceptMasteryItem(BaseModel):
    concept_id: str
    concept_name: str
    score: float = Field(..., ge=0.0, le=1.0)
    attempts: int
    last_attempt: Optional[datetime]

class StudentDashboardResponse(BaseModel):
    student: StudentInfo
    overall_mastery: float = Field(..., ge=0.0, le=1.0)
    accuracy_rate: float = Field(..., ge=0.0, le=1.0)
    concepts: List[ConceptMasteryItem]

class StudentProfileResponse(BaseModel):
    id: str
    user_id: str
    name: str
    email: str
    grade: int
    preferred_language: str

class StudentProfileUpdate(BaseModel):
    preferred_language: Optional[str] = None
