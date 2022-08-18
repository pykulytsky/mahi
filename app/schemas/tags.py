from datetime import date, datetime

from pydantic import BaseModel


class TaskBase(BaseModel):
    description: str | None = None
    deadline: date | None = None
    name: str | None = None
    priority: str | None = None
    done_at: datetime | None = None
    color: str | None = None


class TaskCreate(TaskBase):
    name: str
    project_id: int | None = None


class TaskUpdate(TaskBase):
    is_done: bool | None = True


class TaskInDBBase(TaskBase):
    id: int | None = None
    is_done: bool
    created: datetime
    updated: datetime

    class Config:
        orm_mode = True


class Task(TaskInDBBase):
    pass


class TagBase(BaseModel):
    color: str | None = None
    name: str | None = None


class TagCreate(TagBase):
    name: str


class TagUpdate(TagBase):
    pass


class TagInDB(TagBase):
    id: int

    class Config:
        orm_mode = True


class Tag(TagInDB):
    tasks: list[Task]
