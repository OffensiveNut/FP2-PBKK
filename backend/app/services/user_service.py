import csv
import io
import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import Conflict, NotFound
from app.core.security import hash_password
from app.models.user import RoleEnum, User
from app.schemas.user import UserCreate, UserUpdate


async def create_user(db: AsyncSession, data: UserCreate) -> User:
    existing = await get_user_by_username(db, data.username)
    if existing:
        raise Conflict("Username already taken")
    existing = await get_user_by_email(db, data.email)
    if existing:
        raise Conflict("Email already registered")

    user = User(
        username=data.username,
        email=data.email,
        password_hash=hash_password(data.password),
        role=data.role,
        nama_lengkap=data.nama_lengkap,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def get_user_by_id(db: AsyncSession, user_id: uuid.UUID) -> User | None:
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()


async def get_user_by_username(db: AsyncSession, username: str) -> User | None:
    result = await db.execute(
        select(User).where(User.username == username)
    )
    return result.scalar_one_or_none()


async def get_user_by_email(db: AsyncSession, email: str) -> User | None:
    result = await db.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()


async def get_users(
    db: AsyncSession, skip: int = 0, limit: int = 100
) -> list[User]:
    result = await db.execute(
        select(User).offset(skip).limit(limit)
    )
    return list(result.scalars().all())


async def update_user(
    db: AsyncSession, user_id: uuid.UUID, data: UserUpdate
) -> User:
    user = await get_user_by_id(db, user_id)
    if not user:
        raise NotFound("User not found")

    update_data = data.model_dump(exclude_unset=True)
    if "password" in update_data:
        update_data["password_hash"] = hash_password(update_data.pop("password"))

    for field, value in update_data.items():
        setattr(user, field, value)

    await db.commit()
    await db.refresh(user)
    return user


async def delete_user(db: AsyncSession, user_id: uuid.UUID) -> None:
    user = await get_user_by_id(db, user_id)
    if not user:
        raise NotFound("User not found")
    await db.delete(user)
    await db.commit()


async def bulk_create_users(
    db: AsyncSession, csv_content: str
) -> list[User]:
    reader = csv.DictReader(io.StringIO(csv_content))
    users: list[User] = []
    for row in reader:
        user = User(
            username=row["username"],
            email=row["email"],
            password_hash=hash_password(row["password"]),
            role=RoleEnum(row["role"]),
            nama_lengkap=row["nama_lengkap"],
        )
        db.add(user)
        users.append(user)
    await db.commit()
    for user in users:
        await db.refresh(user)
    return users
