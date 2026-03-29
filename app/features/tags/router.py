from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.features.auth.dependencies import require_superuser
from app.features.tags.schemas import TagCreate, TagRead
from app.features.tags.service import create_tag, delete_tag, get_tags
from app.features.users.model import User

router = APIRouter(prefix="/api/v1/tags", tags=["tags"])


@router.get("/", response_model=list[TagRead])
async def list_tags(db: AsyncSession = Depends(get_db)):
    return await get_tags(db)


@router.post("/", response_model=TagRead, status_code=201)
async def add_tag(
    body: TagCreate,
    _: User = Depends(require_superuser),
    db: AsyncSession = Depends(get_db),
):
    return await create_tag(db, body.name)


@router.delete("/{tag_id}", status_code=204)
async def remove_tag(
    tag_id: UUID,
    _: User = Depends(require_superuser),
    db: AsyncSession = Depends(get_db),
):
    await delete_tag(db, tag_id)
