from pydantic import BaseModel
from typing import Optional


class CourseBase(BaseModel):
    title: str
    description: Optional[str] = None
    cover_image_url: Optional[str] = None


class CourseCreate(CourseBase):
    pass


class CourseRead(CourseBase):
    id: int
    owner_id: int
    cover_image_url: Optional[str] = None

    model_config = {
        "from_attributes": True,
    }
