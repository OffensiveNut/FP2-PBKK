import uuid
from datetime import datetime, time, timedelta, timezone

from fastapi import APIRouter, Depends

WIB = timezone(timedelta(hours=7))
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, get_current_user, require_guru_or_admin
from app.models.pertemuan import JenisPertemuanEnum
from app.models.user import User
from app.schemas.pertemuan import (
    PertemuanGenerateResponse,
    PertemuanResponse,
    PertemuanUpdate,
)
from app.services.pertemuan_service import (
    delete_pertemuan,
    generate_pertemuan,
    get_or_create_today_pertemuan,
    get_pertemuan_by_id,
    get_pertemuan_by_kelas,
    rotate_token,
    update_pertemuan,
)

router = APIRouter()


@router.post("/generate/{kelas_id}", response_model=PertemuanGenerateResponse, status_code=201)
async def generate_pertemuan_endpoint(
    kelas_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_guru_or_admin),
) -> PertemuanGenerateResponse:
    created = await generate_pertemuan(db, kelas_id, created_by=current_user.id)
    return PertemuanGenerateResponse(
        kelas_id=kelas_id,
        jumlah_pertemuan=len(created),
        pertemuan=[PertemuanResponse.model_validate(p) for p in created],
    )


@router.get("/kelas/{kelas_id}", response_model=list[PertemuanResponse])
async def list_by_kelas(
    kelas_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
) -> list[PertemuanResponse]:
    pertemuan_list = await get_pertemuan_by_kelas(db, kelas_id)
    return [PertemuanResponse.model_validate(p) for p in pertemuan_list]


@router.get("/{pertemuan_id}", response_model=PertemuanResponse)
async def get_pertemuan(
    pertemuan_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
) -> PertemuanResponse:
    pertemuan = await get_pertemuan_by_id(db, pertemuan_id)
    return PertemuanResponse.model_validate(pertemuan)


@router.put("/{pertemuan_id}", response_model=PertemuanResponse)
async def update_pertemuan_endpoint(
    pertemuan_id: uuid.UUID,
    data: PertemuanUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_guru_or_admin),
) -> PertemuanResponse:
    pertemuan = await update_pertemuan(
        db,
        pertemuan_id,
        tanggal_pertemuan=data.tanggal_pertemuan,
        waktu_mulai_aktual=data.waktu_mulai_aktual,
        waktu_selesai_aktual=data.waktu_selesai_aktual,
        deskripsi=data.deskripsi,
        jenis_pertemuan=data.jenis_pertemuan,
    )
    return PertemuanResponse.model_validate(pertemuan)


@router.delete("/{pertemuan_id}", status_code=204)
async def delete_pertemuan_endpoint(
    pertemuan_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_guru_or_admin),
) -> None:
    await delete_pertemuan(db, pertemuan_id)


@router.post("/{kelas_id}/generate-token", response_model=PertemuanResponse, status_code=201)
async def generate_token_endpoint(
    kelas_id: uuid.UUID,
    jenis_pertemuan: JenisPertemuanEnum = JenisPertemuanEnum.OFFLINE,
    waktu_selesai: str | None = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_guru_or_admin),
) -> PertemuanResponse:
    waktu_selesai_time = None
    if waktu_selesai:
        try:
            waktu_selesai_time = time.fromisoformat(waktu_selesai)
        except Exception:
            waktu_selesai_time = None
    pertemuan = await get_or_create_today_pertemuan(
        db, kelas_id, created_by=current_user.id, jenis_pertemuan=jenis_pertemuan, waktu_selesai=waktu_selesai_time
    )
    return PertemuanResponse.model_validate(pertemuan)


@router.post("/{pertemuan_id}/rotate-token", response_model=PertemuanResponse)
async def rotate_token_endpoint(
    pertemuan_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_guru_or_admin),
) -> PertemuanResponse:
    pertemuan = await get_pertemuan_by_id(db, pertemuan_id)
    if pertemuan.waktu_selesai_aktual:
        selesai_dt = datetime.combine(pertemuan.tanggal_pertemuan, pertemuan.waktu_selesai_aktual).replace(tzinfo=WIB)
        if datetime.now(timezone.utc) > selesai_dt:
            from app.core.exceptions import Forbidden
            raise Forbidden("Waktu pertemuan telah selesai, tidak dapat merotasi token")
    pertemuan = await rotate_token(db, pertemuan_id)
    return PertemuanResponse.model_validate(pertemuan)
