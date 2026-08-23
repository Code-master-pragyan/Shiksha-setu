from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select
from pydantic import BaseModel
from typing import Optional

from app.db.database import get_db
from app.db.models.user import User
from app.db.models.student import StudentProfile
from app.core.security import verify_password, create_access_token

router = APIRouter(prefix="/auth", tags=["auth"])

class LoginRequest(BaseModel):
    email: str
    password: str
    role: str

class UserInfo(BaseModel):
    id: str
    email: str
    name: str
    role: str

class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    user: UserInfo
    student_id: Optional[str] = None

@router.post("/login", response_model=LoginResponse)
def login(req: LoginRequest, db: Session = Depends(get_db)):
    # 1. Find user by email
    user = db.scalar(select(User).where(User.email == req.email))
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )
    
    # 2. Verify password
    if not user.hashed_password or not verify_password(req.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )
        
    # 3. Verify role
    if user.role != req.role:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"User is not registered as a {req.role}",
        )
        
    # 4. Check for student ID
    student_id = None
    if user.role == "student":
        student_profile = db.scalar(select(StudentProfile).where(StudentProfile.user_id == user.id))
        if student_profile:
            student_id = str(student_profile.id)

    # 5. Create token
    access_token = create_access_token(
        data={"sub": str(user.id), "role": user.role, "student_id": student_id}
    )
    
    user_info = UserInfo(
        id=str(user.id),
        email=user.email,
        name=user.name,
        role=user.role
    )
    
    return LoginResponse(
        access_token=access_token,
        token_type="bearer",
        user=user_info,
        student_id=student_id
    )
