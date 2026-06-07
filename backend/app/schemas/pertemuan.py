import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.pertemuan import JenisPertemuanEnum


class PertemuanBase(BaseModel):
    kelas_id: uuid.UUID
    deskripsi: str
    waktu_selesai: datetime
    jenis_pertemuan: JenisPertemuanEnum
    token_presensi: str = Field(..., max_length=10)
    created_by: uuid.UUID


class PertemuanCreate(PertemuanBase):
    pass


class PertemuanUpdate(BaseModel):
    kelas_id: uuid.UUID | None = None
    deskripsi: str | None = None
    waktu_selesai: datetime | None = None
    jenis_pertemuan: JenisPertemuanEnum | None = None
    token_presensi: str | None = Field(None, max_length=10)
    created_by: uuid.UUID | None = None


class PertemuanResponse(PertemuanBase):
    id: uuid.UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
