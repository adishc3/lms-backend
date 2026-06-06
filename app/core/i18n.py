import json
from pathlib import Path
from typing import Any

from app.core.config import settings

LOCALES_DIR = Path(__file__).resolve().parent.parent.parent / "locales"
SUPPORTED_LOCALES = [item.strip() for item in settings.SUPPORTED_LOCALES.split(",") if item.strip()]
DEFAULT_LOCALE = settings.DEFAULT_LOCALE or "en"

_translations: dict[str, dict[str, str]] = {}


def _load_locale(locale: str) -> dict[str, str]:
    locale_path = LOCALES_DIR / f"{locale}.json"
    if not locale_path.exists():
        return {}
    try:
        return json.loads(locale_path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def get_preferred_locale(accept_language: str | None) -> str:
    if not accept_language:
        return DEFAULT_LOCALE
    for part in accept_language.split(","):
        lang = part.split(";")[0].strip().lower()
        if lang in SUPPORTED_LOCALES:
            return lang
        if "-" in lang:
            base_lang = lang.split("-")[0]
            if base_lang in SUPPORTED_LOCALES:
                return base_lang
    return DEFAULT_LOCALE


def translate(key: str, locale: str | None = None) -> str:
    target_locale = (locale or DEFAULT_LOCALE).lower()
    if target_locale not in _translations:
        _translations[target_locale] = _load_locale(target_locale)
    return _translations.get(target_locale, {}).get(key, key)


def get_locale_strings(locale: str) -> dict[str, str]:
    selected_locale = locale.lower()
    if selected_locale not in _translations:
        _translations[selected_locale] = _load_locale(selected_locale)
    return _translations.get(selected_locale, {})
