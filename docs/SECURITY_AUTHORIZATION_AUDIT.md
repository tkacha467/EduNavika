# EduNavika — Security & Authorization Architecture Audit (Phase 1 & 2)

**Audit Completion Date:** October 27, 2026  
**Auditor:** Principal Application Security Engineer & System Reliability Architect  
**Scope:** Authentication Lifecycle, Token & Session Mechanics, Role-Based Access Control (RBAC), Horizontal Data Isolation (IDOR Elimination), Rate Limiting, and Standard/Curriculum Gates.  
**Baseline Commit:** `43be188`  
**Security Status:** **REMEDIATED & HARDENED**

---

## 1. Executive Summary

A comprehensive security audit of EduNavika's authentication, session management, and authorization subsystems was conducted. Prior to remediation, six critical vulnerabilities undermined account security and data confidentiality, notably:
1. Direct disclosure of password reset tokens and links via API responses (Account Takeover).
2. Account enumeration on password reset and login endpoints.
3. Unauthenticated password changes without session verification.
4. Total absence of server-side authorization guards on student adaptive learning and assessment endpoints (Insecure Direct Object References).
5. Hardcoded student standard mocking returning "Grade 10" for all enrolled accounts.
6. Permissive CORS configurations allowing credentials with wildcards.

All identified vulnerabilities have been systematically remediated with server-authoritative security dependencies in `backend/app/core/security.py`, hardened endpoints in `backend/app/api/v1/endpoints/auth.py`, `users.py`, `competitive.py`, `teacher_actions.py`, and `curriculum.py`, and verified with automated test suites.

---

## 2. Security Vulnerability Inventory & Remediation Evidence

### 2.1 SEC-01: Critical Account Takeover via Password Reset Token Leak
- **Vulnerability Class:** CWE-200 (Exposure of Sensitive Information to an Unauthorized Actor) / CWE-640 (Weak Password Recovery Mechanism)
- **Severity:** **CRITICAL (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H — Score: 9.8)**
- **Root Cause:**
  `/api/v1/auth/forgot-password` previously generated a cryptographically random reset token, but returned both `reset_token` and `reset_link` directly inside the HTTP JSON response body. Any anonymous caller requesting a password reset for any victim's email address could immediately read the token from the response and invoke `/api/v1/auth/reset-password` to overwrite the victim's password.
- **Remediation:**
  - Removed all sensitive token and link attributes from the `/api/v1/auth/forgot-password` response schema.
  - Reset tokens are now stored strictly in an in-memory session registry (`RESET_TOKENS`) with a reduced TTL of 15 minutes.
  - Token is single-use and immediately deleted upon consumption.
  - Response body now returns only a generic confirmation message.

### 2.2 SEC-02: User Account Enumeration via Forgot-Password Endpoint
- **Vulnerability Class:** CWE-204 (Observable Response Discrepancy)
- **Severity:** **MEDIUM (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N — Score: 5.3)**
- **Root Cause:**
  When a queried email was not present in the database, `/api/v1/auth/forgot-password` returned `HTTP 404: No account found associated with {email}`, allowing unauthenticated attackers to systematically harvest registered user accounts.
- **Remediation:**
  - Implemented uniform response behavior. Whether the email exists or not, the endpoint returns `HTTP 200 OK` with the exact same message: `"If an account exists associated with this email address, password reset instructions have been recorded."`

### 2.3 SEC-03: Unauthenticated Password Change via Direct Endpoint Call
- **Vulnerability Class:** CWE-306 (Missing Authentication for Critical Function)
- **Severity:** **HIGH (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N — Score: 7.5)**
- **Root Cause:**
  `/api/v1/auth/change-password` accepted `email`, `current_password`, and `new_password` as raw payload fields without requiring an active Bearer JWT session (`Depends(get_current_user)` was absent).
- **Remediation:**
  - Bound `/change-password` directly to `current_user: User = Depends(get_current_user)`.
  - Added horizontal validation asserting `payload.email == current_user.email`; cross-account password changes trigger `HTTP 403 Forbidden`.
  - Enforced minimum password length of 8 characters.

### 2.4 SEC-04: Horizontal Authorization Bypass (IDOR) on Student Data
- **Vulnerability Class:** CWE-639 (Authorization Bypass Through User-Controlled Key)
- **Severity:** **CRITICAL (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N — Score: 8.1)**
- **Root Cause:**
  Endpoints taking `student_id` or `session_id` accepted arbitrary IDs without validating whether the caller owned the corresponding account. A student could query another student's adaptive schedule, profile, or assessment session simply by changing the ID in the request.
- **Remediation:**
  - Built `verify_student_ownership(current_user, target_student_id, db)` in `backend/app/core/security.py`.
  - Enforced ownership verification on:
    - `/api/v1/competitive/assessments/start`
    - `/api/v1/competitive/assessments/{session_id}`
    - `/api/v1/competitive/assessments/{session_id}/save`
    - `/api/v1/competitive/assessments/{session_id}/submit`
    - `/api/v1/users/students/{id}`
    - `/api/v1/users/students/{id}/language`
  - Unauthorized access attempts by other students immediately fail with `HTTP 403 Forbidden`.

