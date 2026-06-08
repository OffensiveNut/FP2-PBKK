import uuid
from datetime import date, datetime, time

from pydantic import BaseModel, ConfigDict, Field

from app.models.pertemuan import JenisPertemuanEnum


class PertemuanBase(BaseModel):
    kelas_id: uuid.UUID
    tanggal_pertemuan: date
    waktu_mulai_aktual: time
    waktu_selesai_aktual: time
    deskripsi: str
    jenis_pertemuan: JenisPertemuanEnum


class PertemuanCreate(PertemuanBase):
    pass


class PertemuanUpdate(BaseModel):
    tanggal_pertemuan: date | None = None
    waktu_mulai_aktual: time | None = None
    waktu_selesai_aktual: time | None = None
    deskripsi: str | None = None
    jenis_pertemuan: JenisPertemuanEnum | None = None


class PertemuanResponse(PertemuanBase):
    id: uuid.UUID
    token_presensi: str
    token_expires_at: datetime
    created_by: uuid.UUID

    model_config = ConfigDict(from_attributes=True)


class PertemuanGenerateResponse(BaseModel):
    kelas_id: uuid.UUID
    jumlah_pertemuan: int
    pertemuan: list[PertemuanResponse]
