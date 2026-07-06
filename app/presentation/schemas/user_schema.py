from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr


class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    avatar_url: str | None = None


class UserUpdate(BaseModel):
    username: str
    email: EmailStr
    avatar_url: str | None = None


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    email: str
    avatar_url: str | None
    created_at: datetime | None


class UserAvailability(BaseModel):
    username_available: bool | None
    email_available: bool | None
