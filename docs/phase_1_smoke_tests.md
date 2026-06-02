# Phase 1 Smoke Tests

Date: 2026-05-27

Environment: dev server started with temporary SQLite DB (`DATABASE_URL=sqlite:///./test.db`, `SECRET_KEY=testing`).

Commands used to start server (PowerShell):

```powershell
$env:DATABASE_URL="sqlite:///./test.db"; $env:SECRET_KEY="testing"; .\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Smoke test requests (executed via Python `httpx`):

- Register:
  - POST http://127.0.0.1:8000/auth/register
  - Payload: {"email": "smoke2@example.com", "password": "testing123"}
  - Result: 200 OK; returned created `User` JSON.

- Login:
  - POST http://127.0.0.1:8000/auth/login
  - Payload: {"email": "smoke2@example.com", "password": "testing123"}
  - Result: 200 OK; returned `access_token` and `token_type`.

Notes and fixes applied during testing:
- Installed missing `email-validator` dependency required by `pydantic.EmailStr`.
- Installed `pydantic-settings` and added compatibility import for `BaseSettings` to support Pydantic v2.
- Created `static/` directory to satisfy `StaticFiles` mount used by templates.
- Replaced `bcrypt` with `pbkdf2_sha256` in `app/core/security.py` to avoid native `bcrypt` backend issues and 72-byte password limit during local testing.

Conclusion: Basic auth flows (register, login) are functioning with the development configuration.

Next recommended actions:
- Replace `Base.metadata.create_all` with Alembic migrations for DB schema management.
- Implement token-based auth dependency to protect routes.
- Add unit/integration tests for auth flows.
