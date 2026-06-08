import uuid
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field


class SemesterConfigBase(BaseModel):
    nama_semester: str = Field(..., max_length=50)
    tanggal_mulai: date
    tanggal_selesai: date
    is_active: bool = False


class SemesterConfigCreate(SemesterConfigBase):
    pass


class SemesterConfigUpdate(BaseModel):
    nama_semester: str | None = Field(None, max_length=50)
    tanggal_mulai: date | None = None
    tanggal_selesai: date | None = None
    is_active: bool | None = None


class SemesterConfigResponse(SemesterConfigBase):
    id: uuid.UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
