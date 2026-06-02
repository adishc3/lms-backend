<<<<<<< HEAD
# Beginner LMS — Quick start

Prereqs: Python 3.12+, Docker (optional)

## Local development

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload
```

From the repository root you can run the included helper script instead of changing directories:

```powershell
.\start-backend.ps1
```

## Docker Compose

Create a `.env` file from `.env.example`, then run:

```powershell
docker compose up --build
```

## Testing

```powershell
.\.venv\Scripts\Activate.ps1
python -m pytest -q
```

## CI/CD

This repository includes a GitHub Actions workflow at `.github/workflows/ci.yml` that runs the test suite on pushes and pull requests to `main`.

## Documentation

- `docs/architecture_overview.md` — architecture and component design.
- `docs/api_overview.md` — endpoint reference and API surface.
- `CONTRIBUTING.md` — contribution workflow and developer expectations.
- `docs/phase_*.md` — phase completion records.

## Environment

Copy `.env.example` to `.env` and customize values for local development or production.
=======
# lms-backend
>>>>>>> 2482a1d4d941267d3df1903147e945a33b3e94b8
