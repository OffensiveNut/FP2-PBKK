import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class KelasBase(BaseModel):
    semester_id: uuid.UUID
    nama_kelas: str = Field(..., max_length=100)
    deskripsi: str


class KelasCreate(KelasBase):
    pass


class KelasUpdate(BaseModel):
    semester_id: uuid.UUID | None = None
    nama_kelas: str | None = Field(None, max_length=100)
    deskripsi: str | None = None


class KelasResponse(KelasBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
