import random
import string
import uuid
from datetime import date, datetime, time, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.exceptions import Conflict, NotFound
from app.models.jadwal_kelas import HariEnum, JadwalKelas
from app.models.kelas import Kelas
from app.models.pertemuan import JenisPertemuanEnum, Pertemuan
from app.models.semester_config import SemesterConfig

TOKEN_LENGTH = 6


_HARI_MAP = {
    HariEnum.SENIN: 0,
    HariEnum.SELASA: 1,
    HariEnum.RABU: 2,
    HariEnum.KAMIS: 3,
    HariEnum.JUMAT: 4,
    HariEnum.SABTU: 5,
    HariEnum.MINGGU: 6,
}


def _generate_token() -> str:
    return "".join(random.choices(string.digits, k=TOKEN_LENGTH))


async def generate_pertemuan(
    db: AsyncSession,
    kelas_id: uuid.UUID,
    created_by: uuid.UUID,
) -> list[Pertemuan]:
    result = await db.execute(
        select(Kelas).where(Kelas.id == kelas_id).options(
            selectinload(Kelas.semester),
            selectinload(Kelas.jadwal_kelas),
            selectinload(Kelas.pertemuan),
        )
    )
    kelas = result.scalar_one_or_none()
    if not kelas:
        raise NotFound("Kelas tidak ditemukan")

    semester: SemesterConfig = kelas.semester
    if not semester:
        raise NotFound("Kelas tidak memiliki semester config")

    if not kelas.jadwal_kelas:
        raise NotFound("Kelas tidak memiliki jadwal, buat jadwal terlebih dahulu")

    existing_dates: set[date] = {p.tanggal_pertemuan for p in kelas.pertemuan}

    created: list[Pertemuan] = []

    for jadwal in kelas.jadwal_kelas:
        target_weekday = _HARI_MAP[jadwal.hari]
        current = semester.tanggal_mulai

        while current <= semester.tanggal_selesai:
            if current.weekday() == target_weekday and current not in existing_dates:
                token = _generate_token()
                expires_at = datetime(
                    current.year, current.month, current.day,
                    jadwal.waktu_mulai.hour, jadwal.waktu_mulai.minute,
                    tzinfo=timezone.utc,
                ) + timedelta(minutes=2)

                pertemuan = Pertemuan(
                    kelas_id=kelas_id,
                    tanggal_pertemuan=current,
                    waktu_mulai_aktual=jadwal.waktu_mulai,
                    waktu_selesai_aktual=jadwal.waktu_selesai,
                    deskripsi=f"Pertemuan {jadwal.hari.value.title()} - {current.isoformat()}",
                    jenis_pertemuan=JenisPertemuanEnum.OFFLINE,
                    token_presensi=token,
                    token_expires_at=expires_at,
                    created_by=created_by,
                )
                db.add(pertemuan)
                created.append(pertemuan)
                existing_dates.add(current)
            current += timedelta(days=1)

    await db.commit()
    for p in created:
        await db.refresh(p)
    return created


async def get_pertemuan_by_kelas(
    db: AsyncSession, kelas_id: uuid.UUID
) -> list[Pertemuan]:
    result = await db.execute(
        select(Pertemuan)
        .where(Pertemuan.kelas_id == kelas_id)
        .order_by(Pertemuan.tanggal_pertemuan)
    )
    return list(result.scalars().all())


async def get_pertemuan_by_id(
    db: AsyncSession, pertemuan_id: uuid.UUID
) -> Pertemuan:
    result = await db.execute(
        select(Pertemuan).where(Pertemuan.id == pertemuan_id)
    )
    pertemuan = result.scalar_one_or_none()
    if not pertemuan:
        raise NotFound("Pertemuan tidak ditemukan")
    return pertemuan


async def update_pertemuan(
    db: AsyncSession,
    pertemuan_id: uuid.UUID,
    *,
    tanggal_pertemuan: date | None = None,
    waktu_mulai_aktual: time | None = None,
    waktu_selesai_aktual: time | None = None,
    deskripsi: str | None = None,
    jenis_pertemuan: JenisPertemuanEnum | None = None,
) -> Pertemuan:
    pertemuan = await get_pertemuan_by_id(db, pertemuan_id)

    if tanggal_pertemuan is not None:
        pertemuan.tanggal_pertemuan = tanggal_pertemuan
    if waktu_mulai_aktual is not None:
        pertemuan.waktu_mulai_aktual = waktu_mulai_aktual
    if waktu_selesai_aktual is not None:
        pertemuan.waktu_selesai_aktual = waktu_selesai_aktual
    if deskripsi is not None:
        pertemuan.deskripsi = deskripsi
    if jenis_pertemuan is not None:
        pertemuan.jenis_pertemuan = jenis_pertemuan

    await db.commit()
    await db.refresh(pertemuan)
    return pertemuan


async def delete_pertemuan(
    db: AsyncSession, pertemuan_id: uuid.UUID
) -> None:
    pertemuan = await get_pertemuan_by_id(db, pertemuan_id)
    await db.delete(pertemuan)
    await db.commit()


async def rotate_token(
    db: AsyncSession, pertemuan_id: uuid.UUID
) -> Pertemuan:
    pertemuan = await get_pertemuan_by_id(db, pertemuan_id)
    pertemuan.token_presensi = _generate_token()
    pertemuan.token_expires_at = datetime.now(timezone.utc) + timedelta(minutes=2)
    await db.commit()
    await db.refresh(pertemuan)
    return pertemuan
