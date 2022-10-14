from typing import TYPE_CHECKING, Optional
from sqlmodel import SQLModel, Field, Relationship

from app.models.link_tables import UserReactionLink

if TYPE_CHECKING:
    from app.models import Task, User


class ReactionBase(SQLModel):
    emoji: str


class Reaction(ReactionBase, table=True):
    id: int | None = Field(default=None, primary_key=True)

    task_id: int | None = Field(default=None, foreign_key="task.id")
    task: Optional["Task"] = Relationship(back_populates="reactions")

    users: list["User"] = Relationship(
        back_populates="reactions", link_model=UserReactionLink)


class ReactionCreate(ReactionBase):
    task_id: int


class ReactionRead(ReactionBase):
    users: list  # TODO UserRead


class ReactionReadDetail(ReactionRead):
    task: int | None = None  # TODO TaskRead


class ReactionUpdate(SQLModel):
    emoji: str | None = None
