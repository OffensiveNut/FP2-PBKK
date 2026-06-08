import uuid

from fastapi import APIRouter, Depends, File, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, get_current_user, require_admin
from app.core.exceptions import NotFound
from app.models.user import User
from app.schemas.user import UserCreate, UserCreateResponse, UserResponse, UserUpdate
from app.services.user_service import (
    bulk_create_users,
    create_user,
    delete_user,
    get_user_by_id,
    get_users,
    update_user,
)

router = APIRouter()


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)) -> UserResponse:
    return UserResponse.model_validate(current_user)


@router.get("/", response_model=list[UserResponse])
async def list_users(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),
) -> list[UserResponse]:
    users = await get_users(db, skip=skip, limit=limit)
    return [UserResponse.model_validate(u) for u in users]


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),
) -> UserResponse:
    user = await get_user_by_id(db, user_id)
    if not user:
        raise NotFound("User not found")
    return UserResponse.model_validate(user)


@router.post("/", response_model=UserCreateResponse, status_code=201)
async def create_user_endpoint(
    data: UserCreate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),
) -> UserCreateResponse:
    user, generated_password = await create_user(db, data)
    return UserCreateResponse(
        **UserResponse.model_validate(user).model_dump(),
        generated_password=generated_password,
    )


@router.put("/{user_id}", response_model=UserResponse)
async def update_user_endpoint(
    user_id: uuid.UUID,
    data: UserUpdate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),
) -> UserResponse:
    user = await update_user(db, user_id, data)
    return UserResponse.model_validate(user)


@router.delete("/{user_id}", status_code=204)
async def delete_user_endpoint(
    user_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),
) -> None:
    await delete_user(db, user_id)


@router.post("/bulk", response_model=list[UserResponse], status_code=201)
async def bulk_create(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),
) -> list[UserResponse]:
    content = (await file.read()).decode()
    users = await bulk_create_users(db, content)
    return [UserResponse.model_validate(u) for u in users]
