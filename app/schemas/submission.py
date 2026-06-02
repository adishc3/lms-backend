from pydantic import BaseModel, ConfigDict
from datetime import datetime


class SubmissionCreate(BaseModel):
    content: str | None = None
    # file uploads are handled as multipart form-data; this field records stored path when returned
    file_path: str | None = None


class SubmissionRead(BaseModel):
    id: int
    assignment_id: int
    user_id: int
    content: str | None
    submitted_at: datetime
    grade: int | None
    feedback: str | None
    file_path: str | None

    model_config = ConfigDict(from_attributes=True)
