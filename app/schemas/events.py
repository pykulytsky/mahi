from pydantic import BaseModel


class Message(BaseModel):
    event: str
    body: dict
