import secrets
from typing import Optional
from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException, status, Response, Request
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.core.security import (
    create_access_token,
    verify_password,
    get_password_hash,
    get_current_user,
)
from backend.app.models import User, StudentProfile, Standard, UserRole
from backend.app.services.authentication_service import AuthenticationService
from backend.app.core.config import settings
from backend.app.models.auth_models import AuthSession

router = APIRouter()

CSRF_COOKIE = "edunavika_csrf"
CSRF_HEADER = "X-CSRF-Token"

def _cookie_secure() -> bool:
    return settings.ENV.lower() in {"production", "prod"}

def _csrf(request: Request) -> None:
    cookie = request.cookies.get(CSRF_COOKIE)
    header = request.headers.get(CSRF_HEADER)
    origin = request.headers.get("origin")
    if not cookie or not header or not secrets.compare_digest(cookie, header):
        raise HTTPException(status_code=403, detail="CSRF validation failed.")
    if origin and origin not in settings.BACKEND_CORS_ORIGINS:
        raise HTTPException(status_code=403, detail="CSRF origin validation failed.")

def _set_auth_cookies(response: Response, refresh: str) -> None:
    response.set_cookie("edunavika_refresh", refresh, httponly=True, secure=_cookie_secure(), samesite="lax", max_age=60 * 60 * 24 * 30, path="/api/v1/auth")
    response.set_cookie(CSRF_COOKIE, secrets.token_urlsafe(32), httponly=False, secure=_cookie_secure(), samesite="lax", max_age=60 * 60 * 24 * 30, path="/api/v1/auth")



class LoginRequest(BaseModel):
    email: str
    password: str
    role: Optional[str] = None

class RegisterRequest(BaseModel):
    name: str
    email: str
    password: str


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


@router.post("/login", summary="User Login")
def login(payload: LoginRequest, db: Session = Depends(get_db)):

    email = payload.email.strip().lower()
    lifecycle = AuthenticationService(db)
    if not lifecycle.allow("login", email):
        raise HTTPException(status_code=429, detail="Too many authentication attempts. Please try again later.")

    user = db.query(User).filter(User.email == email).first()

    # Constant-time-like generic error response prevents account enumeration
    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password. Please verify your credentials."
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Account is deactivated. Please contact your system administrator."
        )

    session, refresh_token = lifecycle.create_session(user.id)
    db.commit()
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
        # Resolve authoritative student standard and enrollment from database
        profile = db.query(StudentProfile).filter(
            (StudentProfile.user_id == user.id) | (StudentProfile.id == user.id)
        ).first()

        grade_num = 10
        std_name = "Standard 10"
        std_id = None
        if profile and profile.standard_id:
            std = db.query(Standard).filter(Standard.id == profile.standard_id).first()
            if std:
                grade_num = std.grade_number
                std_name = std.name or f"Standard {std.grade_number}"
                std_id = std.id

        user_data = {
            "id": user.id,
            "email": user.email,
            "full_name": user.name,
            "name": user.name,
            "role": "student",
            "initials": initials,
            "grade": f"Grade {grade_num}",
            "grade_number": grade_num,
            "standard_id": std_id,
            "standard_name": std_name,
            "section": profile.division if profile and profile.division else "A",
            "school": "GSEB Higher Secondary School",
            "roll": profile.enrollment_number if profile and profile.enrollment_number else f"STU-{user.id[:8]}",
            "joined": "Today",
            "streak": 0,
            "weeklyGoal": 0,
            "todayGoal": 0,
            "is_active": user.is_active,
        }

    response = Response()
    _set_auth_cookies(response, refresh_token)
    response.media_type = "application/json"
    response.body = __import__("json").dumps({
        "success": True,
        "access_token": token,
        "token_type": "bearer",
        "user": user_data,
    }).encode()
    return response

@router.post("/register", status_code=status.HTTP_201_CREATED)
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    email = payload.email.strip().lower()
    if len(payload.name.strip()) < 2 or "@" not in email or len(payload.password) < 12:
        raise HTTPException(status_code=400, detail="Invalid registration details.")
    lifecycle = AuthenticationService(db)
    if not lifecycle.allow("register", email):
        raise HTTPException(status_code=429, detail="Too many authentication attempts. Please try again later.")
    if db.query(User).filter(User.email == email).first():
        raise HTTPException(status_code=400, detail="Unable to create account with these details.")
    user = User(name=payload.name.strip(), email=email, hashed_password=get_password_hash(payload.password), role=UserRole.STUDENT, is_active=True)
    db.add(user); db.flush(); db.add(StudentProfile(user_id=user.id)); db.commit()
    return {"success": True, "message": "Account created."}

