from app.models import Reaction, ReactionCreate, ReactionRead

from .base import Manager


class ReactionManager(Manager):
    model = Reaction
    in_schema = ReactionCreate
    read_schema = ReactionRead
