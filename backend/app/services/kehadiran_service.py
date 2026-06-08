import random
import string
import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import Conflict, Forbidden, NotFound
from app.models.kehadiran import Kehadiran, MetodePresensiEnum, StatusHadirEnum
from app.models.kelas import kelas_siswa
from app.models.pertemuan import Pertemuan

TOKEN_LENGTH = 6
TOKEN_ROTATION_MINUTES = 2


def _generate_token() -> str:
    return "".join(random.choices(string.digits, k=TOKEN_LENGTH))


async def rotate_token(db: AsyncSession, pertemuan: Pertemuan) -> Pertemuan:
    pertemuan.token_presensi = _generate_token()
    pertemuan.token_expires_at = datetime.now(timezone.utc) + timedelta(
        minutes=TOKEN_ROTATION_MINUTES
    )
    await db.commit()
    await db.refresh(pertemuan)
    return pertemuan


async def refresh_token_if_expired(
    db: AsyncSession, pertemuan: Pertemuan
) -> Pertemuan:
    if datetime.now(timezone.utc) >= pertemuan.token_expires_at:
        pertemuan = await rotate_token(db, pertemuan)
    return pertemuan


async def _check_siswa_in_kelas(
    db: AsyncSession, siswa_id: uuid.UUID, kelas_id: uuid.UUID
) -> None:
    result = await db.execute(
        select(kelas_siswa).where(
            kelas_siswa.c.siswa_id == siswa_id,
            kelas_siswa.c.kelas_id == kelas_id,
        )
    )
    if not result.scalar_one_or_none():
        raise Forbidden("Siswa tidak terdaftar di kelas ini")


async def _check_duplicate_kehadiran(
    db: AsyncSession, pertemuan_id: uuid.UUID, siswa_id: uuid.UUID
) -> None:
    result = await db.execute(
        select(Kehadiran).where(
            Kehadiran.pertemuan_id == pertemuan_id,
            Kehadiran.siswa_id == siswa_id,
        )
    )
    if result.scalar_one_or_none():
        raise Conflict("Siswa sudah melakukan presensi untuk pertemuan ini")


async def submit_kehadiran_token(
    db: AsyncSession,
    pertemuan_id: uuid.UUID,
    siswa_id: uuid.UUID,
    token: str,
) -> Kehadiran:
    result = await db.execute(
        select(Pertemuan).where(Pertemuan.id == pertemuan_id)
    )
    pertemuan = result.scalar_one_or_none()
    if not pertemuan:
        raise NotFound("Pertemuan tidak ditemukan")

    if datetime.now(timezone.utc) >= pertemuan.token_expires_at:
        await rotate_token(db, pertemuan)
        raise Conflict("Token sudah kadaluarsa, silakan minta token baru")

    if pertemuan.token_presensi != token:
        raise Conflict("Token yang dimasukkan salah")

    await _check_siswa_in_kelas(db, siswa_id, pertemuan.kelas_id)
    await _check_duplicate_kehadiran(db, pertemuan_id, siswa_id)

    kehadiran = Kehadiran(
        pertemuan_id=pertemuan_id,
        siswa_id=siswa_id,
        status_hadir=StatusHadirEnum.HADIR,
        metode_presensi=MetodePresensiEnum.TOKEN,
    )
    db.add(kehadiran)
    await db.commit()
    await db.refresh(kehadiran)
    return kehadiran


async def mark_kehadiran_manual(
    db: AsyncSession,
    pertemuan_id: uuid.UUID,
    siswa_id: uuid.UUID,
    status_hadir: StatusHadirEnum,
    *,
    guru_id: uuid.UUID,
) -> Kehadiran:
    result = await db.execute(
        select(Pertemuan).where(Pertemuan.id == pertemuan_id)
    )
    pertemuan = result.scalar_one_or_none()
    if not pertemuan:
        raise NotFound("Pertemuan tidak ditemukan")

    await _check_siswa_in_kelas(db, siswa_id, pertemuan.kelas_id)
    await _check_duplicate_kehadiran(db, pertemuan_id, siswa_id)

    kehadiran = Kehadiran(
        pertemuan_id=pertemuan_id,
        siswa_id=siswa_id,
        status_hadir=status_hadir,
        metode_presensi=MetodePresensiEnum.MANUAL,
    )
    db.add(kehadiran)
    await db.commit()
    await db.refresh(kehadiran)
    return kehadiran


async def get_kehadiran_by_pertemuan(
    db: AsyncSession, pertemuan_id: uuid.UUID
) -> list[Kehadiran]:
    result = await db.execute(
        select(Kehadiran).where(Kehadiran.pertemuan_id == pertemuan_id)
    )
    return list(result.scalars().all())


async def get_kehadiran_by_siswa(
    db: AsyncSession, siswa_id: uuid.UUID
) -> list[Kehadiran]:
    result = await db.execute(
        select(Kehadiran).where(Kehadiran.siswa_id == siswa_id)
    )
    return list(result.scalars().all())
