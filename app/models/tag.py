from typing import TYPE_CHECKING, Optional
from fastapi_permissions import Allow
from sqlmodel import Field, Relationship, SQLModel

from app.models import Timestamped
from app.models.link_tables import TaskTagLink

if TYPE_CHECKING:
    from app.models import Task, User


class TagBase(SQLModel):
    name: str = Field(index=True)
    color: str | None = None


class Tag(TagBase, Timestamped, table=True):
    id: int | None = Field(default=None, primary_key=True)

    owner_id: int | None = Field(default=None, foreign_key="user.id")
    owner: Optional["User"] = Relationship(back_populates="tags")

    tasks: Optional["Task"] = Relationship(
        back_populates="tags", link_model=TaskTagLink
    )

    def __acl__(self):
        return [
            (Allow, f"user:{self.owner_id}", "view"),
            (Allow, f"user:{self.owner_id}", "edit"),
            (Allow, f"user:{self.owner_id}", "delete"),
        ]


class TagCreate(TagBase):
    owner_id: int | None = None


class TagRead(TagBase):
    id: int


class TagReadDetail(TagRead):
    from app.models.task import TaskRead

    owner: int  # TODO UserRead
    tasks: list[TaskRead]


class TagUpdate(SQLModel):
    name: str | None = None
    color: str | None = None
