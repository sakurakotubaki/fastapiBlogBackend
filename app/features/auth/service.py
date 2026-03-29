from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import BadRequestException, ConflictException, UnauthorizedException
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.features.auth.schemas import TokenResponse
from app.features.users.model import User
from app.features.users.service import get_user_by_email, get_user_by_id


async def register_user(db: AsyncSession, email: str, password: str) -> User:
    existing = await get_user_by_email(db, email)
    if existing:
        raise ConflictException(detail="Email already registered")
    user = User(email=email, hashed_password=hash_password(password))
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def login_user(db: AsyncSession, email: str, password: str) -> TokenResponse:
    user = await get_user_by_email(db, email)
    if not user or not verify_password(password, user.hashed_password):
        raise UnauthorizedException(detail="Incorrect email or password")
    if not user.is_active:
        raise UnauthorizedException(detail="User is inactive")
    return TokenResponse(
        access_token=create_access_token(user.id),
        refresh_token=create_refresh_token(user.id),
    )


async def refresh_tokens(db: AsyncSession, refresh_token: str) -> TokenResponse:
    payload = decode_token(refresh_token)
    if not payload or payload.get("type") != "refresh":
        raise BadRequestException(detail="Invalid refresh token")
    user = await get_user_by_id(db, payload["sub"])
    if not user.is_active:
        raise UnauthorizedException(detail="User is inactive")
    return TokenResponse(
        access_token=create_access_token(user.id),
        refresh_token=create_refresh_token(user.id),
    )
