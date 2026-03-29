from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictException, NotFoundException
from app.features.users.model import User


async def get_user_by_id(db: AsyncSession, user_id: UUID) -> User:
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise NotFoundException(detail="User not found")
    return user


async def get_user_by_email(db: AsyncSession, email: str) -> Optional[User]:
    result = await db.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()


async def get_users(db: AsyncSession, skip: int = 0, limit: int = 100) -> list[User]:
    result = await db.execute(select(User).offset(skip).limit(limit))
    return list(result.scalars().all())


async def update_user(db: AsyncSession, user: User, email: Optional[str] = None) -> User:
    if email and email != user.email:
        existing = await get_user_by_email(db, email)
        if existing:
            raise ConflictException(detail="Email already registered")
        user.email = email
    await db.commit()
    await db.refresh(user)
    return user


async def delete_user(db: AsyncSession, user_id: UUID) -> None:
    user = await get_user_by_id(db, user_id)
    await db.delete(user)
    await db.commit()
