from typing import TYPE_CHECKING, Optional

from sqlmodel import Field, Relationship, SQLModel

from app.models.link_tables import UserReactionLink

if TYPE_CHECKING:
    from app.models import Task, User, Comment


class ReactionBase(SQLModel):
    emoji: str


class Reaction(ReactionBase, table=True):
    id: int | None = Field(default=None, primary_key=True)

    task_id: int | None = Field(default=None, foreign_key="task.id")
    task: Optional["Task"] = Relationship(back_populates="reactions")

    comment_id: int | None = Field(default=None, foreign_key="comment.id")
    comment: Optional["Comment"] = Relationship(back_populates="reactions")

    users: list["User"] = Relationship(
        back_populates="reactions", link_model=UserReactionLink
    )


class ReactionCreate(ReactionBase):
    task_id: int


class ReactionRead(ReactionBase):
    id: int
    users: list  # TODO UserRead
    task_id: int | None = None


class ReactionReadDetail(ReactionRead):
    task: int | None = None  # TODO TaskRead


class ReactionUpdate(SQLModel):
    emoji: str | None = None
