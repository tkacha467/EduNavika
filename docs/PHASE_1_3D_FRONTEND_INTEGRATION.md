# Phase 1.3D Frontend Integration

Backend now requires `X-CSRF-Token` for cookie-authenticated refresh/logout. The frontend has not yet been updated to read/send the CSRF cookie or coordinate refresh calls, so those paths are not operationally verified.
