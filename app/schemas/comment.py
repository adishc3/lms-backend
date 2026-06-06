from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class CommentBase(BaseModel):
    course_id: int
    lesson_id: Optional[int] = None
    content: str


class CommentCreate(CommentBase):
    pass


class CommentRead(BaseModel):
    id: int
    user_id: int
    course_id: Optional[int] = None
    lesson_id: Optional[int] = None
    content: str
    created_at: datetime

    model_config = {
        "from_attributes": True,
    }
