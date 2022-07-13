from typing import Optional
from datetime import datetime
from pydantic import BaseModel


class TodoItemBase(BaseModel):
    description: Optional[str] = None
    deadline: Optional[datetime] = None
    name: Optional[str] = None


class TodoItemCreate(TodoItemBase):
    name: str
    project_id: int


class TodoItemUpdate(TodoItemBase):
    is_done: Optional[bool] = True


class TodoItemInDBBase(TodoItemBase):
    id: Optional[int] = None
    project_id: int

    class Config:
        orm_mode = True


class TodoItem(TodoItemInDBBase):
    pass
