import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.models.user import RoleEnum


class UserBase(BaseModel):
    username: str = Field(..., max_length=50)
    email: EmailStr = Field(..., max_length=100)
    nama_lengkap: str = Field(..., max_length=150)
    role: RoleEnum


class UserCreate(UserBase):
    password: str | None = Field(None, min_length=8, max_length=255)


class UserUpdate(BaseModel):
    username: str | None = Field(None, max_length=50)
    email: EmailStr | None = Field(None, max_length=100)
    nama_lengkap: str | None = Field(None, max_length=150)
    role: RoleEnum | None = None
    password: str | None = Field(None, min_length=8, max_length=255)


class UserResponse(UserBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserCreateResponse(UserResponse):
    generated_password: str | None = None
