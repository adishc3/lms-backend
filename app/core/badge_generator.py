from uuid import uuid4


def generate_badge_code(prefix: str = "BDG") -> str:
    return f"{prefix}-{uuid4().hex[:12].upper()}"