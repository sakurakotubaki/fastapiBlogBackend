from typing import List, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.exceptions import ForbiddenException, NotFoundException
from app.features.blogs.model import Blog
from app.features.tags.model import Tag
from app.features.users.model import User


async def _load_tags(db: AsyncSession, tag_ids: List[UUID]) -> List[Tag]:
    if not tag_ids:
        return []
    result = await db.execute(select(Tag).where(Tag.id.in_(tag_ids)))
    tags = list(result.scalars().all())
    if len(tags) != len(tag_ids):
        raise NotFoundException(detail="One or more tags not found")
    return tags


def _check_permission(blog: Blog, user: User) -> None:
    if blog.author_id != user.id and not user.is_superuser:
        raise ForbiddenException(detail="Not authorized to modify this blog")


async def create_blog(
    db: AsyncSession, title: str, body: str, author_id: UUID, tag_ids: List[UUID]
) -> Blog:
    tags = await _load_tags(db, tag_ids)
    blog = Blog(title=title, body=body, author_id=author_id, tags=tags)
    db.add(blog)
    await db.commit()
    await db.refresh(blog)
    return await get_blog_by_id(db, blog.id)


async def get_blogs(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 20,
    tag_name: Optional[str] = None,
    search: Optional[str] = None,
) -> List[Blog]:
    query = select(Blog).options(selectinload(Blog.tags)).offset(skip).limit(limit)
    if tag_name:
        query = query.join(Blog.tags).where(Tag.name == tag_name)
    if search:
        escaped = search.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
        query = query.where(Blog.title.ilike(f"%{escaped}%", escape="\\"))
    query = query.order_by(Blog.created_at.desc())
    result = await db.execute(query)
    return list(result.scalars().unique().all())


async def get_blog_by_id(db: AsyncSession, blog_id: UUID) -> Blog:
    result = await db.execute(
        select(Blog).options(selectinload(Blog.tags)).where(Blog.id == blog_id)
    )
    blog = result.scalar_one_or_none()
    if not blog:
        raise NotFoundException(detail="Blog not found")
    return blog


async def update_blog(
    db: AsyncSession,
    blog_id: UUID,
    user: User,
    title: Optional[str] = None,
    body: Optional[str] = None,
    tag_ids: Optional[List[UUID]] = None,
) -> Blog:
    blog = await get_blog_by_id(db, blog_id)
    _check_permission(blog, user)
    if title is not None:
        blog.title = title
    if body is not None:
        blog.body = body
    if tag_ids is not None:
        blog.tags = await _load_tags(db, tag_ids)
    await db.commit()
    return await get_blog_by_id(db, blog_id)


async def delete_blog(db: AsyncSession, blog_id: UUID, user: User) -> None:
    blog = await get_blog_by_id(db, blog_id)
    _check_permission(blog, user)
    await db.delete(blog)
    await db.commit()
