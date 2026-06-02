import json
import redis
from typing import Any
from app.core.config import settings

redis_client = None


def get_redis_client():
    global redis_client
    if redis_client is None and settings.REDIS_URL:
        redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)
    return redis_client


def cache_get(key: str) -> Any | None:
    client = get_redis_client()
    if not client:
        return None
    val = client.get(key)
    if val:
        return json.loads(val)
    return None


def cache_set(key: str, value: Any, expire_seconds: int = 3600) -> bool:
    client = get_redis_client()
    if not client:
        return False
    client.set(key, json.dumps(value), ex=expire_seconds)
    return True


def cache_delete(key: str) -> bool:
    client = get_redis_client()
    if not client:
        return False
    return client.delete(key) > 0