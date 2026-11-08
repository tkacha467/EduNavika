# Phase 1.3E CSRF Security Review

Implemented: same-origin frontend requests now include browser credentials and attach the CSRF header for `/auth/` requests from the CSRF cookie. Refresh tokens remain HttpOnly and are never read by JavaScript. Backend double-submit plus origin validation remains the enforcement point.

Unverified: signed/session-bound CSRF tokens and adversarial browser tests.
