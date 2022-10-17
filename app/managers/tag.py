from .base import Manager
from app.models import Tag, TagCreate, TagRead


class TagManager(Manager):
    model = Tag
    in_schema: TagCreate
    read_schema: TagRead
