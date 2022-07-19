from pydantic import BaseModel


class TagBase(BaseModel):
    color: str | None = None
    name: str | None = None


class TagCreate(TagBase):
    name: str


class TagUpdate(TagBase):
    pass


class TagInDB(TagBase):
    id: int

    class Config:
        orm_mode = True


class Tag(TagInDB):
    pass
