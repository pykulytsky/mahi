# Import all the models, so that Base has them before being
# imported by Alembic
from app.models.user import User  # noqa
from app.models.todo import Project, Tag, TagItem, TodoItem

from .base_class import Base  # noqa
