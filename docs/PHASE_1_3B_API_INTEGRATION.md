# Phase 1.3B API Integration

Implemented: public student-only registration; login creates a persistent `AuthSession`; refresh reads an HttpOnly, SameSite=Lax cookie and rotates through `AuthenticationService`; logout revokes the current refresh-token family. Raw refresh tokens are not returned in JSON.

Not yet implemented: reset endpoints and all throttles still need migration off legacy in-memory state; logout-all/session listing and frontend refresh orchestration remain pending.
