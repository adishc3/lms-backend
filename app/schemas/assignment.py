from pydantic import BaseModel, ConfigDict
from datetime import datetime


class AssignmentCreate(BaseModel):
    title: str
    description: str | None = None
    due_date: datetime | None = None
    max_score: int | None = None


class AssignmentRead(BaseModel):
    id: int
    course_id: int
    title: str
    description: str | None
    due_date: datetime | None
    max_score: int | None

    model_config = ConfigDict(from_attributes=True)
