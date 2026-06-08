import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.exceptions import Conflict, NotFound
from app.models.kelas import Kelas
from app.models.user import User
from app.schemas.kelas import KelasCreate, KelasUpdate
from app.services.user_service import get_user_by_id


async def create_kelas(db: AsyncSession, data: KelasCreate) -> Kelas:
    kelas = Kelas(
        semester_id=data.semester_id,
        nama_kelas=data.nama_kelas,
        deskripsi=data.deskripsi,
    )
    db.add(kelas)
    await db.commit()
    await db.refresh(kelas)
    return kelas


async def get_kelas_by_id(db: AsyncSession, kelas_id: uuid.UUID) -> Kelas | None:
    result = await db.execute(
        select(Kelas)
        .where(Kelas.id == kelas_id)
        .options(selectinload(Kelas.gurus), selectinload(Kelas.siswas))
    )
    return result.scalar_one_or_none()


async def get_kelas_list(
    db: AsyncSession, skip: int = 0, limit: int = 100
) -> list[Kelas]:
    result = await db.execute(select(Kelas).offset(skip).limit(limit))
    return list(result.scalars().all())


async def update_kelas(
    db: AsyncSession, kelas_id: uuid.UUID, data: KelasUpdate
) -> Kelas:
    kelas = await get_kelas_by_id(db, kelas_id)
    if not kelas:
        raise NotFound("Kelas not found")

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(kelas, field, value)

    await db.commit()
    await db.refresh(kelas)
    return kelas


async def delete_kelas(db: AsyncSession, kelas_id: uuid.UUID) -> None:
    kelas = await get_kelas_by_id(db, kelas_id)
    if not kelas:
        raise NotFound("Kelas not found")
    await db.delete(kelas)
    await db.commit()


async def add_guru_to_kelas(
    db: AsyncSession, kelas_id: uuid.UUID, guru_id: uuid.UUID
) -> Kelas:
    kelas = await get_kelas_by_id(db, kelas_id)
    if not kelas:
        raise NotFound("Kelas not found")

    guru = await get_user_by_id(db, guru_id)
    if not guru:
        raise NotFound("Guru not found")

    if guru in kelas.gurus:
        raise Conflict("Guru already in kelas")

    kelas.gurus.append(guru)
    await db.commit()
    await db.refresh(kelas)
    return kelas


async def remove_guru_from_kelas(
    db: AsyncSession, kelas_id: uuid.UUID, guru_id: uuid.UUID
) -> Kelas:
    kelas = await get_kelas_by_id(db, kelas_id)
    if not kelas:
        raise NotFound("Kelas not found")

    guru = await get_user_by_id(db, guru_id)
    if not guru:
        raise NotFound("Guru not found")

    if guru not in kelas.gurus:
        raise NotFound("Guru not in kelas")

    kelas.gurus.remove(guru)
    await db.commit()
    await db.refresh(kelas)
    return kelas


async def add_siswa_to_kelas(
    db: AsyncSession, kelas_id: uuid.UUID, siswa_id: uuid.UUID
) -> Kelas:
    kelas = await get_kelas_by_id(db, kelas_id)
    if not kelas:
        raise NotFound("Kelas not found")

    siswa = await get_user_by_id(db, siswa_id)
    if not siswa:
        raise NotFound("Siswa not found")

    if siswa in kelas.siswas:
        raise Conflict("Siswa already in kelas")

    kelas.siswas.append(siswa)
    await db.commit()
    await db.refresh(kelas)
    return kelas


async def remove_siswa_from_kelas(
    db: AsyncSession, kelas_id: uuid.UUID, siswa_id: uuid.UUID
) -> Kelas:
    kelas = await get_kelas_by_id(db, kelas_id)
    if not kelas:
        raise NotFound("Kelas not found")

    siswa = await get_user_by_id(db, siswa_id)
    if not siswa:
        raise NotFound("Siswa not found")

    if siswa not in kelas.siswas:
        raise NotFound("Siswa not in kelas")

    kelas.siswas.remove(siswa)
    await db.commit()
    await db.refresh(kelas)
    return kelas
