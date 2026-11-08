# Phase 1.2 Authentication Implementation Design

## Current state

The current backend uses bcrypt password hashes and expiring signed JWT access tokens. It has no registration endpoint, refresh token endpoint, logout endpoint, session table, reset token table, or persistent rate-limit store. `RESET_TOKENS`, `_FAILED_LOGINS`, and `_FORGOT_REQUESTS` in `backend/app/api/v1/endpoints/auth.py` are process-memory dictionaries.

## Required implementation

Introduce a single server-side authentication-session architecture:

1. `POST /auth/register` validates normalized email, password policy and supported enrollment; creates a student user and profile in one transaction.
2. `password_reset_tokens` stores only SHA-256 token digests, user ID, expiry, consumed/revoked timestamps and creation metadata. The emailed opaque value is never returned by an API.
3. `auth_sessions` stores a refresh-token digest, session family ID, parent session, expiry, revoked/replaced timestamps and user ID. A unique digest index and transactionally locked rotation detect reuse: reuse revokes the whole family.
4. Access JWTs include a `jti` and session ID. Logout revokes the session; authorization rejects revoked/expired sessions.
5. `auth_rate_limits` stores scope/key/window/attempt count and expiry with a uniqueness constraint for durable account and IP throttling.

This design must be delivered with migration, endpoint, transactional concurrency, email-provider, and browser-token-storage implementation; none may be represented as complete before tests run.
