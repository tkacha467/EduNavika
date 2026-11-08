"""Persistent authentication records. Opaque token values are never stored."""
from sqlalchemy import Column, String, DateTime, ForeignKey, Integer, UniqueConstraint
from backend.app.core.database import Base
from backend.app.models.core_models import BaseModelMixin, get_utc_now


class AuthSession(BaseModelMixin, Base):
    __tablename__ = "auth_sessions"
    token_digest = Column(String(64), nullable=False, unique=True, index=True)
    family_id = Column(String(36), nullable=False, index=True)
    parent_session_id = Column(String(36), ForeignKey("auth_sessions.id", ondelete="SET NULL"), nullable=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    expires_at = Column(DateTime(timezone=True), nullable=False, index=True)
    revoked_at = Column(DateTime(timezone=True), nullable=True, index=True)
    replaced_at = Column(DateTime(timezone=True), nullable=True)
    reuse_detected_at = Column(DateTime(timezone=True), nullable=True)


class PasswordResetToken(BaseModelMixin, Base):
    __tablename__ = "password_reset_tokens"
    token_digest = Column(String(64), nullable=False, unique=True, index=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    expires_at = Column(DateTime(timezone=True), nullable=False, index=True)
    consumed_at = Column(DateTime(timezone=True), nullable=True, index=True)
    revoked_at = Column(DateTime(timezone=True), nullable=True, index=True)


class AuthRateLimit(BaseModelMixin, Base):
    __tablename__ = "auth_rate_limits"
    __table_args__ = (UniqueConstraint("scope", "key", "window_started_at", name="uq_auth_rate_limit_window"),)
    scope = Column(String(32), nullable=False, index=True)
    key = Column(String(255), nullable=False)
    window_started_at = Column(DateTime(timezone=True), default=get_utc_now, nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False, index=True)
    attempts = Column(Integer, nullable=False, default=0)
