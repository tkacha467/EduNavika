from fastapi import APIRouter
from backend.app.api.v1.endpoints import (
    curriculum,
    content,
    mcqs,
    assessments,
    attempts,
    learning_events,
    performance,
    revision,
    forgetting_signals,
    teacher_actions,
    users,
    adaptive,
)

api_router = APIRouter()

# Adaptive Learning & Knowledge Decay
api_router.include_router(adaptive.router, tags=["Adaptive Learning"])

# Curriculum hierarchy
api_router.include_router(curriculum.router, tags=["Curriculum"])

# Learning Content
api_router.include_router(content.router, tags=["Learning Content"])

# MCQs & Question Provenance
api_router.include_router(mcqs.router, tags=["MCQs"])

# Assessments
api_router.include_router(assessments.router, tags=["Assessments"])

# Student Attempts & Answers
api_router.include_router(attempts.router, tags=["Student Attempts"])

# Research-Grade Longitudinal Learning Events
api_router.include_router(learning_events.router, tags=["Learning Events"])

# Topic Performance Evidence Aggregation
api_router.include_router(performance.router, tags=["Topic Performance"])

# Revision Plans
api_router.include_router(revision.router, tags=["Revision"])

# Forgetting Evidence Signals
api_router.include_router(forgetting_signals.router, tags=["Forgetting Signals"])

# Teacher Interventions / Actions
api_router.include_router(teacher_actions.router, tags=["Teacher Actions"])

# Users & Profiles
api_router.include_router(users.router, tags=["Users & Profiles"])
