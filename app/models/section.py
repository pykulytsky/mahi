from typing import TYPE_CHECKING, Optional

from fastapi_permissions import Allow
from sqlmodel import Field, Relationship, SQLModel

from app.models import Timestamped

if TYPE_CHECKING:
    from app.models import Project, Task, User


class SectionBase(SQLModel):
    name: str = Field(index=True)
    order: int | None = Field(index=True, default=0)


class Section(SectionBase, Timestamped, table=True):
    id: int | None = Field(default=None, primary_key=True)

    owner_id: int | None = Field(default=None, foreign_key="user.id")
    owner: Optional["User"] = Relationship(back_populates="sections")

    project_id: int | None = Field(default=False, foreign_key="project.id")
    project: Optional["Project"] = Relationship(back_populates="sections")

    tasks: list["Task"] = Relationship(
        back_populates="section", sa_relationship_kwargs={"order_by": "Task.order"}
    )

    def __acl__(self):
        acl_list = [
            (Allow, f"user:{self.owner_id}", "view"),
            (Allow, f"user:{self.owner_id}", "invite"),
            (Allow, f"user:{self.owner_id}", "edit"),
            (Allow, f"user:{self.owner_id}", "delete"),
        ]
        for p in self.project.participants:
            acl_list.append((Allow, f"user:{p.id}", "view"))
            acl_list.append((Allow, f"user:{p.id}", "edit"))

        return acl_list


class SectionCreate(SectionBase):
    project_id: int
    owner_id: int | None = None
    order: int | None = None


class SectionRead(SectionBase):
    id: int
    project_id: int


class SectionReadDetail(SectionBase):
    from app.models.task import TaskRead

    id: int
    project_id: int
    tasks: list[TaskRead]


class SectionUpdate(SQLModel):
    name: str | None = None
    order: int | None = None
