# Contributing to Beginner LMS

Thanks for contributing! This guide explains the workflow and expectations for this repository.

## Setup

1. Copy `.env.example` to `.env`.
2. Create and activate a virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

3. Run tests:

```powershell
python -m pytest -q
```

## Branching and workflow

- Create feature branches from `main`.
- Use descriptive branch names like `feature/admin-management` or `fix/token-expiry`.
- Open pull requests against `main`.
- Include a short summary of changes and testing steps.

## Code style

- Keep code organized by feature and layer.
- Use consistent naming for routers, CRUD helpers, and schemas.
- Add tests for new behavior.

## Documentation

- Add or update docs in `docs/` for new features.
- Keep `README.md` and `.env.example` up to date.
- Document any deployment or environment changes.

## Testing

- Run the test suite before submitting changes.
- Add tests for authentication, authorization, and edge cases.

## Deployment

- Changes to `docker-compose.yml`, `Dockerfile`, or CI should include validation steps.
- Ensure the GitHub Actions workflow in `.github/workflows/ci.yml` continues to pass.
