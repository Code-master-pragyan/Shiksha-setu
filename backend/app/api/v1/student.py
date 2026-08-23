from fastapi import APIRouter, Depends, HTTPException, Path
from sqlalchemy.orm import Session
from sqlalchemy import select, func, cast, Integer
from typing import List

from app.db.database import get_db
from app.db.models.student import StudentProfile
from app.db.models.user import User
from app.db.models.mastery import StudentMastery
from app.db.models.attempt import Attempt
from app.db.models.concept import Concept
from app.api.schemas.student import StudentDashboardResponse, StudentInfo, ConceptMasteryItem, StudentProfileResponse, StudentProfileUpdate
from app.api.deps import get_current_student, CurrentUser

router = APIRouter(prefix="/students", tags=["students"])

@router.get("/{student_id}/dashboard", response_model=StudentDashboardResponse)
def get_student_dashboard(
    student_id: str = Path(..., description="The UUID of the student profile"),
    db: Session = Depends(get_db),
    current_student: CurrentUser = Depends(get_current_student)
):
    if current_student.student_id != student_id:
        raise HTTPException(status_code=403, detail="Not authorized to access this student's data")
        
    # 1. Fetch student profile and user
    student = db.query(StudentProfile).filter(StudentProfile.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student profile not found")
        
    user = student.user
    if not user:
        raise HTTPException(status_code=404, detail="User for student not found")
        
    student_info = StudentInfo(
        id=str(student.id),
        name=user.name,
        grade=student.grade,
        preferred_language=student.preferred_language
    )
    
    # 2. Fetch all mastery records joined with concepts
    mastery_records = db.query(StudentMastery, Concept).join(Concept).filter(StudentMastery.student_id == student.id).all()
    
    concepts_list: List[ConceptMasteryItem] = []
    total_mastery = 0.0
    
    for mastery, concept in mastery_records:
        concepts_list.append(
            ConceptMasteryItem(
                concept_id=str(concept.id),
                concept_name=concept.name,
                score=mastery.mastery_score,
                attempts=mastery.attempts,
                last_attempt=mastery.last_attempt_at
            )
        )
        total_mastery += mastery.mastery_score
        
    # Calculate overall mastery
    overall_mastery = 0.0
    if len(mastery_records) > 0:
        overall_mastery = total_mastery / len(mastery_records)
        
    # 3. Calculate accuracy rate
    attempts_stats = db.query(
        func.count(Attempt.id).label('total_attempts'),
        func.sum(cast(Attempt.correct, Integer)).label('correct_attempts')
    ).filter(Attempt.student_id == student.id).first()
    
    total_attempts = attempts_stats.total_attempts or 0
    total_correct_attempts = attempts_stats.correct_attempts or 0
        
    return StudentDashboardResponse(
        student=student_info,
        overall_mastery=total_mastery / len(concepts_list) if concepts_list else 0.0,
        accuracy_rate=total_correct_attempts / total_attempts if total_attempts > 0 else 0.0,
        concepts=concepts_list
    )

@router.get("/{student_id}/profile", response_model=StudentProfileResponse)
def get_student_profile(
    student_id: str = Path(..., description="The UUID of the student profile"),
    db: Session = Depends(get_db),
    current_student: CurrentUser = Depends(get_current_student)
):
    if current_student.student_id != student_id:
        raise HTTPException(status_code=403, detail="Not authorized to access this student's data")
        
    student = db.scalar(select(StudentProfile).where(StudentProfile.id == student_id))
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
        
    user = student.user
    
    return StudentProfileResponse(
        id=str(student.id),
        user_id=str(user.id),
        name=user.name,
        email=user.email,
        grade=student.grade,
        preferred_language=student.preferred_language
    )

@router.patch("/{student_id}/profile", response_model=StudentProfileResponse)
def update_student_profile(
    req: StudentProfileUpdate,
    student_id: str = Path(..., description="The UUID of the student profile"),
    db: Session = Depends(get_db),
    current_student: CurrentUser = Depends(get_current_student)
):
    if current_student.student_id != student_id:
        raise HTTPException(status_code=403, detail="Not authorized to access this student's data")
        
    student = db.scalar(select(StudentProfile).where(StudentProfile.id == student_id))
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
        
    if req.preferred_language is not None:
        student.preferred_language = req.preferred_language
        
    db.commit()
    
    user = student.user
    return StudentProfileResponse(
        id=str(student.id),
        user_id=str(user.id),
        name=user.name,
        email=user.email,
        grade=student.grade,
        preferred_language=student.preferred_language
    )
