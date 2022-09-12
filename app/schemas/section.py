from datetime import datetime

from pydantic import BaseModel

from .tasks import Task


class SectionBase(BaseModel):
    name: str | None = None
    order: int | None = None
    project_id: int | None = None


class SectionCreate(SectionBase):
    name: str
    project_id: int


class SectionUpdate(SectionBase):
    project_id: int | None = None


class SectionInDBBase(SectionBase):
    id: int | None = None
    project_id: int
    order: int
    created: datetime
    updated: datetime

    class Config:
        orm_mode = True


class Section(SectionInDBBase):
    tasks: list[Task]
