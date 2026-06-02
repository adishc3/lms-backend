# LMS Implementation Plan (Phased)

This document converts the `lms_architecture_summary.md` into a practical, phased implementation plan for a beginner-friendly monolithic LMS built with FastAPI, SQLAlchemy, Alembic, MySQL and server-side templates.

**Assumptions**
- Python 3.12+ target runtime.
- FastAPI + Uvicorn for ASGI server.
- SQLAlchemy + Alembic for ORM and migrations.
- MySQL database.
- Server-side templates (Jinja2) and Bootstrap 5 for frontend.
- JWT authentication and Passlib/Bcrypt for password hashing.

**How to use this plan**
- Work phase-by-phase. Each phase contains deliverables and concrete tasks.
- Keep commits small and feature-scoped. Add tests and simple CI checks per phase.

---

**Phase 0 — Project scaffold & core tooling**
- Objective: Create a reproducible starter repository and developer workflow.
- Deliverables: repo layout, dependency manifests, basic FastAPI app, DB config, Alembic, Dockerfile, README.
- Tasks:
  - Initialize Git repo, `.gitignore` and `README.md`.
  - Create virtual environment and `requirements.txt` or `pyproject.toml`.
  - Add base FastAPI app with app factory and config (dev/prod envs).
  - Add Jinja2 template support and static assets (Bootstrap skeleton).
  - Add SQLAlchemy session, database URL handling, and Alembic initial migration.
  - Add Dockerfile and `docker-compose.yml` for local MySQL + app.
  - Add basic linting (flake8/ruff) and formatting (black/isort) config.
- Acceptance: `uvicorn` runs app; DB connects; Alembic generates initial migration.

**Phase 1 — Authentication & RBAC**
- Objective: Secure user registration, login, roles (student, instructor, admin).
- Deliverables: User model, auth endpoints, JWT login, role checks, password hashing.
- Tasks:
  - Define `User` model, roles enum, and migration scripts.
  - Implement registration and login endpoints (Pydantic schemas + validations).
  - Use Passlib/Bcrypt to hash passwords; store salted hashes.
  - Implement JWT token issuance, refresh pattern (or short-lived access + refresh tokens).
  - Add role-based dependency utilities and decorators for route protection.
  - Add unit tests for registration/login and RBAC enforcement.
- Acceptance: Users can register/login and endpoints respect roles.

**Phase 2 — Course & Lesson core CRUD**
- Objective: Implement core models and CRUD for courses and lessons.
- Deliverables: Course and Lesson models, admin/instructor CRUD endpoints, public listing.
- Tasks:
  - Design `Course` and `Lesson` SQLAlchemy models and migrations.
  - Implement repository/service layer for persistence logic.
  - Build endpoints and templates for listing, creating, editing, viewing courses/lessons.
  - Enforce instructor-only access for create/edit/delete actions.
  - Add simple pagination and search/filter basics.
  - Add tests for CRUD operations and template renders.
- Acceptance: Instructors can create courses/lessons; students can view.

**Phase 3 — Enrollment & access control**
- Objective: Let students enroll and enforce lesson access.
- Deliverables: Enrollment model, enrollment flow, access guard on lessons.
- Tasks:
  - Add `Enrollment` model with user-course relationship and migration.
  - Create endpoints and UI to enroll/unenroll and view enrolled courses.
  - Protect lesson content behind enrollment checks.
  - Add student dashboard to show progress and enrolled courses.
  - Add tests for enrollment flows and ACL logic.
- Acceptance: Only enrolled students can access paid/locked lessons.

**Phase 4 — Admin dashboard & management**
- Objective: Admin UI for user and course management.
- Deliverables: Admin routes, user management, course moderation tools.
- Tasks:
  - Implement admin-only views for user list, role changes, and course moderation.
  - Add activity logs for key admin actions.
  - Add bulk import/export CSV for users or courses (optional).
  - Add tests and basic audit trails.
- Acceptance: Admin can manage users/courses safely.

**Phase 5 — Notifications & background tasks**
- Objective: Email notifications and background processing for heavier tasks.
- Deliverables: Email subsystem, background task runner setup.
- Tasks:
  - Choose background task approach: FastAPI BackgroundTasks for simple jobs or Celery/RQ for robust processing.
  - Integrate SMTP/email provider (SMTP, SendGrid, Mailgun) and template emails.
  - Send notifications when new lessons are published to enrolled students.
  - Add retry and error handling policies for background jobs.
  - Add tests for notification delivery (mocked).
- Acceptance: Notifications delivered (or enqueued) when new lessons are published.

**Phase 6 — File uploads & media management**
- Objective: Support uploading lesson assets and user avatars.
- Deliverables: Secure upload endpoints, storage driver (local / S3), virus-scan considerations.
- Tasks:
  - Add upload endpoints and storage abstraction (local / S3-compatible).
  - Enforce size and file-type validation and signed URLs if using cloud storage.
  - Serve media efficiently (nginx or cloud CDN recommended for production).
  - Add tests for upload flows and access controls.
- Acceptance: Files upload and serve securely; UI shows attachments.

