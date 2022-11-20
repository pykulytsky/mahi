from app.models import Tag, TagCreate, TagRead

from .base import Manager


class TagManager(Manager):
    model = Tag
    in_schema: TagCreate
    read_schema: TagRead
