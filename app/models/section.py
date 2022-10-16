from typing import TYPE_CHECKING, Optional
from sqlmodel import Field, Relationship, SQLModel

from app.models import Timestamped

if TYPE_CHECKING:
    from app.models import Project, Task


class SectionBase(SQLModel):
    name: str = Field(index=True)
    order: int = Field(index=True)


class Section(SectionBase, Timestamped, table=True):
    id: int | None = Field(default=None, primary_key=True)

    project_id: int | None = Field(default=False, foreign_key="project.id")
    project: Optional["Project"] = Relationship(back_populates="sections")

    tasks: list["Task"] = Relationship(back_populates="section")


class SectionCreate(SectionBase):
    project_id: int
    order: int | None = None


class SectionRead(SectionBase):
    id: int


class SectionReadDetail(SectionRead):
    from app.models.task import TaskRead

    tasks: list[TaskRead]


class SectionUpdate(SQLModel):
    name: str | None = None
    order: int | None = None
