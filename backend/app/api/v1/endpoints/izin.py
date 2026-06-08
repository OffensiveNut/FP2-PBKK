import uuid

from fastapi import APIRouter, Depends, File, UploadFile
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.deps import get_db, get_current_user, require_guru_or_admin
from app.core.exceptions import Forbidden, NotFound
from app.models.izin import Izin, StatusApprovalEnum
from app.models.pertemuan import Pertemuan
from app.models.user import User
from app.schemas.izin import IzinResponse
from app.services.file_service import save_upload

router = APIRouter()


class IzinCreateRequest(BaseModel):
    pertemuan_id: uuid.UUID
    alasan: str
    file_bukti: str | None = None


class IzinUpdateStatusRequest(BaseModel):
    pass


@router.post("/upload")
async def upload_bukti(
    file: UploadFile = File(...),
    _: User = Depends(get_current_user),
) -> dict[str, str]:
    filepath = await save_upload(file)
    return {"file_bukti": filepath}


@router.post("/", response_model=IzinResponse, status_code=201)
async def create_izin(
    data: IzinCreateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> IzinResponse:
    result = await db.execute(
        select(Pertemuan).where(Pertemuan.id == data.pertemuan_id)
    )
    if not result.scalar_one_or_none():
        raise NotFound("Pertemuan tidak ditemukan")

    izin = Izin(
        pertemuan_id=data.pertemuan_id,
        siswa_id=current_user.id,
        alasan=data.alasan,
        file_bukti=data.file_bukti,
    )
    db.add(izin)
    await db.commit()
    await db.refresh(izin)
    return IzinResponse.model_validate(izin)


@router.get("/", response_model=list[IzinResponse])
async def list_izin(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[IzinResponse]:
    if current_user.role in ("GURU", "ADMIN"):
        result = await db.execute(
            select(Izin).options(selectinload(Izin.siswa), selectinload(Izin.pertemuan))
        )
        izin_list = result.scalars().all()
    else:
        result = await db.execute(
            select(Izin)
            .where(Izin.siswa_id == current_user.id)
            .options(selectinload(Izin.siswa), selectinload(Izin.pertemuan))
        )
        izin_list = result.scalars().all()
    return [IzinResponse.model_validate(i) for i in izin_list]


@router.get("/{izin_id}", response_model=IzinResponse)
async def get_izin(
    izin_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> IzinResponse:
    result = await db.execute(
        select(Izin)
        .where(Izin.id == izin_id)
        .options(selectinload(Izin.siswa), selectinload(Izin.pertemuan))
    )
    izin = result.scalar_one_or_none()
    if not izin:
        raise NotFound("Izin tidak ditemukan")
    if current_user.role == "SISWA" and izin.siswa_id != current_user.id:
        raise Forbidden("Anda hanya dapat melihat izin sendiri")
    return IzinResponse.model_validate(izin)


@router.put("/{izin_id}/approve", response_model=IzinResponse)
async def approve_izin(
    izin_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_guru_or_admin),
) -> IzinResponse:
    result = await db.execute(select(Izin).where(Izin.id == izin_id))
    izin = result.scalar_one_or_none()
    if not izin:
        raise NotFound("Izin tidak ditemukan")
    izin.status_approval = StatusApprovalEnum.APPROVED
    await db.commit()
    await db.refresh(izin)
    return IzinResponse.model_validate(izin)


@router.put("/{izin_id}/reject", response_model=IzinResponse)
async def reject_izin(
    izin_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_guru_or_admin),
) -> IzinResponse:
    result = await db.execute(select(Izin).where(Izin.id == izin_id))
    izin = result.scalar_one_or_none()
    if not izin:
        raise NotFound("Izin tidak ditemukan")
    izin.status_approval = StatusApprovalEnum.REJECTED
    await db.commit()
    await db.refresh(izin)
    return IzinResponse.model_validate(izin)
