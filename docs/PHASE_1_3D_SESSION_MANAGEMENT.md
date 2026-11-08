# Phase 1.3D Session Management

Added authenticated `GET /auth/sessions` with safe metadata only and owner-scoped `DELETE /auth/sessions/{session_id}`. Cross-account IDs return not found. Logout revokes the current family and logout-all revokes all refresh sessions. Access JWTs remain valid until their existing expiry; immediate access-token revocation is not implemented.
