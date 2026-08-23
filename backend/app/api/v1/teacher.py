from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.db.database import get_db

from app.api.schemas.teacher import TeacherSummaryResponse, StudentDetailResponse
from app.services.teacher_insights import TeacherInsightService
from app.api.deps import get_current_teacher, CurrentUser

router = APIRouter()

def get_insight_service():
    return TeacherInsightService()

@router.get("/insights", response_model=TeacherSummaryResponse)
def get_teacher_insights(
    grade: Optional[int] = Query(None, description="Filter by student grade"),
    subject: Optional[str] = Query(None, description="Filter by concept subject"),
    concept_id: Optional[str] = Query(None, description="Filter by specific concept ID"),
    status: Optional[str] = Query(None, description="Filter by insight status (e.g. at_risk)"),
    db: Session = Depends(get_db),
    service: TeacherInsightService = Depends(get_insight_service),
    current_teacher: CurrentUser = Depends(get_current_teacher)
):
    try:
        return service.get_class_summary(
            db=db,
            grade=grade,
            subject=subject,
            concept_id=concept_id,
            status_filter=status
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/students/{student_id}/insights", response_model=StudentDetailResponse)
def get_student_insights(
    student_id: str,
    db: Session = Depends(get_db),
    service: TeacherInsightService = Depends(get_insight_service),
    current_teacher: CurrentUser = Depends(get_current_teacher)
):
    try:
        return service.get_student_detail(db=db, student_id=student_id)
    except ValueError as ve:
        raise HTTPException(status_code=404, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
