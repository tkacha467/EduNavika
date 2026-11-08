# Phase 1.3D CSRF Security

Refresh and logout now require a double-submit CSRF token: a non-HttpOnly `edunavika_csrf` cookie must match `X-CSRF-Token`; supplied origins are checked against configured origins. Refresh tokens remain HttpOnly, SameSite=Lax, scoped to `/api/v1/auth`, and use `Secure` in production. Frontend header integration and adversarial tests remain pending.
