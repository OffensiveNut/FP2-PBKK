import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.izin import StatusApprovalEnum


class IzinBase(BaseModel):
    pertemuan_id: uuid.UUID
    siswa_id: uuid.UUID
    alasan: str
    file_bukti: str | None = Field(None, max_length=255)


class IzinCreate(IzinBase):
    pass


class IzinUpdate(BaseModel):
    pertemuan_id: uuid.UUID | None = None
    siswa_id: uuid.UUID | None = None
    alasan: str | None = None
    file_bukti: str | None = Field(None, max_length=255)
    status_approval: StatusApprovalEnum | None = None


class IzinResponse(IzinBase):
    id: uuid.UUID
    status_approval: StatusApprovalEnum
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
