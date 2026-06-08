from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Column, DateTime, ForeignKey, String, Table, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.jadwal_kelas import JadwalKelas
    from app.models.pertemuan import Pertemuan
    from app.models.semester_config import SemesterConfig
    from app.models.user import User

kelas_guru = Table(
    "kelas_guru",
    Base.metadata,
    Column("kelas_id", UUID(as_uuid=True), ForeignKey("kelas.id"), primary_key=True),
    Column("guru_id", UUID(as_uuid=True), ForeignKey("users.id"), primary_key=True),
)

kelas_siswa = Table(
    "kelas_siswa",
    Base.metadata,
    Column("kelas_id", UUID(as_uuid=True), ForeignKey("kelas.id"), primary_key=True),
    Column("siswa_id", UUID(as_uuid=True), ForeignKey("users.id"), primary_key=True),
)


class Kelas(Base):
    __tablename__ = "kelas"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    semester_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("semester_config.id"), nullable=False
    )
    nama_kelas: Mapped[str] = mapped_column(String(100), nullable=False)
    deskripsi: Mapped[str] = mapped_column(Text, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    semester: Mapped["SemesterConfig"] = relationship(
        "SemesterConfig", back_populates="kelas"
    )
    gurus: Mapped[list["User"]] = relationship(
        "User", secondary=kelas_guru, backref="kelas_diampu"
    )
    siswas: Mapped[list["User"]] = relationship(
        "User", secondary=kelas_siswa, backref="kelas_diikuti"
    )
    pertemuan: Mapped[list["Pertemuan"]] = relationship(
        "Pertemuan", back_populates="kelas", cascade="all, delete-orphan"
    )
    jadwal_kelas: Mapped[list["JadwalKelas"]] = relationship(
        "JadwalKelas", back_populates="kelas", cascade="all, delete-orphan"
    )
