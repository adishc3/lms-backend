from fastapi import APIRouter
from app.core.config import settings

router = APIRouter(prefix="/sso", tags=["sso"])


@router.get("/providers")
def list_sso_providers():
    providers = []
    if settings.SSO_PROVIDER:
        providers.append(
            {
                "provider": settings.SSO_PROVIDER,
                "client_id": settings.SSO_CLIENT_ID,
                "metadata_url": settings.SSO_METADATA_URL,
            }
        )
    return {"providers": providers}


@router.get("/config")
def get_sso_configuration():
    return {
        "provider": settings.SSO_PROVIDER,
        "client_id": settings.SSO_CLIENT_ID,
        "metadata_url": settings.SSO_METADATA_URL,
        "sso_available": bool(settings.SSO_PROVIDER and settings.SSO_CLIENT_ID),
    }
