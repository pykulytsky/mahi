from typing import Optional, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship
from app.models.base import Timestamped

if TYPE_CHECKING:
    from app.models import User, Reaction, Project, Task


class CommentBase(SQLModel):
    body: str | None = None
    reason: str | None = None


class Comment(CommentBase, Timestamped, table=True):
    id: int | None = Field(default=None, primary_key=True)

    owner_id: int | None = Field(default=None, foreign_key="user.id")
    owner: Optional["User"] = Relationship(back_populates="comments")

    project_id: int | None = Field(default=None, foreign_key="project.id")
    project: Optional["Project"] = Relationship(back_populates="comments")

    task_id: int | None = Field(default=None, foreign_key="task.id")
    task: Optional["Task"] = Relationship(back_populates="comments")

    parent_comment_id: int | None = Field(default=None, foreign_key="comment.id")
    parent: Optional["Comment"] = Relationship(
        back_populates="comments", sa_relationship_kwargs=dict(remote_side="Comment.id")
    )
    comments: list["Comment"] = Relationship(back_populates="parent")
    reactions: list["Reaction"] = Relationship(back_populates="comment")


class CommentCreate(CommentBase):
    owner_id: int | None = None
    body: str | None = None
    reason: str | None = None

    parent_comment_id: int | None = None


class CommentRead(CommentBase):
    pass
