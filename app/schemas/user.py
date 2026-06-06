from pydantic import BaseModel, EmailStr
from typing import Optional
from app.models.user import Role


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: Optional[str] = None
    role: Optional[str] = None
    organization_id: Optional[int] = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserRead(BaseModel):
    id: int
    email: EmailStr
    full_name: Optional[str] = None
    is_active: bool
    role: str
    organization_id: Optional[int] = None

    model_config = {
        "from_attributes": True,
    }


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    is_active: Optional[bool] = None
    role: Optional[Role] = None
