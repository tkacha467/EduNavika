# Phase 1.3 Authentication Architecture

Phase 1.3 introduces three persistent records: `auth_sessions` for hashed opaque refresh tokens and token-family metadata, `password_reset_tokens` for single-use hashed reset tokens, and `auth_rate_limits` for database-backed throttling. No opaque token value is represented in the schema.

The required endpoint implementation remains pending: registration, refresh rotation with row locking/reuse-family revocation, logout/session listing, reset delivery abstraction, and rate-limit integration must use these tables transactionally.
