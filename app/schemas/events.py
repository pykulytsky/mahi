from datetime import datetime
from pydantic import BaseModel


class Message(BaseModel):
    event: str
    body: dict
    dt: str = str(datetime.now())
