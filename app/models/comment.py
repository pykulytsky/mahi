from sqlmodel import SQLModel


class CommentBase(SQLModel):
    body: str
