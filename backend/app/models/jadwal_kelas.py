from __future__ import annotations

import enum
import uuid
from datetime import time
from typing import TYPE_CHECKING

from sqlalchemy import Enum, ForeignKey, Time
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.kelas import Kelas


class HariEnum(str, enum.Enum):
    SENIN = "SENIN"
    SELASA = "SELASA"
    RABU = "RABU"
    KAMIS = "KAMIS"
    JUMAT = "JUMAT"
    SABTU = "SABTU"
    MINGGU = "MINGGU"


class JadwalKelas(Base):
    __tablename__ = "jadwal_kelas"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    kelas_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("kelas.id"), nullable=False
    )
    hari: Mapped[HariEnum] = mapped_column(Enum(HariEnum), nullable=False)
    waktu_mulai: Mapped[time] = mapped_column(Time, nullable=False)
    waktu_selesai: Mapped[time] = mapped_column(Time, nullable=False)

    kelas: Mapped["Kelas"] = relationship("Kelas", back_populates="jadwal_kelas")
