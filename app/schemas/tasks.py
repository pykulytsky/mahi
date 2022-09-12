from datetime import date, datetime

from pydantic import BaseModel

from .tags import TagInDB


class TaskBase(BaseModel):
    description: str | None = None
    deadline: date | None = None
    name: str | None = None
    priority: str | None = None
    done_at: datetime | None = None
    color: str | None = None
    is_important: bool | None = False
    remind_at: datetime | None = None
    order: int | None = None


class TaskCreate(TaskBase):
    name: str
    project_id: int | None = None
    section_id: int | None = None


class TaskUpdate(TaskBase):
    is_done: bool | None = True
    project_id: int | None = None
    section_id: int | None = None


class TaskInDBBase(TaskBase):
    id: int | None = None
    is_done: bool
    order: int
    created: datetime
    updated: datetime

    class Config:
        orm_mode = True


class Task(TaskInDBBase):
    tags: list[TagInDB] | None = None


class TaskJSONSerializable(BaseModel):
    id: int
    name: str
    project_id: int
    is_important: bool
    is_done: bool

    class Config:
        orm_mode = True


class TaskReorder(BaseModel):
    source_id: int
    source_type: str
    destination_id: int
    destination_type: str
    order: int
