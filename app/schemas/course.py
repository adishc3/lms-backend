from pydantic import BaseModel
from typing import Optional


class CourseBase(BaseModel):
    title: str
    description: Optional[str] = None
    cover_image_url: Optional[str] = None
    price: int = 0
    is_paid: bool = False
    prerequisite_course_id: Optional[int] = None


class CourseCreate(CourseBase):
    pass


class CourseRead(CourseBase):
    id: int
    owner_id: int
    price: int
    is_paid: bool
    prerequisite_course_id: Optional[int] = None
    cover_image_url: Optional[str] = None
    total_lessons: int = 0

    model_config = {
        "from_attributes": True,
    }
