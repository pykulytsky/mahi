from typing import TYPE_CHECKING

from pydantic import EmailStr
from sqlmodel import Field, Relationship, SQLModel

from .link_tables import Assignee, Participant, UserReactionLink

if TYPE_CHECKING:
    from app.models import Project, Reaction, Tag, Task


class UserBase(SQLModel):
    email: EmailStr = Field(index=True)
    first_name: str
    last_name: str


class User(UserBase, table=True):
    id: int | None = Field(default=None, primary_key=True)

    password: str
    is_active: bool = Field(default=True)

    projects: list["Project"] = Relationship(back_populates="owner")
    tags: list["Tag"] = Relationship(back_populates="owner")
    tasks: list["Task"] = Relationship(back_populates="owner")
    assigned_tasks: list["Task"] = Relationship(
        back_populates="assigned_to", link_model=Assignee
    )

    participated_projects: list["Project"] = Relationship(
        back_populates="participants", link_model=Participant
    )
    reactions: list["Reaction"] = Relationship(
        back_populates="users", link_model=UserReactionLink
    )


class UserCreate(UserBase):
    password: str


class UserRead(UserBase):
    id: int
    is_active: bool


class UserReadDetail(UserBase):
    from app.models.project import ProjectRead
    from app.models.reaction import ReactionRead
    from app.models.tag import TagRead
    from app.models.task import TaskRead

    projects: list[ProjectRead]
    participated_projects: list[ProjectRead]
    tags: list[TagRead]
    tasks: list[TaskRead]
    assigned_tasks: list[TaskRead]
    reactions: list[ReactionRead]


class UserUpdate(SQLModel):
    email: EmailStr | None = None
    first_name: str | None = None
    last_name: str | None = None
