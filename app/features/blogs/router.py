from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.features.auth.dependencies import get_current_user
from app.features.blogs.schemas import BlogCreate, BlogRead, BlogUpdate
from app.features.blogs.service import create_blog, delete_blog, get_blog_by_id, get_blogs, update_blog
from app.features.users.model import User

router = APIRouter(prefix="/api/v1/blogs", tags=["blogs"])


@router.post("/", response_model=BlogRead, status_code=201)
async def add_blog(
    body: BlogCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await create_blog(db, body.title, body.body, current_user.id, body.tag_ids)


@router.get("/", response_model=List[BlogRead])
async def list_blogs(
    skip: int = 0,
    limit: int = Query(default=20, le=100),
    tag: Optional[str] = None,
    search: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    return await get_blogs(db, skip=skip, limit=limit, tag_name=tag, search=search)


@router.get("/{blog_id}", response_model=BlogRead)
async def read_blog(blog_id: UUID, db: AsyncSession = Depends(get_db)):
    return await get_blog_by_id(db, blog_id)


@router.put("/{blog_id}", response_model=BlogRead)
async def edit_blog(
    blog_id: UUID,
    body: BlogUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await update_blog(db, blog_id, current_user, body.title, body.body, body.tag_ids)


@router.delete("/{blog_id}", status_code=204)
async def remove_blog(
    blog_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await delete_blog(db, blog_id, current_user)
