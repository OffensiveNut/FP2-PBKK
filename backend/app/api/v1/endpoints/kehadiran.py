import uuid

from fastapi import APIRouter, Depends
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.deps import get_db, get_current_user, require_guru_or_admin, require_siswa
from app.core.exceptions import NotFound
from app.models.kehadiran import Kehadiran, StatusHadirEnum
from app.models.kelas import Kelas
from app.models.pertemuan import Pertemuan
from app.models.user import User
from app.schemas.kehadiran import KehadiranResponse
from app.services.kehadiran_service import (
    get_kehadiran_by_pertemuan,
    get_kehadiran_by_siswa,
    mark_kehadiran_manual,
    submit_kehadiran_token,
)
from app.utils.csv_exporter import export_kehadiran_to_csv

router = APIRouter()


class TokenSubmitRequest(BaseModel):
    pertemuan_id: uuid.UUID
    token: str


class ManualMarkRequest(BaseModel):
    pertemuan_id: uuid.UUID
    siswa_id: uuid.UUID
    status_hadir: StatusHadirEnum


@router.post("/token", response_model=KehadiranResponse, status_code=201)
async def submit_token(
    data: TokenSubmitRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> KehadiranResponse:
    kehadiran = await submit_kehadiran_token(
        db, pertemuan_id=data.pertemuan_id, siswa_id=current_user.id, token=data.token
    )
    return KehadiranResponse.model_validate(kehadiran)


@router.post("/manual", response_model=KehadiranResponse, status_code=201)
async def mark_manual(
    data: ManualMarkRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_guru_or_admin),
) -> KehadiranResponse:
    kehadiran = await mark_kehadiran_manual(
        db,
        pertemuan_id=data.pertemuan_id,
        siswa_id=data.siswa_id,
        status_hadir=data.status_hadir,
        guru_id=current_user.id,
    )
    return KehadiranResponse.model_validate(kehadiran)


@router.get("/pertemuan/{pertemuan_id}", response_model=list[KehadiranResponse])
async def list_by_pertemuan(
    pertemuan_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_guru_or_admin),
) -> list[KehadiranResponse]:
    kehadiran_list = await get_kehadiran_by_pertemuan(db, pertemuan_id)
    return [KehadiranResponse.model_validate(k) for k in kehadiran_list]


@router.get("/siswa/{siswa_id}", response_model=list[KehadiranResponse])
async def list_by_siswa(
    siswa_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[KehadiranResponse]:
    if current_user.id != siswa_id and current_user.role == "SISWA":
        from app.core.exceptions import Forbidden
        raise Forbidden("Anda hanya dapat melihat presensi sendiri")
    kehadiran_list = await get_kehadiran_by_siswa(db, siswa_id)
    return [KehadiranResponse.model_validate(k) for k in kehadiran_list]


@router.get("/export/pertemuan/{pertemuan_id}")
async def export_pertemuan_csv(
    pertemuan_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_guru_or_admin),
) -> PlainTextResponse:
    result = await db.execute(
        select(Pertemuan).where(Pertemuan.id == pertemuan_id)
    )
    pertemuan = result.scalar_one_or_none()
    if not pertemuan:
        raise NotFound("Pertemuan tidak ditemukan")

    kehadiran_list = await get_kehadiran_by_pertemuan(db, pertemuan_id)
    csv_content = export_kehadiran_to_csv(kehadiran_list)
    return PlainTextResponse(
        csv_content,
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=rekap_pertemuan_{pertemuan_id}.csv"},
    )


@router.get("/export/kelas/{kelas_id}")
async def export_kelas_csv(
    kelas_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_guru_or_admin),
) -> PlainTextResponse:
    result = await db.execute(
        select(Kelas).where(Kelas.id == kelas_id)
        .options(selectinload(Kelas.pertemuan))
    )
    kelas = result.scalar_one_or_none()
    if not kelas:
        raise NotFound("Kelas tidak ditemukan")

    pertemuan_ids = [p.id for p in kelas.pertemuan]
    if not pertemuan_ids:
        return PlainTextResponse(
            "Nama Siswa,Username,NIS,Kelas,Tanggal Pertemuan,Deskripsi Pertemuan,Status Hadir,Metode Presensi,Waktu Presensi\n",
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename=rekap_kelas_{kelas_id}.csv"},
        )

    result = await db.execute(
        select(Kehadiran)
        .where(Kehadiran.pertemuan_id.in_(pertemuan_ids))
        .options(
            selectinload(Kehadiran.siswa),
            selectinload(Kehadiran.pertemuan).selectinload(Pertemuan.kelas),
        )
    )
    kehadiran_list = list(result.scalars().all())
    csv_content = export_kehadiran_to_csv(kehadiran_list, kelas=kelas)
    return PlainTextResponse(
        csv_content,
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=rekap_kelas_{kelas_id}.csv"},
    )
