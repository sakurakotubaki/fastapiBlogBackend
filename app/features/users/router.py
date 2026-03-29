from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.features.auth.dependencies import get_current_user, require_superuser
from app.features.users.model import User
from app.features.users.schemas import UserRead, UserUpdate
from app.features.users.service import delete_user, get_user_by_id, get_users, update_user

router = APIRouter(prefix="/api/v1/users", tags=["users"])


@router.get("/me", response_model=UserRead)
async def read_me(current_user: User = Depends(get_current_user)):
    return current_user


@router.put("/me", response_model=UserRead)
async def update_me(
    body: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await update_user(db, current_user, email=body.email)


@router.get("/", response_model=list[UserRead])
async def list_users(
    skip: int = 0,
    limit: int = 100,
    _: User = Depends(require_superuser),
    db: AsyncSession = Depends(get_db),
):
    return await get_users(db, skip=skip, limit=limit)


@router.get("/{user_id}", response_model=UserRead)
async def read_user(
    user_id: UUID,
    _: User = Depends(require_superuser),
    db: AsyncSession = Depends(get_db),
):
    return await get_user_by_id(db, user_id)


@router.delete("/{user_id}", status_code=204)
async def remove_user(
    user_id: UUID,
    _: User = Depends(require_superuser),
    db: AsyncSession = Depends(get_db),
):
    await delete_user(db, user_id)
