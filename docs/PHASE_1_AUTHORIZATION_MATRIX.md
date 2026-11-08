# Phase 1 Authorization Matrix

| Capability | Student | Teacher | Reviewer | Admin |
|---|---:|---:|---:|---:|
| Own learning record | Yes | Oversight | No | Yes |
| Other student record | No | Yes | No | Yes |
| Question review | No | Yes | Yes | Yes |
| Teacher operations | No | Yes | No | Yes |
| Competitive curriculum for Class 10 | No | Yes | Yes | Yes |

Server-side ownership, reviewer, teacher, admin, and curriculum-standard helpers are in `backend/app/core/security.py`. A complete endpoint inventory remains required before release.
