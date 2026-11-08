# Phase 0 Security Audit

## Verified controls

- Passwords use bcrypt hashing and verification in `backend/app/core/security.py`.
- JWT validation checks signature, expiry, subject, active user status, and bearer presence.
- Reviewer, teacher, and admin dependencies enforce server-side role checks.
- Student ownership is checked through `verify_student_ownership`; curriculum access applies a grade/exam restriction helper.
- Login and forgot-password paths use generic responses and simple five-attempt, five-minute process-local throttles.
- Targeted tests completed with 64 passed and 1 failed; the failure was an external hard-coded database expectation, not an observed mutation of `D:\EduNavika\edunavika.db`.

## Findings

| Severity | Finding | Risk | Evidence | Required remediation |
|---|---|---|---|---|
| Critical | Default JWT secret is checked into code. | Token forgery if deployment omits environment configuration. | `backend/app/core/config.py` | Fail startup outside test/dev when a high-entropy externally supplied secret is absent; rotate any deployed secret. |
| Critical | Default user accounts with plaintext source passwords are auto-created on non-test startup for an empty database. | Unauthorized access and credential disclosure. | `auth.py:ensure_default_accounts`; `main.py:on_startup` | Remove production seeding; move fixture users to tests only; rotate exposed credentials. |
| High | No token revocation/session store or explicit server logout endpoint was found. Password changes/resets do not invalidate issued JWTs. | Stolen bearer token remains valid to expiry. | `security.py:create_access_token`, auth routes | Add token/session versioning or a revocation store; invalidate on password change/reset/logout. |
| High | Reset tokens and throttles reside in process memory. | Tokens disappear on restart and limits can be bypassed across processes. | `auth.py` module globals | Use a transactional/TTL-backed store and IP + account abuse controls. |
| Medium | CORS permits local origins only, which is appropriate for development but not a production origin allowlist. | Deployment misconfiguration risk. | `config.py:BACKEND_CORS_ORIGINS` | Make production origins explicit and environment-owned. |
| Medium | Startup schema creation and content sync may mutate the configured database. | Accidental mutation when an environment is misclassified. | `main.py:on_startup` | Run migrations/seeding as explicit deployment jobs; make application startup read-only. |

## Authorization assessment

The current source includes meaningful role and ownership controls and targeted tests exercise anonymous, role, and cross-student cases. This is not a complete route-by-route proof: the full suite cannot presently collect, and every endpoint should be catalogued against an explicit authorization policy before release.
