# Architecture Overview

This repository implements a beginner-friendly Learning Management System using FastAPI.

## Core components

- `app/main.py` — application entrypoint, middleware, lifespan startup, router registration.
- `app/core/config.py` — environment-backed settings and deployment configuration.
- `app/core/security.py` — password hashing and JWT access token generation.
- `app/db/session.py` — SQLAlchemy engine, session factory, and declarative base.
- `app/models/` — SQLAlchemy models for users, courses, lessons, enrollments, quizzes, AI usage, and more.
- `app/schemas/` — Pydantic models for request/response validation.
- `app/crud/` — persistence helpers and business logic for each domain model.
- `app/api/` — FastAPI routers exposing auth, courses, admin, quizzes, and AI endpoints.

## Design principles

- Keep authorization logic centralized in `app/api/deps.py`.
- Separate models, schemas, CRUD, and API layers to simplify maintenance.
- Use environment configuration for deployable behavior and secrets.
- Provide background tasks, file uploads, and AI integration as composable features.

## Deployment

- `Dockerfile` builds the Python app container.
- `docker-compose.yml` runs the app and MySQL database together.
- `.env.example` documents required environment variables.

## Documentation locations

- API docs are available automatically from FastAPI at `/docs` and `/redoc`.
- Configuration guidance is in `.env.example`.
- Workflow documentation is in `README.md` and `CONTRIBUTING.md`.
