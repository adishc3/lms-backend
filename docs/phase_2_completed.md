# Phase 2 — Course & Lesson CRUD Completed

Completed tasks for Phase 2:

- Added `Course` model: `app/models/course.py`
- Added `Lesson` model: `app/models/lesson.py`
- Added course schemas: `app/schemas/course.py`
- Added lesson schemas: `app/schemas/lesson.py`
- Added course CRUD helpers: `app/crud/course.py`
- Added lesson CRUD helpers: `app/crud/lesson.py`
- Added protected course and lesson endpoints: `app/api/courses.py`
- Added auth dependency and token-based user access: `app/api/deps.py`
- Updated login to OAuth2 password flow and added `/auth/me`: `app/api/auth.py`
- Added course router to app bootstrap: `app/main.py`

Testing summary:

- Verified `/auth/register` and `/auth/login` with `TestClient`.
- Verified `/auth/me` protected endpoint returns logged-in user.
- Promoted a test user to `instructor` and verified instructor-only `/courses/` creation.
- Verified course listing and lesson creation via `/courses/{course_id}/lessons`.

Notes:

- Course creation and lesson creation are protected by instructor/admin roles.
- Public course listing is available via `GET /courses/`.

Next recommended actions:

- Add enrollment model and access control for student course access.
- Add admin user management and instructor role assignment flows.
- Add template views for courses and lessons if UI support is desired.
