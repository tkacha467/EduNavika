import secrets
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
from pydantic import BaseModel, EmailStr
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.core.security import (
    create_access_token,
    verify_password,
    get_password_hash,
)
from backend.app.models import User, UserRole

router = APIRouter()

# In-memory secure token store for password resets
# Format: { token: { "email": str, "expires_at": datetime } }
RESET_TOKENS: Dict[str, Dict[str, Any]] = {}


class LoginRequest(BaseModel):
    email: str
    password: str
    role: Optional[str] = None


class ForgotPasswordRequest(BaseModel):
    email: str


class ResetPasswordRequest(BaseModel):
    email: str
    token: str
    new_password: str


class ChangePasswordRequest(BaseModel):
    email: str
    current_password: str
    new_password: str


def ensure_default_accounts(db: Session):
    """Ensure student and teacher default accounts exist in the database."""
    # Student
    s_email = "kachatushar108@gmail.com"
    student = db.query(User).filter(User.email == s_email).first()
    if not student:
        student = User(
            name="Tushar Kacha",
            email=s_email,
            hashed_password=get_password_hash("Tushar@21"),
            role=UserRole.STUDENT,
            is_active=True,
        )
        db.add(student)

    # Teacher
    t_email = "tushar.kacha141862@marwadiuniversity.ac.in"
    teacher = db.query(User).filter(User.email == t_email).first()
    if not teacher:
        teacher = User(
            name="Prof. Tushar Kacha",
            email=t_email,
            hashed_password=get_password_hash("2120@8030"),
            role=UserRole.TEACHER,
            is_active=True,
        )
        db.add(teacher)

    db.commit()


@router.post("/login", summary="User Login")
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    ensure_default_accounts(db)

    email = payload.email.strip().lower()
    user = db.query(User).filter(User.email == email).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password. Please verify your credentials."
        )

    if not verify_password(payload.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password. Please verify your credentials."
        )

    user_role_str = user.role.value.lower()
    token = create_access_token(subject=user.id)

    # Construct user profile data
    initials = "".join([part[0].upper() for part in user.name.split() if part])[:2] or "U"
    
    if user_role_str == "teacher":
        user_data = {
            "id": user.id,
            "email": user.email,
            "full_name": user.name,
            "name": user.name,
            "role": "teacher",
            "initials": initials,
            "grade": "Grade 10",
            "section": "Science",
            "school": "Marwadi University · GSEB Faculty",
            "subjects": "Mathematics & Physics",
            "is_active": user.is_active,
        }
    else:
        user_data = {
            "id": user.id,
            "email": user.email,
            "full_name": user.name,
            "name": user.name,
            "role": "student",
            "initials": initials,
            "grade": "Grade 10",
            "section": "Science",
            "school": "GSEB Higher Secondary School",
            "roll": "STU-2026-0814",
            "joined": "July 2024",
            "streak": 12,
            "weeklyGoal": 85,
            "todayGoal": 3,
            "is_active": user.is_active,
        }

    return {
        "success": True,
        "access_token": token,
        "token_type": "bearer",
        "user": user_data,
    }


@router.post("/forgot-password", summary="Request Password Reset Link")
def forgot_password(payload: ForgotPasswordRequest, db: Session = Depends(get_db)):
    ensure_default_accounts(db)
    email = payload.email.strip().lower()
    user = db.query(User).filter(User.email == email).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No account found associated with {email}"
        )

    # Generate token valid for 60 minutes
    reset_token = secrets.token_urlsafe(32)
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=60)
    RESET_TOKENS[reset_token] = {
        "email": email,
        "expires_at": expires_at,
    }

    reset_link = f"http://localhost:3000/#/reset-password?token={reset_token}&email={email}"

    return {
        "success": True,
        "message": f"Password reset instructions and secure link generated for {email}",
        "email": email,
        "reset_token": reset_token,
        "reset_link": reset_link,
        "expires_in_minutes": 60,
    }


@router.post("/reset-password", summary="Reset Password with Token")
def reset_password(payload: ResetPasswordRequest, db: Session = Depends(get_db)):
    ensure_default_accounts(db)
    token = payload.token.strip()
    email = payload.email.strip().lower()

    token_info = RESET_TOKENS.get(token)
    if not token_info:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired password reset link. Please request a new link."
        )

    if token_info["email"] != email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token email mismatch."
        )

    if datetime.now(timezone.utc) > token_info["expires_at"]:
        del RESET_TOKENS[token]
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password reset token has expired. Please request a new reset link."
        )

    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    user.hashed_password = get_password_hash(payload.new_password)
    db.commit()

    # Invalidate token after single use
    del RESET_TOKENS[token]

    return {
        "success": True,
        "message": "Your password has been successfully reset! You can now log in with your new password.",
    }


@router.post("/change-password", summary="Change Password for Logged In User")
def change_password(payload: ChangePasswordRequest, db: Session = Depends(get_db)):
    ensure_default_accounts(db)
    email = payload.email.strip().lower()
    user = db.query(User).filter(User.email == email).first()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    if not verify_password(payload.current_password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect. Please try again."
        )

    user.hashed_password = get_password_hash(payload.new_password)
    db.commit()

    return {
        "success": True,
        "message": "Password updated successfully!",
    }
