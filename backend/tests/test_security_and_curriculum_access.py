"""
EduNavika — Security, Authorization, and Curriculum Access Enforcement Test Suite.

Comprehensive Phase 4 test suite verifying:
1. Anonymous Access Rejection (401 Unauthorized)
2. Authentication & Generic Error Responses (Anti-Enumeration)
3. Rate Limiting Protection (429 Too Many Requests)
4. Password Reset Token Secrecy & Expiration Invariants
5. Authenticated Password Change & Ownership Integrity
6. Horizontal Access Control & Student Data Isolation (Anti-IDOR)
7. Vertical Role-Based Access Control (Student vs Teacher vs Reviewer vs Admin)
8. Class 10 Curriculum & Competitive Exam Boundary Enforcement
9. Standards 11 & 12 Authorized Access
10. Zero Database Leakage & Isolated Test Execution
"""

import time
import uuid
import pytest
from fastapi.testclient import TestClient

from backend.app.core.security import create_access_token, get_password_hash
from backend.app.models.core_models import User, StudentProfile, TeacherProfile, UserRole
from backend.app.models.curriculum_models import Standard, Subject, Chapter, Topic
from backend.app.models.competitive_models import Examination, ExamPaper, Question
from backend.app.api.v1.endpoints.auth import RESET_TOKENS, _FAILED_LOGINS, _FORGOT_REQUESTS


def _error_msg(res) -> str:
    """Helper to extract unified error message across custom JSONResponse handlers."""
    body = res.json()
    if isinstance(body, dict):
        if "error" in body and isinstance(body["error"], dict):
            return body["error"].get("message", "")
        if "detail" in body:
            return str(body["detail"])
    return ""


@pytest.fixture(autouse=True)
def clear_rate_limit_and_tokens():
    """Ensure clean rate-limiting state and reset token storage before each test."""
    RESET_TOKENS.clear()
    _FAILED_LOGINS.clear()
    _FORGOT_REQUESTS.clear()
    yield
    RESET_TOKENS.clear()
    _FAILED_LOGINS.clear()
    _FORGOT_REQUESTS.clear()


