from pydantic import BaseModel
from .tasks import Task


class ProjectBase(BaseModel):
    name: str | None = None
    description: str | None = None
    icon: str | None = None
    accent_color: str | None = None
    is_favorite: bool | None = False
    is_pinned: bool | None = False
    is_editable: bool | None = False


class ProjectCreate(ProjectBase):
    name: str


class ProjectUpdate(ProjectBase):
    pass


class ProjectInDBBase(ProjectBase):
    id: int | None = None
    tags: list[int] | None = None

    class Config:
        orm_mode = True


class Project(ProjectInDBBase):
    owner_id: int
    tasks: list[Task]
