from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel

from app.features.tags.schemas import TagRead


class BlogCreate(BaseModel):
    title: str
    body: str
    tag_ids: List[UUID] = []


class BlogUpdate(BaseModel):
    title: Optional[str] = None
    body: Optional[str] = None
    tag_ids: Optional[List[UUID]] = None


class BlogRead(BaseModel):
    id: UUID
    title: str
    body: str
    author_id: UUID
    tags: List[TagRead] = []
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
