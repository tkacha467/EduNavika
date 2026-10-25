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

