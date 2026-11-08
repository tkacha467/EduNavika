# Phase 1.3H CSRF Session Binding

**Critical gap:** the current double-submit CSRF value is random but not bound to `AuthSession`; equality alone does not prevent cookie injection. Recommended design: persist a SHA-256 CSRF digest and expiry on each refresh session, issue the raw token only in the readable CSRF cookie, and require digest/session/expiry validation before refresh or logout. Rotation issues a new session-bound CSRF value; revocation invalidates it implicitly.
