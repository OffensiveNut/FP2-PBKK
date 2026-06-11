import uuid
from datetime import time

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db, require_admin, require_guru_or_admin
from app.core.exceptions import NotFound
from app.models.jadwal_kelas import JadwalKelas
from app.models.kelas import Kelas
from app.models.user import User
from app.schemas.jadwal_kelas import (
    JadwalKelasCreate,
    JadwalKelasResponse,
    JadwalKelasUpdate,
)
from app.schemas.kelas import KelasCreate, KelasResponse, KelasUpdate
from app.services.kelas_service import (
    add_guru_to_kelas,
    add_siswa_to_kelas,
    create_kelas,
    delete_kelas,
    get_kelas_by_id,
    get_kelas_list,
    remove_guru_from_kelas,
    remove_siswa_from_kelas,
    update_kelas,
)

router = APIRouter()


class MemberRequest(BaseModel):
    user_id: uuid.UUID


@router.get("/", response_model=list[KelasResponse])
async def list_kelas(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
) -> list[KelasResponse]:
    kelas_list = await get_kelas_list(db, skip=skip, limit=limit)
    return [KelasResponse.model_validate(k) for k in kelas_list]


@router.post("/", response_model=KelasResponse, status_code=201)
async def create_kelas_endpoint(
    data: KelasCreate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),
) -> KelasResponse:
    kelas = await create_kelas(db, data)
    return KelasResponse.model_validate(kelas)


@router.get("/{kelas_id}", response_model=KelasResponse)
async def get_kelas(
    kelas_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
) -> KelasResponse:
    kelas = await get_kelas_by_id(db, kelas_id)
    if not kelas:
        raise NotFound("Kelas not found")
    return KelasResponse.model_validate(kelas)


@router.put("/{kelas_id}", response_model=KelasResponse)
async def update_kelas_endpoint(
    kelas_id: uuid.UUID,
    data: KelasUpdate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),
) -> KelasResponse:
    kelas = await update_kelas(db, kelas_id, data)
    return KelasResponse.model_validate(kelas)


@router.delete("/{kelas_id}", status_code=204)
async def delete_kelas_endpoint(
    kelas_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),
) -> None:
    await delete_kelas(db, kelas_id)


@router.post("/{kelas_id}/guru", response_model=KelasResponse)
async def add_guru(
    kelas_id: uuid.UUID,
    data: MemberRequest,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),
) -> KelasResponse:
    kelas = await add_guru_to_kelas(db, kelas_id, data.user_id)
    return KelasResponse.model_validate(kelas)


@router.delete("/{kelas_id}/guru/{guru_id}", response_model=KelasResponse)
async def remove_guru(
    kelas_id: uuid.UUID,
    guru_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),
) -> KelasResponse:
    kelas = await remove_guru_from_kelas(db, kelas_id, guru_id)
    return KelasResponse.model_validate(kelas)


@router.post("/{kelas_id}/siswa", response_model=KelasResponse)
async def add_siswa(
    kelas_id: uuid.UUID,
    data: MemberRequest,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),
) -> KelasResponse:
    kelas = await add_siswa_to_kelas(db, kelas_id, data.user_id)
    return KelasResponse.model_validate(kelas)


@router.delete("/{kelas_id}/siswa/{siswa_id}", response_model=KelasResponse)
async def remove_siswa(
    kelas_id: uuid.UUID,
    siswa_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),
) -> KelasResponse:
    kelas = await remove_siswa_from_kelas(db, kelas_id, siswa_id)
    return KelasResponse.model_validate(kelas)


@router.get("/{kelas_id}/jadwal", response_model=list[JadwalKelasResponse])
async def list_jadwal_kelas(
    kelas_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
) -> list[JadwalKelasResponse]:
    result = await db.execute(
        select(JadwalKelas).where(JadwalKelas.kelas_id == kelas_id)
    )
    return [JadwalKelasResponse.model_validate(j) for j in result.scalars().all()]


@router.post("/{kelas_id}/jadwal", response_model=JadwalKelasResponse, status_code=201)
async def create_jadwal_kelas(
    kelas_id: uuid.UUID,
    data: JadwalKelasCreate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),
) -> JadwalKelasResponse:
    kelas = await get_kelas_by_id(db, kelas_id)
    if not kelas:
        raise NotFound("Kelas not found")

    jadwal = JadwalKelas(
        kelas_id=kelas_id,
        hari=data.hari,
        waktu_mulai=data.waktu_mulai,
        waktu_selesai=data.waktu_selesai,
    )
    db.add(jadwal)
    await db.commit()
    await db.refresh(jadwal)
    return JadwalKelasResponse.model_validate(jadwal)


@router.put("/{kelas_id}/jadwal/{jadwal_id}", response_model=JadwalKelasResponse)
async def update_jadwal_kelas(
    kelas_id: uuid.UUID,
    jadwal_id: uuid.UUID,
    data: JadwalKelasUpdate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),
) -> JadwalKelasResponse:
    result = await db.execute(
        select(JadwalKelas).where(
            JadwalKelas.id == jadwal_id, JadwalKelas.kelas_id == kelas_id
        )
    )
    jadwal = result.scalar_one_or_none()
    if not jadwal:
        raise NotFound("Jadwal not found")

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(jadwal, field, value)

    await db.commit()
    await db.refresh(jadwal)
    return JadwalKelasResponse.model_validate(jadwal)


@router.delete("/{kelas_id}/jadwal/{jadwal_id}", status_code=204)
async def delete_jadwal_kelas(
    kelas_id: uuid.UUID,
    jadwal_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),
) -> None:
    result = await db.execute(
        select(JadwalKelas).where(
            JadwalKelas.id == jadwal_id, JadwalKelas.kelas_id == kelas_id
        )
    )
    jadwal = result.scalar_one_or_none()
    if not jadwal:
        raise NotFound("Jadwal not found")
    await db.delete(jadwal)
    await db.commit()
