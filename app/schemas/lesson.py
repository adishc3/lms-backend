from pydantic import BaseModel
from typing import Optional


class LessonBase(BaseModel):
    title: str
    content: str


class LessonCreate(LessonBase):
    pass


class LessonUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None


class FileMetadata(BaseModel):
    public_id: str
    resource_type: str
    file_name: str


class LessonRead(LessonBase):
    id: int
    course_id: int
    asset_path: Optional[str] = None
    asset_metadata: Optional[FileMetadata] = None

    model_config = {
        "from_attributes": True,
    }
