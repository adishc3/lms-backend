from pydantic import BaseModel
from typing import Optional


class OrganizationCreate(BaseModel):
    name: str


class OrganizationRead(BaseModel):
    id: int
    name: str

    model_config = {
        "from_attributes": True,
    }


class OrganizationAssignUser(BaseModel):
    user_id: int
    organization_id: Optional[int] = None
