import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.kehadiran import MetodePresensiEnum, StatusHadirEnum


class KehadiranBase(BaseModel):
    pertemuan_id: uuid.UUID
    siswa_id: uuid.UUID
    status_hadir: StatusHadirEnum
    metode_presensi: MetodePresensiEnum


class KehadiranCreate(KehadiranBase):
    pass


class KehadiranUpdate(BaseModel):
    pertemuan_id: uuid.UUID | None = None
    siswa_id: uuid.UUID | None = None
    status_hadir: StatusHadirEnum | None = None
    metode_presensi: MetodePresensiEnum | None = None


class KehadiranResponse(KehadiranBase):
    id: uuid.UUID
    waktu_presensi: datetime

    model_config = ConfigDict(from_attributes=True)
