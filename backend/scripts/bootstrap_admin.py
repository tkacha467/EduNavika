"""Explicit, idempotent administrator bootstrap. Run only after migrations.

Set EDUNAVIKA_BOOTSTRAP_EMAIL, EDUNAVIKA_BOOTSTRAP_PASSWORD and
EDUNAVIKA_BOOTSTRAP_NAME in the environment. Credentials are never logged.
"""
import os
import uuid
from backend.app.core.database import SessionLocal
from backend.app.core.security import get_password_hash
from backend.app.models.core_models import User, UserRole


def main() -> None:
    email = os.environ.get("EDUNAVIKA_BOOTSTRAP_EMAIL", "").strip().lower()
    password = os.environ.get("EDUNAVIKA_BOOTSTRAP_PASSWORD", "")
    name = os.environ.get("EDUNAVIKA_BOOTSTRAP_NAME", "Initial administrator").strip()
    if not email or len(password) < 12:
        raise SystemExit("Set EDUNAVIKA_BOOTSTRAP_EMAIL and a password of at least 12 characters.")
    with SessionLocal() as db:
        existing = db.query(User).filter(User.email == email).first()
        if existing:
            if existing.role != UserRole.ADMIN:
                raise SystemExit("Existing account is not an administrator.")
            return
        db.add(User(id=str(uuid.uuid4()), name=name, email=email, hashed_password=get_password_hash(password), role=UserRole.ADMIN, is_active=True))
        db.commit()


if __name__ == "__main__":
    main()
