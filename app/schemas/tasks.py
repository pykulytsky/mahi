from datetime import date

from pydantic import BaseModel


class TaskBase(BaseModel):
    description: str | None = None
    deadline: date | None = None
    name: str | None = None


class TaskCreate(TaskBase):
    name: str
    project_id: int


class TaskUpdate(TaskBase):
    is_done: bool | None = True


class TaskInDBBase(TaskBase):
    id: int | None = None
    project_id: int

    class Config:
        orm_mode = True


class Task(TaskInDBBase):
    pass
