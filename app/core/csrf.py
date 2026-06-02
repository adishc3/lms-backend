import secrets
from fastapi import HTTPException, status
from fastapi.security import APIKeyHeader

csrf_header = APIKeyHeader(name="X-CSRF-Token", auto_error=False)


def generate_csrf_token() -> str:
    return secrets.token_urlsafe(32)


async def verify_csrf(form_token: str | None, header_token: str | None) -> bool:
    if not form_token or not header_token:
        return False
    return secrets.compare_digest(form_token, header_token)