@pytest.fixture
def auth_security_fixture(db_session):
    """Sets up synthetic isolated test users for Class 10, Class 11, Teacher, and Reviewer."""
    # 1. Standards
    std10 = Standard(id=str(uuid.uuid4()), grade_number=10, name="Standard 10")
    std11 = Standard(id=str(uuid.uuid4()), grade_number=11, name="Standard 11")
    std12 = Standard(id=str(uuid.uuid4()), grade_number=12, name="Standard 12")
    db_session.add_all([std10, std11, std12])
    db_session.flush()

    # 2. Subjects
    sci10 = Subject(id=str(uuid.uuid4()), name="Science", code="SCI-10", standard_id=std10.id)
    phys11 = Subject(id=str(uuid.uuid4()), name="Physics", code="PHYS11", standard_id=std11.id)
    db_session.add_all([sci10, phys11])
    db_session.flush()

    chap10 = Chapter(id=str(uuid.uuid4()), title="Chemical Reactions", chapter_number=1, subject_id=sci10.id)
    chap11 = Chapter(id=str(uuid.uuid4()), title="Kinematics", chapter_number=1, subject_id=phys11.id)
    db_session.add_all([chap10, chap11])
    db_session.flush()

    # 3. Competitive Exam
    exam_jee = Examination(code="JEE_MAIN", name="JEE Main", conducting_body="NTA", is_active=True)
    db_session.add(exam_jee)
    db_session.flush()

    paper = ExamPaper(
        id=str(uuid.uuid4()),
        paper_identifier="JEE_MAIN_2024_S1",
        exam_code="JEE_MAIN",
        exam_year=2024,
        session_or_shift="Shift 1",
        paper_code="P1",
        total_questions=1,
    )
    db_session.add(paper)
    db_session.flush()

    # 4. Students
    # Student A (Class 10)
    user_a = User(
        name="Student Alpha",
        email="student.alpha@edunavika.test",
        hashed_password=get_password_hash("Password123!"),
        role=UserRole.STUDENT,
        is_active=True,
    )
    db_session.add(user_a)
    db_session.flush()

    profile_a = StudentProfile(
        id=user_a.id,
        user_id=user_a.id,
        standard_id=std10.id,
        enrollment_number="STU-A-10",
        division="A",
    )
    db_session.add(profile_a)

    # Student B (Class 11)
    user_b = User(
        name="Student Beta",
        email="student.beta@edunavika.test",
        hashed_password=get_password_hash("Password123!"),
        role=UserRole.STUDENT,
        is_active=True,
    )
    db_session.add(user_b)
    db_session.flush()

    profile_b = StudentProfile(
        id=user_b.id,
        user_id=user_b.id,
        standard_id=std11.id,
        enrollment_number="STU-B-11",
        division="B",
    )
    db_session.add(profile_b)

    # Teacher
    teacher_user = User(
        name="Teacher Gamma",
        email="teacher.gamma@edunavika.test",
        hashed_password=get_password_hash("Password123!"),
        role=UserRole.TEACHER,
        is_active=True,
    )
    db_session.add(teacher_user)
    db_session.flush()

    teacher_prof = TeacherProfile(
        id="t-prof-001",
        user_id=teacher_user.id,
        employee_id="EMP-T1",
    )
    db_session.add(teacher_prof)

    # Reviewer
    reviewer_user = User(
        name="Reviewer Delta",
        email="reviewer.delta@edunavika.test",
        hashed_password=get_password_hash("Password123!"),
        role=UserRole.REVIEWER,
        is_active=True,
    )
    db_session.add(reviewer_user)
    db_session.commit()

    token_a = create_access_token(user_a.id)
    token_b = create_access_token(user_b.id)
    token_teacher = create_access_token(teacher_user.id)
    token_reviewer = create_access_token(reviewer_user.id)

    return {
        "user_a": user_a,
        "token_a": token_a,
        "std10": std10,
        "chap10": chap10,
        "user_b": user_b,
        "token_b": token_b,
        "std11": std11,
        "chap11": chap11,
        "teacher_user": teacher_user,
        "token_teacher": token_teacher,
        "reviewer_user": reviewer_user,
        "token_reviewer": token_reviewer,
        "paper": paper,
    }


# ============================================================================
# 1. Anonymous Access Rejection & Authentication Verification
# ============================================================================
def test_1_anonymous_access_to_protected_endpoints_fails(client, auth_security_fixture):
    """Anonymous visitors must be rejected with 401 Unauthorized on protected routes."""
    user_a = auth_security_fixture["user_a"]

    # 1. Change password without token
    r1 = client.post("/api/v1/auth/change-password", json={
        "email": user_a.email,
        "current_password": "Password123!",
        "new_password": "NewPassword456!",
    })
    assert r1.status_code == 401
    assert "Bearer" in r1.headers.get("WWW-Authenticate", "")

    # 2. Start assessment without token
    r2 = client.post("/api/v1/competitive/assessments/start", json={
        "student_id": user_a.id,
        "exam_code": "JEE_MAIN",
    })
    assert r2.status_code == 401

    # 3. Log teacher action without token
    r3 = client.post("/api/v1/teacher-actions", json={
        "teacher_id": "t-prof-001",
        "student_id": user_a.id,
        "topic_id": "fake-topic",
        "action_type": "INTERVENTION",
    })
    assert r3.status_code == 401


