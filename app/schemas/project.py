from typing import List, Optional

from pydantic import BaseModel


class ProjectBase(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    icon: Optional[str] = None
    accent_color: Optional[str] = None


class ProjectCreate(ProjectBase):
    name: str


class ProjectUpdate(ProjectBase):
    is_favorite: Optional[bool] = False
    is_pinned: Optional[bool] = False


class ProjectInDBBase(ProjectBase):
    id: Optional[int] = None
    tags: Optional[List[int]] = None

    class Config:
        orm_mode = True


class Project(ProjectInDBBase):
    owner_id: int
