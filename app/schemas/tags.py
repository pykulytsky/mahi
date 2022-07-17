from pydantic import BaseModel


class TagBase(BaseModel):
    color: str | None = None
    name: str | None = None


class TagCreate(TagBase):
    name: str


class TagUpdate(TagBase):
    pass


class Tag(TagBase):
    id: int
    projects: list[int]

    class Config:
        orm_mode = True
