from sqlmodel import Field, SQLModel


class Participant(SQLModel, table=True):
    user_id: int | None = Field(default=None, foreign_key="user.id", primary_key=True)
    project_id: int | None = Field(
        default=None, foreign_key="project.id", primary_key=True
    )


class TaskTagLink(SQLModel, table=True):
    task_id: int | None = Field(default=None, foreign_key="task.id", primary_key=True)
    tag_id: int | None = Field(default=None, foreign_key="tag.id", primary_key=True)


class ProjectTagLink(SQLModel, table=True):
    project: int | None = Field(
        default=None, foreign_key="project.id", primary_key=True
    )
    tag_id: int | None = Field(default=None, foreign_key="tag.id", primary_key=True)


class UserReactionLink(SQLModel, table=True):
    user_id: int | None = Field(default=None, foreign_key="user.id", primary_key=True)
    reaction_id: int | None = Field(
        default=None, foreign_key="reaction.id", primary_key=True
    )


class Assignee(SQLModel, table=True):
    user_id: int | None = Field(default=None, foreign_key="user.id", primary_key=True)
    task_id: int | None = Field(default=None, foreign_key="task.id", primary_key=True)
