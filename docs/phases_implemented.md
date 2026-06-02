# Implemented Phases and Features

This document lists each planned phase and the features we have implemented so far.


## Phase 15 — Database Migrations & Production Readiness
- Implemented: Alembic scaffold and initial migration capturing current SQLAlchemy models.
- Files: `alembic/`, `alembic.ini`, initial migration `0001_initial.py`.

## Phase 16 — API Rate Limiting & Sanitization
- Implemented: In-memory rate limiting middleware and HTML sanitization for lesson content.
- Files: `app/middleware/rate_limit.py`, `app/core/sanitization.py`, updated `requirements.txt` (bleach).

## Phase 17 — Course Progress Tracking
- Implemented: `LessonCompletion` model, CRUD helpers, API endpoints to mark completion and fetch course progress.
- Files: `app/models/lesson_completion.py`, `app/crud/lesson_completion.py`, `app/schemas/lesson_completion.py`, API updates in `app/api/courses.py`, migration `0002_add_lesson_completions.py`.

## Phase 18 — Email Verification & Password Reset
- Implemented: `email_verified_at` on `User`; JWT-based verification and password reset tokens; endpoints to verify, resend verification, request password reset, and confirm new password.
- Files: updates in `app/models/user.py`, `app/api/auth.py`, `app/core/security.py`, migration `0004_add_email_verified.py`.

## Phase 20 — Student Dashboard & UX
- Implemented: Student-facing dashboard showing enrolled courses, progress bars, due items, and quick actions.
- Files: Added dashboard endpoint in `app/main.py`, created `templates/student_dashboard.html` template.

## Certificates (Partial — Phase 23)
- Implemented: `Certificate` model and automatic issuance when a user completes all lessons in a course.
- Files: `app/models/certificate.py`, `app/crud/certificate.py`, updated `app/crud/lesson_completion.py` (auto-issue), migration `0003_add_certificates.py`, test `tests/test_progress_certificate.py`.

---

All implemented features have corresponding tests added where appropriate and migrations applied.