@router.post("/refresh")
def refresh(request: Request, response: Response, db: Session = Depends(get_db)):
    _csrf(request)
    raw = request.cookies.get("edunavika_refresh")
    rotated = AuthenticationService(db).rotate(raw) if raw else None
    if not rotated:
        response.delete_cookie("edunavika_refresh", path="/api/v1/auth"); response.delete_cookie(CSRF_COOKIE, path="/api/v1/auth")
        raise HTTPException(status_code=401, detail="Authentication session is invalid or expired.")
    session, replacement = rotated
    _set_auth_cookies(response, replacement)
    return {"success": True, "access_token": create_access_token(session.user_id), "token_type": "bearer"}

@router.post("/logout")
def logout(request: Request, response: Response, db: Session = Depends(get_db)):
    _csrf(request)
    raw = request.cookies.get("edunavika_refresh")
    if raw:
        from backend.app.services.authentication_service import digest
        from backend.app.models.auth_models import AuthSession
        session = db.query(AuthSession).filter(AuthSession.token_digest == digest(raw)).first()
        if session: AuthenticationService(db).revoke_family(session.family_id)
    response.delete_cookie("edunavika_refresh", path="/api/v1/auth"); response.delete_cookie(CSRF_COOKIE, path="/api/v1/auth")
    return {"success": True}

@router.post("/logout-all")
def logout_all(response: Response, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    AuthenticationService(db).revoke_all(current_user.id)
    response.delete_cookie("edunavika_refresh", path="/api/v1/auth")
    return {"success": True}

@router.get("/sessions")
def list_sessions(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    sessions = db.query(AuthSession).filter(AuthSession.user_id == current_user.id, AuthSession.revoked_at.is_(None)).all()
    return [{"id": s.id, "created_at": s.created_at, "expires_at": s.expires_at} for s in sessions if s.expires_at > __import__("datetime").datetime.now(__import__("datetime").timezone.utc)]

@router.delete("/sessions/{session_id}")
def revoke_session(session_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    session = db.query(AuthSession).filter(AuthSession.id == session_id, AuthSession.user_id == current_user.id).first()
    if not session: raise HTTPException(status_code=404, detail="Session not found.")
    AuthenticationService(db).revoke_family(session.family_id)
    return {"success": True}


@router.post("/forgot-password", summary="Request Password Reset Link")
def forgot_password(payload: ForgotPasswordRequest, db: Session = Depends(get_db)):
    email = payload.email.strip().lower()
    lifecycle = AuthenticationService(db)
    if not lifecycle.allow("password_reset", email):
        raise HTTPException(status_code=429, detail="Too many authentication attempts. Please try again later.")

    user = db.query(User).filter(User.email == email).first()

    # Generate token only if active user exists, but never leak token in response
    if user and user.is_active:
        lifecycle.issue_reset(user.id)

    # Consistent generic response prevents account enumeration (SEC-01 & SEC-02)
    return {
        "success": True,
        "message": "If an account exists associated with this email address, password reset instructions have been recorded. (Note: Email delivery service is unconfigured in offline mode; reset tokens are maintained in the secure session registry).",
    }


@router.post("/reset-password", summary="Reset Password with Token")
def reset_password(payload: ResetPasswordRequest, db: Session = Depends(get_db)):
    token = payload.token.strip()
    email = payload.email.strip().lower()

    if len(payload.new_password) < 8:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New password must be at least 8 characters in length."
        )

    token_info = AuthenticationService(db).consume_reset(token)
    if not token_info:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired password reset link. Please request a new link."
        )

    if token_info.user_id != (db.query(User.id).filter(User.email == email).scalar()):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token email mismatch."
        )

    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid reset request.")

    user.hashed_password = get_password_hash(payload.new_password)
    db.commit()
    AuthenticationService(db).revoke_all(user.id)

    return {
        "success": True,
        "message": "Your password has been successfully reset! You can now log in with your new password.",
    }


@router.post("/change-password", summary="Change Password for Logged In User")
def change_password(
    payload: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    email = payload.email.strip().lower()
    if email != current_user.email.lower():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: You cannot change the password of another account."
        )

    if not verify_password(payload.current_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect. Please try again."
        )

    if len(payload.new_password) < 8:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New password must be at least 8 characters in length."
        )

    current_user.hashed_password = get_password_hash(payload.new_password)
    db.commit()

    return {
        "success": True,
        "message": "Password updated successfully!",
    }
