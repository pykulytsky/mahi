from .base import Manager
from app.models import Reaction, ReactionCreate, ReactionRead


class ReactionManager(Manager):
    model = Reaction
    in_schema = ReactionCreate
    read_schema = ReactionRead
