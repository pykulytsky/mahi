from pydantic import BaseModel
from fastapi_permissions import Allow

from .section import Section
from .tasks import Task


class ProjectBase(BaseModel):
    name: str | None = None
    description: str | None = None
    icon: str | None = None
    accent_color: str | None = None
    is_favorite: bool | None = False
    is_pinned: bool | None = False
    is_editable: bool | None = True
    show_completed_tasks: bool | None = True


class ProjectCreate(ProjectBase):
    name: str


class ProjectUpdate(ProjectBase):
    pass


class ProjectInDBBase(ProjectBase):
    id: int | None = None
    tags: list[int] | None = None

    class Config:
        orm_mode = True


class Participant(BaseModel):
    id: int

    class Config:
        orm_mode = True


class Project(ProjectInDBBase):
    owner_id: int
    tasks: list[Task]
    sections: list[Section]
    participants: list[Participant]

    def __acl__(self):
        acl_list = [
            (Allow, f"user:{self.owner_id}", "view"),
            (Allow, f"user:{self.owner_id}", "edit"),
            (Allow, f"user:{self.owner_id}", "delete"),
        ]
        for p in self.participants:
            acl_list.append((Allow, f"user:{p.id}", "view"))
            acl_list.append((Allow, f"user:{p.id}", "edit"))

        return acl_list
