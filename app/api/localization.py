from fastapi import APIRouter, HTTPException, Query
from app.core.i18n import SUPPORTED_LOCALES, get_locale_strings

router = APIRouter(prefix="/localization", tags=["localization"])


@router.get("/strings")
def get_localization_strings(lang: str = Query("en", description="Locale code, e.g. en, es")):
    if lang not in SUPPORTED_LOCALES:
        raise HTTPException(status_code=400, detail=f"Unsupported locale: {lang}")
    return {
        "locale": lang,
        "strings": get_locale_strings(lang),
    }
