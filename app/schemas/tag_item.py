from pydantic import BaseModel


class TagItemBase(BaseModel):
    task_id: int
    tag_id: int


class TagItemCreate(TagItemBase):
    pass


class TagItem(TagItemBase):
    id: int

    class Config:
        orm_mode = True
