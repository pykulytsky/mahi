from datetime import datetime

from pydantic import BaseModel, EmailStr


# Shared properties
class UserBase(BaseModel):
    email: EmailStr | None = None
    first_name: str | None = None
    last_name: str | None = None
    avatar: str | None = None
    tasks_goal_per_day: int | None = None


class UserCreate(UserBase):
    email: EmailStr
    password: str


class UserUpdate(UserBase):
    password: str | None = None


class UserInDBBase(UserBase):
    id: int | None = None
    email_verified: bool | None = False

    class Config:
        orm_mode = True


# Additional properties to return via API
class User(UserInDBBase):
    def principals(self):
        return [f"user:{self.id}"]


# Additional properties stored in DB
class UserInDB(UserInDBBase):
    password: str


class Activity(BaseModel):
    id: int
    journal_id: int | None = None
    action: str
    created: datetime

    project_id: int | None = None
    task_id: int | None = None
    tag_id: int | None = None

    actor: User

    class Config:
        orm_mode = True
