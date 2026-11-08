from datetime import datetime, timedelta, timezone
from typing import Any, Union, Optional
import bcrypt
from jose import jwt
from backend.app.core.config import settings
def create_access_token(subject: Union[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        return bcrypt.checkpw(
            plain_password.encode("utf-8")[:72],
            hashed_password.encode("utf-8")
        )
    except Exception:
        return False


def get_password_hash(password: str) -> str:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode("utf-8")[:72], salt).decode("utf-8")


from fastapi import Depends, HTTPException, status

from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from backend.app.core.database import get_db

security_bearer = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security_bearer),
    db: Session = Depends(get_db),
):
    """
    Authenticates request via Bearer JWT token.
    Raises 401 if token is missing, expired, or user is not found.
    """
    if not credentials or not credentials.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required. Missing Bearer token.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = credentials.credentials
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: str = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload. Missing subject claim.",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials. Token expired or invalid signature.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    from backend.app.models.core_models import User
    user = db.query(User).filter(User.id == user_id, User.is_active == True).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authenticated user account not found or deactivated.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


def get_current_reviewer(
    current_user = Depends(get_current_user),
):
    """
    Enforces server-side role-based authorization for question review.
    Permits TEACHER, ADMIN, and REVIEWER roles.
    Rejects STUDENT and unauthorized callers with 403 Forbidden.
    """
    role_val = current_user.role.value if hasattr(current_user.role, "value") else str(current_user.role)
    if role_val.upper() not in ("TEACHER", "ADMIN", "REVIEWER"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Access denied: User with role '{role_val}' is not authorized to perform question review.",
        )
    return current_user


def get_current_teacher(
    current_user = Depends(get_current_user),
):
    """
    Enforces server-side role-based authorization for teacher operations.
    Permits TEACHER and ADMIN roles.
    """
    role_val = current_user.role.value if hasattr(current_user.role, "value") else str(current_user.role)
    if role_val.upper() not in ("TEACHER", "ADMIN"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Access denied: User with role '{role_val}' does not have teacher privileges.",
        )
    return current_user


def get_current_admin(
    current_user = Depends(get_current_user),
):
    """
    Enforces server-side role-based authorization for administrative operations.
    Permits only ADMIN role.
    """
    role_val = current_user.role.value if hasattr(current_user.role, "value") else str(current_user.role)
    if role_val.upper() != "ADMIN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Access denied: User with role '{role_val}' does not have administrator privileges.",
        )
    return current_user


def get_current_student(
    current_user = Depends(get_current_user),
):
    """
    Ensures caller is an authenticated user (STUDENT, TEACHER, or ADMIN).
    """
    return current_user


def verify_student_ownership(
    current_user: Any,
    target_student_id: str,
    db: Session,
) -> None:
    """
    Horizontal Authorization Guard:
    Ensures that a student can only access their own profile, learning events,
    adaptive practice, attempts, and assessments.
    Teachers and Admins are permitted for institutional oversight.
    """
    role_val = current_user.role.value if hasattr(current_user.role, "value") else str(current_user.role)
    if role_val.upper() in ("TEACHER", "ADMIN"):
        return

    # Direct user ID match
    if current_user.id == target_student_id:
        return

    # Check student profile ID match
    from backend.app.models.core_models import StudentProfile
    profile = db.query(StudentProfile).filter(
        StudentProfile.user_id == current_user.id,
        StudentProfile.id == target_student_id
    ).first()
    if profile:
        return

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Access denied: You are not authorized to access another student's private learning records.",
    )


def verify_curriculum_standard_access(
    current_user: Any,
    db: Session,
    standard_id: Optional[str] = None,
    exam_code: Optional[str] = None,
    chapter_id: Optional[str] = None,
) -> None:
    """
    Standard & Curriculum Isolation Guard:
    Enforces Class 10 vs Class 11/12 boundaries based on authoritative database enrollment.
    - Class 10 users cannot access JEE/NEET competitive exams or Class 11/12 curricula.
    - Class 11/12 users access curriculum according to their enrolled standard.
    - Teachers and Admins have institutional access across standards.
    """
    role_val = current_user.role.value if hasattr(current_user.role, "value") else str(current_user.role)
    if role_val.upper() in ("TEACHER", "ADMIN", "REVIEWER"):
        return

    from backend.app.models.core_models import StudentProfile
    from backend.app.models.curriculum_models import Standard, Chapter, Subject

    profile = db.query(StudentProfile).filter(
        (StudentProfile.user_id == current_user.id) | (StudentProfile.id == current_user.id)
    ).first()

    grade_number = 10
    if profile and profile.standard_id:
        std = db.query(Standard).filter(Standard.id == profile.standard_id).first()
        if std and std.grade_number:
            grade_number = std.grade_number

    # Class 10 strict restrictions
    if grade_number == 10:
        if exam_code and exam_code.upper() in ("JEE_MAIN", "JEE_ADVANCED", "NEET_UG"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied: Competitive exam module '{exam_code}' is restricted to Standards 11 and 12.",
            )
        if standard_id:
            target_std = db.query(Standard).filter(Standard.id == standard_id).first()
            if target_std and target_std.grade_number in (11, 12):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Access denied: Class 10 students are not permitted to access Standard {target_std.grade_number} curriculum.",
                )
        if chapter_id:
            chap = db.query(Chapter).filter(Chapter.id == chapter_id).first()
            if chap and chap.subject_id:
                subj = db.query(Subject).filter(Subject.id == chap.subject_id).first()
                if subj and subj.standard_id:
                    c_std = db.query(Standard).filter(Standard.id == subj.standard_id).first()
                    if c_std and c_std.grade_number in (11, 12):
                        raise HTTPException(
                            status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"Access denied: Chapter belongs to Standard {c_std.grade_number} curriculum, restricted for Class 10.",
                        )
