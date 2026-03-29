from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.features.auth.schemas import LoginRequest, RefreshRequest, RegisterRequest, TokenResponse
from app.features.auth.service import login_user, refresh_tokens, register_user
from app.features.users.schemas import UserRead

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


@router.post("/register", response_model=UserRead, status_code=201)
async def register(body: RegisterRequest, db: AsyncSession = Depends(get_db)):
    return await register_user(db, body.email, body.password)


@router.post("/login", response_model=TokenResponse)
async def login(body: LoginRequest, db: AsyncSession = Depends(get_db)):
    return await login_user(db, body.email, body.password)


@router.post("/refresh", response_model=TokenResponse)
async def refresh(body: RefreshRequest, db: AsyncSession = Depends(get_db)):
    return await refresh_tokens(db, body.refresh_token)