**Phase 7 — Quizzes & assessments**
- Objective: Add quiz model, student attempts, grading and result display.
- Deliverables: Quiz CRUD, attempt tracking, auto/manual grading.
- Tasks:
  - Design `Quiz`, `Question`, `Option`, and `Attempt` models and migrations.
  - Build instructor UI to author quizzes and set correct answers/weights.
  - Implement student attempt flow, auto-grading for objective questions.
  - Add reporting UI for instructors to review results.
  - Add unit/integration tests for grading logic.
- Acceptance: Quizzes can be created and graded; scores recorded.

**Phase 8 — AI features (optional, phased-in)**
- Objective: Add AI assistants and generators as opt-in features.
- Deliverables: Integration with external LLM APIs, safe prompt tooling, caching.
- Tasks (phase-wise):
  - Phase 8.1: `AI Study Assistant` — simple Q&A with lesson context, rate-limited, opt-in per course.
  - Phase 8.2: `AI Quiz Generator` — export candidate questions from lesson text for instructor review.
  - Phase 8.3: `Progress Insights` & `Enrollment Recommender` — batch jobs analyzing progress.
  - Add usage logging, cost controls, and privacy controls (student opt-in/out).
  - Implement caching for repeated prompts and content hashing to reduce cost.
  - Add tests and a usage quota mechanism for admin control.
- Acceptance: AI features operate behind feature flags and respect privacy settings.

**Phase 9 — Testing, security hardening & performance**
- Objective: Ensure robustness, fix security issues, and optimize performance.
- Deliverables: Test suite, security audit, performance metrics.
- Tasks:
  - Add unit and integration tests covering auth, enrollment, and key flows.
  - Run static analysis and security scanners (bandit, safety, dependency checks).
  - Implement rate limiting, input sanitization, CSRF protections for forms (if applicable).
  - Add caching layers (Redis) for session or heavy read queries.
  - Run basic load tests for expected concurrency and optimize DB indices and queries.
- Acceptance: Test coverage for critical flows; documented security checklist passed.

**Phase 10 — Deployment & CI/CD**
- Objective: Productionize the app with repeatable deployments.
- Deliverables: CI pipeline, Docker images, deployment manifests, monitoring.
- Tasks:
  - Create CI pipeline: run lint, tests, build image, run migrations in staging.
  - Publish Docker images and provide `docker-compose` for quick deploys.
  - Add deployment manifests for target infra (Docker Swarm / Kubernetes / Platform-specific).
  - Add logging (structured logs), metrics (Prometheus), and alerting.
  - Set up backups for MySQL and periodic schema snapshot tests.
- Acceptance: Deployment pipeline deploys a working instance to staging.

**Phase 11 — Documentation, onboarding & polish**
- Objective: Make the project easy to use, contribute to, and operate.
- Deliverables: README, architecture docs, API docs, contributor guide.
- Tasks:
  - Publish `README.md` with quickstart, environment vars, and run instructions.
  - Generate OpenAPI docs and add human-friendly API usage examples.
  - Create contributor guide, code style guide, and issue templates.
  - Add admin and user-facing help pages.
- Acceptance: New developers can run and contribute; end users have basic help/docs.

**Phase 12 — Release & handoff**
- Objective: Finalize the repository for review, demo, or handoff.
- Deliverables: release readiness summary, final polish notes, and handoff checklist.
- Tasks:
  - Confirm all phases are documented and the README reflects the final setup.
  - Validate the app startup, tests, and CI configuration.
  - Add a release readiness doc and final project summary.
  - Ensure the repo is easy for the next developer or deployment owner to onboard.
- Acceptance: The project is ready for review and handoff with a clear release checklist.

**Phase 13 — Project completion & maintenance**
- Objective: Close out the MVP and prepare the codebase for future maintenance.
- Deliverables: completion summary, maintenance checklist, and future enhancement notes.
- Tasks:
  - Document the final project status and long-term maintenance expectations.
  - Add guidance for dependency reviews, security checks, and feature roadmap updates.
  - Keep documentation current for developers and operators.
  - Add issue/project template guidance for future work.
- Acceptance: The project is positioned for ongoing maintenance and future enhancements.

**Phase 14 — Future roadmap & continuous improvement**
- Objective: Plan the next evolution of the LMS beyond the MVP release.
- Deliverables: roadmap priorities, upgrade opportunities, and improvement cadence.
- Tasks:
  - Define new feature categories such as analytics, authoring, and multi-tenancy.
  - Document production hardening and observability goals.
  - Establish a review cycle for security, dependencies, and user feedback.
  - Keep a lightweight staging/testing environment for ongoing releases.
- Acceptance: The project has a clear path for future enhancements and maintenance.

---

**Recommended immediate next steps**
- Complete Phase 0 scaffold and verify local run. Then proceed Phase 1.
- Keep each phase in a separate feature branch; open PRs and use CI to validate.

**Appendix — Suggested minimal repo layout**
- `app/` — FastAPI app packages (`auth`, `courses`, `lessons`, `users`, `ai`, `admin`).
- `alembic/` — migrations.
- `tests/` — unit & integration tests.
- `docker-compose.yml`, `Dockerfile`, `Makefile`.
- `requirements.txt` or `pyproject.toml`.

---

Plan created from `lms_architecture_summary.md`.
