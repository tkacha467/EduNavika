from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.app.core.database import get_db
from backend.app.core.security import get_password_hash
from backend.app.models import User, StudentProfile, TeacherProfile, UserRole
from backend.app.schemas.user import (
    UserCreate,
    UserResponse,
    StudentProfileCreate,
    StudentProfileResponse,
    TeacherProfileCreate,
    TeacherProfileResponse,
)

router = APIRouter()


@router.post("/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED, summary="Create a new user")
def create_user(payload: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == payload.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with this email already exists"
        )
    user_data = payload.model_dump(exclude={"password"})
    user = User(
        **user_data,
        hashed_password=get_password_hash(payload.password)
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.get("/users/{id}", response_model=UserResponse, summary="Get user by ID")
def get_user(id: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


@router.post("/students", response_model=StudentProfileResponse, status_code=status.HTTP_201_CREATED, summary="Create a student profile")
def create_student_profile(payload: StudentProfileCreate, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == payload.user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    if user.role != UserRole.STUDENT:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User does not have STUDENT role")
    
    existing = db.query(StudentProfile).filter(StudentProfile.user_id == payload.user_id).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Student profile already exists for this user")

    profile = StudentProfile(**payload.model_dump())
    db.add(profile)
    db.commit()
    db.refresh(profile)
    return profile


@router.get("/students/{id}", response_model=StudentProfileResponse, summary="Get student profile by ID")
def get_student_profile(id: str, db: Session = Depends(get_db)):
    profile = db.query(StudentProfile).filter(StudentProfile.id == id).first()
    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student profile not found")
    return profile


@router.post("/teachers", response_model=TeacherProfileResponse, status_code=status.HTTP_201_CREATED, summary="Create a teacher profile")
def create_teacher_profile(payload: TeacherProfileCreate, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == payload.user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    if user.role != UserRole.TEACHER:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User does not have TEACHER role")

    existing = db.query(TeacherProfile).filter(TeacherProfile.user_id == payload.user_id).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Teacher profile already exists for this user")

    profile = TeacherProfile(**payload.model_dump())
    db.add(profile)
    db.commit()
    db.refresh(profile)
    return profile


@router.get("/teachers/{id}", response_model=TeacherProfileResponse, summary="Get teacher profile by ID")
def get_teacher_profile(id: str, db: Session = Depends(get_db)):
    profile = db.query(TeacherProfile).filter(TeacherProfile.id == id).first()
    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Teacher profile not found")
    return profile
