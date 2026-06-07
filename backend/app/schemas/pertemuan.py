import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.pertemuan import JenisPertemuanEnum


class PertemuanBase(BaseModel):
    kelas_id: uuid.UUID
    deskripsi: str
    waktu_selesai: datetime
    jenis_pertemuan: JenisPertemuanEnum


class PertemuanCreate(PertemuanBase):
    pass


class PertemuanUpdate(BaseModel):
    kelas_id: uuid.UUID | None = None
    deskripsi: str | None = None
    waktu_selesai: datetime | None = None
    jenis_pertemuan: JenisPertemuanEnum | None = None


class PertemuanResponse(PertemuanBase):
    id: uuid.UUID
    token_presensi: str
    token_expires_at: datetime
    created_by: uuid.UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
