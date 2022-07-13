from typing import List, Optional

from pydantic import BaseModel


class TagBase(BaseModel):
    color: Optional[str] = None
    name: Optional[str] = None


class TagCreate(TagBase):
    name: str


class TagUpdate(TagBase):
    pass


class Tag(TagBase):
    id: int
    projects: List[int]

    class Config:
        orm_mode = True
