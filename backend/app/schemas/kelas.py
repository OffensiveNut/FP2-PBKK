import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class KelasBase(BaseModel):
    nama_kelas: str = Field(..., max_length=100)
    jadwal: str = Field(..., max_length=255)


class KelasCreate(KelasBase):
    pass


class KelasUpdate(BaseModel):
    nama_kelas: str | None = Field(None, max_length=100)
    jadwal: str | None = Field(None, max_length=255)


class KelasResponse(KelasBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
