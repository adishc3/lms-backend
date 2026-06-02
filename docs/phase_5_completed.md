# Phase 5 — Notifications & Background Tasks Completed

Completed tasks for Phase 5:

- Added SMTP/email configuration in `app/core/config.py`.
- Added reusable email sending utility in `app/core/email.py`.
- Added a helper in `app/crud/enrollment.py` to find enrolled students for a course.
- Enhanced lesson creation in `app/api/courses.py` to enqueue email notifications using FastAPI `BackgroundTasks`.
- Notifications are now sent to active enrolled students when a new lesson is published.

Testing summary:

- Verified the app imports the new email module and routes remain operational.
- Verified lesson creation can enqueue notifications when SMTP is configured.

Notes:

- Email sending is disabled by default via `EMAIL_ENABLED=False`.
- You can configure SMTP values in `.env` or environment variables for dev and production.
- Background tasks allow non-blocking lesson publish notifications without delaying the API response.
