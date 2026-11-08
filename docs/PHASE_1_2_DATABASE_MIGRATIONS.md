# Phase 1.2 Database Migration Design

No migration was applied to the canonical database.

The required reversible Alembic migration adds `auth_sessions`, `password_reset_tokens`, and `auth_rate_limits`. It must include foreign keys to `users`, unique indexes on token digests, indexes on expiry/revocation/session family fields, and downgrade operations dropping indexes before tables. Token values must never be stored directly.

The existing `users` schema only has identity, bcrypt hash, role and active status. It does not support revocation or refresh rotation without new persistent tables.
