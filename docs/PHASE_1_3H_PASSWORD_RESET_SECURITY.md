# Phase 1.3H Password Reset Security

Digest-only persistent reset tokens and session revocation exist, but the API currently commits token consumption before password/session updates. Phase 1.3H must make this a single transaction and verify concurrent consumption.
