from __future__ import annotations

import enum
import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Enum, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.pertemuan import Pertemuan
    from app.models.user import User


class StatusApprovalEnum(str, enum.Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


class Izin(Base):
    __tablename__ = "izin"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    pertemuan_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("pertemuan.id"), nullable=False
    )
    siswa_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    alasan: Mapped[str] = mapped_column(Text, nullable=False)
    file_bukti: Mapped[str | None] = mapped_column(String(255), nullable=True)
    status_approval: Mapped[StatusApprovalEnum] = mapped_column(
        Enum(StatusApprovalEnum), default=StatusApprovalEnum.PENDING, nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    pertemuan: Mapped["Pertemuan"] = relationship("Pertemuan", back_populates="izin")
    siswa: Mapped["User"] = relationship("User", backref="izin")
