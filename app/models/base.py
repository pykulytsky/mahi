from datetime import datetime
from sqlmodel import SQLModel, Field


class Timestamped(SQLModel):
    created: datetime = Field(default=datetime.utcnow())
    updated: datetime = Field(default_factory=datetime.now)
