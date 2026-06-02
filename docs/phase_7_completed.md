# Phase 7 — Quizzes & Assessments Completed

Completed tasks for Phase 7:

- Added quiz assessment models in `app/models/quiz.py`:
  - `Quiz`
  - `Question`
  - `Option`
  - `QuizAttempt`
  - `AttemptAnswer`
- Added quiz schema definitions in `app/schemas/quiz.py`.
- Added CRUD support for quiz creation, retrieval, and attempt submission in `app/crud/quiz.py`.
- Added quiz API endpoints in `app/api/quizzes.py`:
  - `POST /quizzes/`
  - `GET /quizzes/course/{course_id}`
  - `GET /quizzes/{quiz_id}`
  - `POST /quizzes/{quiz_id}/attempts`
  - `GET /quizzes/{quiz_id}/attempts`
  - `GET /quizzes/{quiz_id}/attempts/{attempt_id}`
- Registered the quizzes router in `app/main.py`.
- Extended `app/models/course.py` with `quizzes` relationship.

Testing summary:

- Verified quiz creation can be performed by course instructors.
- Verified enrolled students can access quizzes and submit attempts.
- Verified attempts are scoped to the correct quiz and user.

Notes:

- Instructor/admin users can view all quiz attempts for a quiz.
- Students can only view their own attempts.
- This phase adds the assessment core needed for quizzes and grading workflows.
