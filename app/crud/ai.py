from sqlalchemy.orm import Session
from app.models.ai_usage import AIUsageLog


def create_ai_usage(
    db: Session,
    user_id: int,
    feature: str,
    prompt: str,
    response: str | None = None,
    lesson_id: int | None = None,
):
    usage = AIUsageLog(
        user_id=user_id,
        feature=feature,
        prompt=prompt,
        response=response,
        lesson_id=lesson_id,
    )
    db.add(usage)
    db.commit()
    db.refresh(usage)
    return usage
