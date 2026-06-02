# API Overview

The LMS API exposes the following endpoint groups:

## Authentication
- `POST /auth/register` — register a new user.
- `POST /auth/login` — login and receive a JWT access token.
- `GET /auth/me` — fetch current authenticated user.

## Courses
- `GET /courses/` — list courses.
- `GET /courses/{course_id}` — get course details.
- `POST /courses/` — create a course (instructor/admin only).
- `PUT /courses/{course_id}` — update a course (owner/admin only).
- `DELETE /courses/{course_id}` — delete a course (owner/admin only).
- `POST /courses/{course_id}/enroll` — enroll in a course.

## Lessons
- `GET /courses/{course_id}/lessons` — list lessons for a course.
- `GET /courses/{course_id}/lessons/{lesson_id}` — fetch a lesson.
- `POST /courses/{course_id}/lessons` — create a lesson (owner/admin only).
- `POST /courses/{course_id}/lessons/{lesson_id}/upload` — upload an asset for a lesson.

## Admin
- `GET /admin/users` — list users (admin only).
- `GET /admin/users/{user_id}` — get a user by ID (admin only).
- `PUT /admin/users/{user_id}` — update user role or active state (admin only).

## Quizzes
- `POST /quizzes/` — create a quiz for a course (instructor/admin only).
- `GET /quizzes/course/{course_id}` — list quizzes for a course.
- `GET /quizzes/{quiz_id}` — get quiz details.
- `POST /quizzes/{quiz_id}/attempts` — submit a quiz attempt.
- `GET /quizzes/{quiz_id}/attempts` — list quiz attempts.
- `GET /quizzes/{quiz_id}/attempts/{attempt_id}` — get a single attempt.

## AI
- `POST /ai/study-assistant` — ask a lesson-specific question using AI.
- `POST /ai/quiz-generator` — generate quiz prompts from a lesson.

## OpenAPI docs
FastAPI automatically exposes:
- `/docs` — Swagger UI
- `/redoc` — ReDoc docs
