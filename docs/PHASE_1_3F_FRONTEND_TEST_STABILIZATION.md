# Phase 1.3F Frontend Test Stabilization

Replaced the obsolete default-account assertion with fail-closed authentication assertions. Added a deterministic `fetch` mock at the shared frontend test boundary, preventing real relative API requests. `npm test` now passes 37 tests; expected error-state logging remains noisy but originates from mocked failures.
