# Phase 1.3H Access Token Revocation

Access JWT expiry remains the configured `ACCESS_TOKEN_EXPIRE_MINUTES` (default 10080 minutes). Logout/logout-all/password reset revoke refresh sessions immediately but do not invalidate already issued access JWTs; maximum exposure is the remaining access-token lifetime.
