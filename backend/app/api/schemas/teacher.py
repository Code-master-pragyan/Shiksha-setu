from typing import List, Optional
from pydantic import BaseModel, Field

class TeacherInsight(BaseModel):
    student_id: str
    concept_id: str
    concept_name: str
    mastery_score: float
    recent_accuracy: Optional[float] = Field(None, description="Recent accuracy as a float from 0.0 to 1.0, or None if zero attempts")
    consecutive_errors: int
    status: str = Field(description="at_risk, needs_attention, improving, on_track")
    trend: str = Field(description="improving, stable, declining, unknown")
    reason: str
    recommended_action: str

class TeacherSummaryResponse(BaseModel):
    total_students: int
    at_risk: int
    needs_attention: int
    improving: int
    on_track: int
    insights: List[TeacherInsight]

class StudentDetailResponse(BaseModel):
    student_id: str
    grade: int
    preferred_language: str
    insights: List[TeacherInsight]
