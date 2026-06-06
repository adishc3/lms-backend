from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class EventBase(BaseModel):
    title: str
    description: Optional[str] = None
    starts_at: datetime
    ends_at: Optional[datetime] = None
    location: Optional[str] = None
    join_url: Optional[str] = None
    is_live: bool = False


class EventCreate(EventBase):
    pass


class EventRead(EventBase):
    id: int
    course_id: int

    model_config = {
        "from_attributes": True,
    }