### 2.5 SEC-05: Missing Rate Limiting on Sensitive Authentication Routes
- **Vulnerability Class:** CWE-307 (Improper Restriction of Excessive Authentication Attempts)
- **Severity:** **HIGH (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:L — Score: 7.3)**
- **Root Cause:**
  `/login` and `/forgot-password` permitted unlimited requests without throttling, exposing the application to automated credential stuffing and denial of service.
- **Remediation:**
  - Implemented an in-memory sliding-window rate limiter:
    - Maximum 5 failed login attempts per 5-minute rolling window per account.
    - Maximum 5 password reset requests per 5-minute rolling window per account.
  - Exceeding the threshold triggers `HTTP 429 Too Many Requests` with a `Retry-After: 300` header.
  - Successful login instantly resets the failed attempt counter.

### 2.6 SEC-06: Permissive Wildcard CORS Configuration
- **Vulnerability Class:** CWE-942 (Overly Permissive Cross-Domain Whitelist)
- **Severity:** **MEDIUM (CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:H/I:L/A:N — Score: 5.6)**
- **Root Cause:**
  `settings.BACKEND_CORS_ORIGINS = ["*"]` was combined with `allow_credentials=True`, violating browser security standards and risking unauthorized cross-origin requests.
- **Remediation:**
  - Restricted CORS origins to explicit development and staging domains (`http://localhost:3000`, `http://127.0.0.1:3000`, `http://localhost:5173`, `http://127.0.0.1:5173`, `http://localhost:8000`, `http://127.0.0.1:8000`).

---

## 3. Server-Authoritative Role & Permission Matrix

| Operation / Endpoint Group | Anonymous | Student | Teacher | Reviewer | Administrator |
|:---|:---:|:---:|:---:|:---:|:---:|
| **Public Information** (`GET /health`, `GET /competitive/exams`, `GET /standards`) | **ALLOW** | **ALLOW** | **ALLOW** | **ALLOW** | **ALLOW** |
| **Authentication** (`POST /auth/login`, `POST /auth/forgot-password`, `POST /auth/reset-password`) | **ALLOW** | **ALLOW** | **ALLOW** | **ALLOW** | **ALLOW** |
| **Password Change** (`POST /auth/change-password`) | **401** | **OWN ONLY** | **OWN ONLY** | **OWN ONLY** | **OWN ONLY** |
| **Student Profile & Learning History** (`GET /users/students/{id}`) | **401** | **OWN ONLY (403)** | **ALLOW** | **403** | **ALLOW** |
| **Competitive Assessment Start** (`POST /competitive/assessments/start`) | **401** | **OWN ONLY + STD GATED** | **ALLOW** | **403** | **ALLOW** |
| **Assessment Answering & Submit** (`POST /competitive/assessments/{id}/save`, `/submit`) | **401** | **OWN SESSION (403)** | **ALLOW** | **403** | **ALLOW** |
| **Teacher Interventions** (`POST /teacher-actions`, `GET /teachers/{id}/actions`) | **401** | **403** | **ALLOW** | **403** | **ALLOW** |
| **Question Verification Portal** (`GET /competitive/questions/review-queue`, `POST /.../review`) | **401** | **403** | **ALLOW** | **ALLOW** | **ALLOW** |
| **Official NTA Answer-Key Reconciliation** (`POST /competitive/questions/reconcile-answer-keys`) | **401** | **403** | **ALLOW** | **ALLOW** | **ALLOW** |
| **Standard & Curriculum Mutation** (`POST /standards`, `POST /subjects`, `POST /chapters`) | **401** | **403** | **CURRICULUM ONLY** | **403** | **ALLOW (FULL)** |
| **Privileged User Provisioning** (`POST /users` with TEACHER/ADMIN/REVIEWER) | **403** | **403** | **403** | **403** | **ALLOW** |

---

## 4. Session & Token Lifecycle Specifications

1. **Authentication Token Mechanism:**
   - Standard RFC 7519 Bearer JSON Web Tokens (JWT).
   - Signed with HMAC-SHA256 (`HS256`) using server-managed `settings.SECRET_KEY`.
   - Payload contains:
     - `sub`: Authoritative UUID of the user.
     - `exp`: UTC expiration timestamp (default: 7 days).
2. **Token Validation Invariant:**
   - Every incoming request parses the Authorization header (`Bearer <token>`).
   - Tokens with invalid signatures, expired timestamps, or non-existent active user accounts are immediately rejected with `HTTP 401 Unauthorized` and `WWW-Authenticate: Bearer`.
3. **Session Invalidation:**
   - Password changes invalidate old passwords immediately.
   - Client logout removes the Bearer token and role from browser `localStorage`.
   - Reset tokens expire after 15 minutes and are erased upon initial use.
