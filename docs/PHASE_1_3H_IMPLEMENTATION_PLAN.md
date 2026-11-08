# Phase 1.3H Implementation Plan

| Gap | Code change | Required evidence |
|---|---|---|
| Session-bound CSRF | Add CSRF digest/expiry to `AuthSession`, reversible migration, issue/validate/rotate service methods | API forgery, cross-session, expiry, revocation and rotation tests |
| Refresh replay | Replace service-only assumptions with API concurrency tests on isolated DB | Concurrent real transactions; family isolation assertion |
| Reset consumption | Make token consume/password/session invalidation one transaction | Replay/expiry/concurrent consume tests |
| Rate limiting | Atomic upsert/update suitable for target DB | restart/multi-instance/concurrency tests |
| Email | Provider-neutral interface with development adapter | no-token-log/failure tests |

No canonical migration will be executed.
