from pydantic import BaseModel
from datetime import datetime

from .users import User


class ReactionBase(BaseModel):
    emoji: str
    task_id: int


class ReactionCreate(ReactionBase):
    pass


class ReactionInDB(ReactionBase):
    id: int
    created: datetime
    updated: datetime
    users: list[User]

    class Config:
        orm_mode = True


class Reaction(ReactionInDB):
    pass


class ReactionUserCreate(BaseModel):
    reaction_id: int
