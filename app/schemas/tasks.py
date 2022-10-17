from datetime import date, datetime

from fastapi_permissions import Allow, Authenticated
from pydantic import BaseModel

from .reactions import Reaction
from .tags import TagInDB


class TaskBase(BaseModel):
    description: str | None = None
    deadline: date | None = None
    name: str | None = None
    priority: str | None = None
    completed_at: datetime | None = None
    color: str | None = None
    is_important: bool | None = False
    remind_at: datetime | None = None
    order: int | None = None


class TaskCreate(TaskBase):
    name: str
    project_id: int | None = None
    section_id: int | None = None
    owner_id: int | None = None


class TaskUpdate(TaskBase):
    is_completed: bool | None = True
    project_id: int | None = None
    section_id: int | None = None


class TaskInDBBase(TaskBase):
    id: int | None = None
    is_completed: bool
    order: int
    created: datetime
    updated: datetime

    class Config:
        orm_mode = True


class TaskPreview(BaseModel):
    id: int
    is_completed: int
    order: int

    class Config:
        orm_mode = True


class TaskOwner(BaseModel):
    id: int
    email: str
    avatar: str | None = None
    first_name: str | None = None
    last_name: str | None = None

    class Config:
        orm_mode = True


class Task(TaskInDBBase):
    tags: list[TagInDB] | None = None
    project_id: int | None = None
    section_id: int | None = None
    reactions: list[Reaction]
    owner: TaskOwner | None = None


class Project(BaseModel):
    id: int
    name: str
    owner: TaskOwner
    participants: list[TaskOwner]
    accent_color: str | None = None

    class Config:
        orm_mode = True


class Section(BaseModel):
    id: int
    name: str
    project: Project

    class Config:
        orm_mode = True


class TaskDetail(TaskInDBBase):
    reactions: list[Reaction]
    owner: TaskOwner | None = None
    tags: list[TagInDB] | None = None
    project: Project | None = None
    section: Section | None = None

    def __acl__(self):
        acl_list = []

        if self.owner:
            acl_list.extend(
                [
                    (Allow, f"user:{self.owner.id}", "view"),
                    (Allow, f"user:{self.owner.id}", "edit"),
                    (Allow, f"user:{self.owner.id}", "delete"),
                ]
            )
        else:
            acl_list.append((Allow, Authenticated, "delete"))  # TODO delete

        if self.project:
            acl_list.append((Allow, f"user:{self.project.owner.id}", "view"))
            acl_list.append((Allow, f"user:{self.project.owner.id}", "view"))
            acl_list.append((Allow, f"user:{self.project.owner.id}", "view"))
            for p in self.project.participants:
                acl_list.append((Allow, f"user:{p.id}", "view"))
                acl_list.append((Allow, f"user:{p.id}", "edit"))

        else:
            acl_list.append((Allow, f"user:{self.section.project.owner.id}", "view"))
            acl_list.append((Allow, f"user:{self.section.project.owner.id}", "view"))
            acl_list.append((Allow, f"user:{self.section.project.owner.id}", "view"))
            for p in self.section.project.participants:
                acl_list.append((Allow, f"user:{p.id}", "view"))
                acl_list.append((Allow, f"user:{p.id}", "edit"))

        return acl_list


class TaskJSONSerializable(BaseModel):
    id: int
    name: str
    project_id: int
    is_important: bool
    is_completed: bool

    class Config:
        orm_mode = True


class TaskReorder(BaseModel):
    source_id: int
    source_type: str
    destination_id: int
    destination_type: str
    order: int
