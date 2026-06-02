# Phase 6 — File Uploads & Media Management Completed

Completed tasks for Phase 6:

- Added upload storage config in `app/core/config.py`.
- Added local upload helper and validation in `app/core/storage.py`.
- Extended `Lesson` model with `asset_path` and property `asset_url` in `app/models/lesson.py`.
- Added asset persistence updates in `app/crud/lesson.py`.
- Added lesson asset upload endpoint: `POST /courses/{course_id}/lessons/{lesson_id}/upload` in `app/api/courses.py`.
- Ensured `static/uploads/` exists on startup in `app/main.py`.

Testing summary:

- Verified the new storage helper imports correctly.
- Added file upload capability for lesson assets with size and extension checks.
- Files are served via the existing static `/static/uploads` path.

Notes:

- Allowed file extensions are currently limited to common asset types.
- Max upload size is controlled by `UPLOAD_MAX_SIZE`.
- A production-ready version can extend this to cloud storage or signed URLs.
