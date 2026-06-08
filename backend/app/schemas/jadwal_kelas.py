import uuid
from datetime import time

from pydantic import BaseModel, ConfigDict

from app.models.jadwal_kelas import HariEnum


class JadwalKelasBase(BaseModel):
    hari: HariEnum
    waktu_mulai: time
    waktu_selesai: time


class JadwalKelasCreate(JadwalKelasBase):
    pass


class JadwalKelasUpdate(BaseModel):
    hari: HariEnum | None = None
    waktu_mulai: time | None = None
    waktu_selesai: time | None = None


class JadwalKelasResponse(JadwalKelasBase):
    id: uuid.UUID
    kelas_id: uuid.UUID

    model_config = ConfigDict(from_attributes=True)