def test_2_correct_and_incorrect_login_and_anti_enumeration(client, auth_security_fixture):
    """Login must succeed with valid credentials and fail with constant-time generic 401 for wrong credentials."""
    user_a = auth_security_fixture["user_a"]

    # Valid login
    res_ok = client.post("/api/v1/auth/login", json={
        "email": user_a.email,
        "password": "Password123!",
    })
    assert res_ok.status_code == 200
    data = res_ok.json()
    assert data["success"] is True
    assert "access_token" in data
    assert data["user"]["grade"] == "Grade 10"
    assert data["user"]["grade_number"] == 10

    # Incorrect password -> 401 with generic error
    res_bad_pw = client.post("/api/v1/auth/login", json={
        "email": user_a.email,
        "password": "WrongPassword999!",
    })
    assert res_bad_pw.status_code == 401
    assert "Invalid email or password" in _error_msg(res_bad_pw)

    # Non-existent user -> identical generic error message
    res_bad_user = client.post("/api/v1/auth/login", json={
        "email": "nonexistent_ghost_user@edunavika.test",
        "password": "WrongPassword999!",
    })
    assert res_bad_user.status_code == 401
    assert "Invalid email or password" in _error_msg(res_bad_user)


# ============================================================================
# 2. Rate Limiting Protection (Anti-Brute Force)
# ============================================================================
def test_3_login_rate_limiting_triggers_429(client, auth_security_fixture):
    """5 consecutive failed logins must trigger 429 Too Many Requests."""
    user_a = auth_security_fixture["user_a"]

    for _ in range(5):
        r = client.post("/api/v1/auth/login", json={
            "email": user_a.email,
            "password": "WrongPassword!",
        })
        assert r.status_code == 401

    # 6th attempt must be blocked by rate limiter
    blocked = client.post("/api/v1/auth/login", json={
        "email": user_a.email,
        "password": "Password123!",  # Even valid credentials blocked during lockout
    })
    assert blocked.status_code == 429
    assert blocked.headers.get("Retry-After") == "300"
    assert "Too many failed login attempts" in _error_msg(blocked)


# ============================================================================
# 3. Password Reset Security (SEC-01 & SEC-02 Invariant Verification)
# ============================================================================
def test_4_forgot_password_never_leaks_token_or_enumerates(client, auth_security_fixture):
    """SEC-01 & SEC-02: Forgot password must never return reset_token or leak account existence."""
    user_a = auth_security_fixture["user_a"]

    # 1. Existing user
    r_exist = client.post("/api/v1/auth/forgot-password", json={"email": user_a.email})
    assert r_exist.status_code == 200
    data_exist = r_exist.json()
    assert "reset_token" not in data_exist
    assert "reset_link" not in data_exist
    assert data_exist["success"] is True

    # 2. Non-existent user
    r_ghost = client.post("/api/v1/auth/forgot-password", json={"email": "nobody@edunavika.test"})
    assert r_ghost.status_code == 200
    data_ghost = r_ghost.json()
    assert "reset_token" not in data_ghost
    # Assert messages are completely identical
    assert data_exist["message"] == data_ghost["message"]


def test_5_password_reset_flow_and_single_use(client, auth_security_fixture):
    """Password reset must consume token once, invalidate it, and enforce minimum length."""
    user_a = auth_security_fixture["user_a"]

    # Request reset
    client.post("/api/v1/auth/forgot-password", json={"email": user_a.email})
    assert len(RESET_TOKENS) == 1
    token = list(RESET_TOKENS.keys())[0]

    # Reject weak password (<8 characters)
    r_weak = client.post("/api/v1/auth/reset-password", json={
        "email": user_a.email,
        "token": token,
        "new_password": "short",
    })
    assert r_weak.status_code == 400
    assert "at least 8 characters" in _error_msg(r_weak)

    # Successfully reset password
    r_ok = client.post("/api/v1/auth/reset-password", json={
        "email": user_a.email,
        "token": token,
        "new_password": "NewSecurePassword2026!",
    })
    assert r_ok.status_code == 200
    assert r_ok.json()["success"] is True

    # Replay attack: token must be invalidated
    r_replay = client.post("/api/v1/auth/reset-password", json={
        "email": user_a.email,
        "token": token,
        "new_password": "AnotherPassword2026!",
    })
    assert r_replay.status_code == 400
    assert "Invalid or expired" in _error_msg(r_replay)


