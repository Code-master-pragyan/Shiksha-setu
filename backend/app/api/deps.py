from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from sqlalchemy import select
from typing import Optional
from pydantic import BaseModel

from app.db.database import get_db
from app.db.models.user import User
from app.db.models.student import StudentProfile
from app.core.security import decode_access_token

# Using a standard bearer token
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login")

class CurrentUser(BaseModel):
    id: str
    role: str
    student_id: Optional[str] = None
    email: str

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> CurrentUser:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception
        
    user_id = payload.get("sub")
    if user_id is None:
        raise credentials_exception
        
    user = db.scalar(select(User).where(User.id == user_id))
    if user is None:
        raise credentials_exception
        
    return CurrentUser(
        id=str(user.id),
        role=user.role,
        student_id=payload.get("student_id"),
        email=user.email
    )

def get_current_user_optional(token: Optional[str] = Depends(OAuth2PasswordBearer(tokenUrl="api/v1/auth/login", auto_error=False)), db: Session = Depends(get_db)) -> Optional[CurrentUser]:
    if not token:
        return None
    try:
        return get_current_user(token=token, db=db)
    except HTTPException:
        return None

def get_current_student(current_user: CurrentUser = Depends(get_current_user)) -> CurrentUser:
    if current_user.role != "student" or not current_user.student_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Requires student privileges",
        )
    return current_user

def get_current_teacher(current_user: CurrentUser = Depends(get_current_user)) -> CurrentUser:
    if current_user.role != "teacher":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Requires teacher privileges",
        )
    return current_user
