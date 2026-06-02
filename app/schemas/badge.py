from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class BadgeBase(BaseModel):
    user_id: int
    course_id: Optional[int] = None
    badge_code: Optional[str] = Field(default=None, max_length=64)
    badge_name: str = Field(max_length=255)
    badge_description: Optional[str] = None


class BadgeCreate(BadgeBase):
    pass


class BadgeRead(BadgeBase):
    id: int
    awarded_at: datetime

    model_config = {"from_attributes": True}