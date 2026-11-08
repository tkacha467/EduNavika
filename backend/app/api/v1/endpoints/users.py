from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from backend.app.core.database import get_db
from backend.app.core.security import (
    get_password_hash,
    get_current_user,
    verify_student_ownership,
    security_bearer,
)
from backend.app.models import User, StudentProfile, TeacherProfile, UserRole
from backend.app.schemas.user import (
    UserCreate,
    UserResponse,
    StudentProfileCreate,
    StudentProfileResponse,
    StudentLanguageUpdate,
    TeacherProfileCreate,
    TeacherProfileResponse,
)

router = APIRouter()


@router.post("/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED, summary="Create a new user")
def create_user(
    payload: UserCreate,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security_bearer),
    db: Session = Depends(get_db)
):
    # Role escalation guard: only administrators can create privileged accounts (TEACHER, ADMIN, REVIEWER)
    if payload.role and payload.role != UserRole.STUDENT:
        if not credentials:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Privileged user creation (TEACHER, ADMIN, REVIEWER) requires administrator authorization."
            )
        admin_user = get_current_user(credentials, db)
        if admin_user.role != UserRole.ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only administrators can create privileged accounts."
            )

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
def get_user(
    id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.id != id and current_user.role not in (UserRole.ADMIN, UserRole.TEACHER):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: You cannot view another user's account details."
        )
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
def get_student_profile(
    id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    verify_student_ownership(current_user, id, db)
    profile = db.query(StudentProfile).filter(StudentProfile.id == id).first()
    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student profile not found")
    return profile


@router.get("/students/{id}/language", summary="Get student preferred language")
def get_student_language(
    id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    verify_student_ownership(current_user, id, db)
    profile = db.query(StudentProfile).filter(StudentProfile.id == id).first()
    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student profile not found")
    return {
        "student_id": profile.id,
        "preferred_language": profile.preferred_language or "en",
        "supported_languages": ["en", "hi", "gu"],
    }


@router.put("/students/{id}/language", summary="Update student preferred language")
def update_student_language(
    id: str,
    payload: StudentLanguageUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    verify_student_ownership(current_user, id, db)
    profile = db.query(StudentProfile).filter(StudentProfile.id == id).first()
    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student profile not found")
    
    lang = payload.preferred_language.strip().lower()
    if lang not in ("en", "hi", "gu"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported language '{payload.preferred_language}'. Must be one of: en, hi, gu"
        )
    
    profile.preferred_language = lang
    db.commit()
    db.refresh(profile)
    return {
        "student_id": profile.id,
        "preferred_language": profile.preferred_language,
        "message": f"Language preference updated to '{lang}' successfully"
    }


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
