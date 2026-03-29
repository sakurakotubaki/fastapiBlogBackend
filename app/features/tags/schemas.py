from uuid import UUID

from pydantic import BaseModel


class TagCreate(BaseModel):
    name: str


class TagRead(BaseModel):
    id: UUID
    name: str

    model_config = {"from_attributes": True}
