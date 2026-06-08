import uuid

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, require_admin
from app.core.exceptions import NotFound
from app.models.semester_config import SemesterConfig
from app.models.user import User
from app.schemas.semester_config import (
    SemesterConfigCreate,
    SemesterConfigResponse,
    SemesterConfigUpdate,
)

router = APIRouter()


@router.get("/", response_model=list[SemesterConfigResponse])
async def list_semesters(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),
) -> list[SemesterConfigResponse]:
    result = await db.execute(
        select(SemesterConfig).offset(skip).limit(limit)
    )
    return [SemesterConfigResponse.model_validate(s) for s in result.scalars().all()]


@router.post("/", response_model=SemesterConfigResponse, status_code=201)
async def create_semester(
    data: SemesterConfigCreate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),
) -> SemesterConfigResponse:
    semester = SemesterConfig(**data.model_dump())
    db.add(semester)
    await db.commit()
    await db.refresh(semester)
    return SemesterConfigResponse.model_validate(semester)


@router.get("/{semester_id}", response_model=SemesterConfigResponse)
async def get_semester(
    semester_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),
) -> SemesterConfigResponse:
    result = await db.execute(
        select(SemesterConfig).where(SemesterConfig.id == semester_id)
    )
    semester = result.scalar_one_or_none()
    if not semester:
        raise NotFound("Semester not found")
    return SemesterConfigResponse.model_validate(semester)


@router.put("/{semester_id}", response_model=SemesterConfigResponse)
async def update_semester(
    semester_id: uuid.UUID,
    data: SemesterConfigUpdate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),
) -> SemesterConfigResponse:
    result = await db.execute(
        select(SemesterConfig).where(SemesterConfig.id == semester_id)
    )
    semester = result.scalar_one_or_none()
    if not semester:
        raise NotFound("Semester not found")

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(semester, field, value)

    await db.commit()
    await db.refresh(semester)
    return SemesterConfigResponse.model_validate(semester)


@router.delete("/{semester_id}", status_code=204)
async def delete_semester(
    semester_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),
) -> None:
    result = await db.execute(
        select(SemesterConfig).where(SemesterConfig.id == semester_id)
    )
    semester = result.scalar_one_or_none()
    if not semester:
        raise NotFound("Semester not found")
    await db.delete(semester)
    await db.commit()
