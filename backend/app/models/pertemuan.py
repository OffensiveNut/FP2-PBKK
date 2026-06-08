from __future__ import annotations

import enum
import uuid
from datetime import date, datetime, time
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Date, Enum, ForeignKey, String, Text, Time
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.kelas import Kelas
    from app.models.kehadiran import Kehadiran
    from app.models.izin import Izin
    from app.models.user import User


class JenisPertemuanEnum(str, enum.Enum):
    ONLINE = "ONLINE"
    OFFLINE = "OFFLINE"


class Pertemuan(Base):
    __tablename__ = "pertemuan"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    kelas_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("kelas.id"), nullable=False
    )
    tanggal_pertemuan: Mapped[date] = mapped_column(Date, nullable=False)
    waktu_mulai_aktual: Mapped[time] = mapped_column(Time, nullable=False)
    waktu_selesai_aktual: Mapped[time] = mapped_column(Time, nullable=False)
    deskripsi: Mapped[str] = mapped_column(Text, nullable=False)
    jenis_pertemuan: Mapped[JenisPertemuanEnum] = mapped_column(
        Enum(JenisPertemuanEnum), nullable=False
    )
    token_presensi: Mapped[str] = mapped_column(String(10), nullable=False)
    token_expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    created_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )

    kelas: Mapped["Kelas"] = relationship("Kelas", back_populates="pertemuan")
    pembuat: Mapped["User"] = relationship("User", backref="pertemuan_dibuat")
    kehadiran: Mapped[list["Kehadiran"]] = relationship(
        "Kehadiran", back_populates="pertemuan", cascade="all, delete-orphan"
    )
    izin: Mapped[list["Izin"]] = relationship(
        "Izin", back_populates="pertemuan", cascade="all, delete-orphan"
    )
