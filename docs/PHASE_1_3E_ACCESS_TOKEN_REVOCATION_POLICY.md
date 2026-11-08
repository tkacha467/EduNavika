# Phase 1.3E Access Token Revocation Policy

The current architecture uses bounded access-token revocation: access JWTs remain valid until their configured expiry; refresh sessions are revoked immediately on logout, logout-all and password reset. Immediate JWT denylisting is not implemented and must not be claimed.
