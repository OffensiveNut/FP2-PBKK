from collections.abc import AsyncGenerator

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import AsyncSessionLocal
from app.core.exceptions import Forbidden, Unauthorized
from app.core.security import decode_access_token
from app.models.user import User

bearer_scheme = HTTPBearer()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    token = credentials.credentials
    try:
        payload = decode_access_token(token)
    except Exception:
        raise Unauthorized("Invalid or expired token")

    user_id: str | None = payload.get("sub")
    if user_id is None:
        raise Unauthorized("Token missing subject")

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if user is None:
        raise Unauthorized("User not found")
    return user


async def require_admin(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != "ADMIN":
        raise Forbidden("Admin access required")
    return current_user


async def require_guru(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != "GURU":
        raise Forbidden("Guru access required")
    return current_user


async def require_siswa(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != "SISWA":
        raise Forbidden("Siswa access required")
    return current_user


async def require_guru_or_admin(
    current_user: User = Depends(get_current_user),
) -> User:
    if current_user.role not in ("GURU", "ADMIN"):
        raise Forbidden("Guru or Admin access required")
    return current_user
