from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlmodel import Field, Relationship, SQLModel

from app.models.base import Timestamped

from .link_tables import Participant
from .task import TaskRead

if TYPE_CHECKING:
    from app.models import Section, Task, User


class ProjectBase(SQLModel):
    name: str = Field(index=True)
    description: str | None = Field(default=None, index=True)

    is_favorite: bool = Field(default=False)
    is_editable: bool = Field(default=True)
    deadline: datetime | None = Field(default=None)

    accent_color: str | None = Field(default=None)
    icon: str | None = Field(default=None)
    show_completed_tasks: bool = Field(default=False)


class Project(ProjectBase, Timestamped, table=True):
    id: int | None = Field(default=None, primary_key=True)

    owner_id: int | None = Field(default=None, foreign_key="user.id")
    owner: Optional["User"] = Relationship(back_populates="projects")
    participants: list["User"] = Relationship(
        back_populates="participated_projects", link_model=Participant
    )

    tasks: list["Task"] = Relationship(back_populates="project")
    sections: list["Section"] = Relationship(back_populates="project")


class ProjectCreate(ProjectBase):
    pass


class ProjectRead(ProjectBase):
    id: int


class ProjectReadDetail(ProjectRead):
    from app.models.user import UserRead

    tasks: list[TaskRead]
    owner: UserRead


class ProjectUpdate(SQLModel):
    name: str | None = None
    description: str | None = None
    deadline: datetime | None = None
    accent_color: str | None = None
    icon: str | None = None

    is_favorite: bool | None = False
    is_editable: bool | None = True
    show_completed_tasks: bool | None = False
