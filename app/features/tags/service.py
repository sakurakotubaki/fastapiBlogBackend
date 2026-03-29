from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictException, NotFoundException
from app.features.tags.model import Tag


async def get_tags(db: AsyncSession) -> list[Tag]:
    result = await db.execute(select(Tag))
    return list(result.scalars().all())


async def get_tag_by_id(db: AsyncSession, tag_id: UUID) -> Tag:
    result = await db.execute(select(Tag).where(Tag.id == tag_id))
    tag = result.scalar_one_or_none()
    if not tag:
        raise NotFoundException(detail="Tag not found")
    return tag


async def create_tag(db: AsyncSession, name: str) -> Tag:
    existing = await db.execute(select(Tag).where(Tag.name == name))
    if existing.scalar_one_or_none():
        raise ConflictException(detail="Tag already exists")
    tag = Tag(name=name)
    db.add(tag)
    await db.commit()
    await db.refresh(tag)
    return tag


async def delete_tag(db: AsyncSession, tag_id: UUID) -> None:
    tag = await get_tag_by_id(db, tag_id)
    await db.delete(tag)
    await db.commit()
