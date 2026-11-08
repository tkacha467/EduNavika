"""Transactional persistence primitives for authentication lifecycle endpoints."""
import hashlib
import secrets
import uuid
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from backend.app.models.auth_models import AuthSession, PasswordResetToken, AuthRateLimit


def now() -> datetime:
    return datetime.now(timezone.utc)


def digest(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


class AuthenticationService:
    def __init__(self, db: Session): self.db = db

    def create_session(self, user_id: str, parent: AuthSession | None = None) -> tuple[AuthSession, str]:
        raw = secrets.token_urlsafe(48)
        session = AuthSession(id=str(uuid.uuid4()), user_id=user_id, token_digest=digest(raw), family_id=parent.family_id if parent else str(uuid.uuid4()), parent_session_id=parent.id if parent else None, expires_at=now() + timedelta(days=30))
        self.db.add(session)
        return session, raw

    def rotate(self, raw: str) -> tuple[AuthSession, str] | None:
        session = self.db.query(AuthSession).filter(AuthSession.token_digest == digest(raw)).with_for_update().first()
        if not session: return None
        if session.revoked_at or session.expires_at <= now() or session.replaced_at:
            self.db.query(AuthSession).filter(AuthSession.family_id == session.family_id, AuthSession.revoked_at.is_(None)).update({AuthSession.revoked_at: now()}, synchronize_session=False)
            if session.replaced_at: session.reuse_detected_at = now()
            self.db.commit(); return None
        session.replaced_at = now()
        created = self.create_session(session.user_id, session)
        self.db.commit()
        return created

    def revoke_family(self, family_id: str) -> None:
        self.db.query(AuthSession).filter(AuthSession.family_id == family_id, AuthSession.revoked_at.is_(None)).update({AuthSession.revoked_at: now()}, synchronize_session=False); self.db.commit()

    def revoke_all(self, user_id: str) -> None:
        self.db.query(AuthSession).filter(AuthSession.user_id == user_id, AuthSession.revoked_at.is_(None)).update({AuthSession.revoked_at: now()}, synchronize_session=False); self.db.commit()

    def issue_reset(self, user_id: str) -> str:
        raw = secrets.token_urlsafe(48)
        self.db.add(PasswordResetToken(id=str(uuid.uuid4()), user_id=user_id, token_digest=digest(raw), expires_at=now() + timedelta(minutes=15)))
        self.db.commit(); return raw

    def consume_reset(self, raw: str) -> PasswordResetToken | None:
        token = self.db.query(PasswordResetToken).filter(PasswordResetToken.token_digest == digest(raw)).with_for_update().first()
        if not token or token.consumed_at or token.revoked_at or token.expires_at <= now(): return None
        token.consumed_at = now(); self.db.commit(); return token

    def allow(self, scope: str, key: str, limit: int = 5, seconds: int = 300) -> bool:
        cutoff = now() - timedelta(seconds=seconds)
        row = self.db.query(AuthRateLimit).filter(AuthRateLimit.scope == scope, AuthRateLimit.key == key, AuthRateLimit.expires_at > now()).with_for_update().first()
        if not row:
            row = AuthRateLimit(id=str(uuid.uuid4()), scope=scope, key=key, attempts=0, expires_at=now() + timedelta(seconds=seconds)); self.db.add(row)
        row.attempts += 1; self.db.commit()
        return row.attempts <= limit
