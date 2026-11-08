# EduNavika — Curriculum & Standard Access Policy (Phase 3)

**Document Version:** 1.0.0  
**Effective Date:** October 27, 2026  
**Auditor:** Principal Full-Stack Architect & Educational Policy Lead  
**Applicability:** Standards 10, 11, and 12 (GSEB / NCERT) & Competitive Exam Preparation (JEE Main, JEE Advanced, NEET UG)

---

## 1. Product Context & Objectives

EduNavika serves secondary and higher secondary school students across Gujarat State Secondary and Higher Secondary Education Board (GSEB) and NCERT curricula:
- **Standard 10 (Secondary School Certificate - SSC):** General foundational curriculum (Science, Mathematics, Social Studies, English, Gujarati, Hindi). Students at this stage have not chosen specialized streams (Science / Commerce / Arts).
- **Standards 11 & 12 (Higher Secondary Certificate - HSC Science):** Advanced pre-university science streams (Group A: Physics, Chemistry, Mathematics; Group B: Physics, Chemistry, Biology). These students actively prepare for competitive national examinations (JEE Main, JEE Advanced, NEET UG).

**Core Safety Mandate:**
Under no circumstances may Standard 10 students be exposed to, confused by, or served Standard 11–12 advanced science or competitive entrance test modules through direct API manipulation, query parameter tampering, dashboard widgets, recommendations, or search results.

---

## 2. Authoritative Enrollment Source

1. **Standard & Stream Determination:**
   - The authoritative source of a student's enrolled grade is the relational database record:
     `User.id -> StudentProfile.standard_id -> Standard.grade_number`
   - Client-supplied `grade` strings, URL tokens, and request body parameters are treated as untrusted hints and are **never** used to determine access eligibility.
2. **Fallback & Cold-Start Policy:**
   - If an account has an incomplete or missing `standard_id`, the system defaults to `grade_number = 10` (the least-privilege foundational standard) and logs an auditable notice, rather than granting speculative access to senior competitive curricula.

---

## 3. Curriculum Access Rules by Standard

### 3.1 Standard 10 (Class 10)
- **Permitted Scope:**
  - Standard 10 textbook chapters, syllabus navigation, and formative exercises.
  - Class 10 adaptive practice, spaced revision recommendations, and board examination preparation.
- **Strict Prohibitions:**
  - **No Competitive Examinations:** `JEE_MAIN`, `JEE_ADVANCED`, and `NEET_UG` are restricted. Calls to `/api/v1/competitive/assessments/start` with competitive exam codes return `HTTP 403 Forbidden`.
  - **No Standard 11–12 Curricula:** Direct API requests to `/api/v1/curriculum/standards/{id}/subjects` or `/api/v1/competitive/chapters/{chapter_id}/questions` targeting Standard 11 or 12 return `HTTP 403 Forbidden`.
  - **No Leakage:** Chapter-wise recommendation algorithms and search results filter candidates to the student's enrolled standard.
  - **No Empty Cards:** Frontend UI renders zero competitive preparation cards or dead exam navigation for Standard 10 profiles.

### 3.2 Standards 11 & 12 (Classes 11 and 12 Science)
- **Permitted Scope:**
  - Standard-appropriate HSC Science subjects (Physics, Chemistry, Mathematics, Biology).
  - Competitive entrance modules:
    - **Group A (Mathematics stream):** Eligible for `JEE_MAIN` and `JEE_ADVANCED`.
    - **Group B (Biology stream):** Eligible for `NEET_UG`.
  - Full-length and chapter-specific computer-based mock tests with server-authoritative timers.
- **Cross-Standard Revision Rules:**
  - Standard 12 students are permitted to access Standard 11 foundational topics where designated as official prerequisites in the NCERT syllabus map.
  - Standard 11 students may not access Standard 12 content in advance unless explicitly marked as preview-eligible by a teacher intervention.

---

## 4. Comprehensive Curriculum Access Matrix

| Role & Assigned Standard | Class 10 Curriculum | Class 11 Science Curriculum | Class 12 Science Curriculum | JEE Main / JEE Adv Mock Tests | NEET UG Mock Tests |
|:---|:---:|:---:|:---:|:---:|:---:|
| **Anonymous Visitor** | Read-Only Summary | Read-Only Summary | Read-Only Summary | **401 Unauthorized** | **401 Unauthorized** |
| **Student (Standard 10)** | **FULL ACCESS** | **403 FORBIDDEN** | **403 FORBIDDEN** | **403 FORBIDDEN** | **403 FORBIDDEN** |
| **Student (Standard 11 - Group A)** | Prerequisite Review | **FULL ACCESS** | **403 FORBIDDEN** | **FULL ACCESS** | **403 (Stream Gate)** |
| **Student (Standard 11 - Group B)** | Prerequisite Review | **FULL ACCESS** | **403 FORBIDDEN** | **403 (Stream Gate)** | **FULL ACCESS** |
| **Student (Standard 12 - Group A)** | Prerequisite Review | **FULL (Prerequisites)** | **FULL ACCESS** | **FULL ACCESS** | **403 (Stream Gate)** |
| **Student (Standard 12 - Group B)** | Prerequisite Review | **FULL (Prerequisites)** | **FULL ACCESS** | **403 (Stream Gate)** | **FULL ACCESS** |
| **Teacher** | **FULL ACCESS** | **FULL ACCESS** | **FULL ACCESS** | **FULL ACCESS** | **FULL ACCESS** |
| **Reviewer** | Content Review | Content Review | Content Review | Question Audit Queue | Question Audit Queue |
| **Administrator** | Full Admin | Full Admin | Full Admin | Full Admin | Full Admin |

---

## 5. Backend Enforcement Architecture

Enforcement is centralized in `backend/app/core/security.py`:
```python
verify_curriculum_standard_access(
    current_user: User,
    db: Session,
    standard_id: Optional[str] = None,
    exam_code: Optional[str] = None,
    chapter_id: Optional[str] = None,
) -> None
```
- Validates the student's authoritative database profile.
- Rejects unauthorized exam codes with:
  `HTTP 403 Forbidden: Access denied: Competitive exam module '{exam_code}' is restricted to Standards 11 and 12.`
- Rejects senior standard requests with:
  `HTTP 403 Forbidden: Access denied: Class 10 students are not permitted to access Standard {target_grade} curriculum.`
- Prevents horizontal and vertical privilege leakage across all API routes.
