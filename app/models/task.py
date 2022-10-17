from datetime import date
from typing import TYPE_CHECKING, Optional

from fastapi_permissions import Allow
from sqlmodel import Field, Relationship, SQLModel

from app.models import Timestamped
from app.models.link_tables import Assignee, TaskTagLink

if TYPE_CHECKING:
    from app.models import Project, Reaction, Section, Tag, User


class TaskBase(SQLModel):
    name: str = Field(index=True)
    description: str | None = Field(default=None)
    order: int = Field(index=True, default=0)
    deadline: date | None = Field(default=None)


class Task(TaskBase, Timestamped, table=True):
    id: int | None = Field(default=None, primary_key=True)

    project_id: int | None = Field(default=None, foreign_key="project.id")
    project: Optional["Project"] = Relationship(back_populates="tasks")
    section_id: int | None = Field(default=None, foreign_key="section.id")
    section: Optional["Section"] = Relationship(back_populates="tasks")
    tags: Optional["Tag"] = Relationship(back_populates="tasks", link_model=TaskTagLink)
    reactions: list["Reaction"] = Relationship(back_populates="task")

    owner_id: int | None = Field(default=None, foreign_key="user.id")
    owner: Optional["User"] = Relationship(back_populates="tasks")
    assigned_to: list["User"] = Relationship(
        back_populates="assigned_tasks", link_model=Assignee
    )

    def __acl__(self):
        acl_list = [
            (Allow, f"user:{self.owner_id}", "view"),
            (Allow, f"user:{self.owner_id}", "edit"),
            (Allow, f"user:{self.owner_id}", "assign"),
            (Allow, f"user:{self.owner_id}", "complete"),
            (Allow, f"user:{self.owner_id}", "delete"),
        ]
        if self.project:
            for p in self.project.participants:
                acl_list.append((Allow, f"user:{p.id}", "view"))
                acl_list.append((Allow, f"user:{p.id}", "edit"))
        elif self.section:
            for p in self.section.project.participants:
                acl_list.append((Allow, f"user:{p.id}", "view"))
                acl_list.append((Allow, f"user:{p.id}", "edit"))

        return acl_list


class TaskCreate(TaskBase):
    order: int | None = None
    project_id: int | None = None
    section_id: int | None = None
    owner_id: int | None = None


class TaskRead(TaskBase):
    id: int


class TaskReadDetail(TaskRead):
    from app.models.reaction import ReactionRead
    from app.models.section import SectionRead
    from app.models.tag import TagRead

    section: SectionRead | None = None
    tags: list[TagRead]
    reactions: list[ReactionRead]


class TaskUpdate(SQLModel):
    name: str | None = None
    description: str | None = None
    order: int | None = None
    project_id: int | None = None
    section_id: int | None = None


class TaskReorder(SQLModel):
    source_id: int
    source_type: str
    destination_id: int
    destination_type: str
    order: int