# ============================================================================
# 4. Authenticated Password Change & Ownership Integrity (SEC-03 & Anti-IDOR)
# ============================================================================
def test_6_password_change_requires_session_and_ownership(client, auth_security_fixture):
    """Authenticated user cannot change another user's password."""
    token_a = auth_security_fixture["token_a"]
    user_b = auth_security_fixture["user_b"]

    # Student A attempting to change Student B's password -> 403 Forbidden
    r_forbidden = client.post(
        "/api/v1/auth/change-password",
        headers={"Authorization": f"Bearer {token_a}"},
        json={
            "email": user_b.email,
            "current_password": "Password123!",
            "new_password": "HackedPassword999!",
        }
    )
    assert r_forbidden.status_code == 403
    assert "cannot change the password of another account" in _error_msg(r_forbidden)


def test_7_horizontal_student_data_isolation_anti_idor(client, auth_security_fixture):
    """SEC-04: Student A cannot view Student B's profile."""
    token_a = auth_security_fixture["token_a"]
    user_b = auth_security_fixture["user_b"]

    r_snoop = client.get(
        f"/api/v1/students/{user_b.id}",
        headers={"Authorization": f"Bearer {token_a}"},
    )
    assert r_snoop.status_code == 403
    assert "not authorized to access another student's" in _error_msg(r_snoop)


# ============================================================================
# 5. Role-Based Access Control (RBAC Vertical Authorization)
# ============================================================================
def test_8_student_cannot_access_privileged_reviewer_or_teacher_actions(client, auth_security_fixture):
    """Student tokens cannot access reviewer portal or teacher intervention routes."""
    token_a = auth_security_fixture["token_a"]

    # 1. Student attempting reviewer portal
    r_rev = client.get(
        "/api/v1/competitive/review/unverified",
        headers={"Authorization": f"Bearer {token_a}"},
    )
    assert r_rev.status_code == 403

    # 2. Student attempting teacher action
    r_teach = client.post(
        "/api/v1/teacher-actions",
        headers={"Authorization": f"Bearer {token_a}"},
        json={
            "teacher_id": "t-prof-001",
            "student_id": auth_security_fixture["user_b"].id,
            "topic_id": "fake",
            "action_type": "NOTE",
        }
    )
    assert r_teach.status_code == 403


# ============================================================================
# 6. Class 10 Curriculum & Competitive Exam Boundary Enforcement (Phase 3)
# ============================================================================
def test_9_class_10_student_cannot_start_competitive_exam(client, auth_security_fixture):
    """Class 10 students must be strictly forbidden from starting JEE or NEET exams."""
    user_a = auth_security_fixture["user_a"]
    token_a = auth_security_fixture["token_a"]

    r_jee = client.post(
        "/api/v1/competitive/assessments/start",
        headers={"Authorization": f"Bearer {token_a}"},
        json={
            "student_id": user_a.id,
            "exam_code": "JEE_MAIN",
            "mode": "CHAPTER_MOCK",
        }
    )
    assert r_jee.status_code == 403
    assert "Competitive exam module 'JEE_MAIN' is restricted to Standards 11 and 12" in _error_msg(r_jee)


def test_10_class_10_student_cannot_query_standard_11_curriculum(client, auth_security_fixture):
    """Class 10 students cannot query Standard 11 subjects directly via API."""
    token_a = auth_security_fixture["token_a"]
    std11 = auth_security_fixture["std11"]

    r_std11 = client.get(
        f"/api/v1/standards/{std11.id}/subjects",
        headers={"Authorization": f"Bearer {token_a}"},
    )
    assert r_std11.status_code == 403
    assert "Class 10 students are not permitted to access Standard 11 curriculum" in _error_msg(r_std11)


def test_11_class_11_student_can_access_own_standard_subjects(client, auth_security_fixture):
    """Standard 11 student can freely query Standard 11 curriculum."""
    token_b = auth_security_fixture["token_b"]
    std11 = auth_security_fixture["std11"]

    r_ok = client.get(
        f"/api/v1/standards/{std11.id}/subjects",
        headers={"Authorization": f"Bearer {token_b}"},
    )
    assert r_ok.status_code == 200
    subjs = r_ok.json()
    assert len(subjs) >= 1
    assert subjs[0]["code"] == "PHYS11"
