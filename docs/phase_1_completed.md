# Phase 1 — Authentication & RBAC Completed

Completed tasks for Phase 1:

- Added SQLAlchemy DB session and Base: `app/db/session.py`
- Added `User` model and `Role` enum: `app/models/user.py`
- Added Pydantic schemas: `app/schemas/user.py`, `app/schemas/token.py`
- Added password hashing and JWT utilities: `app/core/security.py`
- Added CRUD helpers for users: `app/crud/user.py`
- Implemented auth endpoints: `app/api/auth.py` (`/auth/register`, `/auth/login`)
- Hooked auth router into application and auto-create tables for development: `app/main.py`
- Added package `__init__` files for Python package imports.

Notes:
- Passwords are hashed with bcrypt via Passlib.
- JWTs are issued with `python-jose` using `HS256` and `SECRET_KEY` from `app/core/config.py`.
- This is a development setup. For production, replace `Base.metadata.create_all` with Alembic migrations and secure secrets.
