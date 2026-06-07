from __future__ import annotations

import enum
import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Enum, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.pertemuan import Pertemuan
    from app.models.user import User


class StatusHadirEnum(str, enum.Enum):
    HADIR = "HADIR"
    ALPA = "ALPA"
    SAKIT = "SAKIT"
    IZIN = "IZIN"


class MetodePresensiEnum(str, enum.Enum):
    TOKEN = "TOKEN"
    MANUAL = "MANUAL"


class Kehadiran(Base):
    __tablename__ = "kehadiran"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    pertemuan_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("pertemuan.id"), nullable=False
    )
    siswa_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    status_hadir: Mapped[StatusHadirEnum] = mapped_column(
        Enum(StatusHadirEnum), nullable=False
    )
    metode_presensi: Mapped[MetodePresensiEnum] = mapped_column(
        Enum(MetodePresensiEnum), nullable=False
    )
    waktu_presensi: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    pertemuan: Mapped["Pertemuan"] = relationship(
        "Pertemuan", back_populates="kehadiran"
    )
    siswa: Mapped["User"] = relationship("User", backref="kehadiran")
