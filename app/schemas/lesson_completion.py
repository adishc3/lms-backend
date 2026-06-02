from pydantic import BaseModel, ConfigDict
from datetime import datetime


class LessonCompletionRead(BaseModel):
    lesson_id: int
    completed_at: datetime
    time_spent_minutes: int | None = None

    model_config = ConfigDict(from_attributes=True)
