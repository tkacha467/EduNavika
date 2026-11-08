# Phase 1.3C Frontend Integration

Backend uses an HttpOnly refresh cookie scoped to `/api/v1/auth`. No frontend orchestration changed in this increment; refresh must be coordinated in a single client promise and terminal failure must clear access state before the frontend can be accepted.
